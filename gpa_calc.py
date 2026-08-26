import sqlite3
import pandas as pd
from database import DB_NAME, get_user_settings

def convert_ucd_mark_to_grade(percentage, scale_type = "Standard 40% Pass"):
    """
    translates percentage score into matching UCD letter grades and gpa points
    """
    # safeguarding
    if percentage < 0: percentage = 0.0
    if percentage > 100: percentage = 100.0

 
    # SCALE 1: STANDARD CONVERSION GRADE SCALE (40% PASS) - DEFAULT
    if scale_type == "Standard 40% Pass":
        if percentage >= 90.00: return "A+", 4.2
        elif percentage >= 80.00: return "A", 4.0
        elif percentage >= 70.00: return "A-", 3.8
        elif percentage >= 66.67: return "B+", 3.6
        elif percentage >= 63.33: return "B", 3.4
        elif percentage >= 60.00: return "B-", 3.2
        elif percentage >= 56.67: return "C+", 3.0
        elif percentage >= 53.33: return "C", 2.8
        elif percentage >= 50.00: return "C-", 2.6
        elif percentage >= 46.67: return "D+", 2.4
        elif percentage >= 43.33: return "D", 2.2
        elif percentage >= 40.00: return "D-", 2.0
        elif percentage >= 30.00: return "E", 1.6
        else: return "F", 1.0

    # SCALE 2: ALTERNATIVE LINEAR CONVERSION GRADE SCALE (40% PASS)
    elif scale_type == "Alternative Linear 40% Pass":
        if percentage >= 95.00: return "A+", 4.2
        elif percentage >= 90.00: return "A", 4.0
        elif percentage >= 85.00: return "A-", 3.8
        elif percentage >= 80.00: return "B+", 3.6
        elif percentage >= 75.00: return "B", 3.4
        elif percentage >= 70.00: return "B-", 3.2
        elif percentage >= 65.00: return "C+", 3.0
        elif percentage >= 60.00: return "C", 2.8
        elif percentage >= 55.00: return "C-", 2.6
        elif percentage >= 50.00: return "D+", 2.4
        elif percentage >= 45.00: return "D", 2.2
        elif percentage >= 40.00: return "D-", 2.0
        elif percentage >= 30.00: return "E", 1.6
        else: return "F", 1.0

    # SCALE 3: ALTERNATIVE NON-LINEAR CONVERSION GRADE SCALE (50% PASS)
    elif scale_type == "Alternative Non-Linear 50% Pass":
        if percentage >= 95.00: return "A+", 4.2
        elif percentage >= 90.00: return "A", 4.0
        elif percentage >= 85.00: return "A-", 3.8
        elif percentage >= 80.00: return "B+", 3.6
        elif percentage >= 75.00: return "B", 3.4
        elif percentage >= 70.00: return "B-", 3.2
        elif percentage >= 65.00: return "C+", 3.0
        elif percentage >= 60.00: return "C", 2.8
        elif percentage >= 55.00: return "C-", 2.6
        elif percentage >= 52.00: return "D+", 2.4
        elif percentage >= 51.00: return "D", 2.2
        elif percentage >= 50.00: return "D-", 2.0
        elif percentage >= 33.33: return "E", 1.6
        else: return "F", 1.0

    # SCALE 4: ALTERNATIVE LINEAR CONVERSION GRADE SCALE (60% PASS)
    elif scale_type == "Alternative Linear 60% Pass":
        if percentage >= 96.67: return "A+", 4.2
        elif percentage >= 93.33: return "A", 4.0
        elif percentage >= 90.00: return "A-", 3.8
        elif percentage >= 86.67: return "B+", 3.6
        elif percentage >= 83.33: return "B", 3.4
        elif percentage >= 80.00: return "B-", 3.2
        elif percentage >= 76.67: return "C+", 3.0
        elif percentage >= 73.33: return "C", 2.8
        elif percentage >= 70.00: return "C-", 2.6
        elif percentage >= 66.67: return "D+", 2.4
        elif percentage >= 63.33: return "D", 2.2
        elif percentage >= 60.00: return "D-", 2.0
        elif percentage >= 45.00: return "E", 1.6
        else: return "F", 1.0

    return "D-", 2.0

def convert_us_mark_to_grade(percentage):

    if percentage >= 93.0: return "A", 4.0
    elif percentage >= 90.0: return "A-", 3.7
    elif percentage >= 87.0: return "B+", 3.3
    elif percentage >= 83.0: return "B", 3.0
    elif percentage >= 80.0: return "B-", 2.7
    elif percentage >= 77.0: return "C+", 2.3
    elif percentage >= 73.0: return "C", 2.0
    elif percentage >= 70.0: return "C-", 1.7
    elif percentage >= 67.0: return "D+", 1.3
    elif percentage >= 65.0: return "D", 1.0
    else: return "F", 0.0

def convert_percentage_to_grade(percentage):

    if percentage >= 70.0: return "1st", percentage
    elif percentage >= 60.0: return "2:1", percentage
    elif percentage >= 50.0: return "2:2", percentage
    elif percentage >= 40.0: return "Pass", percentage
    else: return "Fail", percentage


def calculate_running_module_score(module_code):
    '''
    gets assessments from certain module that have been graded,
    calculates running score,
    returns dict with raw percentage, corresponding letter grade, gpa value
    '''

    user_profile = get_user_settings()
    system = user_profile["system"]

    with sqlite3.connect(DB_NAME) as conn:
        query = '''
                SELECT
                    assessment_percentage,
                    received_grade,
                    component_scale
                FROM assessments
                WHERE module_code = ?
                '''

        df = pd.read_sql_query(query, conn, params = (module_code,))

    if df.empty:
        return {"percentage" : 0.0, "letter" : "NG", "points" : 0.0, "completed_weight" : 0.0}



    completed_weight = 0
    points = 0

    for idx, row in df.iterrows():
        weight = float(row["assessment_percentage"])
        grade = float(row["received_grade"])

        if pd.notna(grade):
            completed_weight += weight
            points += weight * (float(grade) / 100.0)


    if completed_weight == 0:
        return {"percentage" : 0.0, "letter" : "Pending", "points": 0.0, "completed_weight" : 0.0}


    running_percentage = (points / completed_weight) * 100.0

    if "UCD" in system:
        scale = df["Component Scale"].iloc[0] if not df["Component Scale"].empty else "standard 40% Pass"
        letter_grade, gpa_points = convert_ucd_mark_to_grade(running_percentage, scale_type = scale)
    elif "US" in system:
        letter_grade, gpa_points = convert_us_mark_to_grade(running_percentage)
    else:
        letter_grade, gpa_points = convert_percentage_to_grade(running_percentage)


    return {
        "percentage" : running_percentage,
        "letter" : letter_grade,
        "points" : gpa_points,
        "completed_weight" : completed_weight
    }