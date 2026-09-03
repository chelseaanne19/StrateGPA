import streamlit as st
import pandas as pd
from database import (
    get_modules_dataframe, get_assessments_dataframe,
    insert_module, delete_module, update_module,
    insert_assessment, delete_assessment, update_assessment,
    get_user_settings
)
import streamlit_shadcn_ui as ui
from helper_functions import shadcn_text, set_page

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 1. PAGE SETUP
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
st.set_page_config(page_title = "Module and Assessment Registration", layout = "wide")
set_page("Module and Assessment Registration", "Register your modules and assessments here to populate your weekly metrics and grade pages.")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 2. LOAD SETTINGS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
user_profile = get_user_settings()
df_modules = get_modules_dataframe()
df_assessments = get_assessments_dataframe()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 3. SESSION STATE FLAGS FOR DIALOG WINDOWS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if "trigger_edit" not in st.session_state:
    st.session_state.trigger_edit = False
if "code_to_edit" not in st.session_state:
    st.session_state.code_to_edit = ""


if "trigger_edit_module" not in st.session_state:
    st.session_state.trigger_edit_module = False
if "trigger_edit_assessment" not in st.session_state:
    st.session_state.trigger_edit_assessment = False

if "code_to_edit" not in st.session_state:
    st.session_state.code_to_edit = ""
if "assessment_id_to_edit" not in st.session_state:
    st.session_state.assessment_id_to_edit = ""

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 4. DIALOG WINDOWS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@st.dialog("Confirm Assessment Details")
def confirm_assessment_submission(module_code, title, percentage, must_pass, weeks_list, is_final_exam, component_scale = None):
    st.warning("Please review assessment information carefully before submitting.")
    st.write(f"Module Code: **{module_code}**")
    st.write(f"Assignment Title: **{title}**")
    st.write(f"Weeks Due: **{", ".join(map(str, weeks_list))}**")
    st.write(f"Weighting: **{percentage}%**")
    st.write(f"Must Pass: **{'Yes' if must_pass else 'No'}**")
    if component_scale:
        st.write(f"Component Scale: **{component_scale}**")
    st.write("Is everything correct?")

    no, yes = st.columns([1, 1])
    with no:
        if st.button("No, Go Back", use_container_width = True, key = "unconfirm_assessment_submission"):
            st.rerun()
    with yes:
        if st.button("Yes, Submit", use_container_width = True, key = "confirm_assessment_submission", type = "primary"):
            must_pass_int = 1 if must_pass else 0
            success = insert_assessment(module_code, title, percentage, must_pass_int, weeks_list, is_final_exam, component_scale = component_scale)
            if success:
                st.success(f"{title} Created Successfully!")
                st.rerun()
            else:
                st.error("Error occurred while saving assessment details.")

@st.dialog("Edit Module Details")
def edit_module_submission(orig_module_code):

    resulting_row = df_modules.loc[df_modules["Module Code"] == orig_module_code]
    if resulting_row.empty:
        st.error("Could not load module details.")
        return

    orig_module_title = resulting_row["Module Title"].values[0]
    orig_semester = resulting_row["Semester"].values[0]
    semester_index = 1 if orig_semester == "Autumn" else 1

    with st.form("edit_module_form"):
        new_code = ui.input("Enter new module code:", value = orig_module_code, key = "new_mod_code")
        new_title = ui.input("Enter new module title:", value = orig_module_title, key = "new_mod_title")
        new_semester = ui.select("Choose correct semester:", options = ["Spring", "Autumn"], index = semester_index, key = "new_mod_semester")

        if st.form_submit_button("Confirm Module Details", key = "confirm_module_details"):
            if new_code.strip() and new_title.strip():
                success = update_module(orig_module_code, new_code.strip(), new_title.strip(), new_semester)

                if success:
                    st.session_state.trigger_edit_module = False
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("A module with this **code** or **title** *already exists* in your database.")
            else:
                st.error("Please fill in all fields.")

