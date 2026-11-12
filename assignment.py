import random
import sqlite3 # communication with a SQLite database
from contextlib import closing # helper for closing the connection

DB_PATH = "assignments.db" # to save how many participants have been assigned to what groups

def _connect(): # _ means helper: not meant to be used from other files
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None) # open database file/create it; timeout = wait 30 seconds if different participant currently holds database lock
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            pid TEXT PRIMARY KEY, grp INTEGER NOT NULL, ts TEXT DEFAULT CURENT_TIMESTAMP)
    """) #participant ID, participant group, time of assignement
    return conn

def get_or_assign_group(pid, groups): #participants prolific id, list of group numbers eg. [1,2,3]
    with closing(_connect()) as conn: #opens conn and closes it as soon as indented block ends
        conn.execute("BEGIN IMMEDIATE") # begin immediate: participant has a lock, so two people can never be assigned based on the same counts
        try: # if this does not work, except undoes everything since BEGIN so DB stays consistent
            row = conn.execute(
                "SELECT grp FROM assignments WHERE pid = ?", (pid,) #pid filled into ? to avoid sql injection
            ).fetchone() #fetchone returns the matches row as a tupel, otherwise returns none, the tupel has only one element as it only asked for grp

            if row: #in case of a participant rerunning/reopening the page, true= a row was found false= no row was found
                conn.execute("COMMIT") # end transaction with conn and release the lock
                return row[0] # return the only col that row has rn which is grp

            counts = {g: 0 for g in groups} # initialisiert jede gruppe auf 0
            for g,n in conn.execute( # returns tupels of (group, number)
                "SELECT grp, COUNT(*) FROM assignments GROUP BY grp"
            ):
                if g in counts: #all groups who already have participants get n assigned
                    counts[g] = n
            fewest = min(counts.values()) #smallest participant count
            candidates = [g for g, n in counts.items() if n == fewest] #list of groups with smallest participant number
            # first g is what get's put into the list
            grp = random.choice(candidates) #assign
            
            conn.execute( #remember assignement
                "INSERT INTO assignments (pid, grp) VALUES (?,?)", (pid, grp)
            )
            conn.execute("COMMIT") #release lock
            return grp
        
        except Exception:
            conn.execute("ROLLBACK")
            raise