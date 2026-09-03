# StrateGPA
The application is live @
**[https://strategpa.streamlit.app/](https://strategpa.streamlit.app/)**
___

**StrateGPA** is a multi-user web app I have built for college students who find themselves overwhelmed by continuous assessments, losing track of deadlines, and having zero time management.

Traditional calendars are undoubtedly useful.
They show you *when* assessments might be due, but they don't show you the 30 hours of work hitting you that Monday.

StrateGPA turns a messy syllabus into a visual workload chart, handles all the GPA translation math, and calculates exactly what assessment scores you need in order to achieve your target grades for the semester.

___

## Why I Built This

I've been known for having zero time management skills, always working on assessments yet still always feeling like I was lacking in the amount of study I should be doing. I built this app so I could:
* **See stress before it hits:** If I can see in Week 2 that Week 7 has a 45% workload spike across three modules, I can start studying early and avoid pulling stressful all-nighters.
* **Get rid of study guilt:** The app calculates exactly what average score I need on upcoming assignments to maintain my target GPA. Once I hit that threshold, I won't feel very guilty taking rests and spending free time with friends.

___

## Stack

* **Frontend:** Python, Streamlit, and Streamlit-Shadcn-UI for the interactive card designs.
* **Database & Auth:** Supabase (PostgreSQL) handles the cloud database and secure user login accounts.
* **Calculations:** Pandas dataframes manage the grade aggregations and timeline sorting.
* **Charts:** Plotly / Altair for the weekly stress heatmaps.

___

## Engineering Hurdles I Handled

While building this, I ran into a few tricky software problems that I had to research and fix:

1. **Fixing the Cloud Lag:** When I first connected the app to Supabase, every single cursor click or text input caused the app to freeze and flash because Streamlit reruns the whole script over the internet. I solved this by implementing **`@st.cache_data`** to hold data in fast local RAM, and wrapped inputs in **`@st.fragment`** to isolate changes locally. The app went from lagging to feeling instantaneous.
2. **Data Cleanups (Cascades):** If a user deletes or renames a module code, any assessments tied to it used to get left behind as broken, orphaned rows. I wrote custom database handlers in Python to ensure that whenever a module changes, it automatically sweeps through the assessments table to keep the data perfectly clean.
3. **Multi-User Firewall Privacy:** Because I wanted my friends to use this too, I tied every single database row directly to the user's verified login email as a master key. This ensures our workspaces are completely separate - multiple users can use it at the same time and will never see each others' private grades or modules.
4. **Weird Grading Math:** Different universities use totally different scales (like UCD's 4.2 GPA scale vs the standard US 4.0 or raw percentages). I built a custom math engine that tracks the remaining runway marks of your syllabus, translates the curves, and prints out easy-to-read advisory milestones.

---

## Folder Layout

* `app.py` - The main entry point, login screen, and page navigation router.
* `database.py` - All the data-fetching, writing, caching, and cleanup functions.
* `gpa_calc.py` - The math engine that translates grades and target score predictions.
* `views/` - The frontend pages (Weekly Workload, Academic Performance, Grade Entry, Module and Assessments Registration, Help Guide, Feedback).
* `requirements.txt` - Tells the cloud server exactly which libraries to install.
* `.streamlit/config.toml` - My custom colour codes.
