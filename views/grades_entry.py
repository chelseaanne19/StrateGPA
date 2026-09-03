import streamlit as st
import pandas as pd
from database import (
    get_modules_dataframe,
    get_user_settings,
    update_assessment_grade,
    get_assessments_from
)
import streamlit_shadcn_ui as ui
from helper_functions import shadcn_text, set_page

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 1. PAGE SETUP
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
st.set_page_config(page_title = "StrateGPA: Log Grades", layout = "wide")
set_page("Log Achieved Grades", "Update your results here as soon as you receive them to keep your target GPA / Honours predictions accurate.")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 2. LOAD SETTINGS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
user_profile = get_user_settings()
df_modules = get_modules_dataframe()
selected_semester = ui.select("Select Semester:", options = ["Autumn", "Spring"])
ui.separator()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 3. LOAD MODULES AND THEIR RESPECTIVE ASSESSMENTS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if df_modules.empty:
    st.info("No courses registered yet. Please navigate to **Module and Assessment Registration** to add modules and assessments")
else:
    semester_modules = df_modules[df_modules["Semester"] == selected_semester]
    if semester_modules.empty:
        st.warning(f"No registered modules located for {selected_semester}.")
    else:
        for idx, row in semester_modules.iterrows():
            code = row["Module Code"]
            title = row["Module Title"]

            with st.expander(f"**{code}: {title}**"):
                df_ass = get_assessments_from(code)

                if df_ass.empty:
                    st.caption("No assessments logged for this module yet.")
                else:
                    for a_idx, a_row in df_ass.iterrows():
                        a_id = int(a_row["Assessment ID"])
                        a_title = a_row["Assessment Title"]
                        weight = float(a_row["Weight %"])
                    
                        current_grade_raw = a_row.get("Result")

                        if current_grade_raw is None or pd.isna(current_grade_raw):
                            is_graded = False
                            default_val = 0.0
                        else:
                            try:
                                default_val = float(current_grade_raw)
                                is_graded = True
                            except (ValueError, TypeError):
                                clean_str = str(a_row.get("Result", "Pending")).replace("%", "").strip()
                                if clean_str != "Pending" and clean_str != "":
                                    default_val = float(clean_str)
                                    is_graded = True
                                else:
                                    is_graded = False
                                    default_val = 0.0

                        col_info, col_input = st.columns([1, 1])
                        with col_info:
                            st.write("")
                            st.write("")
                            shadcn_text(f"{a_title}", variant = "subheading", color = "sky")
                            shadcn_text(f"{weight:.0f}% of module", variant = "subheading", color = "navy")

                            if is_graded:
                                st.write("")
                                shadcn_text(f"Current recorded result: {default_val}", variant = "subheading", color = "grey")
                            else:
                                st.write("")
                                shadcn_text("Pending Grade ....", variant = "subheading", color = "grey")

                        with col_input:
                            with st.form(key = f"grade_submission_form_{a_id}"):

                                new_score = st.number_input(
                                    "Achieved Mark (%):",
                                    min_value = 0.0,
                                    max_value = 100.0,
                                    value = default_val,
                                    step = 0.5,
                                    key = f"input_score_{a_id}",
                                    label_visibility = "collapsed"
                                )

                                col_save, col_clear = st.columns([1, 1])
                                with col_save:
                                    if st.form_submit_button("Save", use_container_width = True, type = "primary"):
                                        success = update_assessment_grade(a_id, new_score)
                                        if success:
                                            st.toast("Saved!", duration = "long")
                                            st.rerun()
                                        else:
                                            st.error("Error saving.")

                                with col_clear:
                                    if st.form_submit_button("Clear", use_container_width = True):
                                        success = update_assessment_grade(a_id, None)
                                        if success:
                                            st.toast("Grade Cleared!", duration = "long")
                                            st.rerun()
                                        else:
                                            st.error("Error clearing grade.")