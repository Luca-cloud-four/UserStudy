
# UserStudy
A Streamlit application for a user study

app.py is the app created with streamlit, the thing participants use
assignment.py is to assign randomly
database.py is to save the responses
requirements.py are the required python packages

how to start the app: (run the following in power shell)
streamlit run app.py

pilot:
each comment with "pilot" is an instruction on what to change after the pilot study

getting a csv of the results:
stop the app, than run:
python -c "import sqlite3, pandas as pd; pd.read_sql('SELECT * FROM ratings', sqlite3.connect('assignments.db')).to_csv('ratings.csv', index=False)"

setup:
py -m pip install streamlit-sortables

the link that participants will click on on prolific to get to my study:
https://userstudy-gbxezjew4zusm9g5upjwlr.streamlit.app/

data is stored:
on my supabase account