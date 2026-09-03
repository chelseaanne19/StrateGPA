import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# CLOUD INITIALISATION
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"].strip()
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"].strip()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_current_user_id():
    """
    Extracts authenticated user email session token
    """
    return st.session_state.get("user_id", "default_guest_profile")

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# USER CONFIGURATIONS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@st.cache_data
def get_user_settings():
    """
    Fetches user settings from the Supabase cloud table
    """

    current_uid = get_current_user_id()
    if not current_uid:
        return None
    try:
        response = supabase.table("settings").select("*").eq("user_id", current_uid).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None

def save_user_settings(institution, system, target, teaching_weeks_autumn, teaching_weeks_spring):
    """
    Saves user profile records to Supabase database
    """
    current_uid = get_current_user_id()
    payload = {
        "user_id" : current_uid,
        "institution" : institution,
        "grading_system" : system,
        "target_grade" : float(target),
        "weeks_autumn" : int(teaching_weeks_autumn),
        "weeks_spring" : int(teaching_weeks_spring)
    }

    try:
        response = supabase.table("settings").upsert(payload, on_conflict = "user_id").execute()
        if not response.data:
            raise RuntimeError("Supabase did not return the saved settings.")
        st.cache_data.clear()
        return 1
    except Exception as e:
        raise RuntimeError(f"{e}") from e

def clear_user_settings():
    """
    Clears user settings to allow re-configuration
    """
    current_uid = get_current_user_id()

    supabase.table("settings").delete().eq("user_id", current_uid).execute()
    st.cache_data.clear()
    return True



# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# DATAFRAMES
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@st.cache_data
def get_modules_dataframe():
    """
    Gets all registered modules to return as a DataFrame
    """

    current_uid = get_current_user_id()
    try:
        response = supabase.table("modules").select("*").eq("user_id", current_uid).execute()

        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns = {
                "module_code" : "Module Code",
                "module_title" : "Module Title",
                "semester" : "Semester"
            },
            inplace = True)
            return df[["Module Code", "Module Title", "Semester"]]
        return pd.DataFrame(columns = ["Module Code", "Module Title", "Semester"])
    except Exception:
        return pd.DataFrame(columns = ["Module Code", "Module Title", "Semester"])

def get_assessments_dataframe():
    """
    Gets all registered assessments to return as a DataFrame
    """
    current_uid = get_current_user_id()
    try:
        response = supabase.table("assessments").select("*").eq("user_id", current_uid).execute()

        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns = {
                "id" : "Assessment ID",
                "module_code" : "Module Code",
                "assessment_title" : "Assessment Title",
                "assessment_percentage" : "Weight %",
                "week" : "Week Due",
                "component_scale" :"Component Scale"
            },
            inplace = True)

            if "must_pass_component" in df.columns:
                df["Must Pass"] = df["must_pass_component"].map({1: "Yes", 0: "No"}).fillna("No")
            else:
                df["Must Pass"] = "No"

            if "received_grade" in df.columns:
                df["Result"] = df["received_grade"].apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "Pending")
            else:
                df["Result"] = "Pending"

            user_profile = get_user_settings()
            if "UCD" in user_profile["grading_system"]:
                return df[["Assessment ID", "Assessment Title", "Module Code", "Weight %", "Week Due", "Component Scale", "Must Pass", "Result"]]
            else:
                return df[["Assessment ID", "Assessment Title", "Module Code", "Weight %", "Week Due", "Must Pass", "Result"]]

    except Exception:
            return pd.DataFrame(columns = ["Assessment ID", "Assessment Title", "Module Code", "Weight %", "Must Pass", "Week Due", "Result", "Component Scale"])

