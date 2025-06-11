import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, Tuple

# Application paths
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'chess_tasks.db')
EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Create necessary directories
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Task types and themes with their available figures
TASK_THEME_FIGURES = {
    'Цикл с пустыми и закрашенными точками': [1, 2],  # 1 - filled point, 2 - empty point
    'Цикл с закрашенными точками': [1],  # 1 - filled point
    'Замкнутый путь с перегородками': [1, 3],  # 1 - point, 3 - wall
    'Путь ладьи 1-2-3 с перегородками': [3, 6],  # 3 - wall, 6 - rook
    'Несколько замкнутых циклов': [1, 2],  # 1 - filled point, 2 - empty point
    'Выход для ладьи': [4, 5, 6],  # 4 - start, 5 - end, 6 - rook
    'Маршрут к базе для 2 ладей': [4, 6, 7],  # 4 - start, 6 - rook, 7 - base
    'Проведи ладью в правильном порядке': [4, 5, 6],  # 4 - start, 5 - end, 6 - rook
    'Путь ладьи по коридорам': [4, 5, 6],  # 4 - start, 5 - end, 6 - rook
    'Маршрут через клетки': [4, 5, 6],  # 4 - start, 5 - end, 6 - rook
    'Простой математический лабиринт': [4, 5, 6],  # 4 - start, 5 - end, 6 - rook
    'Кольцевой маршрут максимальной длины': [4, 5, 6]  # 4 - start, 5 - end, 6 - rook
}

# Task types and themes
TASK_TYPES = {
    'Замкнутые': [
        'Цикл с пустыми и закрашенными точками',
        'Цикл с закрашенными точками',
        'Замкнутый путь с перегородками',
        'Путь ладьи 1-2-3 с перегородками',
        'Несколько замкнутых циклов'
    ],
    'Незамкнутые': [
        'Выход для ладьи',
        'Маршрут к базе для 2 ладей',
        'Проведи ладью в правильном порядке',
        'Путь ладьи по коридорам',
        'Маршрут через клетки',
        'Простой математический лабиринт',
        'Кольцевой маршрут максимальной длины'
    ]
}

# Grid settings
DEFAULT_GRID_SIZE = 8  # Default grid size for new tasks
GRID_SIZE_SETTINGS = {
    'Легко': 6,
    'Средне': 8,
    'Сложно': 10,
    'Невозможно': 16
}

# Complexity settings
COMPLEXITY_SETTINGS = {
    'Легко': {'cell_size': 100, 'margin': 50, 'grid_size': GRID_SIZE_SETTINGS['Легко']},
    'Средне': {'cell_size': 80, 'margin': 50, 'grid_size': GRID_SIZE_SETTINGS['Средне']},
    'Сложно': {'cell_size': 60, 'margin': 50, 'grid_size': GRID_SIZE_SETTINGS['Сложно']},
    'Невозможно': {'cell_size': 40, 'margin': 50, 'grid_size': GRID_SIZE_SETTINGS['Невозможно']}
}

# Task validation settings
VALIDATION_SETTINGS = {
    'max_attempts': 100,  # Maximum attempts to generate a valid task
    'solution_timeout': 5.0,  # Maximum time (seconds) to find a solution
    'min_unique_paths': 1,  # Minimum number of unique paths required
    'max_unique_paths': 1,  # Maximum number of unique paths allowed
    'min_wall_density': 0.1,  # Minimum wall density (walls / total cells)
    'max_wall_density': 0.3   # Maximum wall density (walls / total cells)
}

# UI Theme colors
UI_COLORS = {
    'primary': '#2C3E50',      # Dark blue-gray
    'secondary': '#34495E',    # Lighter blue-gray
    'accent': '#E74C3C',       # Red accent
    'background': '#ECF0F1',   # Light gray
    'text': '#2C3E50',         # Dark text
    'grid': '#95A5A6',         # Grid lines
    'wall': '#E74C3C',         # Wall color
    'figure': '#2C3E50',       # Figure color
    'highlight': '#3498DB',    # Highlight color
    'success': '#27AE60',      # Success color
    'warning': '#F1C40F',      # Warning color
    'error': '#E74C3C'         # Error color
}

# Figure types and their properties
FIGURE_TYPES = {
    1: {  # Закрашенный круг
        'name': 'Закрашенный круг',
        'color': '#000000',
        'type': 'filled_circle',
        'symbol': '●',
        'description': 'Закрашенная точка'
    },
    2: {  # Незакрашенный круг
        'name': 'Незакрашенный круг',
        'color': '#000000',
        'type': 'circle',
        'symbol': '○',
        'description': 'Незакрашенная точка'
    },
    3: {  # Стена
        'name': 'Стена',
        'color': '#000000',
        'type': 'wall',
        'symbol': '─',
        'description': 'Стена',
        'orientation': 'horizontal'  # По умолчанию горизонтальная
    },
    4: {  # Старт
        'name': 'Старт',
        'color': '#000000',
        'type': 'start',
        'symbol': '1',
        'description': 'Точка старта'
    },
    5: {  # Финиш
        'name': 'Финиш',
        'color': '#000000',
        'type': 'end',
        'symbol': '2',
        'description': 'Точка финиша'
    },
    6: {  # Ладья
        'name': 'Ладья',
        'color': '#808080',
        'type': 'rook',
        'symbol': '■',
        'description': 'Ладья'
    },
    7: {  # База
        'name': 'База',
        'color': '#3498DB',
        'type': 'base',
        'symbol': 'B',
        'description': 'База для ладьи'
    }
}

@contextmanager
def db_connection() -> Generator[Tuple[sqlite3.Connection, sqlite3.Cursor], None, None]:
    """Context manager for database connections to ensure proper cleanup"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        yield conn, cursor
    finally:
        if conn:
            try:
                conn.commit()
                conn.close()
            except sqlite3.Error:
                pass

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tasks table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            theme TEXT NOT NULL,
            grid_size INTEGER NOT NULL
        )
    ''')
    
    # Create task_figures table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_figures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            figure_type INTEGER,
            x INTEGER,
            y INTEGER,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    return conn, cursor

# Initialize directories
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

def get_export_path(task_id: int) -> str:
    """Get the export path for a task"""
    return os.path.join(EXPORT_DIR, f'task_{task_id}.cdr')
