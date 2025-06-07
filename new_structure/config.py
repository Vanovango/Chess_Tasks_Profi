import sqlite3

DB_PATH = './chess_tasks'


def init_db():
    connection = sqlite3.connect('chess_tasks')
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,
            task_theme TEXT,
            name TEXT,
            complexity TEXT,
            objects TEXT        
        );
        
    """)
    connection.commit()

    return connection, cursor
