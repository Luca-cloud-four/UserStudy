
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
