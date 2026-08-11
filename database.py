'''
functions involving SQL
'''

import sqlite3
import pandas as pd

DB_NAME = "module_and_assignments.db"

# TO CREATE TABLES
def table_setup():
    # opening connection context manager
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # modules table
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS modules (
                        module_code TEXT PRIMARY KEY,
                        module_title TEXT NOT NULL UNIQUE,
                        semester TEXT NOT NULL
                        )
                    ''')

        # assessments table
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS assessments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_code TEXT NOT NULL,
                        assessment_title TEXT NOT NULL,
                        assessment_percentage INTEGER NOT NULL,
                        must_pass_component INTEGER NOT NULL,
                        FOREIGN KEY (module_code) REFERENCES modules (module_code) ON DELETE CASCADE
                        )
                    ''')

        # assessment weeks table
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS assessment_weeks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        assessment_id INTEGER NOT NULL,
                        week INTEGER NOT NULL,
                        FOREIGN KEY (assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
                        )
                    ''')

        conn.commit()
