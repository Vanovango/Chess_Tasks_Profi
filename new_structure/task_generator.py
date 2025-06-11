from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import random
import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Set
from config import (
    COMPLEXITY_SETTINGS, TASK_TYPES, UI_COLORS, DB_PATH,
    VALIDATION_SETTINGS, FIGURE_TYPES, db_connection
)

class TaskGenerator(QtWidgets.QMainWindow):
    def __init__(self, task_type: str, task_theme: str, complexity: str):
        super().__init__()
        self.task_type = task_type
        self.task_theme = task_theme
        self.complexity = complexity
        
        # Get grid settings
        settings = COMPLEXITY_SETTINGS[complexity]
        self.CELL_SIZE = int(settings['cell_size'])
        self.MARGIN = int(settings['margin'])
        self.GRID_SIZE = int(settings['grid_size'])
        
        # Calculate window dimensions
        self.SCREEN_WIDTH = int(self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN)
        self.SCREEN_HEIGHT = int(self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN + 200)
        
        # Initialize task data
        self.walls = []
        self.figures = {}
        self.solution = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Генератор задач")
        self.resize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # Main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Info block
        info_block = QtWidgets.QFrame()
        info_block.setStyleSheet(f"""
            QFrame {{
                background: {UI_COLORS['background']};
                border-radius: 12px;
                border: 2px solid {UI_COLORS['primary']};
                padding: 18px;
            }}
        """)
        info_layout = QtWidgets.QVBoxLayout(info_block)
        info_label = QtWidgets.QLabel(
            f"<b>Тип:</b> {self.task_type}<br>"
            f"<b>Тема:</b> {self.task_theme}<br>"
            f"<b>Сложность:</b> {self.complexity}"
        )
        info_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        info_label.setStyleSheet(f"font-size: 18px; color: {UI_COLORS['primary']};")
        info_layout.addWidget(info_label)
        main_layout.addWidget(info_block)

        # Grid area block
        grid_block = QtWidgets.QFrame()
        grid_block.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 16px;
                border: 2px solid {UI_COLORS['grid']};
                box-shadow: 0 4px 24px rgba(44,62,80,0.08);
            }}
        """)
        grid_layout = QtWidgets.QVBoxLayout(grid_block)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(0)
        self.canvas = TaskCanvas(self)
        self.canvas.setStyleSheet("background: transparent;")
        grid_layout.addWidget(self.canvas)
        main_layout.addWidget(grid_block, stretch=1)

        # Button block
        button_block = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_block)
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_style = f"""
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                padding: 12px 0;
                min-width: 160px;
                min-height: 44px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['secondary']};
            }}
        """
        self.generate_button = QtWidgets.QPushButton("Сгенерировать")
        self.generate_button.setStyleSheet(button_style)
        self.generate_button.clicked.connect(self.generate_task)
        button_layout.addWidget(self.generate_button)

        self.save_button = QtWidgets.QPushButton("Сохранить")
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_task)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QtWidgets.QPushButton("Отмена")
        self.cancel_button.setStyleSheet(button_style)
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        main_layout.addWidget(button_block, alignment=Qt.AlignCenter)

    def generate_task(self):
        """Generate a new task"""
        try:
            # Clear previous task
            self.walls = []
            self.figures = {}
            self.solution = None
            
            # Generate task based on type and theme
            if self.task_type == "Замкнутые":
                self.generate_closed_task()
            else:
                self.generate_open_task()
            
            # Validate the generated task
            if not self.validate_task():
                QtWidgets.QMessageBox.warning(
                    self, "Предупреждение",
                    "Сгенерированная задача не прошла валидацию. Попробуйте еще раз."
                )
                return
            
            # Update canvas
            self.canvas.update()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка",
                f"Ошибка при генерации задачи: {str(e)}"
            )

    def save_task(self):
        """Save the generated task to database"""
        if not self.walls or not self.figures:
            QtWidgets.QMessageBox.warning(
                self, "Предупреждение",
                "Сначала сгенерируйте задачу"
            )
            return
            
        try:
            # Generate task name
            name = f"{self.task_type} - {self.task_theme} ({self.complexity})"
            
            # Prepare task data
            task_data = {
                'task_type': self.task_type,
                'task_theme': self.task_theme,
                'name': name,
                'complexity': self.complexity,
                'grid_size': self.GRID_SIZE,
                'walls': json.dumps(self.walls),
                'figures': json.dumps(self.figures),
                'solution': json.dumps(self.solution) if self.solution else None,
                'is_valid': True,
                'has_unique_solution': bool(self.solution)
            }
            
            # Save to database using context manager
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO tasks (
                        task_type, task_theme, name, complexity,
                        grid_size, walls, figures, solution,
                        is_valid, has_unique_solution
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_data['task_type'], task_data['task_theme'],
                    task_data['name'], task_data['complexity'],
                    task_data['grid_size'], task_data['walls'],
                    task_data['figures'], task_data['solution'],
                    task_data['is_valid'], task_data['has_unique_solution']
                ))
                
                task_id = cursor.lastrowid
            
            QtWidgets.QMessageBox.information(
                self, "Успех",
                f"Задача успешно сохранена (ID: {task_id})"
            )
            
            # Close window
            self.close()
            
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось сохранить задачу: {str(e)}"
            )

    def validate_task(self) -> bool:
        """Validate the generated task"""
        if not self.walls or not self.figures:
            return False

        # Check wall density
        total_cells = self.GRID_SIZE * self.GRID_SIZE
        wall_density = len(self.walls) / total_cells
        if not (VALIDATION_SETTINGS['min_wall_density'] <= wall_density <= VALIDATION_SETTINGS['max_wall_density']):
            return False

        # Check if there are required figures based on task type
        if self.task_type == "Замкнутые":
            if not any(fig_type in [1, 2] for fig_type in self.figures.values()):
                return False
        else:  # Незамкнутые
            if not any(fig_type in [4, 5] for fig_type in self.figures.values()):
                return False

        # Validate solution exists
        if not self.find_solution():
            return False

        return True

    def find_solution(self) -> bool:
        """Find a valid solution for the task"""
        if self.task_type == "Замкнутые":
            return self.find_closed_path_solution()
        else:
            return self.find_open_path_solution()

    def find_closed_path_solution(self) -> bool:
        """Find a valid closed path solution"""
        points = [pos for pos, fig_type in self.figures.items() if fig_type in [1, 2]]
        if not points:
            return False

        # Try to find a valid cycle through all points
        visited = set()
        path = []
        
        def is_valid_move(x: int, y: int) -> bool:
            return (0 <= x < self.GRID_SIZE and 
                   0 <= y < self.GRID_SIZE and 
                   f"{x},{y}" not in self.walls)

        def can_reach_next_point(start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
            queue = [(start, [start])]
            seen = {start}
            
            while queue:
                (x, y), path = queue.pop(0)
                if (x, y) == end:
                    return path
                
                # Try rook moves
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_x, new_y = x + dx, y + dy
                    if (is_valid_move(new_x, new_y) and 
                        (new_x, new_y) not in seen):
                        seen.add((new_x, new_y))
                        queue.append(((new_x, new_y), path + [(new_x, new_y)]))
            return []

        # Try to connect all points
        current = tuple(map(int, points[0].split(",")))
        visited.add(points[0])
        path = [current]
        
        while len(visited) < len(points):
            next_point = None
            next_path = None
            
            # Find closest unvisited point
            for point in points:
                if point not in visited:
                    target = tuple(map(int, point.split(",")))
                    temp_path = can_reach_next_point(current, target)
                    if temp_path:
                        if not next_path or len(temp_path) < len(next_path):
                            next_point = point
                            next_path = temp_path
            
            if not next_path:
                return False
                
            visited.add(next_point)
            path.extend(next_path[1:])
            current = tuple(map(int, next_point.split(",")))

        # Check if we can close the path
        final_path = can_reach_next_point(current, tuple(map(int, points[0].split(","))))
        if not final_path:
            return False

        path.extend(final_path[1:])
        self.solution = path
        return True

    def find_open_path_solution(self) -> bool:
        """Find a valid open path solution"""
        start = None
        end = None
        for pos, fig_type in self.figures.items():
            if fig_type == 4:  # Start
                start = tuple(map(int, pos.split(",")))
            elif fig_type == 5:  # End
                end = tuple(map(int, pos.split(",")))

        if not start or not end:
            return False

        def is_valid_move(x: int, y: int) -> bool:
            return (0 <= x < self.GRID_SIZE and 
                   0 <= y < self.GRID_SIZE and 
                   f"{x},{y}" not in self.walls)

        # BFS to find path
        queue = [(start, [start])]
        seen = {start}
        
        while queue:
            (x, y), path = queue.pop(0)
            if (x, y) == end:
                self.solution = path
                return True
            
            # Try rook moves
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (is_valid_move(new_x, new_y) and 
                    (new_x, new_y) not in seen):
                    seen.add((new_x, new_y))
                    queue.append(((new_x, new_y), path + [(new_x, new_y)]))
        
        return False

    def generate_closed_task(self):
        """Generate a closed path task"""
        self.walls = []
        self.figures = {}
        
        # Add points based on complexity
        num_points = {
            'Легко': 3,
            'Средне': 4,
            'Сложно': 5,
            'Невозможно': 6
        }[self.complexity]
        
        # Place points
        points_placed = 0
        attempts = 0
        while points_placed < num_points and attempts < 100:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            pos = f"{x},{y}"
            
            if pos not in self.figures:
                self.figures[pos] = random.choice([1, 2])  # Random point type
                points_placed += 1
            attempts += 1

        # Add walls
        wall_count = int(self.GRID_SIZE * self.GRID_SIZE * random.uniform(
            VALIDATION_SETTINGS['min_wall_density'],
            VALIDATION_SETTINGS['max_wall_density']
        ))
        
        walls_placed = 0
        attempts = 0
        while walls_placed < wall_count and attempts < 100:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            pos = f"{x},{y}"
            
            if pos not in self.walls and pos not in self.figures:
                self.walls.append(pos)
                walls_placed += 1
            attempts += 1

    def generate_open_task(self):
        """Generate an open path task"""
        self.walls = []
        self.figures = {}
        
        # Place start point
        x1 = random.randint(0, self.GRID_SIZE - 1)
        y1 = random.randint(0, self.GRID_SIZE - 1)
        self.figures[f"{x1},{y1}"] = 4  # Start
        
        # Place end point
        while True:
            x2 = random.randint(0, self.GRID_SIZE - 1)
            y2 = random.randint(0, self.GRID_SIZE - 1)
            if (x2, y2) != (x1, y1):
                self.figures[f"{x2},{y2}"] = 5  # End
                break
        
        # Add walls
        wall_count = int(self.GRID_SIZE * self.GRID_SIZE * random.uniform(
            VALIDATION_SETTINGS['min_wall_density'],
            VALIDATION_SETTINGS['max_wall_density']
        ))
        
        walls_placed = 0
        attempts = 0
        while walls_placed < wall_count and attempts < 100:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            pos = f"{x},{y}"
            
            if pos not in self.walls and pos not in self.figures:
                self.walls.append(pos)
                walls_placed += 1
            attempts += 1

    def update_ui(self):
        """Update UI with current values"""
        # Update grid settings based on new complexity
        settings = COMPLEXITY_SETTINGS[self.complexity]
        self.CELL_SIZE = int(settings['cell_size'])
        self.MARGIN = int(settings['margin'])
        self.GRID_SIZE = int(settings['grid_size'])
        
        # Update window title
        self.setWindowTitle("Генератор задач")
        
        # Update info label
        if hasattr(self, 'info_label'):
            self.info_label.setText(
                f"<b>Тип:</b> {self.task_type}<br>"
                f"<b>Тема:</b> {self.task_theme}<br>"
                f"<b>Сложность:</b> {self.complexity}"
            )
        
        # Reset task data
        self.walls = []
        self.figures = {}
        self.solution = None
        
        # Force canvas redraw
        if hasattr(self, 'canvas'):
            self.canvas.update()

class TaskCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw grid
        self.draw_grid(painter)
        
        # Draw walls
        self.draw_walls(painter)
        
        # Draw figures
        self.draw_figures(painter)
    
    def draw_grid(self, painter):
        """Draw the task grid"""
        painter.setPen(QPen(QColor(UI_COLORS['grid']), 1))
        
        # Draw vertical lines
        for i in range(self.parent.GRID_SIZE + 1):
            x = self.parent.MARGIN + i * self.parent.CELL_SIZE
            painter.drawLine(x, self.parent.MARGIN,
                           x, self.parent.MARGIN + self.parent.GRID_SIZE * self.parent.CELL_SIZE)
        
        # Draw horizontal lines
        for i in range(self.parent.GRID_SIZE + 1):
            y = self.parent.MARGIN + i * self.parent.CELL_SIZE
            painter.drawLine(self.parent.MARGIN, y,
                           self.parent.MARGIN + self.parent.GRID_SIZE * self.parent.CELL_SIZE, y)
    
    def draw_walls(self, painter):
        """Draw walls on the grid"""
        painter.setPen(QPen(QColor(UI_COLORS['wall']), 3))
        for wall in self.parent.walls:
            start = wall['start']
            end = wall['end']
            x1 = self.parent.MARGIN + start[0] * self.parent.CELL_SIZE
            y1 = self.parent.MARGIN + start[1] * self.parent.CELL_SIZE
            x2 = self.parent.MARGIN + end[0] * self.parent.CELL_SIZE
            y2 = self.parent.MARGIN + end[1] * self.parent.CELL_SIZE
            painter.drawLine(x1, y1, x2, y2)
    
    def draw_figures(self, painter):
        """Draw figures on the grid"""
        for pos, figure_type in self.parent.figures.items():
            x, y = map(int, pos.split(','))
            cell_x = self.parent.MARGIN + x * self.parent.CELL_SIZE
            cell_y = self.parent.MARGIN + y * self.parent.CELL_SIZE
            
            # Draw figure based on type
            if figure_type == 1:  # Filled point
                painter.setBrush(QBrush(QColor(FIGURE_TYPES[1]['color'])))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(cell_x + 5, cell_y + 5,
                                  self.parent.CELL_SIZE - 10,
                                  self.parent.CELL_SIZE - 10)
            elif figure_type == 2:  # Empty point
                painter.setBrush(QBrush(QColor(FIGURE_TYPES[2]['color'])))
                painter.setPen(QPen(QColor(FIGURE_TYPES[2]['border']), 2))
                painter.drawEllipse(cell_x + 5, cell_y + 5,
                                  self.parent.CELL_SIZE - 10,
                                  self.parent.CELL_SIZE - 10)
            # Add other figure types as needed 