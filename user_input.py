# to handle user input of modules and assessments through streamlit forms

import streamlit as st
import pandas as pd
from database import (
    table_setup, get_modules_dataframe, get_assessments_dataframe,
    insert_module, delete_module, update_module,
    insert_assessment, delete_assessment, update_assessment
)


# session state flags for dialog windows
if "trigger_edit" not in st.session_state:
    st.session_state.trigger_edit = False
if "code_to_edit" not in st.session_state:
    st.session_state.code_to_edit = ""


# PAGE CONFIGURATION
st.set_page_config(page_title = "Module and Assessment Registration", layout = "wide")
table_setup()



# MODULE SECTION
@st.dialog("Confirm Module Details")
def confirm_module_submission(module_code, module_title, trimester):
    st.warning("Please review module information carefully before submitting.")
    st.write(f"**Module Code:** {module_code}")
    st.write(f"**Module Title:** {module_title}")
    st.write(f"**Trimester:** {trimester}")

    st.write("Is everything correct?")

    # choices
    no, yes = st.columns([1, 1])
    with no:
        if st.button("No, Go Back", use_container_width = True, key = "confirm_no"):
            st.rerun()

    with yes:
        if st.button("Yes, Submit", use_container_width = True, key = "confirm_yes"):
            success = insert_module(module_code, module_title, trimester)

            if success:
                st.success(f"{module_code} Registered Successfully!")
                st.rerun()
            else:
                st.error("A module with this **code** or **title** *already exists* in your database.")

@st.dialog("Edit Module Details")
def edit_module_submission(df, orig_module_code):

    # original database row
    resulting_row = df.loc[df["Module Code"] == orig_module_code]

    if resulting_row.empty:
        st.error("Could not load module details.")
        return

    orig_module_title = resulting_row["Module Title"].values[0]
    trimester = resulting_row["Trimester"].values[0]

    with st.form("edit_module_form"):
        new_code = st.text_input("Enter new module code:", value = orig_module_code)
        new_title = st.text_input("Enter new module title:", value = orig_module_title)
        trimester = st.selectbox("Choose correct semester:", options = ["Autumn", "Spring"])

        if st.form_submit_button("Confirm Module Details"):
            if new_code and new_title:
                success = update_module(orig_module_code, new_code, new_title, trimester)

                if success:
                    st.session_state.trigger_edit = False
                    st.rerun()
                else:
                    st.error("A module with this **code** or **title** *already exists* in your database.")
            else:
                st.error("Please fill in all fields.")

    
def render_module_section():
    st.markdown("### Module Management")
    df_modules = get_modules_dataframe()


    # row into two columns, one for database view of all modules, one for module submission
    col_table, col_form = st.columns([1, 1])

    with col_table:
        with st.container(border = True):
            st.markdown("#### Current Registered Modules")
            if df_modules.empty:
                st.info("No modules created yet.")
            else:
                st.dataframe(df_modules, use_container_width = True, hide_index = True, height = 280)
    with col_form:
        with st.container(border = True):
            with st.form("new_module_form"):
                module_code = st.text_input("Enter Module Code", placeholder = "e.g. COMP10030")
                module_title = st.text_input("Enter Module Title")
                trimester = st.selectbox("Choose Trimester", options = ["Autumn", "Spring"])

                if st.form_submit_button("Register Module"):
                    if module_code and module_title:
                        confirm_module_submission(module_code, module_title, trimester)
                    else:
                        st.error("Please fill in all fields.")

            # other edit options
            del_section, edit_section = st.columns([1, 1])
            with del_section:
                with st.expander("Delete Existing Module"):
                    df = get_modules_dataframe()
                    if not df.empty:
                        del_choice = st.selectbox("Choose module to delete:", df["Module Code"].tolist())
                        if st.button("Delete Module Permanently", type = "secondary"):
                            delete_module(del_choice)
                            st.success(f"{del_choice} deleted.")
                            st.rerun()

            with edit_section:
                with st.expander("Edit Existing Module"):
                    if not df_modules.empty:
                        edit_choice = st.selectbox("Choose module to edit:", df["Module Code"].tolist(), key = "edit_select")
                        if st.button("Edit Module", type = "secondary", key = "edit_button"):
                            st.session_state.trigger_edit = True
                            st.session_state.code_to_edit = edit_choice
                            st.rerun()




# running
render_module_section()
if st.session_state.get("trigger_edit", False):
    df = get_modules_dataframe()
    edit_module_submission(df, st.session_state.code_to_edit)