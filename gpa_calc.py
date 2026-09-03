import pandas as pd
from database import get_user_settings, get_current_user_id
from database import supabase
import streamlit as st

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
    
    user_profile = get_user_settings()
    if not user_profile:
        return {"Module Average": 0.0, "Letter_Grade": "Pending", "Module GPA": 0.0, "Weight Graded": 0.0}

    system = user_profile["grading_system"]
    current_uid = get_current_user_id()

    try:
        response = supabase.table("assessments").select(
            "assessment_percentage, received_grade, component_scale"
        ).eq("user_id", current_uid).eq("module_code", module_code).execute()
        
        assessments_data = response.data if response.data else []
    except Exception:
        assessments_data = []
        
    if not assessments_data:
        return {"Module Average": 0.0, "Letter_Grade": "NG", "Module GPA": 0.0, "Weight Graded": 0.0, "Evaluation Status" : "PENDING", "Performance Status" : "Assessments have yet to be registered."}
    

    df = pd.DataFrame(assessments_data)
    
    earned_assessment_percentage = 0.0
    total_assessment_percentage = 0.0
    module_gpa_points = 0.0
    

    for idx, row in df.iterrows():

        assessment_percentage = float(row["assessment_percentage"])
        received_grade = row["received_grade"]

        if "UCD" in system:
            component_scale = row["component_scale"]
        

        if pd.notna(received_grade) and received_grade != "":
            received_grade = float(received_grade)
            percentage_of_module = received_grade * (assessment_percentage / 100.0)
            earned_assessment_percentage += percentage_of_module
            total_assessment_percentage += assessment_percentage
        
          
            if "UCD" in system:
                _, assessment_gpa_points = convert_ucd_mark_to_grade(received_grade, scale_type = component_scale)
                module_gpa_points += assessment_gpa_points * assessment_percentage
            elif "US" in system:
                _, assessment_gpa_points = convert_us_mark_to_grade(received_grade)
                module_gpa_points += assessment_gpa_points * assessment_percentage
                  
    if total_assessment_percentage == 0:
        return {"Module Average": 0.0, "Letter_Grade": "Pending", "Module GPA": 0.0, "Weight Graded": 0.0, "Evaluation Status" : "PENDING", "Performance Status" : "Assessments have yet to be registered."}
    

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
        "Module Average": final_running_percentage,
        "Letter_Grade": final_letter,
        "Module GPA": round(final_module_gpa, 2),
        "Weight Graded": total_assessment_percentage,
        
        "Evaluation Status": "FINALISED GRADE" if total_assessment_percentage >= 100 else "PROVISIONAL GRADE",
        "Performance Status": "Module fully assessed." if total_assessment_percentage >= 100 else "SUBJECT TO IMPROVEMENT: Some assessments have yet to be graded."
    }


