
import csv
import os

FILE_NAME = "students.csv"
students = []


# Load existing student records
def load_students():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", newline="") as file:
            reader = csv.DictReader(file)
            students.extend(reader)


# Save student records
def save_students():
    fields = [
        "name", "age", "roll", "maths", "python",
        "sql", "total", "percentage", "grade", "result"
    ]

    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(students)


# Calculate student performance
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

    return total, percentage, grade, result


# Add new student
def add_student():
    print("\n===== ADD NEW STUDENT =====")

    name = input("Enter student name: ").strip()

    try:
        age = int(input("Enter age: "))
        roll = input("Enter roll number: ").strip()

        if age <= 0 or not name or not roll:
            print("Invalid student details!")
            return

        if any(s["roll"] == roll for s in students):
            print("Roll number already exists!")
            return

        maths = int(input("Enter Maths marks: "))
        python = int(input("Enter Python marks: "))
        sql = int(input("Enter SQL marks: "))

        if any(mark < 0 or mark > 100 for mark in
               [maths, python, sql]):
            print("Marks must be between 0 and 100!")
            return

    except ValueError:
        print("Please enter valid numbers!")
        return

    total, percentage, grade, result = calculate_result(
        maths, python, sql
    )

    student = {
        "name": name,
        "age": age,
        "roll": roll,
        "maths": maths,
        "python": python,
        "sql": sql,
        "total": total,
        "percentage": round(percentage, 2),
        "grade": grade,
        "result": result
    }

    students.append(student)
    save_students()

    print("\nStudent added successfully!")
    print(f"Total: {total}/300")
    print(f"Percentage: {percentage:.2f}%")
    print(f"Grade: {grade}")
    print(f"Result: {result}")


# Display all students
def display_students():
    print("\n===== ALL STUDENTS =====")

    if not students:
        print("No student records found.")
        return

    for s in students:
        print("-" * 40)
        print("Name:", s["name"])
        print("Roll Number:", s["roll"])
        print("Total:", s["total"], "/300")
        print("Percentage:", s["percentage"], "%")
        print("Grade:", s["grade"])
        print("Result:", s["result"])


# Search student
def search_student():
    roll = input("\nEnter roll number: ").strip()

    for s in students:
        if s["roll"] == roll:
            print("\nStudent Found!")
            print("Name:", s["name"])
            print("Percentage:", s["percentage"], "%")
            print("Grade:", s["grade"])
            print("Result:", s["result"])
            return

    print("Student not found!")


# Find highest scorer
def find_topper():
    if not students:
        print("No student records available.")
        return

    topper = max(students, key=lambda s: float(s["percentage"]))

    print("\n===== CLASS TOPPER =====")
    print("Name:", topper["name"])
    print("Roll Number:", topper["roll"])
    print("Percentage:", topper["percentage"], "%")
    print("Grade:", topper["grade"])


# Main menu
def main():
    load_students()

    while True:
        print("\n================================")
        print(" STUDENT PERFORMANCE ANALYSIS")
        print("================================")
        print("1. Add Student")
        print("2. Display All Students")
        print("3. Search Student")
        print("4. Find Class Topper")
        print("5. Exit")

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
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
