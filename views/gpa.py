import streamlit as st
import pandas as pd
from database import get_modules_dataframe, get_user_settings
from gpa_calc import calculate_module_gpa, calculate_semester_gpa
import streamlit_shadcn_ui as ui


st.set_page_config(page_title = "Academic Performance", layout = "wide")

def shadcn_text(text: str, variant: str = "heading"):
    variant_styles = {
        "title": {
            "class": "shadcn-t-title",
            "css": "font-size: 44px; font-weight: 700; letter-spacing: -0.05em; color: #09090b; margin-bottom: 16px;"
        },
        "heading": {
            "class": "shadcn-t-heading",
            "css": "font-size: 24px; font-weight: 600; letter-spacing: -0.025em; color: #09090b; margin-top: 16px; margin-bottom: 8px;"
        },
        "subheading": {
            "class": "shadcn-t-sub",
            "css": "font-size: 13px; font-weight: 400; color: #71717a; margin-bottom: 12px; line-height: 1.4;"
        }
    }
    
    style = variant_styles.get(variant, variant_styles["heading"])

    return st.markdown(
        f"""
        <style>
        @import url('https://googleapis.com');
        .shadcn-base-txt {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        </style>
        <div class="shadcn-base-txt" style="{style['css']}">{text}</div>
        """,
        unsafe_allow_html=True
    )

shadcn_text("Academic Performance", variant = "title")
shadcn_text("GPA metrics, track provisional and final grades, learn where work needs to improve", variant = "subheading")
st.write("____")


user_profile = get_user_settings()


selected_semester = ui.select("Choose semester",
    options = ["Autumn", "Spring"]
)
semester_standings = calculate_semester_gpa(selected_semester)
st.write("____")
icon_col, icon_text = st.columns([0.03, 0.97], gap="small")

with icon_col:
    # Safely parses the native Streamlit Material engine 
    st.markdown("### :material/book:") 

with icon_text:
    shadcn_text("University Framework Tracker", variant="heading")

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