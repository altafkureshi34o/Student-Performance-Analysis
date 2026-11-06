import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import sqlite3
from pathlib import Path


import sqlite3
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = Path(__file__).with_name("students.db")

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide"
)


# Database connection and data loading
def get_students():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        "SELECT * FROM students ORDER BY id DESC",
        conn
    )

    conn.close()
    return df


def calculate_result(maths, python, sql):
    total = maths + python + sql
    percentage = total / 3

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    elif percentage >= 40:
        grade = "E"
    else:
        grade = "F"

    result = "Pass" if min(maths, python, sql) >= 33 else "Fail"

    return total, round(percentage, 2), grade, result


# Dashboard heading
st.title("🎓 Student Performance Dashboard")
st.caption("Student Management and Academic Analytics System")

df = get_students()

# Sidebar
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    ["Dashboard", "Student Records", "Add Student", "Update Marks", "Delete Student"]
)

st.sidebar.info("Powered by Python, SQLite and Streamlit")


# DASHBOARD PAGE
if page == "Dashboard":

    st.header("Academic Overview")

    if df.empty:
        st.warning("No student records available. Add students first.")

    else:
        total_students = len(df)
        average = df["percentage"].mean()
        passed = (df["result"] == "Pass").sum()
        failed = (df["result"] == "Fail").sum()

        topper = df.loc[df["percentage"].idxmax()]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Students", total_students)
        col2.metric("Class Average", f"{average:.2f}%")
        col3.metric("Passed Students", int(passed))
        col4.metric("Failed Students", int(failed))

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("Pass vs Fail")

            fig, ax = plt.subplots()
            ax.pie(
                [passed, failed],
                labels=["Pass", "Fail"],
                autopct="%1.1f%%",
                startangle=90
            )
            ax.axis("equal")
            st.pyplot(fig)
            plt.close(fig)

        with right:
            st.subheader("Subject-wise Average")

            subjects = ["Maths", "Python", "SQL"]
            averages = [
                df["maths"].mean(),
                df["python"].mean(),
                df["sql"].mean()
            ]

            fig, ax = plt.subplots()
            ax.bar(subjects, averages)
            ax.set_ylabel("Average Marks")
            ax.set_ylim(0, 100)
            st.pyplot(fig)
            plt.close(fig)

        st.divider()

        st.subheader("🏆 Class Topper")

        c1, c2, c3 = st.columns(3)
        c1.metric("Name", topper["name"])
        c2.metric("Roll Number", topper["roll"])
        c3.metric("Percentage", f"{topper['percentage']:.2f}%")

        st.subheader("Recent Student Records")
        st.dataframe(
            df[["name", "roll", "total", "percentage", "grade", "result"]].head(10),
            use_container_width=True,
            hide_index=True
        )


# STUDENT RECORDS PAGE
elif page == "Student Records":

    st.header("📋 All Student Records")

    search = st.text_input("Search by name or roll number")

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["name"].astype(str).str.contains(
                search, case=False, na=False
            )
            |
            filtered["roll"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    st.write(f"Records found: {len(filtered)}")

    st.dataframe(filtered, use_container_width=True, hide_index=True)


# ADD STUDENT PAGE
elif page == "Add Student":

    st.header("➕ Add New Student")

    with st.form("add_student_form"):

        name = st.text_input("Student Name")
        age = st.number_input("Age", min_value=1, max_value=100, value=21)
        roll = st.text_input("Roll Number")

        maths = st.number_input("Maths Marks", 0, 100, 0)
        python = st.number_input("Python Marks", 0, 100, 0)
        sql = st.number_input("SQL Marks", 0, 100, 0)

        submitted = st.form_submit_button("Add Student")

        if submitted:

            if not name.strip() or not roll.strip():
                st.error("Please enter student name and roll number.")

            else:
                total, percentage, grade, result = calculate_result(
                    maths, python, sql
                )

                try:
                    conn = sqlite3.connect(DB_PATH)

                    conn.execute("""
                        INSERT INTO students
                        (name, age, roll, maths, python, sql,
                         total, percentage, grade, result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name.strip(), age, roll.strip(),
                        maths, python, sql,
                        total, percentage, grade, result
                    ))

                    conn.commit()
                    conn.close()

                    st.success("Student added successfully!")
                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error("This roll number already exists!")


# UPDATE MARKS PAGE
elif page == "Update Marks":

    st.header("✏️ Update Student Marks")

    if df.empty:
        st.warning("No student records available.")

    else:
        roll = st.selectbox("Select Roll Number", df["roll"].tolist())

        student = df[df["roll"] == roll].iloc[0]

        with st.form("update_form"):

            maths = st.number_input(
                "Maths Marks", 0, 100, int(student["maths"])
            )
            python = st.number_input(
                "Python Marks", 0, 100, int(student["python"])
            )
            sql = st.number_input(
                "SQL Marks", 0, 100, int(student["sql"])
            )

            submitted = st.form_submit_button("Update Student")

            if submitted:

                total, percentage, grade, result = calculate_result(
                    maths, python, sql
                )

                conn = sqlite3.connect(DB_PATH)

                conn.execute("""
                    UPDATE students
                    SET maths=?, python=?, sql=?,
                        total=?, percentage=?, grade=?, result=?
                    WHERE roll=?
                """, (
                    maths, python, sql, total,
                    percentage, grade, result, roll
                ))

                conn.commit()
                conn.close()

                st.success("Student updated successfully!")
                st.rerun()


# DELETE STUDENT PAGE
elif page == "Delete Student":

    st.header("🗑️ Delete Student")

    if df.empty:
        st.warning("No student records available.")

    else:
        roll = st.selectbox("Select Student Roll Number", df["roll"].tolist())

        student = df[df["roll"] == roll].iloc[0]

        st.write("Student Name:", student["name"])

        confirm = st.checkbox("I confirm that I want to delete this student.")

        if st.button("Delete Student", type="primary"):

            if confirm:
                conn = sqlite3.connect(DB_PATH)

                conn.execute(
                    "DELETE FROM students WHERE roll=?",
                    (roll,)
                )

                conn.commit()
                conn.close()

                st.success("Student deleted successfully!")
                st.rerun()

            else:
                st.error("Please confirm before deleting.")


st.divider()
st.caption("Student Performance Analysis System | Python + SQLite + Pandas + Streamlit")
