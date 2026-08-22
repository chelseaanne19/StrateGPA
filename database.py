'''
functions involving SQL
'''

import sqlite3
import pandas as pd

DB_NAME = "modules_and_assessments.db"

# ___________________
# TABLES
# ___________________
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
                        week INTEGER NOT NULL,
                        received_grade REAL DEFAULT NULL,
                        FOREIGN KEY (module_code) REFERENCES modules (module_code)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                        )
                    ''')

        # settings
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        institution_name TEXT NOT NULL,
                        grading_system TEXT NOT NULL,
                        target_gpa REAL NOT NULL,
                        teaching_weeks_autumn INTEGER NOT NULL DEFAULT 12,
                        teaching_weeks_spring INTEGER NOT NULL DEFAULT 14
                        )
                    ''')

        conn.commit()


# _________________
# SETTINGS / CONFIGURATIONS
# _________________
def get_user_settings():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute('''
                    SELECT
                        institution_name,
                        grading_system,
                        target_gpa,
                        teaching_weeks_autumn,
                        teaching_weeks_spring
                    FROM settings
                    LIMIT 1
                    ''')

        row = cur.fetchone()

    if row:
        return{"institution" : row[0],
               "system" : row[1],
               "target_gpa" : row[2],
               "teaching_weeks_autumn" : int(row[3]),
               "teaching_weeks_spring" : int(row[4])}

    return None

def save_user_settings(institution, system, target, teaching_weeks_autumn, teaching_weeks_spring):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM settings")
        cur.execute('''
                    INSERT INTO settings
                        (institution_name,
                        grading_system,
                        target_gpa,
                        teaching_weeks_autumn,
                        teaching_weeks_spring)
                    VALUES
                        (?, ?, ?)
                    ''',
                    (
                        (institution, system, target, teaching_weeks_autumn, teaching_weeks_spring)
                    )
                    )
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


