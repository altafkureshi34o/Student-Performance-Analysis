
import csv
import sqlite3

with open("students.csv", "r", newline="") as file:
    reader = csv.DictReader(file)
    students = list(reader)

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

for s in students:
    cursor.execute("""
        INSERT OR IGNORE INTO students
        (name, age, roll, maths, python, sql,
         total, percentage, grade, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        s["name"],
        int(s["age"]),
        s["roll"],
        int(s["maths"]),
        int(s["python"]),
        int(s["sql"]),
        int(s["total"]),
        float(s["percentage"]),
        s["grade"],
        s["result"]
    ))

conn.commit()
print("Old student data imported successfully!")
print("Total records in CSV:", len(students))

conn.close()
