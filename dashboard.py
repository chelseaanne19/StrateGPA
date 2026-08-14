import streamlit as st
import pandas as pd
from database import get_modules_dataframe, get_weekly_workload


# session state flags for current week
if "current_week" not in st.session_state:
    st.session_state.current_week = 1

st.set_page_config(page_title = "StrateGPA Dashboard", layout = "wide")

st.title("Weekly Workload")
st.caption("Track upcoming busy weeks to balance schedule accordingly.")

##################
# UI
##################

with st.sidebar:
    st.slider("Current Academic Week:",
              min_value = 1,
              max_value = 17,
              value = st.session_state.current_week
              )

# filters
choose_trim, choose_mod = st.columns([1, 1])

with choose_trim:
    selected_trimester = st.selectbox("Select trimester:", options = ["Autumn", "Spring"])


# get all modules
df_modules = get_modules_dataframe()
if not df_modules.empty:
    trimester_modules = df_modules[df_modules["Trimester"] == selected_trimester]["Module Code"].tolist()
else:
    trimester_modules = []


# filtering options
filter_options = ["All Modules"] + trimester_modules


with choose_mod:
    selected_module = st.selectbox("Select module:", options = filter_options)

mod_query_params = None if selected_module == "All Modules" else selected_module


####################
# DATA
####################

chart_df = get_weekly_workload(selected_trimester, module_code = mod_query_params)

full_timeline_df = pd.DataFrame({"Week" : list(range(1, 18))})
chart_df = pd.merge(full_timeline_df, chart_df, on = "Week", how = "left").fillna(0)

####################
# METRICS
####################

busiest_row = chart_df.loc[chart_df["Total Workload (%)"].idxmax()]

busiest_week = int(busiest_row["Week"])

busiest_row = chart_df.loc[chart_df["Total Workload (%)"].idxmax()]
busiest_week = int(busiest_row["Week"])
max_workload = busiest_row["Total Workload (%)"]
total_term_weight = chart_df["Total Workload (%)"].sum()

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    with st.container(border=True):
        st.metric(
            label="🔥 Busiest Week Window", 
            value=f"Week {busiest_week}" if max_workload > 0 else "Clear Term",
            delta=f"{max_workload:.1f}% Due" if max_workload > 0 else None,
            delta_color="inverse" # Turns red automatically on spikes to catch recruiter focus
        )

with m_col2:
    with st.container(border=True):
        st.metric(
            label="📈 Tracker Weight Configured", 
            value=f"{total_term_weight:.1f}%",
            delta=f"{100.0 - total_term_weight:.1f}% Remaining"
        )

with m_col3:
    with st.container(border = True):
        deadline_count = int((chart_df["Total Workload (%)"] > 0).sum())
        st.metric(
            label = "Evaluation hubs",
            value = f"{deadline_count} Critical Weeks",
            delta = "Time Synchronised"
        )

st.write(f"### 📈 Workload Heatmap: {selected_module}")

if total_term_weight == 0:
    st.info("No active assessments located for this dashboard filter configuration parameter selection.")
else:
    # Draw the dynamic, enterprise-grade workload column chart
    st.bar_chart(
        data=chart_df,
        x="Week",
        y="Total Workload (%)",
        color="#1f77b4", # Polished corporate slate blue brand profile
        use_container_width=True
    )