@st.cache_data
def get_assessments_from(module_code):
    """
    Gets all registered assessments from a certain module and returns as a DataFrame
    """

    current_uid = get_current_user_id()

    try:
        response = supabase.table("assessments").select("*").eq("user_id", current_uid).eq("module_code", module_code).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns = {
                "id" : "Assessment ID",
                "assessment_title" : "Assessment Title",
                "module_code" : "Module Code",
                "assessment_percentage" : "Weight %",
                "week" : "Week Due",
                "component_scale" : "Component Scale"
            },
            inplace = True)

            if "must_pass_component" in df.columns:
                df["Must Pass"] = df["must_pass_component"].map({1: "Yes", 0: "No"}).fillna("No")
            else:
                df["Must Pass"] = "No"

            if "received_grade" in df.columns:
                df["Result"] = df["received_grade"].apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "Pending")
            else:
                df["Result"] = "Pending"

            df["Semester"] = "Active"

            return df[["Assessment ID", "Assessment Title", "Module Code", "Weight %", "Semester", "Must Pass", "Week Due", "Result", "Component Scale"]]
            
        return pd.DataFrame(columns=["Assessment ID", "Assessment Title", "Module Code", "Weight %", "Semester", "Must Pass", "Week Due", "Result", "Component Scale"])
    except Exception:
        return pd.DataFrame(columns=["Assessment ID", "Assessment Title", "Module Code", "Weight %", "Semester", "Must Pass", "Week Due", "Result", "Component Scale"])


# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# INSERTS
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def insert_module(code_input, title_input, semester):
    """
    Inserts module linked securely to the user session
    """

    current_uid = get_current_user_id()
    payload = {
        "user_id" : current_uid,
        "module_code" : code_input.strip().upper(),
        "module_title" : title_input.strip(),
        "semester" : semester
    }
    try:
        supabase.table("modules").insert(payload).execute()
        st.cache_data.clear()
        return True
    except Exception:
        return False

def insert_assessment(module_code, title, percentage, must_pass, weeks_list, is_final_exam=False, component_scale = None):
    """
    Inserts dedicated row entries for each targeted week period.
    Handles exact remainder allocations cleanly for continuous assessment splits.
    """
    current_uid = get_current_user_id()
    num_weeks = len(weeks_list)
    
    # Defensive Gate: Terminate execution gracefully if no weeks are checked
    if num_weeks == 0:
        return False
        
    # Force absolute data typing conversions up front to prevent text errors
    try:
        raw_pct = int(float(percentage))
        base_weight = raw_pct // num_weeks
        remainder = raw_pct % num_weeks
    except (ValueError, TypeError) as e:
        print(f"❌ Type Conversion Failure inside insert_assessment arguments: {e}")
        return False
        
    payload_batch = []
    
    for index, week_num in enumerate(weeks_list):
        # Keeps your sleek single-sentence title components fully aligned
        display_title = f"{title} (Wk {week_num})" if num_weeks > 1 and not is_final_exam else title
        
        # Apply your verified custom remainder balancing rules cleanly
        if is_final_exam:
            row_weight = raw_pct
        else:
            row_weight = base_weight + remainder if index == num_weeks - 1 else base_weight

        # 💡 CRUCIAL PRODUCTION SAFEGUARD: Clean up your dictionary keys and data types
        # Every single item here perfectly mirrors your Supabase SQL schema definitions!
        payload_batch.append({
            "user_id": str(current_uid),
            "module_code": str(module_code).strip().upper(),
            "assessment_title": str(display_title).strip(),
            "assessment_percentage": int(row_weight),
            "must_pass_component": int(must_pass),
            "week": int(week_num),
            "component_scale": str(component_scale).strip(),
            "received_grade": None  # Default to explicit database Null for ungraded inputs
        })
        
    try:
        # Fire the bulk list payload down to your cloud table
        response = supabase.table("assessments").insert(payload_batch).execute()
        
        # If Supabase successfully returns written data rows, return True!
        if response.data:
            st.cache_data.clear()
            return True
        return False
    except Exception as server_error:
        # 💡 THE TELEMETRY HOOK: This prints the exact database issue straight to your local terminal!
        print("--- 🐛 SUPABASE DEPLOYMENT INSERTION ERROR DIAGNOSTIC ---")
        print(f"Error Message: {server_error}")
        print(f"Attempted Payload: {payload_batch}")
        print("---------------------------------------------------------")
        return False

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# UPDATES
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def update_module(old_code, new_code, new_title, new_semester):
    """
    Updates a module row's parameters inside cloud table.
    """

    current_uid = get_current_user_id()
    clean_old = old_code.strip().upper()
    clean_new = new_code.strip().upper()
    clean_title = new_title.strip()

    try:
        supabase.table("assessments").update({"module_code" : clean_new}).eq("user_id", current_uid).eq("module_code", clean_old).execute()
        payload = {
        "module_code" : clean_new,
        "module_title" : clean_title,
        "semester" : new_semester
    }
        supabase.table("modules").update(payload).eq("user_id", current_uid).eq("module_code", clean_old).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.write(f"{e}")
        return False

