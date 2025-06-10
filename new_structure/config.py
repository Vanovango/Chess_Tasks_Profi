import sqlite3
import os

# Application paths
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'chess_tasks.db')
EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Create necessary directories
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

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
    1: {'name': 'Закрашенная точка', 'color': '#000000'},
    2: {'name': 'Пустая точка', 'color': '#FFFFFF', 'border': '#000000'},
    3: {'name': 'Перегородка', 'color': '#E74C3C'},
    4: {'name': 'Старт', 'color': '#27AE60'},
    5: {'name': 'Финиш', 'color': '#E74C3C'},
    6: {'name': 'Ладья', 'color': '#2C3E50'},
    7: {'name': 'База', 'color': '#3498DB'}
}

def init_db():
    """Initialize the database with the required schema"""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Create tasks table with all necessary fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            task_theme TEXT NOT NULL,
            name TEXT NOT NULL,
            complexity TEXT NOT NULL,
            grid_size INTEGER NOT NULL,
            walls TEXT,           -- JSON array of wall coordinates
            figures TEXT,         -- JSON object of figure positions and types
            solution TEXT,        -- JSON object containing the solution
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_valid BOOLEAN DEFAULT 1,
            has_unique_solution BOOLEAN DEFAULT 0,
            export_path TEXT,     -- Path to exported CDR file if exists
            validation_notes TEXT -- Additional validation information
        );
    """)

    # Create indexes for faster searching
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_search 
        ON tasks(task_type, task_theme, complexity, name);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_validation 
        ON tasks(is_valid, has_unique_solution);
    """)

    connection.commit()
    return connection, cursor

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(DB_PATH)

def get_export_path(task_id: int) -> str:
    """Get the export path for a task"""
    return os.path.join(EXPORT_DIR, f'task_{task_id}.cdr')
