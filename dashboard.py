import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).with_name("students.db")

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "navy": "#172B4D",
    "blue": "#356AE6",
    "teal": "#11998E",
    "amber": "#E6A23C",
    "red": "#DC5B63",
    "muted": "#66758A",
}
SUBJECTS = {"Maths": "maths", "Python": "python", "SQL": "sql"}

# Explicit light styling prevents low-contrast labels in forms on dark OS/browser themes.
st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    .stApp { background: #F4F7FB; color: #172B4D; }
    [data-testid="stHeader"] { background: rgba(244,247,251,.92); }
    .block-container { max-width: 1450px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
        color: #172B4D;
    }
    h1 { font-weight: 750; letter-spacing: -0.035em; }
    h2, h3 { font-weight: 700; letter-spacing: -0.02em; }
    [data-testid="stCaptionContainer"] p { color: #66758A !important; }
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E4EAF2;
    }
    section[data-testid="stSidebar"] * { color: #172B4D; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E4EAF2;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 5px 18px rgba(23,43,77,.055);
    }
    [data-testid="stMetricLabel"] p { color: #66758A !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #172B4D !important; }
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #E1E8F0;
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 6px 22px rgba(23,43,77,.05);
    }
    /* Form labels and helper text: force dark readable text */
    div[data-testid="stForm"] label,
    div[data-testid="stForm"] label p,
    div[data-testid="stForm"] [data-testid="stWidgetLabel"],
    div[data-testid="stForm"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stForm"] [data-testid="stMarkdownContainer"] p {
        color: #243B5A !important;
        opacity: 1 !important;
        font-weight: 650 !important;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background: #F8FAFD !important;
        color: #172B4D !important;
        border-color: #CBD5E1 !important;
        border-radius: 10px !important;
    }
    input::placeholder { color: #8290A3 !important; opacity: 1 !important; }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #356AE6 !important;
        box-shadow: 0 0 0 1px #356AE6 !important;
    }
    div[data-testid="stForm"] button[kind="primary"],
    .stDownloadButton button,
    .stButton button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.7rem;
    }
    div[data-testid="stForm"] button[kind="primary"],
    .stButton button[kind="primary"] {
        background: #356AE6;
        border: 1px solid #356AE6;
        color: #FFFFFF !important;
    }
    .stDownloadButton button {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        color: #243B5A !important;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid #E4EAF2;
        border-radius: 14px;
        overflow: hidden;
    }
    hr { border-color: #E2E8F0; }
    .hero {
        background: linear-gradient(115deg, #172B4D 0%, #254B80 58%, #356AE6 100%);
        padding: 1.6rem 1.8rem;
        border-radius: 20px;
        margin-bottom: 1.4rem;
        box-shadow: 0 10px 28px rgba(23,43,77,.14);
    }
    .hero h1 { color: #FFFFFF !important; margin: 0; font-size: 2rem; }
    .hero p { color: #E5EDFA !important; margin: .45rem 0 0; }
    .section-note { color: #66758A; margin-top: -.45rem; margin-bottom: 1rem; }
    @media (max-width: 700px) {
        .block-container { padding: 1rem 1rem 2rem; }
        .hero { padding: 1.2rem; }
        .hero h1 { font-size: 1.55rem; }
        div[data-testid="stForm"] { padding: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_students():
    """Load the existing SQLite table without changing its schema."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM students ORDER BY id DESC", conn)


def calculate_result(maths, python, sql):
    """Keep the project's original grading thresholds and pass rule."""
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


def save_student(name, age, roll, maths, python, sql):
    total, percentage, grade, result = calculate_result(maths, python, sql)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO students
            (name, age, roll, maths, python, sql, total, percentage, grade, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, age, roll, maths, python, sql, total, percentage, grade, result),
        )


def filtered_students(data, key_prefix="dashboard"):
    a, b, c = st.columns([1.5, 1, 1])
    with a:
        query = st.text_input("Search by student name or roll number", key=f"{key_prefix}_search")
    with b:
        grades = sorted(data["grade"].dropna().unique().tolist()) if not data.empty else []
        selected_grades = st.multiselect("Filter by grade", grades, key=f"{key_prefix}_grades")
    with c:
        selected_results = st.multiselect(
            "Filter by result", ["Pass", "Fail"], key=f"{key_prefix}_results"
        )

    result = data.copy()
    if query:
        mask = result["name"].astype(str).str.contains(query, case=False, na=False, regex=False)
        mask |= result["roll"].astype(str).str.contains(query, case=False, na=False, regex=False)
        result = result[mask]
    if selected_grades:
        result = result[result["grade"].isin(selected_grades)]
    if selected_results:
        result = result[result["result"].isin(selected_results)]
    return result


def chart_style(ax):
    ax.set_facecolor("#FFFFFF")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#DCE4EF")
    ax.tick_params(colors=COLORS["muted"], labelsize=10)
    ax.grid(axis="y", color="#E9EEF5", linewidth=0.8)
    ax.set_axisbelow(True)


def page_heading(title, subtitle):
    st.title(title)
    st.markdown(f'<p class="section-note">{subtitle}</p>', unsafe_allow_html=True)


st.markdown(
    """
    <div class="hero">
      <h1>🎓 Student Performance Analytics</h1>
      <p>Understand academic outcomes, compare subject performance, and manage student records.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    df = get_students()
except (sqlite3.Error, pd.errors.DatabaseError) as exc:
    st.error(
        f"Could not read the student database at `{DB_PATH}`. "
        "Check that the project database exists and has its original `students` table."
    )
    st.exception(exc)
    st.stop()

st.sidebar.markdown("## 🎓 Student Analytics")
st.sidebar.caption("Academic performance workspace")
page = st.sidebar.radio(
    "MAIN MENU",
    ["Dashboard", "Student Records", "Add Student", "Update Marks", "Delete Student"],
)
st.sidebar.divider()
st.sidebar.caption("Built with Python · SQLite · Streamlit · Pandas")
st.sidebar.caption(f"Records in database: {len(df)}")


if page == "Dashboard":
    page_heading("Dashboard overview", "A snapshot of class performance and subject-level trends.")
    if df.empty:
        st.info("No student records yet. Open **Add Student** to create the first record.")
    else:
        view = filtered_students(df)
        if view.empty:
            st.info("No students match these filters. Try widening your selection.")
        else:
            count = len(view)
            avg = view["percentage"].mean()
            passed = int((view["result"] == "Pass").sum())
            failed = int((view["result"] == "Fail").sum())
            pass_rate = passed / count * 100 if count else 0

            st.markdown("#### Class at a glance")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total students", count)
            k2.metric("Class average", f"{avg:.1f}%")
            k3.metric("Pass rate", f"{pass_rate:.1f}%", f"{passed} passed")
            k4.metric("Need support", failed, "students failed")

            st.divider()
            left, right = st.columns(2, gap="large")
            with left:
                st.subheader("Grade distribution")
                grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
                counts = view["grade"].value_counts().reindex(grade_order, fill_value=0)
                fig, ax = plt.subplots(figsize=(7, 3.7))
                bars = ax.bar(
                    counts.index,
                    counts.values,
                    color=["#356AE6", "#5685EA", "#11998E", "#5AB9A8", "#E6A23C", "#ED8147", "#DC5B63"],
                    width=0.62,
                    zorder=3,
                )
                chart_style(ax)
                ax.set_ylabel("Number of students", color=COLORS["muted"])
                ax.set_ylim(0, max(1, int(counts.max()) + 1))
                ax.bar_label(bars, padding=3, color=COLORS["navy"], fontsize=9)
                fig.tight_layout()
                st.pyplot(fig, width="stretch")
                plt.close(fig)

            with right:
                st.subheader("Average marks by subject")
                subject_means = [view[col].mean() for col in SUBJECTS.values()]
                fig, ax = plt.subplots(figsize=(7, 3.7))
                bars = ax.bar(
                    list(SUBJECTS),
                    subject_means,
                    color=[COLORS["blue"], COLORS["teal"], COLORS["amber"]],
                    width=0.55,
                    zorder=3,
                )
                chart_style(ax)
                ax.set_ylabel("Average marks (out of 100)", color=COLORS["muted"])
                ax.set_ylim(0, 110)
                ax.bar_label(
                    bars,
                    labels=[f"{value:.1f}" for value in subject_means],
                    padding=4,
                    color=COLORS["navy"],
                    fontsize=9,
                )
                fig.tight_layout()
                st.pyplot(fig, width="stretch")
                plt.close(fig)

            st.divider()
            st.subheader("🏆 Top-performing student")
            topper = view.loc[view["percentage"].idxmax()]
            t1, t2, t3 = st.columns(3)
            t1.metric("Student name", topper["name"])
            t2.metric("Roll number", topper["roll"])
            t3.metric("Percentage", f"{topper['percentage']:.2f}%")

            st.subheader("Recent student records")
            recent = view[["name", "roll", "total", "percentage", "grade", "result"]].head(10)
            st.dataframe(recent, width="stretch", hide_index=True)


elif page == "Student Records":
    page_heading("Student records", "Search, filter, review, and export academic records.")
    if df.empty:
        st.info("No student records available. Add a student to get started.")
    else:
        filtered = filtered_students(df, "records")
        st.caption(f"Showing {len(filtered)} of {len(df)} students")
        st.download_button(
            "⬇️ Download filtered CSV",
            data=filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="student_records.csv",
            mime="text/csv",
            disabled=filtered.empty,
        )
        st.dataframe(filtered, width="stretch", hide_index=True)


elif page == "Add Student":
    page_heading("Add a student", "Enter the student's details and subject marks in the fields below.")
    st.info("Required: student name and roll number. Enter marks between 0 and 100 for each subject.")
    with st.form("add_student_form"):
        st.markdown("#### 1. Student information")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Student name *", placeholder="e.g. Rahul Sharma")
        age = c2.number_input("Age *", min_value=1, max_value=100, value=21, step=1)
        roll = c3.text_input("Roll number *", placeholder="e.g. IT2026001")

        st.divider()
        st.markdown("#### 2. Subject marks")
        m1, m2, m3 = st.columns(3)
        maths = m1.number_input("Maths marks (0–100)", min_value=0, max_value=100, value=0, step=1)
        python = m2.number_input("Python marks (0–100)", min_value=0, max_value=100, value=0, step=1)
        sql = m3.number_input("SQL marks (0–100)", min_value=0, max_value=100, value=0, step=1)
        submitted = st.form_submit_button("➕ Add student", type="primary", width="stretch")

    if submitted:
        if not name.strip() or not roll.strip():
            st.error("Please enter both student name and roll number.")
        else:
            try:
                save_student(name.strip(), age, roll.strip(), maths, python, sql)
                st.success("Student added successfully.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("This roll number already exists. Please use a unique roll number.")
            except sqlite3.Error as exc:
                st.error(f"Could not save the student: {exc}")


elif page == "Update Marks":
    page_heading("Update student marks", "Select a student, review their current marks, and save the updated scores.")
    if df.empty:
        st.info("No student records available.")
    else:
        options = df["roll"].tolist()
        roll = st.selectbox(
            "Select student",
            options,
            format_func=lambda value: f"{value} · {df.loc[df['roll'] == value, 'name'].iloc[0]}",
        )
        student = df[df["roll"] == roll].iloc[0]
        st.info(f"Editing marks for **{student['name']}** · Roll number: **{roll}**")
        with st.form("update_form"):
            st.markdown("#### Updated subject marks")
            a, b, c = st.columns(3)
            maths = a.number_input("Maths marks (0–100)", min_value=0, max_value=100, value=int(student["maths"]))
            python = b.number_input("Python marks (0–100)", min_value=0, max_value=100, value=int(student["python"]))
            sql = c.number_input("SQL marks (0–100)", min_value=0, max_value=100, value=int(student["sql"]))
            submitted = st.form_submit_button("💾 Save changes", type="primary", width="stretch")
        if submitted:
            total, percentage, grade, result = calculate_result(maths, python, sql)
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        """UPDATE students SET maths=?, python=?, sql=?, total=?,
                        percentage=?, grade=?, result=? WHERE roll=?""",
                        (maths, python, sql, total, percentage, grade, result, roll),
                    )
                st.success("Student marks updated successfully.")
                st.rerun()
            except sqlite3.Error as exc:
                st.error(f"Could not update marks: {exc}")


elif page == "Delete Student":
    page_heading("Delete a student", "Remove a student record only after checking the selected details.")
    if df.empty:
        st.info("No student records available.")
    else:
        roll = st.selectbox(
            "Select student to delete",
            df["roll"].tolist(),
            format_func=lambda value: f"{value} · {df.loc[df['roll'] == value, 'name'].iloc[0]}",
        )
        student = df[df["roll"] == roll].iloc[0]
        st.warning(
            f"Selected record: **{student['name']}** · Roll **{roll}** · "
            f"Percentage **{student['percentage']:.2f}%**"
        )
        confirm = st.checkbox("I understand this permanently removes this student record.")
        if st.button("🗑️ Delete student", type="primary", disabled=not confirm):
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("DELETE FROM students WHERE roll=?", (roll,))
                st.success("Student deleted successfully.")
                st.rerun()
            except sqlite3.Error as exc:
                st.error(f"Could not delete student: {exc}")


st.divider()
st.caption("Student Performance Analysis · Python · SQLite · Streamlit · Pandas · Matplotlib")
