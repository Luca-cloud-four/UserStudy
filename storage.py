import sqlite3, csv, os
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "assignments.db"
RANKING_FILE = "rankings.csv"
RANKING_FIELDS = ["pid", "trial", "item", "is_repeat", "response_id", "shown_position", "rank", "timestamp"]
COMPLETED_FILE = "completed.csv"


def get_timestamp():
    return datetime.now(timezone.utc).isoformat()


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            pid             TEXT    NOT NULL,
            grp             INTEGER NOT NULL,
            trial           INTEGER NOT NULL,
            informative     INTEGER,
            coherence       INTEGER,
            understandable  INTEGER,
            flow            INTEGER,
            comment         TEXT,
            ts              TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (pid, trial)
        )
    """)
    return conn


def save_rating(row):
    # row is a dictionary with the keys used as :names below
    with closing(_connect()) as conn:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO ratings
                    (pid, grp, trial, informative, coherence, understandable, flow, comment, ts)
                VALUES
                    (:pid, :grp, :trial, :informative, :coherence, :understandable, :flow, :comment, :timestamp)
            """, row)


def save_disclosure(pid, noticed):
    with closing(_connect()) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS disclosure (
                pid TEXT PRIMARY KEY,
                noticed TEXT,
                ts TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.execute(
                "INSERT OR REPLACE INTO disclosure (pid, noticed, ts) VALUES (?,?,?)",
                (pid, noticed, get_timestamp())
            )


def save_ranking(rows):
    file_exists = os.path.exists(RANKING_FILE)
    with open(RANKING_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RANKING_FIELDS)
        if not file_exists:
            writer.writeheader()

        for row in rows:
            row["timestamp"] = get_timestamp()

        writer.writerows(rows)


def participant_has_completed(pid):
    if not os.path.exists(COMPLETED_FILE):
        return False

    with open(COMPLETED_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["pid"] == pid:
                return True

    return False


def mark_participant_completed(pid):
    file_exists = os.path.exists(COMPLETED_FILE)

    with open(COMPLETED_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pid", "timestamp"])

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "pid": pid,
            "timestamp": get_timestamp()
        })
