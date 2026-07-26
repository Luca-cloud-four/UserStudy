import streamlit as st
import random

responses = ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5",
             "Answer 6", "Answer 7", "Answer 8", "Answer 9", "Answer 10",
             "Answer 11", "test", "Answer 13", "Answer 14", "Answer 15",
             "Answer 16", "Answer 17", "Answer 18", "Answer 19", "Answer 20"]

def show_trial(response1, response2):

    st.title("User Study")

    if "selected_answer" not in st.session_state:
        st.session_state.selected_answer = None

    # two columns side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Response 1")
        st.write(response1)
        if st.button(response1, use_container_width=True, key=f"trial{st.session_state.page}_left"):
            st.session_state.selected_answer = response1

    with col2:
        st.subheader("Response 2")
        st.write(response2)
        if st.button(response2, use_container_width=True, key=f"trial{st.session_state.page}_right"):
            st.session_state.selected_answer = response2

    if st.session_state.selected_answer:
        # two liker scales side by side
        col3, col4 = st.columns(2)

        with col3:
            infoR1 = st.radio(
                "I found response 1 informative:",
                [
                    "1 - Strongly disagree",
                    "2 - Disagree",
                    "3 - Somewhat disagree",
                    "4 - Neither agree nor disagree",
                    "5 - Somewhat agree",
                    "6 - Agree",
                    "7 - Strongly agree"
                ],
                index=None
            )

        with col4:
            infoR2 = st.radio(
                "I found response 2 informative:",
                [
                    "1 - Strongly disagree",
                    "2 - Disagree",
                    "3 - Somewhat disagree",
                    "4 - Neither agree nor disagree",
                    "5 - Somewhat agree",
                    "6 - Agree",
                    "7 - Strongly agree"
                ],
                index=None
            )

        if infoR1 is not None and infoR2 is not None:
            if st.button("Continue"):
                st.session_state.page += 1
                st.session_state.selected_answer = None
                st.rerun()
                
        else: 
            st.button("Continue",disabled=True)

if "page" not in st.session_state:
    st.session_state.page = 1

start = (st.session_state.page - 1) * 2 

show_trial(responses[start],responses[start + 1])