import sqlite3


def init_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            logging TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT,
            name TEXT,
            complexity TEXT,
            walls TEXT,
            figures TEXT
            );
    """)

    connection.commit()
    connection.close()