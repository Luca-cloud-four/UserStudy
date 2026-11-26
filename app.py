import uuid
import random
import streamlit as st
from datetime import datetime, timezone
from streamlit_sortables import sort_items
from database import QUERIES, RESPONSES, RANKING_TASKS
from assignment import get_or_assign_group

# debug =========================================

from storage import get_client, save_disclosure

st.subheader("Supabase write test")

try:
    test_pid = "TEST_CONNECTION_123"

    save_disclosure(test_pid, True)

    st.success("Successfully wrote test data to Supabase!")

except Exception as e:
    st.error(f"Supabase write failed: {e}")
# debug end ========================================

GROUPS = list(RESPONSES.keys())

from storage import (
    save_rating,
    save_disclosure,
    save_ranking,
    participant_has_completed,
    mark_participant_completed,
    get_timestamp,
)

NUM_TRIALS_PHASE1 = 3
NUM_TRIALS_PHASE2 = 3
NUM_RESPONSES_TO_RANK = 6
MIN_GAP_BETWEEN_REPEATS = 2

if NUM_TRIALS_PHASE1 > len(QUERIES) or NUM_TRIALS_PHASE2 > len(RANKING_TASKS):
    st.error("NUM_TRIALS is larger than the data in database.py")
    st.stop()

if NUM_TRIALS_PHASE1 < MIN_GAP_BETWEEN_REPEATS or NUM_TRIALS_PHASE2 < MIN_GAP_BETWEEN_REPEATS:
    st.error("NUM_TRIALS must be at least MIN_GAP_BETWEEN_REPEATS")
    st.stop()


# PARTICIPANT ID

if "pid" not in st.session_state:
    st.session_state.pid = (
        st.query_params.get("PROLIFIC_PID") or f"test_{uuid.uuid4().hex[:8]}"
    )

if participant_has_completed(st.session_state.pid):
    st.error("You have already completed this study. Thank you!")
    st.stop()


# STUDY START TIMESTAMP

if "study_start" not in st.session_state:
    st.session_state.study_start = get_timestamp()


# GROUP ASSIGNMENT

if "group" not in st.session_state:
    st.session_state.group = get_or_assign_group(st.session_state.pid, GROUPS)


if "order" not in st.session_state:
    order = list(range(NUM_RESPONSES_TO_RANK))
    random.Random(st.session_state.pid).shuffle(order)
    st.session_state.order = order


def build_sequence(n, seed_text):
    rng = random.Random(seed_text)
    seq = list(range(n))
    p = rng.randint(0, n - MIN_GAP_BETWEEN_REPEATS)
    q = rng.randint(p + MIN_GAP_BETWEEN_REPEATS, n)
    seq.insert(q, seq[p])
    return seq


if "seq1" not in st.session_state:
    st.session_state.seq1 = build_sequence(
        NUM_TRIALS_PHASE1, f"{st.session_state.pid}_phase1"
    )

if "seq2" not in st.session_state:
    st.session_state.seq2 = build_sequence(
        NUM_TRIALS_PHASE2, f"{st.session_state.pid}_phase2"
    )


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


if "page" not in st.session_state:
    st.session_state.page = 1

if "stage" not in st.session_state:
    st.session_state.stage = "read"

if "phase" not in st.session_state:
    st.session_state.phase = "phase1"

if "page2" not in st.session_state:
    st.session_state.page2 = 1

if "stage2" not in st.session_state:
    st.session_state.stage2 = "instruction"


# READ STAGE

def show_read_stage(query, response):
    page = st.session_state.page

    # Record when the response is first displayed
    if "read_start" not in st.session_state:
        st.session_state.read_start = get_timestamp()

    st.write("**Imagine you ask an AI the following question:**")
    st.info(query)

    st.write("**Read what the AI responds:**")
    st.info(response)

    if st.button("Continue", key=f"continue_read_{page}"):

        # Record reading completion
        st.session_state.read_end = get_timestamp()

        start = datetime.fromisoformat(st.session_state.read_start)
        end = datetime.fromisoformat(st.session_state.read_end)

        st.session_state.reading_time = (end - start).total_seconds()

        st.session_state.stage = "rate"
        st.rerun()


# RATE STAGE

def show_rate_stage():
    page = st.session_state.page
    item = st.session_state.seq1[page - 1]
    is_repeat = item in st.session_state.seq1[:page - 1]

    answers = {}

    for key, text in QUESTIONS.items():
        answers[key] = st.radio(
            text,
            LIKERT,
            index=None,
            key=f"{key}_{page}"
        )

    st.write("Please comment on the text you just read.")

    comment = st.text_area(
        "Comment",
        key=f"comment_{page}",
        label_visibility="collapsed"
    )

    all_answered = all(v is not None for v in answers.values())

    if st.button(
        "Continue",
        disabled=not all_answered,
        key=f"continue_rate_{page}"
    ):

        rating_timestamp = get_timestamp()

        save_rating({
            "pid": st.session_state.pid,
            "grp": st.session_state.group,
            "trial": page,
            "item": item,
            "is_repeat": int(is_repeat),
            "informative": int(answers["informative"][0]),
            "coherence": int(answers["coherence"][0]),
            "understandable": int(answers["understandable"][0]),
            "flow": int(answers["flow"][0]),
            "comment": comment,
            "timestamp": rating_timestamp,
        })

        st.session_state.page += 1
        st.session_state.stage = "read"

        # Reset reading timer for next response
        st.session_state.pop("read_start", None)
        st.session_state.pop("read_end", None)
        st.session_state.pop("reading_time", None)

        st.rerun()