@st.dialog("Edit Assessment Details")
def edit_assessment_submission(assessment_id):
    resulting_row = df_assessments.loc[df_assessments["Assessment ID"] == assessment_id]
    if resulting_row.empty:
        st.error("Error loading assessment details.")
        return

    orig_title = resulting_row["Assessment Title"].values[0]
    orig_code = resulting_row["Module Code"].values[0]
    orig_percentage = int(resulting_row["Weight %"].values[0])
    orig_week = int(resulting_row["Week Due"].values[0])
    if "UCD" in user_profile["grading_system"]:
        orig_component_scale = resulting_row["Component Scale"].values[0]
    orig_must_pass = resulting_row["Must Pass"].values[0]
    bool_must_pass = True if orig_must_pass == "Yes" else False

    module_list = df_modules["Module Code"].tolist() if not df_modules.empty else [orig_code]
    code_index = module_list.index(orig_code) if orig_code in module_list else 0
    scale_list = ["Standard 40% Pass", "Alternative Linear 40% Pass", "Alternative Non-Linear 50% Pass", "Alternative 60% Pass"]
    if "UCD" in user_profile["grading_system"]:
        scale_index = scale_list.index(orig_component_scale) if orig_component_scale in scale_list else 0

    with st.form("edit_assessment_form"):
        new_title = ui.input("Enter new assessment title:", value = orig_title, key = "new_ass_title")
        new_code = ui.select("Select correct module:", options = module_list, index = code_index, key = "new_ass_code")
        new_percentage = st.slider("Enter correct weighting:", 0, 100, value = orig_percentage, key = "new_ass_weighting")
        new_must_pass = st.toggle("Must Pass Component", value = bool_must_pass, key = "new_must_pass")
        new_week = ui.select("Select correct week assessment is due:", options = list(range(1, 18)), index = orig_week - 1, key = "new_ass_weeks_list")
        if "UCD" in user_profile["grading_system"]:
            new_component_scale = ui.select("Select correct component scale:", options = scale_list, index = scale_index, key = "new_component_scale")

        if st.form_submit_button("Confirm Assessment Details", key = "confirm_assessment_details"):
            if new_title.strip() and new_code and new_week:
                must_pass_int = 1 if new_must_pass else 0

                success = update_assessment(assessment_id, new_code, new_title.strip(), new_percentage, must_pass_int, new_week, component_scale = new_component_scale if "UCD" in user_profile["grading_system"] else None)

                if success:
                    st.session_state.trigger_edit_assessment = False
                    st.rerun()
                else:
                    st.error("Error updating assessment details.")
            else:
                st.error("Please fill in all fields.")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 5. MODULE SECTION
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  
@st.fragment
def render_module_section():
    shadcn_text("Modules", variant = "title", color = "navy")

    # row into two columns, one for database view of all modules, one for module submission
    col_table, col_form = st.columns([8, 5])

    # LEFT COLUMN: DATABASE PREVIEW
    with col_table:
        with st.container(border = True):
            shadcn_text("Current Registered Modules", variant = "heading", color = "navy")

            if df_modules.empty:
                st.info("No modules created yet. Use the registration form to add your first module.")
            else:
                st.dataframe(df_modules, use_container_width = True, hide_index = True, height = 380)

                del_section, edit_section = st.columns([1, 1])
                with del_section:
                    with st.expander("Delete Existing Module"):
                        module_options = df_modules["Module Code"].tolist()
                        if not df_modules.empty:
                            del_choice = ui.select("Choose module to delete:", module_options, key = "mod_del_choice")
                            if st.button("Delete Module Permanently", type = "secondary", key = "del_mod"):
                                delete_module(del_choice)
                                st.success(f"{del_choice} and all associated assignments deleted.")
                                st.rerun()
                
                with edit_section:
                    with st.expander("Edit Existing Module"):
                        if not df_modules.empty:
                            edit_choice = ui.select("Choose module to edit:", module_options, key = "mod_edit_choice")
                            if st.button("Edit Module", type = "secondary", key = "edit_mod"):
                                st.session_state.trigger_edit_module = True
                                st.session_state.code_to_edit = edit_choice
                                st.rerun()

    # RIGHT COLUMN: MODULE REGISTRATION
    with col_form:
        with st.container(border = True):
            
            shadcn_text("Register Modules Here", variant = "heading", color = "navy")
            with st.container(border = True):
                module_code = ui.input("Enter Module Code", placeholder = "e.g. COMP10030")
                module_title = ui.input("Enter Module Title")
                semester = ui.select("Choose Semester", options = ["Autumn", "Spring"])

           
                trigger_btn = st.button("Register Module")
                decision = ui.alert_dialog(
                            show = trigger_btn,
                            title = "Confirm Module Details",
                            description = f"{module_code}, {module_title}, {semester}",
                            confirm_label = "Register",
                            cancel_label = "Go Back",
                            )

                if decision:
                    if module_code and module_title:
                        success = insert_module(module_code, module_title, semester)
                        if success:
                            st.success("Added!")
                            st.rerun()
                        else:
                            st.error("Error saving.")
                    else:
                        st.error("Please fill in all required fields.")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 6. ASSESSMENT SECTION
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@st.fragment
def render_assessment_section():
    shadcn_text("Assessments", variant = "title", color = "navy")
    
    col_table, col_form = st.columns([8, 5])
    
    with col_table:
        with st.container(border = True):
            shadcn_text("Current Created Assessments", variant = "heading", color = "navy")
            if df_assessments is None or df_assessments.empty:
                st.info("No assessments created yet.")
            else:
                st.dataframe(df_assessments, use_container_width = True, hide_index = True, height = 380)
                
                # edit options
                del_section, edit_section = st.columns([1, 1])
                with del_section:
                    with st.expander("Delete Existing Assessment"):
                        if not df_assessments.empty:
                            del_choice = ui.select("Please select assessment id (refer to table)", options = df_assessments["Assessment ID"].tolist(), key = "ass_del_choice")
                            if st.button("Delete assessment permanently", type = "secondary", key = "del_ass_btn"):
                                delete_assessment(del_choice)
                                st.success(f"Assessment {del_choice} deleted successfully.")
                                st.rerun()

                with edit_section:
                    with st.expander("Edit Existing Assessment"):
                        if not df_assessments.empty:
                            edit_choice = ui.select("Please select assessment id (refer to table)", options = df_assessments["Assessment ID"].tolist(), key = "ass_edit_choice")
                            if st.button("Edit Assessment", type = "secondary", key = "edit_ass_btn"):
                                st.session_state.trigger_edit_assessment = True
                                st.session_state.assessment_id_to_edit = edit_choice
                                st.rerun()

    with col_form:
        with st.container(border = True):
            shadcn_text("Create Assessments Here", variant = "heading", color = "navy")

            with st.container():
                # choose module
                module_options = df_modules["Module Code"].tolist() if not df_modules.empty else []
                module_code = ui.select("Assign Module Code for Assessment", options = module_options, key = "new_module_code")

                if not df_modules.empty and module_code:
                    current_semester = df_modules[df_modules["Module Code"] == module_code]["Semester"].values[0]
                else:
                    current_semester = "Autumn"

                # getting configured exam weeks for that semester
                if user_profile:
                    teaching_weeks = user_profile["weeks_autumn"] if current_semester == "Autumn" else user_profile["weeks_spring"]
                    exam_weeks = list(range(teaching_weeks + 1, teaching_weeks + 4))
                    exam_weeks_str = ", ".join(map(str, exam_weeks))
                else:
                    exam_weeks = [13, 14]
                    exam_weeks_str = "13, 14"

                # toggle to indicate info statements for form
                is_final_exam = st.toggle("Assessment is an end of semester final exam", value = False)


            # form submission
            with st.form("new_assessment_form", clear_on_submit = True):
                if "UCD" in user_profile["grading_system"]:
                    tab_title, tab_weeks, tab_weightings, tab_scales = st.tabs(["Title", "Weeks", "Weightings", "Component Scale"])
                else:
                    tab_title, tab_weeks, tab_weightings = st.tabs(["Title", "Week", "Weightings"])

                with tab_title:
                    title = ui.input("Assessment Title", placeholder = "e.g. In Class Test, MCQ, Group Project")
                    
                with tab_weeks:
                    if is_final_exam:
                        st.info(
                            f"**Automated Exam Placement:** This assessment will be automatically "
                            f"registered across your configured exam block (**Weeks {exam_weeks_str}**) for {current_semester}.\n\n"
                            f"*NOTE: If you already happen to know the exact specific week of your exam, toggle "
                            f"this switch OFF and log the target week manually instead!*")
                        weeks = exam_weeks
                    else:
                        weeks = st.multiselect("**Please select week(s) assessment is due**", options = list(range(1, 18)))

                with tab_weightings:
                    percentage = st.slider("Weight on Final Grade (%)", 0, 100)
                    if not is_final_exam:
                        st.info('''
                            💡 **Assessment Group Entry:** If this assessment has multiple parts spread across the term 
                            (for example: 3 In Class Tests worth 55% *in total together*), enter the name as 'In Class Test',
                            select all 3 weeks, and input **55** as the weight.\n\n
                            StrateGPA will automatically split them into separate tracking items and handle
                            the individual weight distributions for you!
                            ''')
                    st.space("small")
                    must_pass = st.toggle("Must Pass Component")

                if "UCD" in user_profile["grading_system"]:
                    with tab_scales:
                        selected_scale = "Standard 40% Pass"

                        if user_profile and "UCD" in user_profile["grading_system"]:
                            st.write("UCD Mark To Grade Component Scales")

                            selected_scale = st.selectbox(
                            "Select component scale associated for this assessment",
                            options = ["Standard 40% Pass", "Alternative linear 40% Pass", "Alternative Non-Linear 40% Pass", "Alternative Linear 60% Pass"],
                            help = "If unsure, visit the module's website -> 'How will I be assessed' -> 'Assessment Strategy' -> 'Component Scale'")

                            st.caption("If unsure about which scale applies, please refer to the **Assessment Strategy** section on your module's official webpage or Brightspace!")
                
                if st.form_submit_button("Create Assessment"):
                    if module_code and title and weeks:
                        confirm_assessment_submission(module_code, title, percentage, must_pass, weeks, is_final_exam, component_scale = None if "UCD" not in user_profile["grading_system"] else selected_scale)
                    else:
                        st.error("Please fill in all fields.")


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 7. RUN FUNCTIONS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
render_module_section()
st.write("____")
render_assessment_section()

if st.session_state.get("trigger_edit_module", False):
    edit_module_submission(st.session_state.code_to_edit)

if st.session_state.get("trigger_edit_assessment", False):
    edit_assessment_submission(st.session_state.assessment_id_to_edit)
