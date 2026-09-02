import streamlit as st
from database import get_user_settings, save_user_settings
import streamlit_shadcn_ui as ui
from streamlit_extras.steps import *
from helper_functions import shadcn_text, set_page
from database import supabase
# FUNCTION_TESTING123!
setup = True
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 1. SETUP PAGE
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
st.set_page_config(page_title = "StrateGPA", layout = "centered")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 2. SESSION STATE
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

if "user" not in st.session_state:
    st.session_state.user = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 3. AUTHENTICATION
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

if st.session_state.user is None:
    set_page("StrateGPA", "Log in securely.")

    selected_tab = ui.tabs(options = ["Log In", "Sign Up"], key = "login_signup_tabs")

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # a. LOGIN
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    if selected_tab == "Log In":
        email = ui.input("Email", key = "login_email")
        password = ui.input("Password", type = "password", key = "login_pass")
        
        if ui.button("Sign In", key = "signin_submit_btn"):
            if email and password:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email.strip(), 
                        "password": password
                    })

                    if response.user:
                        st.session_state.user = response.user
                        st.session_state.user_id = response.user.id
                        st.toast("Welcome back! Synchronising your workspace...")
                        st.rerun()
                    else:
                        st.error("Authentication failed. Please verify credentials.")
                except Exception as e:
                    st.error(f"{e}")
            else:
                st.error("Please fill out both email and password fields.")

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # b. SIGN UP
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    elif selected_tab == "Sign Up":
        new_email = ui.input("Email", key = "reg_email")
        new_password = ui.input("Password", type = "password", key = "reg_pass")
        
        if ui.button("Create Account", key = "signup_submit_btn"):
            if new_email and new_password:
                try:
                    response = supabase.auth.sign_up({
                        "email": new_email.strip(), 
                        "password": new_password
                    })

                    if response.user:
                        if response.session:
                            st.session_state.user = response.user
                            st.session_state.user_id = response.user.id

                            st.success("Account created!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
            else:
                st.error("Please specify an email and secure password matrix.")
    st.stop()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 4. LOAD AUTHENTICATED USER
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
user = st.session_state.user
st.session_state.user_id = user.id
user_profile = get_user_settings()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 5. welcome window
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@st.dialog(":material/school:")
def welcome_message():
    shadcn_text("Welcome to StrateGPA!", variant = "title")
    shadcn_text("Below is a quick reference guide to understand what StrateGPA entails.", variant = "heading")
    ui.separator()

    ui.card(
        title = "Module and Assessment Registration",
        description = "Log your course modules and assessments here."
    )

    ui.card(
        title = "Grade Entry",
        description = "Open your modules and view their assessments. Save your grades (as percentages) as soon as you receive them to instantly synchronise your charts and GPA metrics!"
    )

    ui.card(
        title = "Weekly Workload",
        description = "Tracks Grade Secured stats, a colour workload heatmap to track busy weeks, and active weekly agendas that flag high-priority modules and assessments."
    )

    ui.card(
        title = "Academic Performance",
        description = "Compares your live running semester academic standing against your Target Honours Goal / GPA, along with individual module grade statistics."
    )

    st.write("")

    ui.alert("Need more clarification? Open the Help Guide for further details.")
    st.session_state.show_welcome = False
    if ui.button("Continue!"):
        st.rerun()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 4. USER CONFIGURES SETTINGS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if user_profile is None:
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
    st.session_state.show_welcome = True
    st.write("____")
    st.stop()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 4. LOAD APP [SETTINGS HAVE ALREADY BEEN CONFIGURED]
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
else:
    if st.session_state.get("show_welcome") == True:
        st.session_state.show_welcome = False
        welcome_message()

    with st.sidebar:
        shadcn_text(f"User: {user.email}", variant = "subheading", color = "grey")
        if ui.button("Log Out", key = "sidebar_logout_btn"):
            try:
                supabase.auth.sign_out()
            finally:
                st.session_state.user = None
                st.session_state.user_id = None
                st.session_state.show_welcome = False
                st.rerun()

        ui.separator()
    
    config_page = st.Page("views/configurations.py", title = "Module and Assessment Registration", icon = ":material/add:")
    grades_page = st.Page("views/grades_entry.py", title = "Grade Entry", icon = ":material/add:")
    weekly_workload_page = st.Page("views/weekly_workload.py", title = "Weekly Workload", icon = ":material/event:")
    academic_performance = st.Page("views/academic_performance.py", title = "Academic Performance", icon = ":material/add_task:")
    help_page = st.Page("views/help_guide.py", title = "Help Guide", icon = ":material/help:")
    feedback_page = st.Page("views/feedback.py", title = "Feedback", icon = ":material/rate_review:")
    pg = st.navigation(
        {
            f"🏫 {user_profile['institution']}": [weekly_workload_page, academic_performance],
                  "System Management": [config_page, grades_page, help_page, feedback_page]
        }
    )

    pg.run()
    
