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
