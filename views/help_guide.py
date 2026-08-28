import streamlit as st
from database import get_user_settings
import streamlit_shadcn_ui as ui

st.set_page_config(page_title = "StrateGPA: Instruction Manual", layout = "wide")
st.title("Instruction Manual")


user_profile = get_user_settings()
system = user_profile["system"]
selected_tab = ui.tabs(
    options=[
    "1. Initial Calibration",
    "2. Syllabus Configurations",
    "3. Logging Results",
    "4. Interpreting Dashboard"
], 
    key="grading_workflow_tabs"
)

if selected_tab == "1. Initial Calibration":
    st.markdown("### Understanding System Calibration")
    st.write("Before data entry begins, StrateGPA bases its calculations on your university's rules.")

    col1, col2 = st.columns(2)

    columns = st.columns(2)
    with columns[0]:
        ui.card(
            title = "University",
            description = f"{user_profile["institution"]}",
            )
        ui.card(
        title = "Current Selected Scale:",
        description = f"{system}",
        )
        ui.card(
            title = "Target GPA",
            description = f"{user_profile["target_gpa"]}",
            )
        ui.card(
            title = "Autumn Teaching Weeks",
            description = f"{user_profile["teaching_weeks_autumn"]}",
                )
        ui.card(
                title = "Spring Teaching Weeks",
                description = f"{user_profile["teaching_weeks_spring"]}",
                )
    with columns[1]:
        items = [
                ui.AccordionItem("sem_lengths", "Why Semester Lengths Matter", "Setting your accurate teaching weeks is useful when inputting final exam assessments and you don't know which exact week the exam is on, and for the weekly workload toggle."),
                ui.AccordionItem("adjust", "How to Adjust", "If you misconfigured these options during setup, please ____"),
                ]
        open_section = ui.accordion(items)



if selected_tab == "2. Syllabus Configurations":
    st.markdown("### Structuring Your Courses & Assessments")
    st.write("To populate pages like *Weekly Workload* and *Academic Performance*, first navigate to **Module and Assessment Registrations**.")
    
    st.markdown("##### Exactly What Needs to Be Filled Out:")
    with st.container(border = True):
        st.markdown('''
        1. **Module Code & Title:** (e.g. Code: `COMP20360`, Title: `Formal Foundations 2`).
        2. **Assessment Title:** (e.g., `Final Exam`, `Weekly Lab MCQ`).
        3. **Weight on Final Grade (%):** Input the true percentage impact this item has toward your total module score out of 100.
        4. **Target Weeks Due:** 
           * *Continuous Assessment:* Check the exact weeks using the multi-select slider. 
           * *Grouped/Repeating Tasks (e.g. 3 Tests worth 55% together):* Input the **total shared weight (55)** and select all active weeks. The system will automatically compute splits and manage fractional remainder allocations perfectly!
        ''')
        
    if "UCD" in system:
        st.info('''
             **UCD Assessment Strategy Lookups:** \n\n
            If your assessment is an MCQ or quantitative element, your lecturer may deploy alternative marking linear curves.\n
            Look up your exact module page code on the **UCD Website** or inspect your\n
            Brightspace curriculum handouts to select the correct sub-scale dropdown option (*Standard, Alt Linear 40, Alt Non-Linear 50, Alt Linear 60*)!\n
        ''')

if selected_tab == "3. Logging Results":
    st.markdown("### Managing Your Results Flow")
    st.write("The **Grade Entry** page is where you input grades.")
    
    st.markdown("#####  How to Maintain Data Flow Symmetry:")
    st.markdown("""
    * **Semester Selection:** Select your semester using the selectbox. The page will dynamically construct cards for each module.
    * **Grade Input:** Enter the raw percentage score you achieved on that specific quiz sheet (e.g. enter `85.5`, do not type symbols or letters).
    * **Upcoming Grades -> Already Graded:** Saving a score immediately transitions that specific assessment out of your *Upcoming Grades / Marks* bucket, and recalculates your Academic Performance metrics natively in real time.
    * **Corrections:** If a grade gets released with a clerical error or an entry gets logged into the wrong row, simply click **'Clear'** to shift that item's status back to pending.
    """)


if selected_tab == "4. Interpreting Dashboard":
    st.markdown("### Understanding StrateGPA")
    
    with st.container(border = True):
        st.markdown("##### How Your Academic Performance Calibrates:")
        st.markdown("""
        1. **Assessment Isolation:** When you log an achieved mark, the conversion matrix translates that raw percentage into a true **Letter Grade** and **GPA Point value** based strictly on that specific assessment's scale rules / your university's grading system.
        2. **Running GPA / Classification:** StrateGPA extracts the current GPA point standings across all of your active modules and calculates the final unweighted mean to determine your running  **GPA** and **Degree Honours Classification**.
        """)
    