# __________________
# DATA / DATAFRAME FETCHING
# __________________
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
                id AS 'Assessment ID',
                assessment_title AS 'Assessment Title',
                module_code AS 'Module Code',
                assessment_percentage AS 'Weight %',
                    CASE WHEN
                    must_pass_component = 1
                    THEN 'Yes'
                    ELSE 'No'
                    END AS 'Must Pass',
                    week AS 'Week Due',
                    CASE WHEN received_grade IS NOT NULL THEN PRINTF('%.1f%%', received_grade) ELSE 'Pending' END AS 'Result'
                FROM assessments
                ORDER BY week ASC, module_code ASC
                '''

        df = pd.read_sql_query(query, conn)

    return df



# INSERT MODULE
def insert_module(code_input, title_input, trimester_input):
    try:
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
        return True
    except sqlite3.IntegrityError:
        return False

# INSERT ASESSMENT
def insert_assessment(module_code, title, percentage, must_pass, weeks_list):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()

            # calculate assessment weighting
            num_weeks = len(weeks_list)
            base_weight = percentage // num_weeks
            remainder = percentage % num_weeks

            for index, week_num in enumerate(weeks_list):
                display_title = f"{title} (Wk {week_num})" if num_weeks > 1 else title

                if index == num_weeks - 1: # last week
                    row_weight = base_weight + remainder
                else:
                    row_weight = base_weight


                cur.execute('''
                            INSERT INTO assessments
                                (module_code,
                                assessment_title,
                                assessment_percentage,
                                must_pass_component,
                                week,
                                received_grade)
                            VALUES
                                (?, ?, ?, ?, ?, NULL)
                            ''',
                            (
                                module_code,
                                display_title,
                                row_weight,
                                must_pass,
                                week_num
                            )
                            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False



# UPDATE MODULE
def update_module(old_code, new_code, new_title, new_trimester):
    try:
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
        return True
    except sqlite3.IntegrityError:
        return False

# UPDATE ASSESSMENT
def update_assessment(assessment_id, new_module_code, new_title, new_percentage, new_must_pass, new_weeks_list):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON")

            cur.execute('''
                        UPDATE assessments
                        SET
                            module_code = ?,
                            assessment_title = ?,
                            assessment_percentage = ?,
                            must_pass_component = ?,
                            week = ?
                        WHERE
                            id = ?
                        ''',
                        (
                            new_module_code,
                            new_title,
                            new_percentage,
                            new_must_pass,
                            new_week,
                            assessment_id
                        )
                        )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# SUBMIT GRADES
def update_assessment_grade(assessment_id, grade):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()

            cur.execute('''
                        UPDATE assessments
                        SET received_grade = ?
                        WHERE id = ?
                        ''',
                        (
                            grade,
                            assessment_id
                        )
                        )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False



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



# _________________________
# WEEKLY WORKLOAD FUNCTIONS
# _________________________

# gets workload grouped by week, always filtered by trimester, and module if selected
def get_weekly_workload(trimester, module_code = None):
    with sqlite3.connect(DB_NAME) as conn:
        query = '''
                SELECT
                    a.week as 'Week',
                    SUM(a.assessment_percentage) AS 'Total Workload (%)',
                    m.module_code AS 'Module'
                FROM assessments a
                JOIN modules m
                ON m.module_code = a.module_code
                WHERE trimester = ?
                '''

        # trimester must always be filtered
        params = [trimester]

        # optional filter of module
        if module_code is not None:
            params.append(module_code)
            query += " AND m.module_code = ?"


        # complete query
        query += " GROUP BY a.week, m.module_code ORDER BY a.week ASC"

        df = pd.read_sql_query(query, conn, params = tuple(params))
        return df

# gets weekly workload contributors as modules
def get_week_contributors(trimester, target_week):
    with sqlite3.connect(DB_NAME) as conn:
        query = ''' 
                SELECT
                    m.module_code AS 'Module Code',
                    m.module_title AS 'Module Title',
                    SUM(a.assessment_percentage) AS 'Contribution (%)'
                    FROM assessments a
                    JOIN modules m ON m.module_code = a.module_code
                    WHERE m.trimester = ? AND a.week = ?
                    GROUP BY m.module_code
                    ORDER BY [Contribution (%)] DESC
                '''

        df = pd.read_sql_query(query, conn, params = (trimester, target_week))

    return df

def get_grade_progress(trimester, module_code = None):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        query = '''
            SELECT 
                COALESCE(SUM(a.assessment_percentage), 0) AS total_weight,
                COALESCE(SUM(CASE WHEN a.received_grade IS NOT NULL THEN a.assessment_percentage ELSE 0 END), 0) AS completed_weight,
                COALESCE(SUM(CASE WHEN a.received_grade IS NOT NULL THEN (a.assessment_percentage * (a.received_grade / 100.0)) ELSE 0 END), 0) AS earned_points
            FROM assessments a
            JOIN modules m ON a.module_code = m.module_code
            WHERE m.trimester = ?
        '''
    
        params = [trimester]

        if module_code is not None:
            query += " AND a.module_code = ?"
            params.append(module_code)
        

        cur.execute(query, tuple(params))
        row = cur.fetchone()
        
        total_weight = float(row[0])
        completed_weight = float(row[1])
        earned_points = float(row[2])
        upcoming_weight = total_weight - completed_weight
        
    return {
        "total_weight": total_weight,
        "completed_weight": completed_weight,
        "earned_points": earned_points,
        "upcoming_weight": upcoming_weight
    }

def get_week_agenda(trimester, target_week):
    with sqlite3.connect(DB_NAME) as conn:
        query = '''
                SELECT
                    a.id AS 'Assessment ID',
                    a.module_code AS 'Module Code',
                    a.assessment_title AS 'Assessment Title',
                    a.assessment_percentage AS 'Weight %',
                    a.must_pass_component AS 'Must Pass',
                    a.received_grade AS 'Received Grade'
                FROM assessments a
                JOIN modules m on a.module_code = m.module_code
                WHERE m.trimester = ? AND a.week = ?
                ORDER BY a.module_code ASC
                '''

        df = pd.read_sql_query(query, conn, params = (trimester, target_week))
        return df