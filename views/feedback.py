import streamlit as st
import streamlit_shadcn_ui as ui
import requests
from helper_functions import shadcn_text

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 1. PAGE SETUP
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
st.set_page_config(page_title = "Feedback Submission", layout = "wide")
shadcn_text("Developer Feedback & Bug Issues", variant = "title")
st.write("____")


shadcn_text("Hello from Creator!", variant = "heading")
ui.card(
        title = "Thank you for using StrateGPA!",
        description = "This is my very first software project, so your input is extremely valuable to me. Whether you encounter a technical bug, have advice on how to improve the code, or want to suggest a feature, please submit the feedback here! All feedback will help me tremendously. Thank you for your support!"
)
st.write("____")


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 2. FEEDBACK FORM
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
feedback_category = ui.select("Select submission category:",
                              options = ["Technical Bug / Crash", "Optimisation Advice / Feature Suggestion", " General Project Input / Other"],
                              key = "feedback_selector")

user_message = ui.textarea(
    "Message",
    placeholder = "Type here ...."
)

if ui.button("Submit"):
    if user_message.strip():
        formspree_endpoint_url = "https://formspree.io/f/xaeyelbz"

        submission_payload = {
            "Category": feedback_category,
            "Message": user_message.strip()
        }

        try:
            response = requests.post(formspree_endpoint_url, json = submission_payload)

            if response.status_code == 200:
                st.success("**Thank you!** Your feedback has been sent to my developer inbox. I appreciate your advice and notes!")
            else:
                st.error("**Interruption Occurred.** Please verify your connection and try again.")
        except Exception:
            st.error("**ERROR**. Unable to clear payload arrays out to cloud host.")
        
    else:
        st.error("Please fill out the message area before submitting.")

st.write("")
st.write("____")
ui.alert(title = "Anonymous Feedback", description = "Submissions are 100% anonymous. No identifying data or emails are tracked.")

