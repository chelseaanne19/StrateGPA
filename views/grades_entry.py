import streamlit as st
import pandas as pd
from database import (
    get_modules_dataframe,
    get_user_settings,
    update_assessment_grade,
    get_assessments_from
)

st.set_page_config(page_title = "StrateGPA: Log Grades", layout = "wide")

st.title("Log Achieved Grades")
st.caption("Update your results here as soon as you receive them to keep your target GPA predictions accurate.")
st.write("____")

user_profile = get_user_settings()
selected_semester = st.selectbox("Select Semester:", options = ["Autumn", "Spring"])

df_modules = get_modules_dataframe()
if df_modules.empty:
    st.info("No courses registered yet. Please navigate to **Module and Assessment Registration** to add modules and assessments")
else:
    semester_modules = df_modules[df_modules["Trimester"] == selected_semester]

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
                    st.write("**Assessments:**")

                    for a_idx, a_row in df_ass.iterrows():
                        a_id = int(a_row["id"])
                        a_title = a_row["assessment_title"]
                        weight = float(a_row["assessment_percentage"])
                        current_grade = a_row["received_grade"]
                        is_graded = pd.notna(current_grade)

                        col_info, col_input = st.columns([1, 1])
                        with col_info:
                            st.write("")
                            st.markdown(f":blue[**{a_title}**]: **{weight:.0f}% of module**")

                            if is_graded:
                                st.caption(f"Current recorded result: **{current_grade:.1f}**")
                            else:
                                st.caption("Pending Grade ....")

                        with col_input:
                            with st.form(key = f"grade_submission_form_{a_id}"):
                                default_val = float(current_grade) if is_graded else 0.0

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

            st.space("small")