def calculate_semester_gpa(semester):
    user_profile = get_user_settings()
    if not user_profile:
        return {
            "overall_score": 0.0,
            "classification": "Uncalibrated Profile",
            "modules_tracked": 0,
            "modules_graded": 0
        }
        

    system = user_profile["grading_system"] 
    current_uid = get_current_user_id()

    try:
        response = supabase.table("modules").select("module_code").eq("user_id", current_uid).eq("semester", semester).execute()
        rows = response.data if response else []
    except Exception as e:
        st.write(f"{e}")
        rows = []
    if not rows:
        return {
            "overall_score": 0.0,
            "classification": "No Registered Modules Located.",
            "modules_tracked": 0,
            "modules_graded": 0
        }
    
    total_module_count = len(rows)
    modules_with_grades = 0
    accumulated_gpa_points = 0.0
    accumulated_raw_percentage = 0.0
    

    for row in rows:
        mod_code = row["module_code"]
        scores = calculate_module_gpa(mod_code)


        if scores["Letter_Grade"] != "NG" and scores["Letter_Grade"] != "Pending":
            modules_with_grades += 1
            accumulated_gpa_points += float(scores["Module GPA"])
            accumulated_raw_percentage += float(scores["Module Average"])
    
    if modules_with_grades == 0:
        return {
            "overall_score": 0.0,
            "classification": "Awaiting Grades",
            "modules_tracked": total_module_count,
            "modules_graded": 0
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
            else: classification_badge = "Fail"

    return {
        "overall_score": round(overall_score, 2),
        "classification": classification_badge,
        "modules_tracked": total_module_count,
        "modules_graded": modules_with_grades
    }

def calculate_target_score(semester):

    user_profile = get_user_settings()
    if not user_profile:
        return {
            "status": "uncalibrated",
            "required_mark": 0.0,
            "message": "system profile settings missing"
        }

    system = user_profile["grading_system"]
    target = float(user_profile["target_grade"])
    current_uid = get_current_user_id()

    try:

        response = supabase.table("modules").select("module_code").eq("user_id", current_uid).eq("semester", semester).execute()
        module_rows = response.data if response.data else []
    except Exception:
        module_rows = []

    if not module_rows:
        return {
            "status": "No Modules",
            "required_mark": 0.0,
            "message": "Please register modules first."
        }

    total_modules = len(module_rows)
    total_graded_percentage = 0.0
    total_secured_marks = 0.0

    valid_codes = [row["module_code"] for row in module_rows]

    try:
  
        ass_response = supabase.table("assessments").select("assessment_percentage, received_grade").eq("user_id", current_uid).in_("module_code", valid_codes).execute()
        assessments_data = ass_response.data if ass_response.data else []
    except Exception:
        assessments_data = []


    for a_row in assessments_data:
        weight = float(a_row["assessment_percentage"])
        grade = a_row["received_grade"]

        if grade is not None:
            total_graded_percentage += weight
            total_secured_marks += (weight / 100.0) * float(grade)

    total_semester_syllabus_capacity = total_modules * 100 
    remaining_upcoming_marks = total_semester_syllabus_capacity - total_graded_percentage

    '''
    if remaining_upcoming_marks <= 0:
        return {
            "status": "Concluded",
            "required_mark": 0.0,
            "message": "Syllabus tracking complete. All grades have been submitted."
        } '''


    if "Percentage" in system:
        total_marks_needed = total_semester_syllabus_capacity * (target / 100.0)
        marks_deficit = total_marks_needed - total_secured_marks
    else:
        if "UCD" in system:
            if target >= 4.2: target_pct_equiv = 90.0
            elif target >= 4.0: target_pct_equiv = 80.0
            elif target >= 3.8: target_pct_equiv = 70.0
            elif target >= 3.6: target_pct_equiv = 66.67
            elif target >= 3.4: target_pct_equiv = 63.33
            elif target >= 3.2: target_pct_equiv = 60.0
            elif target >= 3.0: target_pct_equiv = 56.67
            elif target >= 2.8: target_pct_equiv = 53.33
            elif target >= 2.6: target_pct_equiv = 50.0
            elif target >= 2.4: target_pct_equiv = 46.67
            elif target >= 2.2: target_pct_equiv = 43.33
            else: target_pct_equiv = 40.0
        else:
            if target >= 4.0: target_pct_equiv = 93.0
            elif target >= 3.7: target_pct_equiv = 90.0
            elif target >= 3.3: target_pct_equiv = 87.0
            elif target >= 3.0: target_pct_equiv = 83.0
            elif target >= 2.7: target_pct_equiv = 80.0
            elif target >= 2.3: target_pct_equiv = 77.0
            elif target >= 2.0: target_pct_equiv = 73.0
            else: target_pct_equiv = 65.0

        total_marks_needed = total_semester_syllabus_capacity * (target_pct_equiv / 100.0)
        marks_deficit = total_marks_needed - total_secured_marks

    if marks_deficit <= 0:
        return {
            "status": "Secured",
            "required_mark": 0.0,
            "message": "You have successfully secured enough absolute marks to achieve your target honours / GPA!"
        }


    required_avg = (marks_deficit / remaining_upcoming_marks) * 100.0


    if required_avg > 100.0:
        return {
            "status": "Impossible",
            "required_mark": required_avg,
            "message": f"**Mathematically Out of Scope**: You would need an average of {required_avg:.2f}% across your remaining assessments to achieve the target GPA / Honours."
        }
    elif required_avg < 40.0:
        return {
            "status": "Safe Scope",
            "required_mark": required_avg,
            "message": f"**Comfortable Buffer**: You need an average of {required_avg:.2f}% across your remaining assessments to achieve your target GPA / Honours. Stay consistent!"
        }
    else:
        return {
            "status": "On Track",
            "required_mark": required_avg,
            "message": f"**On Track**: You need an average of {required_avg:.2f}% across your remaining assessments to achieve your target GPA / Honours."
        }
