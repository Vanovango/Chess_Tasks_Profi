import sqlite3

DB_PATH = "./database.db"

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
        
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
    """)


    connection.commit()
    connection.close()