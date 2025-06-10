from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from typing import Optional, Dict
import sqlite3
import json
import os
import subprocess
from datetime import datetime

from config import (
    UI_COLORS, DB_PATH, TASK_TYPES, COMPLEXITY_SETTINGS,
    get_export_path, EXPORT_DIR
)
from create_task import CreateTaskForm

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
        self.preview_button = self.create_action_button("Предпросмотр", UI_COLORS['success'])
        
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
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
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
                    QStandardItem(row[5]),       # Created at
                    QStandardItem("✓" if row[6] else "✗"),  # Valid
                    QStandardItem("✓" if row[7] else "✗"),  # Has solution
                    QStandardItem("✓" if row[8] else "✗")   # Exported
                ]
                self.model.appendRow(items)
            
            # Update filter options
            self.update_filter_options()
            
        except sqlite3.Error as e:
            self.show_error(f"Ошибка при загрузке задач: {str(e)}")
        finally:
            conn.close()

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
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_type, task_theme, name, complexity,
                       grid_size, walls, figures, solution
                FROM tasks
                WHERE id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'task_type': row[0],
                    'task_theme': row[1],
                    'name': row[2],
                    'complexity': row[3],
                    'grid_size': row[4],
                    'walls': json.loads(row[5]),
                    'figures': json.loads(row[6]),
                    'solution': json.loads(row[7]) if row[7] else None
                }
            return None
            
        except (sqlite3.Error, json.JSONDecodeError) as e:
            self.show_error(f"Ошибка при получении данных задачи: {str(e)}")
            return None
        finally:
            conn.close()

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
        """Delete the selected task"""
        task_id = self.get_selected_task_id()
        if not task_id:
            self.show_error("Выберите задачу для удаления")
            return
            
        reply = QtWidgets.QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить эту задачу?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Get export path before deleting
                cursor.execute("SELECT export_path FROM tasks WHERE id = ?", (task_id,))
                export_path = cursor.fetchone()[0]
                
                # Delete task
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                
                # Delete exported file if exists
                if export_path and os.path.exists(export_path):
                    os.remove(export_path)
                
                self.load_tasks()
                
            except sqlite3.Error as e:
                self.show_error(f"Ошибка при удалении задачи: {str(e)}")
            finally:
                conn.close()

    def export_task(self):
        """Export the selected task to CDR format"""
        task_id = self.get_selected_task_id()
        if not task_id:
            self.show_error("Выберите задачу для экспорта")
            return
            
        task_data = self.get_task_data(task_id)
        if not task_data:
            return
            
        try:
            # Generate CDR file
            export_path = get_export_path(task_id)
            self.generate_cdr_file(task_data, export_path)
            
            # Update database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks
                SET export_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (export_path, task_id))
            conn.commit()
            
            # Update UI
            self.load_tasks()
            
            # Show success message
            QtWidgets.QMessageBox.information(
                self, 'Успех',
                f'Задача успешно экспортирована в файл:\n{export_path}'
            )
            
        except Exception as e:
            self.show_error(f"Ошибка при экспорте задачи: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

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
        preview = QtWidgets.QDialog(self)
        preview.setWindowTitle(f"Предпросмотр: {task_data['name']}")
        preview.resize(800, 600)
        
        layout = QtWidgets.QVBoxLayout(preview)
        
        # Add task information
        info = QtWidgets.QLabel(
            f"Тип: {task_data['task_type']}\n"
            f"Тема: {task_data['task_theme']}\n"
            f"Сложность: {task_data['complexity']}\n"
            f"Размер сетки: {task_data['grid_size']}x{task_data['grid_size']}"
        )
        layout.addWidget(info)
        
        # Add preview widget (placeholder)
        preview_widget = QtWidgets.QLabel("Здесь будет предпросмотр задачи")
        preview_widget.setStyleSheet(f"""
            QLabel {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                padding: 20px;
            }}
        """)
        layout.addWidget(preview_widget)
        
        # Add close button
        close_button = QtWidgets.QPushButton("Закрыть")
        close_button.clicked.connect(preview.close)
        layout.addWidget(close_button)
        
        preview.exec_()

    def show_error(self, message: str):
        """Show error message dialog"""
        QtWidgets.QMessageBox.critical(
            self, 'Ошибка',
            message,
            QtWidgets.QMessageBox.Ok
        ) 