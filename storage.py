# WHAT IS THIS FILE?
# It sends all study data to Supabase (a database in the internet). Your old version saved to a file
# on the computer (SQLite + csv). That does not work on Streamlit Cloud, because files there are
# deleted whenever the app restarts. This version keeps all the functions of your old file,
# so app.py can stay the way it is.

import time                                      # built-in Python tool; used to wait a moment between retries
from datetime import datetime, timezone          # tools for the current date and time
import streamlit as st                           # streamlit, needed to read the secret passwords
from supabase import create_client               # the tool that connects Python to Supabase


def get_timestamp():                             # same function as in your old file
    return datetime.now(timezone.utc).isoformat()   # current time as text, e.g. "2026-11-26T10:57:03+00:00"


@st.cache_resource                               # run the function below only ONCE and remember the result
def get_client():                                # gives us a ready-to-use connection to Supabase
    url = st.secrets["supabase"]["url"]          # web address of your project (from secrets)
    key = st.secrets["supabase"]["key"]          # the secret key = the password (from secrets)
    return create_client(url, key)               # connect and hand back the connection


def _save(table, data, conflict):                # helper: writes data into a table
                                                 # table = table name, data = one row or a list of rows
                                                 # conflict = columns that identify a row (for upsert)
    for attempt in range(3):                     # try up to 3 times (attempt = 0, 1, 2)
        try:                                     # run this; if it crashes, jump to "except"
            get_client().table(table).upsert(    # upsert = insert a new row, or overwrite the row if it exists
                data, on_conflict=conflict       # "conflict" says what counts as "the same row"
            ).execute()                          # actually send it to Supabase now
            return                               # it worked -> leave the function
        except Exception:                        # something went wrong (e.g. short network problem)
            if attempt == 2:                     # third failure ...
                raise                            # ... stop and show the error
            time.sleep(1)                        # otherwise wait 1 second and try again


def save_rating(row):                            # phase 1: row = dictionary with one rating
    data = dict(row)                             # make a copy so we do not change the original
    data["ts"] = data.pop("timestamp", None) or get_timestamp()   # the app sends "timestamp"; the table column is called "ts"
    _save("ratings", data, "pid,trial")          # save it; one rating = participant + trial


def save_ranking(rows):                          # phase 2: rows = list of 6 dictionaries
    stamp = get_timestamp()                      # one timestamp for all 6 rows
    data = []                                    # new empty list for the cleaned rows
    for row in rows:                             # go through the 6 rows
        r = dict(row)                            # copy the row
        r.pop("timestamp", None)                 # remove "timestamp" if it is there (the column is called "ts")
        r["ts"] = stamp                          # add the timestamp under the right name
        data.append(r)                           # put the row into the new list
    _save("rankings", data, "pid,trial,shown_position")   # save; one row = participant + round + position


def save_disclosure(pid, noticed):               # answer to "Did you notice the ads?"
    _save("disclosures",                         # table name
          {"pid": pid, "noticed_ads": noticed, "ts": get_timestamp()},   # the row to save
          "pid")                                 # one answer per participant


def participant_has_completed(pid):              # True if this participant already finished the study
    result = (get_client().table("completed")    # look into the table "completed"
              .select("pid")                     # we only need the pid column
              .eq("pid", pid)                    # only rows where pid equals this participant
              .execute())                        # send the request
    return len(result.data) > 0                  # True if at least one row was found


def mark_participant_completed(pid):             # remember that this participant finished
    _save("completed", {"pid": pid, "ts": get_timestamp()}, "pid")   # one row per participant