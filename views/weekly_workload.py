import streamlit as st
import pandas as pd
from database import (
    get_modules_dataframe, get_weekly_workload,
    get_grade_progress, get_week_contributors,
    get_week_agenda, update_assessment_grade,
    get_user_settings
)
import plotly.express as px
from gpa_calc import calculate_semester_gpa
import streamlit_shadcn_ui as ui
from helper_functions import shadcn_text, set_page


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 1. PAGE SETUP
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
st.set_page_config(page_title = "Weekly Workload", layout = "wide")
set_page("Weekly Workload", "Track upcoming busy weeks and plan accordingly")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 2. LOAD SETTINGS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# WEEK AND SEMESTER FILTERS
if "current_week" not in st.session_state:
    st.session_state.current_week = 1

with st.sidebar:
    shadcn_text("Timeline", variant = "heading")
    ui.separator()
    st.session_state.current_week = ui.select(
            "Current Academic Week",
            list(range(1, 18))
        )

    selected_semester = ui.select("Semester", options = ["Autumn", "Spring"])
    ui.separator()

active_week = st.session_state.current_week

df_modules = get_modules_dataframe()
if not df_modules.empty:
    semester_modules = df_modules[df_modules["Semester"] == selected_semester]["Module Code"].tolist()
else:
    semester_modules = []


# MODULE FILTERS
filter_options = ["All Modules"] + semester_modules
selected_module = ui.select("Module:", options = filter_options)
mod_query_params = None if selected_module == "All Modules" else selected_module

ui.separator()


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 3. GRADE PROGRESS CARDS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
shadcn_text("Grade Progress", variant = "heading")
progress = get_grade_progress(selected_semester, module_code = mod_query_params)

chart_df = get_weekly_workload(selected_semester, module_code = mod_query_params)
full_timeline_df = pd.DataFrame({"Week" : list(range(1, 18))})
chart_df = pd.merge(full_timeline_df, chart_df, on = "Week", how = "left").fillna(0)

col1, col2, col3 = st.columns(3)
cols = st.columns(3)
with cols[0]:
    ui.metric_card("Grade Secured", f"{progress['earned_points']:.1f} / {progress['completed_weight']:.1f} Marks",
                delta = f"{progress['completed_weight']:.1f}% coursework graded")
with cols[1]:
    total = progress["total_weight"]
    if total == 100: delta_msg = "Syllabus fully configured (100%)"
    elif total < 100: delta_msg = f"Syllabus incomplete: {total:.1f}% / 100%"
    else: delta_msg = f"Syllabus exceeds 100% ({total:.1f}%). \n\n **Please fix assessment weightings**."
    ui.metric_card("Upcoming Marks / Grades", f"{progress['upcoming_weight']:.1f}% Available", delta = delta_msg)
with cols[2]:
    current_week_row = chart_df[chart_df["Week"] == active_week]
    week_load = float(current_week_row["Total Workload (%)"].values[0]) if not current_week_row.empty else 0.0
    ui.metric_card(f"Week {active_week} Focus", f"{week_load:.1f}% Due" if week_load > 0 else "No assessments due!", delta = "View below to see modules with assessments due.")

st.write("_____")


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 4. WORKLOAD BAR CHART / HEATMAP
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
shadcn_text("Workload Heatmap", variant = "heading")
shadcn_text(f"{selected_module}", variant = "subheading")

user_profile = get_user_settings()

if selected_semester == "Autumn":
    max_teaching_weeks = user_profile["weeks_autumn"] if user_profile else 12
else:
    max_teaching_weeks = user_profile["weeks_spring"] if user_profile else 14

show_exams = st.toggle(f"Include End-of-Semester Assessments (Weeks {max_teaching_weeks + 1}+)", value = True, help = "Toggle off to better view your semester workload before exams.")

if chart_df["Total Workload (%)"].sum() == 0:
    st.info("No active assessments located for this dashboard filter.")
