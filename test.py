import streamlit as st

#st.session_state is a dictionary to save page variables across reruns
# always check if key is missing before assigning value
# access through st.session_State[key] or st.session_state.key


if "count" not in st.session_state:
    st.session_state["count"] = 0

if st.button("Click!!"):
    st.session_state["count"] += 1

st.write(f"Button clicked {st.session_state.count} times")