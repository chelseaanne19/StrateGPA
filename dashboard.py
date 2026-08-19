import streamlit as st
import pandas as pd
from database import (
    get_modules_dataframe, get_weekly_workload,
    get_grade_progress, get_week_contributors,
    get_week_agenda, update_assessment_grade
)

st.set_page_config(page_title = "Dashboard", layout = "wide")

# __________________
# SIDEBAR
# __________________
if "current_week" not in st.session_state:
    st.session_state.current_week = 1

with st.sidebar:
    st.markdown("### Timeline Navigation")
    st.session_state.current_week = st.slider(
            "Set Current Academic Week:",
              min_value = 1,
              max_value = 17,
              value = st.session_state.current_week
              )

active_week = st.session_state.current_week

# ______________________
#
#_______________________
st.title("Performance Dashboard")
st.caption("Track grade progress and workloads ccordingly")
st.write("____")


# filters
col_trim, col_mod = st.columns([1, 1])

with col_trim:
    selected_trimester = st.selectbox("Select trimester:", options = ["Autumn", "Spring"])


# get all modules
df_modules = get_modules_dataframe()
if not df_modules.empty:
    trimester_modules = df_modules[df_modules["Trimester"] == selected_trimester]["Module Code"].tolist()
else:
    trimester_modules = []

# filtering options
filter_options = ["All Modules"] + trimester_modules

with col_mod:
    selected_module = st.selectbox("Select module:", options = filter_options)

mod_query_params = None if selected_module == "All Modules" else selected_module


####################
# CARDS
####################
st.write("### Grade Progress")
progress = get_grade_progress(selected_trimester, module_code = mod_query_params)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border = True):
        st.metric(
            label = "Grade Secured",
            value = f"{progress['earned_points']:.1f} / {progress['completed_weight']:.1f} Marks",
            delta = f"{progress['completed_weight']:.1f}% coursework graded"
        )

with col2:
    with st.container(border = True):
        st.metric(
            label = "Upcoming Marks / Grades",
            value = f"{progress['upcoming_weight']:.1f}% Available",
            delta = f"Total Syllabus Configured: {progress['total_weight']:.1f}%"
        )



chart_df = get_weekly_workload(selected_trimester, module_code = mod_query_params)
full_timeline_df = pd.DataFrame({"Week" : list(range(1, 18))})
chart_df = pd.merge(full_timeline_df, chart_df, on = "Week", how = "left").fillna(0)

with col3:
    with st.container(border = True):
        current_week_row = chart_df[chart_df["Week"] == active_week]
        week_load = float(current_week_row["Total Workload (%)"].values[0]) if not current_week_row.empty else 0.0

        st.metric(
            label = f"Week {active_week} Focus",
            value = f"{week_load:.1f}% Due" if week_load > 0 else "Calm Week",
        )


st.write("_____")



st.write(f"### 📈 Workload Heatmap: {selected_module}")

if chart_df["Total Workload (%)"].sum() == 0:
    st.info("No active assessments located for this dashboard filter.")
else:
    st.bar_chart(
        data = chart_df,
        x = "Week",
        y = "Total Workload (%)",
        color ="#f2de84",
        use_container_width = True
    )