else:
    if show_exams:
        fig = px.bar(
        chart_df,
        x = "Week",
        y = "Total Workload (%)",
        color = "Total Workload (%)",
        color_continuous_scale = [
            (0.0, "#2ecc71"),
            (0.4, "#f39c12"),
            (0.6, "#f75a05"),
            (0.8, "#e74c3c"),
            (1.0, "#e74c3c")
        ],
        range_color = [0, 100],
        labels = {"Week": "Academic Week Number", "Total Workload (%)": "Total Workload (%)"},
        hover_data = {
            "Week": False,
            "Total Workload (%)": True,
            "Module": True
        }
        )

        fig.update_layout(
        height = 400,
        margin = dict(l = 20, r = 20, t = 20, b = 20),
        xaxis = dict(tickmode = "linear", tick0 = 1, dtick = 1, fixedrange = True),
        yaxis = dict(fixedrange = True),
        coloraxis_colorbar = dict(title = "Stress Index"),
        dragmode = False
        )

        chart_config = {"displayModeBar": False, "scrollZoom": False}

        st.plotly_chart(fig, use_container_width = True, config = chart_config)
    else:
        fig = px.bar(
                chart_df[chart_df["Week"] <= max_teaching_weeks],
                x = "Week",
                y = "Total Workload (%)",
                color = "Total Workload (%)",
                color_continuous_scale = [
                    (0.0, "#2ecc71"),
                    (0.4, "#f39c12"),
                    (0.6, "#f75a05"),
                    (0.8, "#e74c3c"),
                    (1.0, "#e74c3c")
                ],
                range_color = [0, 100],
                labels = {"Week": "Academic Week Number", "Total Workload (%)": "Total Workload (%)"},
                hover_data = {
                    "Week": False,
                    "Total Workload (%)": True,
                    "Module": True
                }
                )
        
        fig.update_layout(
                height = 400,
                margin = dict(l = 20, r = 20, t = 20, b = 20),
                xaxis = dict(tickmode = "linear", tick0 = 1, dtick = 1, fixedrange = True),
                yaxis = dict(fixedrange = True),
                coloraxis_colorbar = dict(title = "Stress Index"),
                dragmode = False
                )
        
        chart_config = {"displayModeBar": False, "scrollZoom": False}
        
        st.plotly_chart(fig, use_container_width = True, config = chart_config)
st.write("____")


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 5. WEEKLY AGENDA
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
shadcn_text("Agenda", variant = "heading")
shadcn_text(f"Week {active_week}", variant = "subheading")

selected_tab = ui.tabs(options = ["Important Modules", "Week Tasks"], key = "selected_agenda_tab")

if selected_tab == "Important Modules":
    df_contributors = get_week_contributors(selected_semester, active_week)
    if df_contributors.empty:
        st.info(f"Week {active_week} is clear!")
    else:
        for idx, row in df_contributors.iterrows():
            shadcn_text(f"{row["Module Code"]} : {row["Module Title"]}", variant = "heading", color = "sky")
            ui.progress(value = float(row["Contribution (%)"]), label = f"{float(row["Contribution (%)"]):.1f}% is due.", show_value = True)
            st.write("____")

if selected_tab == "Week Tasks":
    df_agenda = get_week_agenda(selected_semester, active_week)
    if df_agenda.empty:
        st.info(f"Week {active_week} is clear!")
    else:
        for idx, row in df_agenda.iterrows():
            ass_id = int(row['Assessment ID'])
            mod_code = row['Module Code']
            title = row['Assessment Title']
            weight = float(row['Weight %'])
            must_pass = int(row['Must Pass'])
            current_grade = row["Received Grade"]
            is_graded = pd.notna(current_grade)

            # variable for spacing
            s = "\u00A0"

            grade_status = f"Graded: {current_grade:.1f}%" if is_graded else "Grade Pending ...."
            with st.expander(f":blue[**{title}**]{s*4}|{s*4}**{weight:.0f}%** of **{mod_code}**{s*4}|{s*4}{grade_status}"):
                if must_pass == 1:
                    st.error("**MUST PASS THIS ASSESSMENT**")

                with st.expander("Log Grade"):
                    with st.form(key = f"grade_form_{ass_id}"):
                        default_val = float(current_grade) if is_graded else 0.0
                        new_grade_score = st.number_input(
                            "Enter achieved score (0.0 -> 100.0):",
                            min_value = 0.0,
                            max_value = 100.0,
                            value = default_val,
                            step = 0.5,
                            key = f"grade_input_{ass_id}"
                        )
    
                        col_save, col_clear = st.columns(2)
                        with col_save:
                            if st.form_submit_button("Save Grade Score", use_container_width = True, type = "primary"):
                                update_assessment_grade(ass_id, new_grade_score)
                                st.rerun()
                        with col_clear:
                            if st.form_submit_button("Clear Grade", use_container_width = True):
                                update_assessment_grade(ass_id, None)
                                st.rerun()