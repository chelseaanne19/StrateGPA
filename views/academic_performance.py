import streamlit as st
import pandas as pd
from database import get_modules_dataframe, get_user_settings
from gpa_calc import calculate_module_gpa, calculate_semester_gpa, calculate_target_score
import streamlit_shadcn_ui as ui
from helper_functions import shadcn_text, set_page

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 1. PAGE SETUP
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
st.set_page_config(page_title = "Academic Performance", layout = "wide")
set_page("Academic Performance", "GPA metrics, track provisional and final grades, learn where work needs to improve")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 2. LOAD SETTINGS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
df_modules = get_modules_dataframe()
user_profile = get_user_settings()

with st.sidebar:
    shadcn_text("Timeline", variant = "heading")
    ui.separator()
    selected_semester = ui.select("Semester", options = ["Autumn", "Spring"])
    ui.separator()

semester_standings = calculate_semester_gpa(selected_semester)

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 3. CURRENT ACADEMIC STANDING SUMMARY (GPA / HONOURS)
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
icon_col, icon_text = st.columns([0.02, 0.98], gap = "small")

with icon_col:
    st.markdown("#### :material/book:") 
with icon_text:
    if "Percentage" in user_profile["grading_system"]:
        shadcn_text("Current Honours Grade Standing", variant = "heading")
    else:
        shadcn_text("Current GPA Standing", variant = "heading")

ui.metric_card(
        f"{selected_semester} Standing" if "Percentage" in user_profile["grading_system"] else f"{selected_semester} GPA" ,
        semester_standings["overall_score"],
        delta = semester_standings["classification"]
    )
st.write("____")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 4. MODULE GRADE SUMMARIES
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
icon_col_1, icon_text_1 = st.columns([0.02, 0.98], gap = "small")

with icon_col_1:
    st.markdown("#### :material/book:") 
with icon_text_1:
    shadcn_text("Module Grades", variant = "heading")

if df_modules.empty:
    st.info("No courses registered yet. Navigate to **Module and Assessment Registration** to build your syllabus.")
else:
    semester_modules = df_modules[df_modules["Semester"] == selected_semester]
    
    if semester_modules.empty:
        st.warning(f"No registered modules located for {selected_semester}.")
    else:
        for idx, mod_row in semester_modules.iterrows():
            st.write("")
            code = mod_row["Module Code"]
            title = mod_row["Module Title"]
            
            stats = calculate_module_gpa(code)
            
            with st.container():

                col_info, col_pct, col_gpa, col_stats = st.columns(4)
                
                with col_info:
                    ui.card(
                        title = f"{code}",
                        description = f"{title}",
                        key = f"academic_perf_card_info{code}_{idx}"
                    )
                    
                with col_pct:
                    ui.card(
                            title = f"Average Percentage: {stats["Module Average"]:.0f}%",
                            description = f"Syllabus Graded: {stats["Weight Graded"]:.0f}% of module",
                            key = f"academic_perf_card_pct{code}_{idx}"
                    )
                    
                with col_gpa:
                    ui.card(
                        title = f"Letter Grade: {stats["Letter_Grade"]}",
                        description = f"Points Awarded {stats["Module GPA"]}",
                        key = f"academic_perf_card__gpa{code}_{idx}"
                    )

                with col_stats:
                    ui.card(
                        title = f"{stats["Evaluation Status"]}",
                        description = f"{stats["Performance Status"]}",
                        key = f"academic_perf_card_stats{code}_{idx}"
                    )
st.write("____")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 5. GPA / HONOURS TARGET
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
icon_col_2, icon_text_2 = st.columns([0.02, 0.98], gap = "small")

with icon_col_2:
    st.markdown("#### :material/book:") 
with icon_text_2:
    if "Percentage" in user_profile["grading_system"]:
        shadcn_text("Honours Target", variant = "heading")
    else:
        shadcn_text("GPA Target", variant = "heading")

result = calculate_target_score(selected_semester)

with st.container():
        if result["status"] == "Impossible":
            alert_prefix = "X"
            metric_title = "Required Avg (Exceeded)"
            metric_val = "Impossible"
        elif result["status"] == "Secured":
            alert_prefix = "Success"
            metric_title = f"Required Avg (To reach target grade of {user_profile["target_grade"]}):"
            metric_val = "0.0%"
        elif result["status"] in ["No Modules", "Uncalibrated", "Concluded"]:
            alert_prefix = "info"
            metric_title = "Required Avg"
            metric_val = "N/A"
        else:
            alert_prefix = "Target"
            metric_title = "Required Avg"
            metric_val = f"{result["required_mark"]:.1f}%"

        ui.card(
            title = metric_title,
            description = metric_val
        )

        st.write("")
        if result["status"] == "Impossible":
            st.error(result["message"])
        elif result["status"] == "Secured":
            st.balloons()
            st.success(result["message"])
        elif result["status"] in ["No Modules", "Uncalibrated", "Concluded"]:
            st.info(result["message"])
        else:
            st.success(result["message"])

if result["status"] in ["On Track", "Safe Scope"]:
    req_mark = min(max(float(result["required_mark"]), 0.0), 100.0)
    st.write("")

    shadcn_text("Grade Average Needed", variant = "heading")
    st.slider(
        "Required thing",
        min_value = 0.0,
        max_value = 100.0,
        value = req_mark,
        disabled = True,
        label_visibility = "collapsed",
        help = "This bar is to highlight where your required performance sits."
    )