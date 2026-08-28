import streamlit as st
import pandas as pd
from database import get_modules_dataframe, get_user_settings
from gpa_calc import calculate_module_gpa, calculate_semester_gpa
import streamlit_shadcn_ui as ui


st.set_page_config(page_title = "Academic Performance", layout = "wide")
st.title("Academic Performance")
st.caption("GPA metrics, track provisional and final grades, learn where work needs to improve")

user_profile = get_user_settings()


selected_semester = st.selectbox("Choose semester",
    options = ["Autumn", "Spring"]
)
semester_standings = calculate_semester_gpa(selected_semester)

st.markdown("### :material/book: Current Semester GPA")
with st.container(border = True):

    st.metric(
        label = f"{selected_semester} GPA",
        value = semester_standings["overall_score"],
        delta = semester_standings["classification"]
    )  


####
st.write("____")
st.markdown("### :material/book: Module Grades")

df_modules = get_modules_dataframe()
if df_modules.empty:
    st.info("No courses registered yet. Navigate to **Module and Assessment Registration** to build your syllabus.")
else:
    semester_modules = df_modules[df_modules["Trimester"] == selected_semester]
    
    if semester_modules.empty:
        st.warning(f"No registered modules located for {selected_semester}.")
    else:
        for idx, mod_row in semester_modules.iterrows():
            code = mod_row["Module Code"]
            title = mod_row["Module Title"]
            
            stats = calculate_module_gpa(code)
            
            with st.container(border = True):
                col_info, col_pct, col_gpa = st.columns(3)
                
                with col_info:
                    st.markdown(f"##### **{code}**")
                    st.caption(title)
                    
                with col_pct:
                    st.markdown(f"**Average Percentage:** `{stats['Module Average']:.0f}%`")
                    st.caption(f"Syllabus Graded: {stats['Weight Graded']:.0f}% of module")
                    
                with col_gpa:
                    st.markdown(f"**Letter Grade:** `{stats['Letter_Grade']}`")
                    st.caption(f"Points Awarded: {stats['Module GPA']}")

####
st.write("_____")
st.write("### :material/book: GPA Targets")