def update_assessment(assessment_id, new_module_code, new_title, new_percentage, new_must_pass, new_week, component_scale = None):
    """
    Updates assessment row in cloud table.
    """
    payload = {
        "assessment_title" : new_title,
        "assessment_percentage" : int(new_percentage),
        "must_pass_component" : int(new_must_pass),
        "week" : int(new_week),
        "component_scale" : component_scale
    }
    supabase.table("assessments").update(payload).eq("id", assessment_id).execute()
    st.cache_data.clear()
    return True

def update_assessment_grade(assessment_id, grade):
    """
    Inserts the achieved grade percentage to a specific assessment
    """

    try:
        grade_payload = float(grade) if grade is not None else None
        supabase.table("assessments").update({"received_grade" : grade_payload}).eq("id", assessment_id).execute()
        st.cache_data.clear()
        return True
    except Exception:
        return False

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# DELETES
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def delete_module(code_selected):
    """
    Deletes module from cloud table.
    """
    current_uid = get_current_user_id()

    try:
        supabase.table("assessments").delete().eq("user_id", current_uid).eq("module_code", code_selected).execute()
        supabase.table("modules").delete().eq("user_id", current_uid).eq("module_code", code_selected).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.write(f"{e}")
        return False

def delete_assessment(assessment_id):
    """
    Deletes assessment from cloud table.
    """
    supabase.table("assessments").delete().eq("id", assessment_id).execute()
    st.cache_data.clear()
    return True



# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# FUNCTIONS FOR WEEKLY WORKLOAD PAGE [RETURNS DFS / DICTIONARIES]
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@st.cache_data
def get_weekly_workload(semester, module_code = None):
    """
    Aggregates workload percentages categorised by academic week numbers.
    """

    current_uid = get_current_user_id()
    try:
        mod_response = supabase.table("modules").select("module_code").eq("user_id", current_uid).eq("semester", semester).execute()
        valid_codes = [row["module_code"] for row in mod_response.data] if mod_response.data else []

        if not valid_codes:
            return pd.DataFrame(columns = ["Week", "Total Workload (%)", "Module"])

        query = supabase.table("assessments").select("week, assessment_percentage, module_code").eq("user_id", current_uid).in_("module_code", valid_codes)


        if module_code:
            query = query.eq("module_code", module_code)
        ass_response = query.execute()

        if not ass_response.data:
            return pd.DataFrame(columns = ["Week", "Total Workload (%)", "Module Code"])

        df = pd.DataFrame(ass_response.data)
        df_grouped = df.groupby(["week", "module_code"])["assessment_percentage"].sum().reset_index()
        df_grouped.columns = ["Week", "Module", "Total Workload (%)"]
        
        df_final = df_grouped[["Week", "Total Workload (%)", "Module"]]
        
        return df_final.sort_values("Week")

    except Exception:
        return pd.DataFrame(columns = ["Week", "Total Workload (%)", "Module"])

