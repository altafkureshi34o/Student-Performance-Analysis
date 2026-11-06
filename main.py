
import sqlite3

DB_NAME = "students.db"


# Connect to database
def connect_db():
    return sqlite3.connect(DB_NAME)


# Create database table if it does not exist
def create_table():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                roll TEXT UNIQUE NOT NULL,
                maths INTEGER NOT NULL,
                python INTEGER NOT NULL,
                sql INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL NOT NULL,
                grade TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """)


# Calculate student result
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


# Add student
def add_student():
    print("\n===== ADD STUDENT =====")

    name = input("Enter name: ").strip()
    roll = input("Enter roll number: ").strip()

    try:
        age = int(input("Enter age: "))
        maths = int(input("Enter Maths marks: "))
        python = int(input("Enter Python marks: "))
        sql = int(input("Enter SQL marks: "))

        if not name or not roll or age <= 0:
            print("Invalid student details!")
            return

        if any(mark < 0 or mark > 100
               for mark in [maths, python, sql]):
            print("Marks must be between 0 and 100!")
            return

    except ValueError:
        print("Please enter valid numbers!")
        return

    total, percentage, grade, result = calculate_result(
        maths, python, sql
    )

    try:
        with connect_db() as conn:
            conn.execute("""
                INSERT INTO students
                (name, age, roll, maths, python, sql,
                 total, percentage, grade, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, age, roll, maths, python, sql,
                total, percentage, grade, result
            ))

        print("\nStudent added successfully!")
        print("Total:", total, "/300")
        print("Percentage:", percentage, "%")
        print("Grade:", grade)
        print("Result:", result)

    except sqlite3.IntegrityError:
        print("This roll number already exists!")


# Display all students
def display_students():
    print("\n===== ALL STUDENTS =====")

    with connect_db() as conn:
        students = conn.execute("""
            SELECT name, age, roll, total,
                   percentage, grade, result
            FROM students
            ORDER BY id
        """).fetchall()

    if not students:
        print("No student records found.")
        return

    for s in students:
        print("-" * 40)
        print("Name:", s[0])
        print("Age:", s[1])
        print("Roll:", s[2])
        print("Total:", s[3], "/300")
        print("Percentage:", s[4], "%")
        print("Grade:", s[5])
        print("Result:", s[6])


# Search student
def search_student():
    roll = input("\nEnter roll number: ").strip()

    with connect_db() as conn:
        student = conn.execute("""
            SELECT name, age, roll, maths, python, sql,
                   total, percentage, grade, result
            FROM students
            WHERE roll = ?
        """, (roll,)).fetchone()

    if student:
        print("\n===== STUDENT FOUND =====")
        print("Name:", student[0])
        print("Age:", student[1])
        print("Roll:", student[2])
        print("Maths:", student[3])
        print("Python:", student[4])
        print("SQL:", student[5])
        print("Total:", student[6], "/300")
        print("Percentage:", student[7], "%")
        print("Grade:", student[8])
        print("Result:", student[9])
    else:
        print("Student not found!")


# Find class topper
def find_topper():
    with connect_db() as conn:
        topper = conn.execute("""
            SELECT name, roll, percentage, grade
            FROM students
            ORDER BY percentage DESC
            LIMIT 1
        """).fetchone()

    if topper:
        print("\n===== CLASS TOPPER =====")
        print("Name:", topper[0])
        print("Roll:", topper[1])
        print("Percentage:", topper[2], "%")
        print("Grade:", topper[3])
    else:
        print("No student records available.")


# Update student marks
def update_student():
    roll = input("\nEnter roll number to update: ").strip()

    with connect_db() as conn:
        student = conn.execute(
            "SELECT name FROM students WHERE roll = ?",
            (roll,)
        ).fetchone()

    if not student:
        print("Student not found!")
        return

    try:
        maths = int(input("Enter new Maths marks: "))
        python = int(input("Enter new Python marks: "))
        sql = int(input("Enter new SQL marks: "))

        if any(mark < 0 or mark > 100
               for mark in [maths, python, sql]):
            print("Marks must be between 0 and 100!")
            return

    except ValueError:
        print("Please enter valid numbers!")
        return

    total, percentage, grade, result = calculate_result(
        maths, python, sql
    )

    with connect_db() as conn:
        conn.execute("""
            UPDATE students
            SET maths = ?, python = ?, sql = ?,
                total = ?, percentage = ?, grade = ?, result = ?
            WHERE roll = ?
        """, (
            maths, python, sql, total,
            percentage, grade, result, roll
        ))

    print("Student record updated successfully!")


# Delete student
def delete_student():
    roll = input("\nEnter roll number to delete: ").strip()

    with connect_db() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE roll = ?",
            (roll,)
        )

        if cursor.rowcount > 0:
            print("Student deleted successfully!")
        else:
            print("Student not found!")


# Class performance summary
def class_summary():
    with connect_db() as conn:
        summary = conn.execute("""
            SELECT COUNT(*),
                   AVG(percentage),
                   MAX(percentage),
                   MIN(percentage)
            FROM students
        """).fetchone()

        passed = conn.execute("""
            SELECT COUNT(*) FROM students
            WHERE result = 'Pass'
        """).fetchone()[0]

    total_students, average, highest, lowest = summary

    print("\n===== CLASS PERFORMANCE SUMMARY =====")
    print("Total Students:", total_students)

    if total_students == 0:
        print("No records available.")
        return

    print("Class Average:", round(average, 2), "%")
    print("Highest Percentage:", highest, "%")
    print("Lowest Percentage:", lowest, "%")
    print("Passed Students:", passed)
    print("Failed Students:", total_students - passed)


# Main menu
def main():
    create_table()

    while True:
        print("\n===================================")
        print("   STUDENT PERFORMANCE ANALYSIS")
        print("===================================")
        print("1. Add Student")
        print("2. Display All Students")
        print("3. Search Student")
        print("4. Find Class Topper")
        print("5. Update Student Marks")
        print("6. Delete Student")
        print("7. Class Performance Summary")
        print("8. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            display_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            find_topper()
        elif choice == "5":
            update_student()
        elif choice == "6":
            delete_student()
        elif choice == "7":
            class_summary()
        elif choice == "8":
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
