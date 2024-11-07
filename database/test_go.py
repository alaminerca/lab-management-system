# In Python console or script
import sqlite3

with open('database/schema_updates.sql', 'r') as file:
    sql_script = file.read()

with sqlite3.connect('lab_management.db') as conn:
    conn.executescript(sql_script)