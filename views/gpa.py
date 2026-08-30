import streamlit as st
import pandas as pd
from database import get_modules_dataframe, get_user_settings
from gpa_calc import calculate_module_gpa, calculate_semester_gpa, calculate_target_score
import streamlit_shadcn_ui as ui
from helper_functions import shadcn_text


st.set_page_config(page_title = "Academic Performance", layout = "wide")

shadcn_text("Academic Performance", variant = "title", color = "navy")
shadcn_text("GPA metrics, track provisional and final grades, learn where work needs to improve", variant = "subheading", color = "grey")
st.write("____")


user_profile = get_user_settings()


selected_semester = ui.select("Choose semester",
    options = ["Autumn", "Spring"]
)
semester_standings = calculate_semester_gpa(selected_semester)
st.write("____")
icon_col, icon_text = st.columns([0.02, 0.98], gap="small")
with icon_col:
    st.markdown("### :material/book:") 
with icon_text:
    if "Percentage" in user_profile["system"]:
        shadcn_text("Current Honours Grade Standing", variant = "heading")
    else:
        shadcn_text("Current GPA Standing", variant = "heading")


ui.metric_card(
        f"{selected_semester} Standing" if "Percentage" in user_profile["system"] else f"{selected_semester} GPA" ,
        semester_standings["overall_score"],
        delta = semester_standings["classification"]
    )


####
st.write("____")
icon_col_1, icon_text_1 = st.columns([0.02, 0.98], gap="small")
with icon_col_1:
    st.markdown("### :material/book:") 
with icon_text_1:
    shadcn_text("Module Grades", variant = "heading")

df_modules = get_modules_dataframe()
if df_modules.empty:
    st.info("No courses registered yet. Navigate to **Module and Assessment Registration** to build your syllabus.")
else:
    semester_modules = df_modules[df_modules["Trimester"] == selected_semester]
    
    if semester_modules.empty:
        st.warning(f"No registered modules located for {selected_semester}.")
    else:
        for idx, mod_row in semester_modules.iterrows():
            code = mod_row["Module Code"]
            title = mod_row["Module Title"]
            
            stats = calculate_module_gpa(code)
            
            with st.container(border = True):
                col_info, col_pct, col_gpa = st.columns(3)
                
                with col_info:
                    shadcn_text(f"{code}", variant = "heading", color = "navy")
                    shadcn_text(f"{title}", variant = "subheading", color = "grey")
                    
                with col_pct:
                    shadcn_text(f"Average Percentage: {stats['Module Average']:.0f}%", variant = "heading", color = "navy")
                    shadcn_text(f"Syllabus Graded: {stats['Weight Graded']:.0f}% of module", variant = "subheading", color = "grey")
                    
                with col_gpa:
                    shadcn_text(f"Letter Grade: {stats['Letter_Grade']}", variant = "heading", color = "navy")
                    shadcn_text(f"Points Awarded: {stats['Module GPA']}", variant = "subheading", color = "grey")

####
st.write("_____")
icon_col_2, icon_text_2 = st.columns([0.02, 0.98], gap="small")
with icon_col_2:
    st.markdown("### :material/book:") 
with icon_text_2:
    if "Percentage" in user_profile["system"]:
        shadcn_text("Honours Target", variant = "heading")
    else:
        shadcn_text("GPA Target", variant = "heading")

result = calculate_target_score(selected_semester)

with st.container(border = True):
    col_metric, col_msg = st.columns(2)

    with col_metric:
        if result["status"] == "Impossible":
            alert_prefix = "X"
            metric_label = "Required Avg (Exceeded)"
            metric_val = "Impossible"
        elif result["status"] == "Secured":
            alert_prefix = "Success"
            metric_label = "Required Avg"
            metric_val = "0.0%"
        elif result["status"] in ["No Modules", "Uncalibrated", "Concluded"]:
            alert_prefix = "info"
            metric_label = "Required Avg"
            metric_val = "N/A"
        else:
            alert_prefix = "Target"
            metric_label = "Required Avg"
            metric_val = f"{result["required_mark"]:.1f}%"

        st.metric(label = metric_label, value = metric_val)

    with col_msg:
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

    shadcn_text("Thing", variant = "heading")
    st.slider(
        "Required thing",
        min_value = 0.0,
        max_value = 100.0,
        value = req_mark,
        disabled = True,
        label_visibility = "collapsed",
        help = "This bar is to highlight where your required performance sits."
    )