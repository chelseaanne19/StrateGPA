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

        if "Percentage" in system_choice:
            target_score = st.slider("Target Honours Goal:", 40.0, 100.0, 70.0, step = 0.5, format = "%.1f%%")
        elif "4.2" in system_choice:
            target_score = st.slider("Target Honours Goal:", 2.0, 4.2, 3.6, step = 0.05)
        else:
            target_score = st.slider("Target Honours Goal", 2.0, 4.0, 3.5, step = 0.05)


        if st.button("Complete Setup & Initialise Dashboard", type = "primary", use_container_width = True):
            if inst_name.strip():
                save_user_settings(inst_name.strip(), system_choice, target_score)
                st.success("Successfully recorded! Loading application views....")
                st.rerun()
            else:
                st.error("Please fill in fields correctly.")
else:
    st.write("set up pages / views")