import streamlit as st
from database import table_setup, get_user_settings, save_user_settings
import streamlit_shadcn_ui as ui
from streamlit_extras.steps import *
from helper_functions import shadcn_text

table_setup()
user_profile = get_user_settings()

if user_profile is None:
    st.set_page_config(page_title = "Welcome to StrateGPA", layout = "centered")
    st.markdown("# :material/school: StrateGPA")
    st.caption("Welcome to StrateGPA! Please enter the following details to configure the app.")
    st.write("____")

    col1, col2 = st.columns(2)
    with col1:
        s = steps(
            ["University / College Name", "Teaching Weeks", "Grading", "Confirmation"],
            icons = range(1,5),
            key = "setup"
        )

    with col2:
        with s[0]:
            inst_name = ui.input(label = "Please enter the name of your university / college:", type = "text")
            if st.button("Next", key = "next_0"):
                s.next()

        with s[1]:
            col_aut, col_spr = st.columns(2)
            with col_aut:
                weeks_aut = st.number_input(
                    "Autumn Teaching Duration (Weeks):",
                    min_value = 1,
                    max_value = 17,
                    value = 17,
                    step = 1
                )
            with col_spr:
                weeks_spr = st.number_input(
                    "Spring Teaching Duration (Weeks):",
                    min_value = 1,
                    max_value = 17,
                    value = 17,
                    step = 1
                )
            with st.container(horizontal = True):
                if st.button("Back", key = "back_1"):
                    s.previous()
                if st.button("Next", key = "next_1"):
                    s.next()

        with s[2]:
            system_choice = ui.select(label = "Grading Scale System:", options = ["UCD 4.2 Scale", "US 4.0 Scale", "Percentage Only"], value = "UCD 4.2 Scale" if "UCD" in inst_name else "Percentage Only")
            if "Percentage" in system_choice:
                target_score = st.slider("Set Percentage you would like to achieve:", 0, 100, 100, step = 1, key = "target_score_slider_1")
            
                if target_score >= 70: classification = "First-Class Honours (1st)"
                elif target_score >= 60: classification = "Upper Second-Class Honours (2:1)"
                elif target_score >= 50: classification = "Lower Second-Class Honours (2:2)"
                elif target_score >= 40: classification = "Third-Class Honours (3rd)"
                else: classification = "Fail"

            elif "4.2" in system_choice:
                target_score = st.slider("Set GPA score you would like to achieve:", 2.0, 4.2, 4.2, step = 0.05, key = "target_score_slider_2")
                if target_score >= 3.68: classification = "First Class Honours (1st)"
                elif target_score >= 3.08: classification = "Second Class Honours, Grade 1 (2:1)"
                elif target_score >= 2.48: classification = "Second Class Honours, Grade 2 (2:2)"
                elif target_score >= 2.00: classification = "Pass Degree"
                else: classification = "Fail"

            else:
                target_score = st.slider("Set GPA score you would like to achieve:", 2.0, 4.2, 4.2, step = 0.05, key = "target_score_slider_3")
                if target_score >= 3.80: classification = "Summa Cum Laude (Highest Honours)"
                elif target_score >= 3.65: classification = "Magna Cum Laude (High Honours)"
                elif target_score >= 3.50: classification = "Cum Laude (Honours)"
                elif target_score >= 2.00: classification = "Good Academic Standing"
                else: classification = "Fail"



            ui.card(title = f"{classification}", key = "classification")
            with st.container(horizontal = True):
                if st.button("Back", key = "back_2"):
                    s.previous()
                if st.button("Next", key = "next_2"):
                    s.next()

        with s[3]:
            if inst_name.strip():
                st.success("All Done! You're all set!")


                back, save = st.columns(2)
                with back:
                    if st.button("Back", key="back_3", use_container_width = True):
                        s.previous()
                with save:
                    if st.button("Save & Continue", key="save_settings_and_continue", use_container_width = True):
                        success = save_user_settings(inst_name.strip(), system_choice, target_score, weeks_aut, weeks_spr)
                        if success:
                            st.success("Saving!")
                            st.rerun()
                        else:
                            st.error("Error saving details.")
            else:

                st.error("Please fill in all fields.")
        

                back, save = st.columns(2)
                with back:
                    if st.button("Back", key="back_3_error"):
                        s.previous()

    st.write("____")


else:

    config_page = st.Page("views/configurations.py", title = "Module and Assessment Registration", icon = ":material/add:")
    grades_page = st.Page("views/grades_entry.py", title = "Grade Entry", icon = ":material/add:")
    dashboard_page = st.Page("views/dashboard.py", title = "Weekly Workload", icon = ":material/event:")
    gpa_page = st.Page("views/gpa.py", title = "Academic Performance", icon = ":material/add_task:")
    help_page = st.Page("views/help_guide.py", title = "Help Guide", icon = ":material/help:")

    pg = st.navigation(
        {
            f"🏫 {user_profile['institution']}": [dashboard_page, gpa_page],
                  "System Management": [config_page, grades_page, help_page]
        }
    )

    pg.run()
