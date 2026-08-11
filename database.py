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
                        trimester TEXT NOT NULL
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
                        FOREIGN KEY (module_code) REFERENCES modules (module_code)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
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

# TO INITIALISE TABLES (testing with hardcoded data (list) before user input is involved)
def seed_database(MODULES):
    # opening connection context manager
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # querying if data exists in any table
        cur.execute('''
                    SELECT
                        (SELECT COUNT(*)
                        FROM modules) +
                        (SELECT COUNT(*)
                        FROM assessments) +
                        (SELECT COUNT(*)
                        FROM assessment_weeks)
                    ''')

        if cur.fetchone()[0] == 0:
            for module in MODULES:
                cur.execute('''
                            INSERT INTO modules
                            (module_code, module_title, trimester)
                            VALUES
                            (?, ?, ?)
                            ''',
                            (
                                module["Code"],
                                module["Title"],
                                module["Trimester"]
                            )
                            )

                for assessment in module["Assessments"]:
                    cur.execute('''
                                INSERT INTO assessments
                                (module_code, assessment_title, assessment_percentage, must_pass_component)
                                VALUES
                                (?, ?, ?, ?)
                                ''',
                                (
                                    module["Code"],
                                    assessment["Description"],
                                    assessment["Grade Percentage"],
                                    assessment["Must Pass Component"]
                                )
                                )

                    # variable needed for weeks table (need corresponding assessment with week numbers)
                    assessment_id = cur.lastrowid

                    for week in assessment["Weeks"]:
                        cur.execute('''
                                    INSERT INTO assessment_weeks
                                    (assignment_id, week)
                                    VALUES
                                    (?, ?)
                                    ''',
                                    (
                                        assessment_id, week
                                    )
                                    )

    conn.commit()

# FETCHES ALL MODULES AS A DATAFRAME
def get_modules_dataframe():
    # opening connection context manager
    with sqlite3.connect(DB_NAME) as conn:
        query = '''
                SELECT
                module_code AS 'Module Code',
                module_title AS 'Module Title',
                trimester AS 'Trimester'
                FROM modules
                '''

        df = pd.read_sql_query(query, conn)

    return df

# INSERT MODULE
def insert_module(code_input, title_input, trimester_input):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute('''
                    INSERT INTO modules
                    (module_code, module_title, trimester)
                    VALUES
                    (?, ?, ?)
                    ''',
                    (
                        code_input,
                        title_input,
                        trimester_input
                    )
                    )

        conn.commit()

# DELETE MODULE
def delete_module(code_selected):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("PRAGMA foreign_keys = ON")

        cur.execute('''
                    DELETE FROM modules
                    WHERE module_code = ?
                    ''',
                    (
                        code_selected,
                    )
                    )

        conn.commit()