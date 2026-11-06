
import sqlite3

DB_NAME = "students.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


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

    print("Database and table created successfully!")


if __name__ == "__main__":
    create_table()
