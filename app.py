import streamlit as st

# MODULE DETAILS
MODULES = [
    {"Code" : "COMP20360",
     "Title" : "Formal Foundations 2",
     "Trimester" : "Autumn",
     "Assessments" : [
         {"Description" : "Written exam",
          "Weeks" : [14, 15], # end of trimester exam, unconfirmed whether week 14 or 15
          "Must Pass Component" : 0,
          "Grade Percentage" : 50},

         {"Description" : "In class written exam",
          "Weeks" : [4, 8],
          "Must Pass Component" : 0,
          "Grade Percentage" : 50}
        ]
    },
                               
    {"Code" : "COMP20280",
     "Title" : "Data Structures",
     "Trimester" : "Spring",
     "Assessments" : [
         {"Description" : "Solution of data structure problems",
          "Weeks" : [11],
          "Must Pass Component" : 0,
          "Grade Percentage" : 40},

         {"Description" : "Exam",
          "Weeks" : [16, 17], # unconfirmed
          "Must Pass Component" : 0,
          "Grade Percentage" : 60}
        ]
    },

    {"Code" : "COMP20020",
     "Title" : "Digital Systems",
     "Trimester" : "Autumn",
     "Assessments" : [
         {"Description" : "Discovering digital electronics and logic gates",
          "Weeks" : [3],
          "Must Pass Component" : 0,
          "Grade Percentage" : 8},

         {"Description" : "Combinational circuits",
          "Weeks" : [6],
          "Must Pass Component" : 0,
          "Grade Percentage" : 8},

         {"Description" : "Sequential and arithmetic circuits",
          "Weeks" : [9],
          "Must Pass Component" : 0,
          "Grade Percentage" : 8},

         {"Description" : "Digital computer",
          "Weeks" : [12],
          "Must Pass Component" : 0,
          "Grade Percentage" : 8},

         {"Description" : "Written exam",
          "Weeks" : [14, 15], # unconfirmed
          "Must Pass Component" : 0,
          "Grade Percentage" : 68}
        ]
    },

    {"Code" : "COMP20350",
     "Title" : "Object Oriented Programming",
     "Trimester" : "Autumn",
     "Assessments" : [
         {"Description" : "Programming assignments",
          "Weeks" : [9, 12],
          "Must Pass Component" : 0,
          "Grade Percentage" : 30},

         {"Description" : "MCQ",
          "Weeks" : [14, 15],
          "Must Pass Component" : 0,
          "Grade Percentage" : 40},

         {"Description" : "Timed Programming Assessments and weekly lab work",
          "Weeks" : [4, 8, 11],
          "Must Pass Component" : 0,
          "Grade Percentage" : 30}
        ]
    },

    {"Code" : "COMP20320",
     "Title" : "Computer Networking",
     "Trimester" : "Autumn",
     "Assessments" : [
         {"Description" : "Exam",
          "Weeks" : [14, 15],
          "Must Pass Component" : 0,
          "Grade Percentage" : 45},

         {"Description" : "In class tests",
          "Weeks" : [4, 7, 10],
          "Must Pass Component" : 0,
          "Grade Percentage" : 55}
        ]
    },

    {"Code" : "COMP20050",
     "Title" : "Software Engineering Project 2",
     "Trimester" : "Spring",
     "Assessments" : [
         {"Description" : "GROUP WORK: SWE Challenge, 4 sprint assignments, final project release",
          "Weeks" : [5, 7, 9, 11, 12],
          "Must Pass Component" : 0,
          "Grade Percentage" : 85},

         {"Description" : "GROUP WORK: High Level Architectural Design",
          "Weeks" : [3],
          "Must Pass Component" : 0,
          "Grade Percentage" : 15}
        ]
    },

    {"Code" : "COMP20180",
     "Title" : "Intro to Operating Systems",
     "Trimester" : "Spring",
     "Assessments" : [
         {"Description" : "Bare metal computer programming",
          "Weeks" : [3],
          "Must Pass Component" : 0,
          "Grade Percentage" : 9},

         {"Description" : "System calls, interrupts, multitasking",
          "Weeks" : [6],
          "Must Pass Component" : 0,
          "Grade Percentage" : 9},

         {"Description" : "Unix syscall API and shell command syntax",
          "Weeks" : [9],
          "Must Pass Component" : 0,
          "Grade Percentage" : 9},

         {"Description" : "Virtual address spaces, interprocess communication and synchronisation, related topics",
          "Weeks" : [12],
          "Must Pass Component" : 0,
          "Grade Percentage" : 9},

         {"Description" : "Written exam",
          "Weeks" : [16, 17],
          "Must Pass Component" : 0,
          "Grade Percentage" : 60},

         {"Description" : "MCQ",
          "Weeks" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
          "Must Pass Component" : 0,
          "Grade Percentage" : 4}
        ]
    },

    {"Code" : "COMP20290",
     "Title" : "Algorithms",
     "Trimester" : "Spring",
     "Assessments" : [
         {"Description" : "GROUP WORK: Research paper and Implementation of Proposed Methods",
          "Weeks" : [11],
          "Must Pass Component" : 0,
          "Grade Percentage" : 30},

         {"Description" : "Written exam",
          "Weeks" : [16, 17],
          "Must Pass Component" : 0,
          "Grade Percentage" : 70}
        ]
    },

    {"Code" : "MST20050",
     "Title" : "Linear Algebra II",
     "Trimester" : "Spring",
     "Assessments" : [
         {"Description" : "Exam",
          "Weeks" : [16, 17],
          "Must Pass Component" : 0,
          "Grade Percentage" : 80},

         {"Description" : "Online tests",
          "Weeks" : [6, 9],
          "Must Pass Component" : 0,
          "Grade Percentage" : 20}
        ]
    },
           

    {"Code" : "COMP20070",
     "Title" : "Databases and Information Systems I",
     "Trimester" : "Autumn",
     "Assessments" : [
         {"Description" : "In class exam",
          "Weeks" : [6, 7, 8],
          "Must Pass Component" : 0,
          "Grade Percentage" : 20},

         {"Description" : "In class exam",
          "Weeks" : [11, 12, 14],
          "Must Pass Component" : 0,
          "Grade Percentage" : 40},

         {"Description" : "Individual Assignment",
          "Weeks" : [9, 10, 11, 12],
          "Must Pass Component" : 0,
          "Grade Percentage" : 40}
        ]
    }
]

# list of just module codes
MODULE_CODES = []
for module in MODULES:
    for key, value in module.items():
        if key == "Code":
            MODULE_CODES.append(value)




# TITLE
st.title("StrateGPA")



# selectbox for choosing module
code_chosen = st.selectbox("MODULE CODE", MODULE_CODES)

# printing relevant module details
for module in MODULES:
    if module["Code"] == code_chosen:
        st.write(module["Title"])
        for assessment in module["Assessments"]:
            st.write(assessment["Description"])
            st.write(f"Weeks: {assessment["Weeks"]}")
            st.write(f"Worth {assessment["Grade Percentage"]}% of grade")