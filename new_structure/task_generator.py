from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import random
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from config import (
    COMPLEXITY_SETTINGS, TASK_TYPES, UI_COLORS, DB_PATH,
    VALIDATION_SETTINGS, FIGURE_TYPES
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
            
            # Save to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
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
            
            conn.commit()
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
        finally:
            conn.close()

    def validate_task(self) -> bool:
        """Validate the generated task"""
        # TODO: Implement proper validation
        return True

    def generate_closed_task(self):
        """Generate a closed path task"""
        # TODO: Implement closed path generation
        pass

    def generate_open_task(self):
        """Generate an open path task"""
        # TODO: Implement open path generation
        pass

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