from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
import sqlite3
import os
import json
from typing import Optional, List, Dict
from config import (
    DEFAULT_GRID_SIZE, COMPLEXITY_SETTINGS, TASK_TYPES, UI_COLORS, DB_PATH,
    GRID_SIZE_SETTINGS, FIGURE_TYPES
)

class CreateTaskForm(QtWidgets.QMainWindow):
    def __init__(self, task_id: Optional[int] = None, task_type: str = "", task_theme: str = "",
                 name: str = "", complexity: str = "", walls: List[Dict] = None,
                 figures: Dict[str, str] = None):
        super().__init__()
        
        # Initialize task data
        self.task_id = task_id
        self.task_type = task_type
        self.task_theme = task_theme
        self.name = name
        self.complexity = complexity or "Средне"
        self.walls = walls or []
        self.figures = figures or {}
        
        # Set grid size based on complexity
        settings = COMPLEXITY_SETTINGS[self.complexity]
        self.CELL_SIZE = int(settings['cell_size'])
        self.MARGIN = int(settings['margin'])
        self.GRID_SIZE = int(settings['grid_size'])
        
        # Calculate window dimensions
        self.SCREEN_WIDTH = int(self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN)
        self.SCREEN_HEIGHT = int(self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN + 200)
        
        # Setup UI
        self.setup_ui()
        self.load_task_data()

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Редактор задачи")
        self.resize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add task information fields
        info_layout = QtWidgets.QFormLayout()
        
        self.name_input = QtWidgets.QLineEdit(self.name)
        self.name_input.setPlaceholderText("Название задачи")
        info_layout.addRow("Название:", self.name_input)
        
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(TASK_TYPES.keys())
        if self.task_type:
            self.type_combo.setCurrentText(self.task_type)
        info_layout.addRow("Тип:", self.type_combo)
        
        self.theme_combo = QtWidgets.QComboBox()
        self.update_themes()
        if self.task_theme:
            self.theme_combo.setCurrentText(self.task_theme)
        info_layout.addRow("Тема:", self.theme_combo)
        
        self.complexity_combo = QtWidgets.QComboBox()
        self.complexity_combo.addItems(COMPLEXITY_SETTINGS.keys())
        self.complexity_combo.setCurrentText(self.complexity)
        info_layout.addRow("Сложность:", self.complexity_combo)
        
        layout.addLayout(info_layout)
        
        # Add canvas for task editing
        self.canvas = TaskCanvas(self)
        layout.addWidget(self.canvas)
        
        # Add action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.save_button = QtWidgets.QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_task)
        button_layout.addWidget(self.save_button)
        
        self.validate_button = QtWidgets.QPushButton("Проверить")
        self.validate_button.clicked.connect(self.validate_task)
        button_layout.addWidget(self.validate_button)
        
        self.cancel_button = QtWidgets.QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.type_combo.currentTextChanged.connect(self.update_themes)
        self.complexity_combo.currentTextChanged.connect(self.update_grid_size)

    def update_themes(self):
        """Update available themes based on selected task type"""
        self.theme_combo.clear()
        task_type = self.type_combo.currentText()
        if task_type in TASK_TYPES:
            self.theme_combo.addItems(TASK_TYPES[task_type])

    def update_grid_size(self):
        """Update grid size based on selected complexity"""
        complexity = self.complexity_combo.currentText()
        if complexity in COMPLEXITY_SETTINGS:
            settings = COMPLEXITY_SETTINGS[complexity]
            self.CELL_SIZE = int(settings['cell_size'])
            self.MARGIN = int(settings['margin'])
            self.GRID_SIZE = int(settings['grid_size'])
            self.canvas.update_grid()

    def load_task_data(self):
        """Load task data from database if editing existing task"""
        if not self.task_id:
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_type, task_theme, name, complexity,
                       grid_size, walls, figures, solution
                FROM tasks
                WHERE id = ?
            """, (self.task_id,))
            
            row = cursor.fetchone()
            if row:
                self.task_type = row[0]
                self.task_theme = row[1]
                self.name = row[2]
                self.complexity = row[3]
                self.GRID_SIZE = row[4]
                self.walls = json.loads(row[5]) if row[5] else []
                self.figures = json.loads(row[6]) if row[6] else {}
                
                # Update UI
                self.name_input.setText(self.name)
                self.type_combo.setCurrentText(self.task_type)
                self.theme_combo.setCurrentText(self.task_theme)
                self.complexity_combo.setCurrentText(self.complexity)
                self.canvas.update_grid()
                
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные задачи: {str(e)}")
        finally:
            conn.close()

    def save_task(self):
        """Save task to database"""
        try:
            # Validate required fields
            name = self.name_input.text().strip()
            if not name:
                QtWidgets.QMessageBox.warning(self, "Предупреждение", "Введите название задачи")
                return
                
            task_type = self.type_combo.currentText()
            task_theme = self.theme_combo.currentText()
            complexity = self.complexity_combo.currentText()
            
            # Prepare data for database
            task_data = {
                'task_type': task_type,
                'task_theme': task_theme,
                'name': name,
                'complexity': complexity,
                'grid_size': self.GRID_SIZE,
                'walls': json.dumps(self.canvas.walls),
                'figures': json.dumps(self.canvas.figures),
                'solution': None,  # Will be set after validation
                'is_valid': False,
                'has_unique_solution': False
            }
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if self.task_id:
                # Update existing task
                cursor.execute("""
                    UPDATE tasks
                    SET task_type = ?, task_theme = ?, name = ?, complexity = ?,
                        grid_size = ?, walls = ?, figures = ?, solution = ?,
                        updated_at = CURRENT_TIMESTAMP, is_valid = ?,
                        has_unique_solution = ?
                    WHERE id = ?
                """, (
                    task_data['task_type'], task_data['task_theme'],
                    task_data['name'], task_data['complexity'],
                    task_data['grid_size'], task_data['walls'],
                    task_data['figures'], task_data['solution'],
                    task_data['is_valid'], task_data['has_unique_solution'],
                    self.task_id
                ))
            else:
                # Create new task
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
                self.task_id = cursor.lastrowid
            
            conn.commit()
            QtWidgets.QMessageBox.information(self, "Успех", "Задача сохранена")
            
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить задачу: {str(e)}")
        finally:
            conn.close()

    def validate_task(self):
        """Validate the current task"""
        # TODO: Implement task validation
        QtWidgets.QMessageBox.information(self, "Информация", "Валидация задачи будет реализована позже")

class TaskCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.walls = []
        self.figures = {}
        self.selected_cell = None
        self.current_figure_type = 1  # Default to filled point
        
        # Setup widget
        self.setMinimumSize(parent.SCREEN_WIDTH, parent.SCREEN_HEIGHT - 200)
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw grid
        self.draw_grid(painter)
        
        # Draw walls
        self.draw_walls(painter)
        
        # Draw figures
        self.draw_figures(painter)
        
        # Draw selected cell
        if self.selected_cell:
            self.draw_selected_cell(painter)
    
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
        for wall in self.walls:
            start = wall['start']
            end = wall['end']
            x1 = self.parent.MARGIN + start[0] * self.parent.CELL_SIZE
            y1 = self.parent.MARGIN + start[1] * self.parent.CELL_SIZE
            x2 = self.parent.MARGIN + end[0] * self.parent.CELL_SIZE
            y2 = self.parent.MARGIN + end[1] * self.parent.CELL_SIZE
            painter.drawLine(x1, y1, x2, y2)
    
    def draw_figures(self, painter):
        """Draw figures on the grid"""
        for pos, figure_type in self.figures.items():
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
    
    def draw_selected_cell(self, painter):
        """Draw highlight for selected cell"""
        if not self.selected_cell:
            return
            
        x, y = self.selected_cell
        cell_x = self.parent.MARGIN + x * self.parent.CELL_SIZE
        cell_y = self.parent.MARGIN + y * self.parent.CELL_SIZE
        
        painter.setPen(QPen(QColor(UI_COLORS['highlight']), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(cell_x, cell_y,
                        self.parent.CELL_SIZE,
                        self.parent.CELL_SIZE)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            # Get cell coordinates
            x = (event.x() - self.parent.MARGIN) // self.parent.CELL_SIZE
            y = (event.y() - self.parent.MARGIN) // self.parent.CELL_SIZE
            
            if 0 <= x < self.parent.GRID_SIZE and 0 <= y < self.parent.GRID_SIZE:
                self.selected_cell = (x, y)
                pos = f"{x},{y}"
                
                # Toggle figure
                if pos in self.figures:
                    del self.figures[pos]
                else:
                    self.figures[pos] = self.current_figure_type
                
                self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        x = (event.x() - self.parent.MARGIN) // self.parent.CELL_SIZE
        y = (event.y() - self.parent.MARGIN) // self.parent.CELL_SIZE
        
        if 0 <= x < self.parent.GRID_SIZE and 0 <= y < self.parent.GRID_SIZE:
            self.selected_cell = (x, y)
        else:
            self.selected_cell = None
            
        self.update()
    
    def update_grid(self):
        """Update grid size and redraw"""
        self.setMinimumSize(self.parent.SCREEN_WIDTH, self.parent.SCREEN_HEIGHT - 200)
        self.update()
