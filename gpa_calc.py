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

def convert_percentage_to_class(percentage):

    if percentage >= 70.0: return "1st", percentage
    elif percentage >= 60.0: return "2:1", percentage
    elif percentage >= 50.0: return "2:2", percentage
    elif percentage >= 40.0: return "Pass", percentage
    else: return "Fail", percentage

def get_ucd_letter_from_points(points):
    if points >= 4.10: return "A+"
    elif points >= 3.90: return "A"
    elif points >= 3.70: return "A-"
    elif points >= 3.50: return "B+"
    elif points >= 3.30: return "B"
    elif points >= 3.10: return "B-"
    elif points >= 2.90: return "C+"
    elif points >= 2.70: return "C"
    elif points >= 2.50: return "C-"
    elif points >= 2.30: return "D+"
    elif points >= 2.10: return "D"
    elif points >= 2.00: return "D-"
    elif points >= 1.50: return "E"
    else: return "F"

def get_us_letter_from_points(points):
    if points >= 3.85: return "A"
    elif points >= 3.50: return "A-"
    elif points >= 3.15: return "B+"
    elif points >= 2.85: return "B"
    elif points >= 2.50: return "B-"
    elif points >= 2.15: return "C+"
    elif points >= 1.85: return "C"
    elif points >= 1.50: return "C-"
    elif points >= 1.15: return "D+"
    elif points >= 1.00: return "D"
    else: return "F"

def calculate_module_gpa(module_code):
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
        return {"Module Average": 0.0, "Letter_Grade" : "NG", "Module GPA": 0.0, "Weight Graded": 0.0}
    
    
    ##### RUNNING MODULE PERCENTAGES    
    # mcq: worth 20%, scored 90%
    # lab quiz: worth 80%, scored 95%
    # format: [assessment_percentage], [received_grade]
    
    earned_assessment_percentage = 0.0
    total_assessment_percentage = 0.0
    module_gpa_points = 0.0
    
    for idx, row in df.iterrows():
        assessment_percentage = row["assessment_percentage"]
        received_grade = row["received_grade"]
        component_scale = row["component_scale"]
        
        # running percentages
        if pd.notna(received_grade):
            percentage_of_module = received_grade * (assessment_percentage / 100.0)
            earned_assessment_percentage += percentage_of_module
            total_assessment_percentage += assessment_percentage
        
            # gpa calculations FOR assessment only
            if "UCD" in system:
                _, assessment_gpa_points = convert_ucd_mark_to_grade(received_grade, scale_type = component_scale)
                module_gpa_points += assessment_gpa_points * assessment_percentage
            elif "US" in system:
                _, assessment_gpa_points = convert_us_mark_to_grade(received_grade)
                module_gpa_points += assessment_gpa_points * assessment_percentage
                  
    
    if total_assessment_percentage == 0:
        return {"Module Average" : 0.0, "Letter_Grade": "Pending", "Module GPA": 0.0, "Weight Graded": 0.0}
    
    
    final_running_percentage = (earned_assessment_percentage / total_assessment_percentage) * 100
    
    
    if "Percentage" in system:
        final_module_gpa = final_running_percentage
        final_letter = convert_percentage_to_class(final_running_percentage)
    else:
        final_module_gpa = module_gpa_points / total_assessment_percentage
        
        if "UCD" in system:
            final_letter = get_ucd_letter_from_points(final_module_gpa)
        else:
            final_letter = get_us_letter_from_points(final_module_gpa)
    
    return {
        "Module Average" : final_running_percentage,
        "Letter_Grade" : final_letter,
        "Module GPA" : round(final_module_gpa, 2),
        "Weight Graded" : total_assessment_percentage,
        
        "Evaluation Status" : "Fully Assessed" if total_assessment_percentage >= 100 else "Some graded assessments have yet to be registered.",
        "Performance Status" : "Finalised Grade" if total_assessment_percentage >= 100 else "Provisional Grade, subject to improvement."
        }

def calculate_semester_gpa(trimester):
    # get modules table to get all courses for term
    # loop through modules to get module gpa
    # get grade and gpa and honours etc.
    
    user_profile = get_user_settings()
    system = user_profile["system"]
    
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        
        cur.execute('''
                    SELECT
                        module_code
                    FROM
                        modules
                    WHERE
                        trimester = ?
                    ''',
                    (trimester,)
                    )
        
        rows = cur.fetchall()

    if not rows:
        return {
            "overall_score" : 0.0,
            "classification" : "No Registered Modules Located.",
            "modules_tracked" : 0,
            "modules_graded" : 0
            }
    
    total_module_count = len(rows)
    modules_with_grades = 0
    accumulated_gpa_points = 0.0
    accumulated_raw_percentage = 0.0
    
    for row in rows:
        mod_code = row[0]
        scores = calculate_module_gpa(mod_code)
        
        if scores["Letter_Grade"] != "NG" and scores["Letter_Grade"] != "Pending":
            modules_with_grades += 1
            accumulated_gpa_points += float(scores["Module GPA"])
            accumulated_raw_percentage += float(scores["Module Average"])
    
    if modules_with_grades == 0:
        return {
            "overall_score" : 0.0,
            "classification": "Awaiting Grades",
            "modules_tracked" : total_module_count,
            "modules_graded" : 0
            }
    

    if "Percentage" in system:
        overall_score = accumulated_raw_percentage / modules_with_grades
        
        if overall_score >= 70.0: classification_badge = "First Class Honours (1st)"
        elif overall_score >= 60.0: classification_badge = "Second Class Honours, Grade 1 (1:1)"
        elif overall_score >= 50.0: classification_badge = "Second Class Honours, Grade 2 (2:2)"
        elif overall_score >= 40.0: classification_badge = "Pass Degree"
        else: classification_badge = "Fail"
    
    else:
        overall_score = accumulated_gpa_points / modules_with_grades
        
        if "UCD" in system:
            if overall_score >= 3.68: classification_badge = "First Class Honours (1st)"
            elif overall_score >= 3.08: classification_badge = "Second Class Honours, Grade 1 (2:1)"
            elif overall_score >= 2.48: classification_badge = "Second Class Honours, Grade 2 (2:2)"
            elif overall_score >= 2.00: classification_badge = "Pass Degree"
            else: classification_badge = "Fail"
        else:
            if overall_score >= 3.80: classification_badge = "Summa Cum Laude (Highest Honours)"
            elif overall_score >= 3.65: classification_badge = "Magna Cum Laude (High Honours)"
            elif overall_score >= 3.50: classification_badge = "Cum Laude (Honours)"
            elif overall_score >= 2.00: classification_badge = "Good Academic Standing"
            else: classification_badge ="Fail"
    
    

    return {
        "overall_score" : round(overall_score, 2),
        "classification" : classification_badge,
        "modules_tracked" : total_module_count,
        "modules_graded" : modules_with_grades
        }
