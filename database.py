'''
functions involving SQL
'''

import sqlite3
import pandas as pd

DB_NAME = "modules_and_assessments.db"

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
                                    (assessment_id, week)
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

# FETCHES ALL ASSESSMENTS AS A DATAFRAME
def get_assessments_dataframe():
    with sqlite3.connect(DB_NAME) as conn:
        query = '''
                SELECT
                a.id AS 'Assessment ID',
                a.assessment_title AS 'Assessment Title',
                a.module_code AS 'Module Code',
                a.assessment_percentage AS 'Weight %',
                    CASE WHEN
                    a.must_pass_component = 1
                    THEN 'Yes'
                    ELSE 'No'
                    END AS 'Must Pass',
                GROUP_CONCAT(w.weeks, ', ') AS 'Weeks Due'
                FROM assessments a
                LEFT JOIN assessment_weeks w
                    ON a.id = w.assessment_id
                GROUP BY a.id
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

# INSERT ASESSMENT
def insert_assessment(module_code, title, percentage, must_pass, weeks_list):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute('''
                    INSERT INTO assessments
                    (module_code, assessment_title, assessment_percentage, must_pass_component)
                    VALUES
                    (?, ?, ?, ?)
                    ''',
                    (
                        module_code,
                        title,
                        percentage,
                        must_pass
                    )
                    )
        # variable needed for weeks table
        assessment_id = cur.lastrowid

        for week_num in weeks_list:
            cur.execute('''
                        INSERT INTO assessment_weeks
                        (assessment_id, week)
                        VALUES
                        (?, ?)
                        ''',
                        (
                            assessment_id,
                            week_num
                        )
                        )

        conn.commit()



# UPDATE MODULE
def update_module(old_code, new_code, new_title, new_trimester):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("PRAGMA foreign_keys = ON")

        cur.execute('''
                    UPDATE modules
                    SET
                        module_code = ?,
                        module_title = ?,
                        trimester = ?
                    WHERE
                        module_code = ?
                    ''',
                    (
                        new_code,
                        new_title,
                        new_trimester,
                        old_code
                    )
                    )

        conn.commit()

# UPDATE ASSESSMENT
def update_assessment(assessment_id, new_module_code, new_title, new_percentage, new_must_pass, new_weeks_list):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("PRAGMA foreign_keys = ON")

        cur.execute('''
                    UPDATE assessments
                    SET
                        module_code = ?,
                        assessment_title = ?,
                        assessment_percentage = ?,
                        must_pass_component = ?
                    WHERE
                        id = ?
                    ''',
                    (
                        new_module_code,
                        new_title,
                        new_percentage,
                        new_must_pass,
                        assessment_id
                    )
                    )
        cur.execute("DELETE FROM assessment_weeks WHERE assessment_id = ?", (assessment_id,))
        for week_num in new_weeks_list:
            cur.execute('''
                        INSERT INTO assessment_weeks
                        (assessment_id, week)
                        VALUES
                        (?, ?)s
                        ''',
                        (
                            assessment_id,
                            week_num
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

# DELETE ASSESSMENT
def delete_assessment(assessment_id):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("PRAGMA foreign_keys = ON")

        cur.execute('''
                    DELETE FROM assessments
                    WHERE id = ?
                    ''',
                    (
                        assessment_id,
                    )
                    )

        conn.commit()