@st.cache_data
def get_week_contributors(semester, target_week):
    """
    Lists unique module codes that have assessments due in target week.
    """
    current_uid = get_current_user_id()

    try:
        mod_response = supabase.table("modules").select("module_code").eq("user_id", current_uid).eq("semester", semester).execute()
        valid_codes = [r["module_code"] for r in (mod_response.data or []) if r.get("module_code")]

        if not valid_codes:
            return pd.DataFrame(columns = ["module_code"])

        response = supabase.table("assessments").select("module_code", "assessment_percentage").eq("user_id", current_uid).eq("week", int(target_week)).in_("module_code", valid_codes).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df_grouped = df.groupby("module_code")["assessment_percentage"].sum().reset_index()
            df_grouped.columns = ["Module Code", "Weight %"]

            return df_grouped.sort_values(by = "Weight %")
        return pd.DataFrame(columns = ["Module Code", "Weight %"])
    except Exception as e:
        st.error(f"Error {e}")
        return pd.DataFrame(columns = ["Module Code", "Weight"])

@st.cache_data
def get_grade_progress(semester, module_code = None):
    """
    Computers total graded scores user has achieved vs upcoming marks.
    """

    current_uid = get_current_user_id()
    try:

        mod_response = supabase.table("modules").select("module_code").eq("user_id", current_uid).eq("semester", semester).execute()
        valid_codes = [row["module_code"] for row in mod_response.data] if mod_response.data else []
        
        if not valid_codes:
            return {"total_weight": 0.0, "completed_weight": 0.0, "earned_points": 0.0, "upcoming_weight": 0.0}
            

        query = supabase.table("assessments").select("module_code, assessment_percentage, received_grade").eq("user_id", current_uid).in_("module_code", valid_codes)
        
        if module_code is not None:
            query = query.eq("module_code", module_code)
            
        response = query.execute()
        
        if not response.data:
            return {"total_weight": 0.0, "completed_weight": 0.0, "earned_points": 0.0, "upcoming_weight": 0.0}
            

        df = pd.DataFrame(response.data)
        

        df["assessment_percentage"] = df["assessment_percentage"].astype(float)
        df["received_grade"] = pd.to_numeric(df["received_grade"], errors='coerce')
        

        total_weight = df["assessment_percentage"].sum()
        

        completed_df = df[df["received_grade"].notna()]
        completed_weight = completed_df["assessment_percentage"].sum()


        earned_points = (completed_df["assessment_percentage"] * (completed_df["received_grade"] / 100.0)).sum()
        
        upcoming_weight = total_weight - completed_weight
        
        return {
            "total_weight": total_weight,
            "completed_weight": completed_weight,
            "earned_points": earned_points,
            "upcoming_weight": upcoming_weight
        }
    except Exception:
        return {"total_weight": 0.0, "completed_weight": 0.0, "earned_points": 0.0, "upcoming_weight": 0.0}

@st.cache_data
def get_week_agenda(semester, target_week):
    """
    Queries all registered assessments due in a specific week for the active semester.
    """
    current_uid = get_current_user_id()
    try:

        mod_response = supabase.table("modules").select("module_code").eq("user_id", current_uid).eq("semester", semester).execute()
        valid_codes = [row["module_code"] for row in mod_response.data] if mod_response.data else []
        
        if not valid_codes:
            return pd.DataFrame(columns=["Assessment ID", "Module Code", "Assessment Title", "Weight %", "Must Pass", "Received Grade"])
            

        response = supabase.table("assessments").select("id, module_code, assessment_title, assessment_percentage, must_pass_component, received_grade").eq("user_id", current_uid).eq("week", int(target_week)).in_("module_code", valid_codes).order("module_code").execute()
        
        if not response.data:
            return pd.DataFrame(columns=["Assessment ID", "Module Code", "Assessment Title", "Weight %", "Must Pass", "Received Grade"])
            

        df = pd.DataFrame(response.data)
        
        df.rename(columns = {
            "id": "Assessment ID",
            "module_code": "Module Code",
            "assessment_title": "Assessment Title",
            "assessment_percentage": "Weight %"
        }, inplace = True)
        

        df["Must Pass"] = df["must_pass_component"].fillna(0).astype(int)
        df["Received Grade"] = df["received_grade"].apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "Pending")
        

        return df[["Assessment ID", "Module Code", "Assessment Title", "Weight %", "Must Pass", "Received Grade"]]
        
    except Exception:
        return pd.DataFrame(columns=["Assessment ID", "Module Code", "Assessment Title", "Weight %", "Must Pass", "Received Grade"])
