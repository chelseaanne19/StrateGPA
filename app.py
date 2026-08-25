import streamlit as st
from database import table_setup, get_user_settings, save_user_settings

table_setup()
user_profile = get_user_settings()

if user_profile is None:
    st.set_page_config(page_title = "Welcome to StrateGPA", layout = "centered")
    st.title("Welcome Title")
    st.markdown("Please enter the following details to configure the gpa/score tracking:")
    st.write("____")

    with st.container(border = True):
        inst_name = st.text_input("University / College Name:")
        system_choice = st.selectbox("Grading Scale System:", options = ["UCD 4.2 Scale", "US 4.0 Scale", "Percentage Only"])

        col_aut, col_spr = st.columns(2)
        with col_aut:
            weeks_aut = st.number_input(
            "Autumn Teaching Duration (Weeks):",
            min_value = 1,
            max_value = 17,
            value = 17,
            step = 1)

        with col_spr:
            weeks_spr = st.number_input(
            "Spring Teaching Duration (Weeks):",
            min_value = 1,
            max_value = 17,
            value = 14,
            step = 1)

        if "Percentage" in system_choice:
            target_score = st.slider("Target Honours Goal:", 40.0, 100.0, 70.0, step = 0.5, format = "%.1f%%")
        elif "4.2" in system_choice:
            target_score = st.slider("Target Honours Goal:", 2.0, 4.2, 3.6, step = 0.05)
        else:
            target_score = st.slider("Target Honours Goal", 2.0, 4.0, 3.5, step = 0.05)


        if st.button("Complete Setup & Initialise Dashboard", type = "primary", use_container_width = True):
            if inst_name.strip():
                save_user_settings(inst_name.strip(), system_choice, target_score, weeks_aut, weeks_spr)
                st.success("Successfully recorded! Loading application views....")
                st.rerun()
            else:
                st.error("Please fill in fields correctly.")
else:
    config_page = st.Page("views/configurations.py", title = "Module and Assessment Registration", icon = "➕")
    grades_page = st.Page("views/grades_entry.py", title = "Grade Entry", icon = "➕")
    dashboard_page = st.Page("views/dashboard.py", title = "Weekly Workload", icon = "🍡")

    pg = st.navigation(
        {
            f"🏫 {user_profile['institution']}": [dashboard_page],
                  "System Management": [config_page, grades_page]
        }
    )

    pg.run()