# DISCLOSURE

def disclosure():
    answer = st.radio(
        "The AI responses you read contained ads. Did you notice?",
        ["Yes", "No"],
        index=None,
        key="noticed_ads"
    )

    if st.button(
        "Continue",
        disabled=(answer is None),
        key="continue_disclosure"
    ):
        save_disclosure(st.session_state.pid, answer)

        st.session_state.disclosure_timestamp = get_timestamp()
        st.session_state.phase = "phase2"

        st.rerun()


# INSTRUCTION STAGE

def show_instruction_stage(task):
    st.info(
        "You are now seeing different versions on how an ad blocker could label an ad in the same LLM-response, rank your preference:"
    )

    if st.button(
        "Continue",
        key=f"continue_instr_{st.session_state.page2}"
    ):
        st.session_state.stage2 = "rank"
        st.rerun()


# RANK STAGE

def show_rank_stage(task):
    page2 = st.session_state.page2
    item = st.session_state.seq2[page2 - 1]
    is_repeat = item in st.session_state.seq2[:page2 - 1]

    st.write(
        f"**Rank the {NUM_RESPONSES_TO_RANK} responses: "
        "drag the letters on the right into the fields. "
        f"1 = best, {NUM_RESPONSES_TO_RANK} = worst.**"
    )

    order = st.session_state.order

    letters = [
        chr(ord("A") + i)
        for i in range(NUM_RESPONSES_TO_RANK)
    ]

    half = (NUM_RESPONSES_TO_RANK + 1) // 2

    col_left, col_mid, col_right = st.columns([3, 3, 2])

    with col_left:
        for shown_pos in range(0, half):
            st.write(f"**Response {letters[shown_pos]}**")
            st.info(task["responses"][order[shown_pos]])

    with col_mid:
        for shown_pos in range(half, NUM_RESPONSES_TO_RANK):
            st.write(f"**Response {letters[shown_pos]}**")
            st.info(task["responses"][order[shown_pos]])

    with col_right:
        st.write("**Your ranking**")

        containers = [
            {"header": "Responses", "items": letters}
        ]

        for r in range(1, NUM_RESPONSES_TO_RANK + 1):
            title = str(r)

            if r == 1:
                title = "1 (best)"

            if r == NUM_RESPONSES_TO_RANK:
                title = f"{r} (worst)"

            containers.append({
                "header": title,
                "items": []
            })

        result = sort_items(
            containers,
            multi_containers=True,
            direction="vertical",
            key=f"sort_{page2}",
        )

    pool = result[0]["items"]
    fields = result[1:]

    all_placed = len(pool) == 0
    all_unique = all(len(f["items"]) == 1 for f in fields)

    valid = all_placed and all_unique

    if not all_placed:
        st.caption("Please move all letters into the fields.")

    elif not all_unique:
        st.warning("Each field must contain exactly one letter.")

    if st.button(
        "Continue",
        disabled=not valid,
        key=f"continue_rank_{page2}"
    ):

        rank_of = {}

        if valid:
            for r, f in enumerate(fields, start=1):
                rank_of[f["items"][0]] = r

        ranking_timestamp = get_timestamp()

        rows = []

        for shown_pos in range(NUM_RESPONSES_TO_RANK):
            rows.append({
                "pid": st.session_state.pid,
                "trial": page2,
                "item": item,
                "is_repeat": int(is_repeat),
                "response_id": order[shown_pos],
                "shown_position": shown_pos + 1,
                "rank": rank_of[letters[shown_pos]],
                "timestamp": ranking_timestamp,
            })

        save_ranking(rows)

        st.session_state.page2 += 1
        st.session_state.stage2 = "instruction"

        st.rerun()


# MAIN APP

st.title("User Study")

if st.session_state.phase == "phase1":

    index = st.session_state.page - 1

    if index >= len(st.session_state.seq1):
        st.session_state.phase = "disclosure"
        st.rerun()

    else:
        st.progress(index / len(st.session_state.seq1))

        item = st.session_state.seq1[index]
        query = QUERIES[item]
        response = RESPONSES[st.session_state.group][item]

        if st.session_state.stage == "read":
            show_read_stage(query, response)

        else:
            show_rate_stage()


elif st.session_state.phase == "disclosure":

    disclosure()


elif st.session_state.phase == "phase2":

    index2 = st.session_state.page2 - 1

    if index2 >= len(st.session_state.seq2):
        st.session_state.phase = "done"
        st.rerun()

    else:
        st.write("**Part 2**")

        st.progress(index2 / len(st.session_state.seq2))

        task = RANKING_TASKS[st.session_state.seq2[index2]]

        if st.session_state.stage2 == "instruction":
            show_instruction_stage(task)

        else:
            show_rank_stage(task)


else:

    if not st.session_state.get("completion_recorded", False):

        mark_participant_completed(st.session_state.pid)

        st.session_state.completion_timestamp = get_timestamp()
        st.session_state.completion_recorded = True

    st.success("Thank you, you have finished the study!")
