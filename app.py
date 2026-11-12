import uuid                                      # erzeugt zufällige IDs für Testläufe
import streamlit as st
from database import QUERIES, RESPONSES          # die Daten aus database.py
from assignment import get_or_assign_group       # gleichmäßige Gruppenzuteilung
GROUPS = list(RESPONSES.keys())                  # [1, 2, 3, 4, 5]
from storage import save_rating

# Teilnehmer-ID und Gruppe (einmal pro Sitzung) 
if "pid" not in st.session_state:
    st.session_state.pid = (
        st.query_params.get("PROLIFIC_PID") or f"test_{uuid.uuid4().hex[:8]}"  # pilot: "or f"test..." später entfernen
    )

if "group" not in st.session_state:
    st.session_state.group = get_or_assign_group(st.session_state.pid, GROUPS)

# Konfiguration 
LIKERT = [
    "1 - Strongly disagree",
    "2 - Disagree",
    "3 - Somewhat disagree",
    "4 - Neither agree nor disagree",
    "5 - Somewhat agree",
    "6 - Agree",
    "7 - Strongly agree",
]

QUESTIONS = {
    "informative": "I found the response informative:",
    "coherence": "I found the text coherent.",
    "understandable": "I found the text plausibly written.",
    "flow": "The response had a good text flow.",
}

# MIN_WORDS = 10                                   # pilot vl. mindestlänge rein?

# Fortschritt
if "page" not in st.session_state:
    st.session_state.page = 1
if "stage" not in st.session_state:
    st.session_state.stage = "read"

# Lesen
def show_read_stage(query, response):
    st.write("**Imagine you ask an AI the following question:**")
    st.info(query)
    st.write("**Read what the AI responds:**")
    st.info(response)
    if st.button("Continue", key=f"continue_read_{st.session_state.page}"):
        st.session_state.stage = "rate"
        st.rerun()

# Bewerten
def show_rate_stage(query, response):
    page = st.session_state.page

    answers = {}
    for key, text in QUESTIONS.items():
        answers[key] = st.radio(text, LIKERT, index=None, key=f"{key}_{page}")

    st.write(f"Please comment on the text you just read.") # pilot "in at least 10 words"
    comment = st.text_area("Comment", key=f"comment_{page}",
                           label_visibility="collapsed")

    all_answered = all(v is not None for v in answers.values())
    # comment_ok = len(comment.split()) >= MIN_WORDS      # pilot: entkommentieren

    if st.button("Continue", disabled=not (all_answered), # pilot "all_answered and comment_ok"
                 key=f"continue_rate_{page}"):
        save_rating({
            "pid": st.session_state.pid,
            "grp": st.session_state.group,
            "trial": page,
            # "5 - Somewhat agree"[0] is "5", int() turns it into the number 5
            "informative": int(answers["informative"][0]),
            "coherence": int(answers["coherence"][0]),
            "understandable": int(answers["understandable"][0]),
            "flow": int(answers["flow"][0]),
            "comment": comment,
        })
        st.session_state.page += 1
        st.session_state.stage = "read"
        st.rerun()


st.title("User Study")

index = st.session_state.page - 1                # Seite 1 -> Index 0

if index >= len(QUERIES):
    st.success("Thank you, you have finished the study!")
    # st.link_button("Back to Prolific",
    #                "https://app.prolific.com/submissions/complete?cc=DEIN_CODE")
else:
    st.progress(index / len(QUERIES))
    query = QUERIES[index]                                   # gleiche Frage für alle
    response = RESPONSES[st.session_state.group][index]      # Antwort je nach Gruppe
    if st.session_state.stage == "read":
        show_read_stage(query, response)
    else:
        show_rate_stage(query, response)