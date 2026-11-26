# It decides which group (1-5) a participant gets, and remembers it permanently in Supabase.
# The real logic is a small program inside the database (the function "assign_group" from
# supabase_setup.sql). Here we only call it.

from storage import get_client                   # import the Supabase connection function from our file storage.py


def get_or_assign_group(pid, groups):            # same name as before, so app.py does not need to change
                                                 # pid = participant ID, groups = list of groups, e.g. [1, 2, 3, 4, 5]
    result = get_client().rpc(                   # get the connection; rpc = "remote procedure call" = ask the database
                                                 # to run one of its own functions and give us the answer
        "assign_group",                          # name of the database function to run (created in the SQL file)
        {"p_pid": pid, "p_groups": groups},      # the inputs for that function, as a dictionary:
                                                 # the participant ID and the list of possible groups
    ).execute()                                  # execute() = actually send the request to Supabase now
    return int(result.data)                      # result.data holds the answer; int() makes sure it is a whole number (the group)