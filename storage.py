# storage.py
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "assignments.db"   


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)       
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            pid             TEXT    NOT NULL,             -- participant (links to assignments.pid)
            grp             INTEGER NOT NULL,             -- group at the time of rating
            trial           INTEGER NOT NULL,             -- trial number 1-20
            informative     INTEGER,                      -- Likert answers stored as numbers 1-7
            coherence       INTEGER,
            understandable  INTEGER,
            flow            INTEGER,
            comment         TEXT,
            ts              TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (pid, trial)                  -- one rating per participant per trial
        )
    """)
    return conn


def save_rating(row):
    # row is a dictionary with the keys used as :names below
    with closing(_connect()) as conn:                 # closes the connection afterwards
        with conn:                                    # commits on success, rolls back on error
            conn.execute("""
                INSERT OR REPLACE INTO ratings
                    (pid, grp, trial, informative, coherence, understandable, flow, comment)
                VALUES
                    (:pid, :grp, :trial, :informative, :coherence, :understandable, :flow, :comment)
            """, row)

def save_disclosure(pid, noticed):
    with closing(_connect()) as conn: # connection
        with conn:                      # transaction
            conn.execute("""
                CREATE TABLE IF NOT EXISTS disclosure (
                pid TEXT PRIMARY KEY,
                noticed TEXT,
                ts TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.execute("INSERT OR REPLACE INTO disclosure (pid, noticed) VALUES (?,?)",(pid, noticed))
