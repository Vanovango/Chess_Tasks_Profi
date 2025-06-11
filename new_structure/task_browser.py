from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from typing import Optional, Dict, List, Tuple
import sqlite3
import json
import os
import subprocess
from datetime import datetime

from config import (
    UI_COLORS, DB_PATH, TASK_TYPES, COMPLEXITY_SETTINGS,
    get_export_path, EXPORT_DIR, db_connection, FIGURE_TYPES
)
from create_task import CreateTaskForm

class PreviewDialog(QDialog):
    def __init__(self, task_id, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.figures = {}
        self.loadTaskData()
        self.initUI()
        
    def loadTaskData(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Load task info
        cursor.execute('''
            SELECT name, description, type, theme, grid_size 
            FROM tasks WHERE id = ?
        ''', (self.task_id,))
        self.task_data = cursor.fetchone()
        
        # Load figures
        cursor.execute('''
            SELECT figure_type, x, y 
            FROM task_figures 
            WHERE task_id = ?
        ''', (self.task_id,))
        for figure_type, x, y in cursor.fetchall():
            self.figures[(x, y)] = figure_type
            
        conn.close()
        
    def initUI(self):
        self.setWindowTitle(f'Предпросмотр задачи: {self.task_data[0]}')
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f'Название: {self.task_data[0]}'))
        info_layout.addWidget(QLabel(f'Тип: {self.task_data[2]}'))
        info_layout.addWidget(QLabel(f'Тема: {self.task_data[3]}'))
        info_layout.addWidget(QLabel('Описание:'))
        desc_label = QLabel(self.task_data[1] if self.task_data[1] else '')
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        # Preview canvas
        self.canvas = PreviewCanvas(self)
        
        layout.addLayout(info_layout)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)

class PreviewCanvas(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(400, 400)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Calculate cell size
        grid_size = self.parent.task_data[4]  # grid_size
        cell_size = min(self.width(), self.height()) // grid_size
        
        # Draw grid
        for i in range(grid_size + 1):
            painter.drawLine(i * cell_size, 0, i * cell_size, grid_size * cell_size)
            painter.drawLine(0, i * cell_size, grid_size * cell_size, i * cell_size)
        
        # Draw figures
        for (x, y), figure_id in self.parent.figures.items():
            figure = FIGURE_TYPES[figure_id]
            rect_x = x * cell_size
            rect_y = y * cell_size
            
            painter.fillRect(rect_x + 1, rect_y + 1, 
                           cell_size - 2, cell_size - 2, 
                           QColor(figure['color']))
            
            if 'border' in figure:
                pen = QPen(QColor(figure['border']))
                painter.setPen(pen)
                painter.drawRect(rect_x + 1, rect_y + 1, 
                               cell_size - 2, cell_size - 2)

class TaskBrowser(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просмотр задач")
        self.resize(1200, 800)
        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Search and filter section
        search_layout = QtWidgets.QHBoxLayout()
        
        # Search input
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }}
        """)
        search_layout.addWidget(self.search_input)

        # Filter comboboxes
        self.type_filter = self.create_filter_combobox("Вид задачи")
        self.theme_filter = self.create_filter_combobox("Тема")
        self.complexity_filter = self.create_filter_combobox("Сложность")
        
        search_layout.addWidget(self.type_filter)
        search_layout.addWidget(self.theme_filter)
        search_layout.addWidget(self.complexity_filter)
        
        layout.addLayout(search_layout)

        # Task list
        self.task_list = QtWidgets.QTableView()
        self.task_list.setStyleSheet(f"""
            QTableView {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
            }}
            QTableView::item {{
                padding: 5px;
            }}
            QTableView::item:selected {{
                background-color: {UI_COLORS['accent']};
                color: white;
            }}
        """)
        
        # Setup model and proxy for filtering
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.task_list.setModel(self.proxy_model)
        
        # Set column headers
        self.model.setHorizontalHeaderLabels([
            "ID", "Название", "Вид", "Тема", "Сложность", 
            "Дата создания", "Статус", "Решение", "Экспорт"
        ])
        
        # Adjust column widths
        self.task_list.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        for i in [0, 2, 3, 4, 5, 6, 7, 8]:
            self.task_list.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        
        layout.addWidget(self.task_list)

        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.edit_button = self.create_action_button("Редактировать", UI_COLORS['primary'])
        self.delete_button = self.create_action_button("Удалить", UI_COLORS['accent'])
        self.export_button = self.create_action_button("Экспорт в CDR", UI_COLORS['secondary'])
        self.preview_button = self.create_action_button("Посмотреть", UI_COLORS['success'])
        
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.preview_button)
        
        layout.addLayout(button_layout)

        # Connect signals
        self.search_input.textChanged.connect(self.apply_filters)
        self.type_filter.currentTextChanged.connect(self.update_theme_filter)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        self.theme_filter.currentTextChanged.connect(self.apply_filters)
        self.complexity_filter.currentTextChanged.connect(self.apply_filters)
        
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.export_button.clicked.connect(self.export_task)
        self.preview_button.clicked.connect(self.preview_task)
        self.task_list.doubleClicked.connect(self.edit_task)

    def create_filter_combobox(self, placeholder: str) -> QtWidgets.QComboBox:
        """Create a styled filter combobox"""
        combo = QtWidgets.QComboBox()
        combo.setPlaceholderText(placeholder)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url(assets/down_arrow.png);
                width: 12px;
                height: 12px;
            }}
        """)
        return combo

    def create_action_button(self, text: str, color: str) -> QtWidgets.QPushButton:
        """Create a styled action button"""
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-height: 40px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['secondary']};
            }}
            QPushButton:disabled {{
                background-color: {UI_COLORS['background']};
                color: {UI_COLORS['text']};
            }}
        """)
        return button

    def load_tasks(self):
        """Load tasks from database"""
        try:
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    SELECT id, name, task_type, task_theme, complexity, 
                           created_at, is_valid, has_unique_solution,
                           export_path
                    FROM tasks
                    ORDER BY created_at DESC
                """)
                
                self.model.removeRows(0, self.model.rowCount())
                for row in cursor.fetchall():
                    items = [
                        QStandardItem(str(row[0])),  # ID
                        QStandardItem(row[1]),       # Name
                        QStandardItem(row[2]),       # Type
                        QStandardItem(row[3]),       # Theme
                        QStandardItem(row[4]),       # Complexity
                        QStandardItem(self.format_date(row[5])),  # Created at
                        QStandardItem("✓" if row[6] else "✗"),  # Valid
                        QStandardItem("✓" if row[7] else "✗"),  # Has solution
                        QStandardItem("✓" if row[8] else "✗")   # Exported
                    ]
                    self.model.appendRow(items)
                
                # Update filter options
                self.update_filter_options()
                
        except sqlite3.Error as e:
            self.show_error(f"Ошибка при загрузке задач: {str(e)}")
            return False
        except Exception as e:
            self.show_error(f"Неожиданная ошибка: {str(e)}")
            return False
        return True

    def format_date(self, date_str: str) -> str:
        """Format date string to a more readable format"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_str

    def update_filter_options(self):
        """Update available filter options based on current tasks"""
        # Get unique values from model
        types = set()
        themes = set()
        complexities = set()
        
        for row in range(self.model.rowCount()):
            types.add(self.model.item(row, 2).text())
            themes.add(self.model.item(row, 3).text())
            complexities.add(self.model.item(row, 4).text())
        
        # Update comboboxes
        self.type_filter.clear()
        self.type_filter.addItem("Все виды")
        self.type_filter.addItems(sorted(types))
        
        self.theme_filter.clear()
        self.theme_filter.addItem("Все темы")
        self.theme_filter.addItems(sorted(themes))
        
        self.complexity_filter.clear()
        self.complexity_filter.addItem("Все сложности")
        self.complexity_filter.addItems(sorted(complexities))

    def update_theme_filter(self, task_type: str):
        """Update theme filter based on selected task type"""
        self.theme_filter.clear()
        self.theme_filter.addItem("Все темы")
        
        if task_type in TASK_TYPES:
            self.theme_filter.addItems(TASK_TYPES[task_type])

    def apply_filters(self):
        """Apply all filters to the task list"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        theme_filter = self.theme_filter.currentText()
        complexity_filter = self.complexity_filter.currentText()
        
        for row in range(self.model.rowCount()):
            show_row = True
            
            # Apply search filter
            if search_text:
                name = self.model.item(row, 1).text().lower()
                if search_text not in name:
                    show_row = False
            
            # Apply type filter
            if type_filter != "Все виды":
                if self.model.item(row, 2).text() != type_filter:
                    show_row = False
            
            # Apply theme filter
            if theme_filter != "Все темы":
                if self.model.item(row, 3).text() != theme_filter:
                    show_row = False
            
            # Apply complexity filter
            if complexity_filter != "Все сложности":
                if self.model.item(row, 4).text() != complexity_filter:
                    show_row = False
            
            self.task_list.setRowHidden(row, not show_row)

    def get_selected_task_id(self) -> Optional[int]:
        """Get the ID of the currently selected task"""
        indexes = self.task_list.selectedIndexes()
        if not indexes:
            return None
        return int(self.model.item(indexes[0].row(), 0).text())

    def get_task_data(self, task_id: int) -> Optional[Dict]:
        """Get task data from database"""
        try:
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    SELECT task_type, task_theme, name, complexity,
                           grid_size, walls, figures, solution,
                           is_valid, has_unique_solution, export_path
                    FROM tasks
                    WHERE id = ?
                """, (task_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                    
                return {
                    'task_type': row[0],
                    'task_theme': row[1],
                    'name': row[2],
                    'complexity': row[3],
                    'grid_size': row[4],
                    'walls': json.loads(row[5]) if row[5] else [],
                    'figures': json.loads(row[6]) if row[6] else {},
                    'solution': json.loads(row[7]) if row[7] else None,
                    'is_valid': bool(row[8]),
                    'has_unique_solution': bool(row[9]),
                    'export_path': row[10]
                }
                
        except sqlite3.Error as e:
            self.show_error(f"Ошибка при получении данных задачи: {str(e)}")
        except json.JSONDecodeError as e:
            self.show_error(f"Ошибка при разборе данных задачи: {str(e)}")
        except Exception as e:
            self.show_error(f"Неожиданная ошибка: {str(e)}")
        return None

    def edit_task(self):
        """Open task editor for the selected task"""
        task_id = self.get_selected_task_id()
        if not task_id:
            self.show_error("Выберите задачу для редактирования")
            return
            
        task_data = self.get_task_data(task_id)
        if not task_data:
            return
            
        self.create_task_form = CreateTaskForm(
            task_id=task_id,
            task_type=task_data['task_type'],
            task_theme=task_data['task_theme'],
            name=task_data['name'],
            complexity=task_data['complexity'],
            walls=task_data['walls'],
            figures=task_data['figures']
        )
        self.create_task_form.show()

    def delete_task(self):
        """Delete selected task"""
        task_id = self.get_selected_task_id()
        if not task_id:
            self.show_error("Выберите задачу для удаления")
            return
            
        reply = QtWidgets.QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить эту задачу?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                # Get export path before deletion
                task_data = self.get_task_data(task_id)
                export_path = task_data.get('export_path') if task_data else None
                
                # Delete from database
                with db_connection() as (conn, cursor):
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                
                # Delete export file if exists
                if export_path and os.path.exists(export_path):
                    try:
                        os.remove(export_path)
                    except OSError as e:
                        self.show_error(f"Не удалось удалить файл экспорта: {str(e)}")
                
                # Refresh task list
                self.load_tasks()
                
            except sqlite3.Error as e:
                self.show_error(f"Ошибка при удалении задачи: {str(e)}")
            except Exception as e:
                self.show_error(f"Неожиданная ошибка: {str(e)}")

    def export_task(self):
        """Export task to CDR format"""
        task_id = self.get_selected_task_id()
        if not task_id:
            self.show_error("Выберите задачу для экспорта")
            return
            
        task_data = self.get_task_data(task_id)
        if not task_data:
            return
            
        try:
            export_path = get_export_path(task_id)
            self.generate_cdr_file(task_data, export_path)
            
            # Update export path in database
            with db_connection() as (conn, cursor):
                cursor.execute(
                    "UPDATE tasks SET export_path = ? WHERE id = ?",
                    (export_path, task_id)
                )
            
            # Refresh task list
            self.load_tasks()
            
            QtWidgets.QMessageBox.information(
                self, "Успех",
                f"Задача успешно экспортирована в:\n{export_path}"
            )
            
        except Exception as e:
            self.show_error(f"Ошибка при экспорте задачи: {str(e)}")

    def generate_cdr_file(self, task_data: Dict, export_path: str):
        """Generate a CDR file for the task"""
        # TODO: Implement CDR file generation
        # This is a placeholder that creates a simple text file
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(f"Task: {task_data['name']}\n")
            f.write(f"Type: {task_data['task_type']}\n")
            f.write(f"Theme: {task_data['task_theme']}\n")
            f.write(f"Complexity: {task_data['complexity']}\n")
            f.write(f"Grid Size: {task_data['grid_size']}\n")
            f.write("\nWalls:\n")
            for wall in task_data['walls']:
                f.write(f"  {wall}\n")
            f.write("\nFigures:\n")
            for pos, figure_type in task_data['figures'].items():
                f.write(f"  {pos}: {figure_type}\n")
            if task_data['solution']:
                f.write("\nSolution:\n")
                for pos in task_data['solution']:
                    f.write(f"  {pos}\n")

    def preview_task(self):
        """Show task preview"""
        task_id = self.get_selected_task_id()
        if not task_id:
            self.show_error("Выберите задачу для предпросмотра")
            return
            
        task_data = self.get_task_data(task_id)
        if not task_data:
            return
            
        # Create preview window
        preview = PreviewDialog(task_id, self)
        preview.exec_()

    def show_error(self, message: str):
        """Show error message dialog"""
        QtWidgets.QMessageBox.critical(
            self, "Ошибка", message,
            QtWidgets.QMessageBox.Ok
        ) 