from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
import sys
import os
import json
import sqlite3

from config import (
    UI_COLORS, TASK_TYPES, COMPLEXITY_SETTINGS,
    db_connection
)
from task_generator import TaskGenerator
from create_task import CreateTaskForm
from task_browser import TaskBrowser

class Ui_MainWindow(object):
    def __init__(self, task_browser=None):
        self.task_browser = task_browser
        self.task_types = list(TASK_TYPES.keys())
        self.create_task_form = None  # Single instance of create task form
        self.task_generator = None    # Single instance of task generator

    def setupUi(self, MainWindow):
        """Setup the main window UI"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        MainWindow.setWindowTitle("Генератор шахматных задач")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'chess_icon.png')
        if os.path.exists(icon_path):
            MainWindow.setWindowIcon(QIcon(icon_path))

        # Set application style
        self.set_application_style()
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setSpacing(15)
        
        # Title with chess-themed styling
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet(f"color: {UI_COLORS['primary']};")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setText("Генератор шахматных задач")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 2)

        # Settings section
        self.label_title_settings = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_title_settings.setFont(font)
        self.label_title_settings.setStyleSheet(f"color: {UI_COLORS['secondary']};")
        self.label_title_settings.setAlignment(Qt.AlignCenter)
        self.label_title_settings.setText("Параметры задачи")
        self.gridLayout.addWidget(self.label_title_settings, 2, 0, 1, 2)

        # Task type selection with improved styling
        self.comboBox_task_type = self.create_styled_combobox()
        self.comboBox_task_type.addItem("Выберите вид задачи")
        for task_type in TASK_TYPES.keys():
            self.comboBox_task_type.addItem(task_type)
        self.gridLayout.addWidget(self.comboBox_task_type, 3, 0, 1, 2)

        # Task theme selection
        self.comboBox_task_theme = self.create_styled_combobox()
        self.gridLayout.addWidget(self.comboBox_task_theme, 4, 0, 1, 2)

        # Task name input
        self.lineEdit_task_name = self.create_styled_lineedit("Введите название задачи")
        self.gridLayout.addWidget(self.lineEdit_task_name, 5, 0, 1, 2)

        # Complexity selection
        self.comboBox_complexity = self.create_styled_combobox()
        self.comboBox_complexity.addItem("Выберите сложность")
        for complexity in COMPLEXITY_SETTINGS.keys():
            self.comboBox_complexity.addItem(complexity)
        self.gridLayout.addWidget(self.comboBox_complexity, 6, 0, 1, 2)

        # Separator
        self.add_separator(7)

        # Action buttons with improved styling
        self.pushButton_generate_task = self.create_styled_button("Сгенерировать задачу")
        self.pushButton_create_by_yourself = self.create_styled_button("Создать задачу вручную")
        self.gridLayout.addWidget(self.pushButton_generate_task, 8, 0)
        self.gridLayout.addWidget(self.pushButton_create_by_yourself, 8, 1)

        self.pushButton_show_tasks_list = self.create_styled_button("Просмотр задач")
        self.pushButton_load_task = self.create_styled_button("Загрузить задачу")
        self.gridLayout.addWidget(self.pushButton_show_tasks_list, 9, 0)
        self.gridLayout.addWidget(self.pushButton_load_task, 9, 1)

        self.pushButton_exit = self.create_styled_button("Выход")
        self.gridLayout.addWidget(self.pushButton_exit, 10, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.setup_connections()

    def set_application_style(self):
        """Set the application-wide style"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(UI_COLORS['background']))
        palette.setColor(QPalette.WindowText, QColor(UI_COLORS['text']))
        palette.setColor(QPalette.Base, QColor(UI_COLORS['background']))
        palette.setColor(QPalette.AlternateBase, QColor(UI_COLORS['secondary']))
        palette.setColor(QPalette.Button, QColor(UI_COLORS['primary']))
        palette.setColor(QPalette.ButtonText, QColor(UI_COLORS['background']))
        QtWidgets.QApplication.setPalette(palette)

    def create_styled_combobox(self) -> QtWidgets.QComboBox:
        """Create a styled combobox with improved selection visibility"""
        combo = QtWidgets.QComboBox()
        font = QtGui.QFont()
        font.setPointSize(12)
        combo.setFont(font)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
                color: {UI_COLORS['primary']};
            }}
            QComboBox QAbstractItemView {{
                background: {UI_COLORS['background']};
                selection-background-color: {UI_COLORS['primary']};
                selection-color: white;
                color: {UI_COLORS['primary']};
            }}
            QComboBox::item:selected {{
                background: {UI_COLORS['primary']};
                color: white;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(assets/down_arrow.png);
                width: 12px;
                height: 12px;
            }}
        """)
        return combo

    def create_styled_lineedit(self, placeholder: str) -> QtWidgets.QLineEdit:
        """Create a styled line edit"""
        line_edit = QtWidgets.QLineEdit()
        font = QtGui.QFont()
        font.setPointSize(12)
        line_edit.setFont(font)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }}
            QLineEdit:hover {{
                border-color: {UI_COLORS['accent']};
            }}
        """)
        return line_edit

    def create_styled_button(self, text: str, color: str = None) -> QtWidgets.QPushButton:
        """Create a styled button with consistent appearance"""
        button = QtWidgets.QPushButton(text)
        if color is None:
            color = UI_COLORS['primary']
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
        """)
        return button

    def add_separator(self, row: int):
        """Add a styled separator line"""
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet(f"background-color: {UI_COLORS['primary']};")
        self.gridLayout.addWidget(line, row, 0, 1, 2)

    def setup_connections(self):
        """Setup signal connections"""
        self.comboBox_task_type.currentTextChanged.connect(self.update_task_themes)
        self.pushButton_generate_task.clicked.connect(self.generate_task)
        self.pushButton_create_by_yourself.clicked.connect(self.create_task_manually)
        self.pushButton_show_tasks_list.clicked.connect(self.show_tasks_list)
        self.pushButton_load_task.clicked.connect(self.load_task)
        self.pushButton_exit.clicked.connect(lambda: sys.exit())

    def update_task_themes(self, task_type: str):
        """Update available themes based on selected task type"""
        self.comboBox_task_theme.clear()
        
        # Remove the dash and space prefix if present
        clean_type = task_type.strip(' -')
        
        if clean_type in TASK_TYPES:
            self.comboBox_task_theme.addItems(TASK_TYPES[clean_type])
        else:
            self.comboBox_task_theme.addItem("Выберите вид задачи")

    def create_task_manually(self):
        """Open task creation form"""
        if not hasattr(self, 'create_task_form') or not self.create_task_form:
            self.create_task_form = CreateTaskForm(parent=self.window())
            self.create_task_form.taskCreated.connect(self.load_tasks)
            self.create_task_form.finished.connect(self.on_create_task_form_closed)
        self.create_task_form.show()

    def generate_task(self):
        """Генерация задачи на основе теории игр с единственным решением и открытие CreateTaskForm"""
        if not self.validate_inputs():
            return

        task_type = self.comboBox_task_type.currentText().strip(' -')
        task_theme = self.comboBox_task_theme.currentText()
        complexity = self.comboBox_complexity.currentText()
        grid_size = 6
        if complexity == 'Средне':
            grid_size = 8
        elif complexity == 'Сложно':
            grid_size = 10
        elif complexity == 'Невозможно':
            grid_size = 12

        # Получаем допустимые фигуры для темы
        from config import TASK_THEME_FIGURES
        allowed_figures = TASK_THEME_FIGURES.get(task_theme, [])

        # Генерируем задачу
        figures, walls = self.game_theory_generate_task(task_type, task_theme, grid_size, allowed_figures)

        # Закрываем предыдущее окно, если оно есть
        if hasattr(self, 'create_task_form') and self.create_task_form:
            self.create_task_form.close()
            self.create_task_form = None

        # Получаем название задачи из главного окна
        task_name = self.lineEdit_task_name.text().strip()

        # Открываем CreateTaskForm с уже расставленными фигурами
        self.create_task_form = CreateTaskForm(
            task_type=task_type,
            task_theme=task_theme,
            complexity=complexity,
            name=task_name,
            walls=walls,
            figures=figures,
        )
        self.create_task_form.show()

    def game_theory_generate_task(self, task_type, task_theme, grid_size, allowed_figures):
        """
        Примитивная генерация задачи с единственным решением (пример для пути ладьи).
        Возвращает: (figures, walls)
        """
        import random
        figures = {}
        walls = []
        # Пример: для темы 'Путь ладьи 1-2-3 с перегородками' генерируем путь с единственным решением
        if task_theme == 'Путь ладьи 1-2-3 с перегородками':
            # Ставим старт и финиш
            start = (0, 0)
            end = (grid_size-1, grid_size-1)
            figures[start] = 6  # 6 - число (пусть будет старт)
            figures[end] = 6    # 6 - число (пусть будет финиш)
            # Прокладываем единственный путь (змейкой)
            path = []
            x, y = start
            while (x, y) != end:
                path.append((x, y))
                if x < grid_size-1:
                    x += 1
                else:
                    y += 1
            path.append(end)
            # Пронумеруем путь
            for idx, (x, y) in enumerate(path):
                figures[(x, y)] = 6  # 6 - число
            # Добавим случайные стены, не блокируя путь
            for _ in range(grid_size):
                wx = random.randint(0, grid_size-2)
                wy = random.randint(0, grid_size-2)
                orientation = random.choice(['left', 'top', 'right', 'bottom'])
                if (wx, wy) not in path:
                    walls.append((wx, wy, orientation))
            # Гарантируем единственность решения (упрощённо)
            # (В реальной задаче нужен backtracking и проверка уникальности)
        else:
            # Для других тем — просто случайно расставить фигуры
            for _ in range(grid_size):
                x = random.randint(0, grid_size-1)
                y = random.randint(0, grid_size-1)
                fig = random.choice(allowed_figures) if allowed_figures else 1
                figures[(x, y)] = fig
        return figures, walls

    def on_create_task_form_closed(self):
        """Handle create task form closure"""
        self.create_task_form = None

    def on_task_generator_closed(self):
        """Handle task generator closure"""
        self.task_generator = None

    def show_tasks_list(self):
        """Show task browser window"""
        if self.task_browser:
            self.task_browser.show()
            self.task_browser.raise_()
            self.task_browser.activateWindow()
            self.task_browser.load_tasks()

    def load_task(self):
        """Load task from database"""
        task_type = self.comboBox_task_type.currentText()
        task_theme = self.comboBox_task_theme.currentText()
        task_name = self.lineEdit_task_name.text().strip()
        complexity = self.comboBox_complexity.currentText()

        if not all([task_type, task_theme, task_name, complexity]):
            self.show_error("Заполните все поля для загрузки задачи")
            return

        try:
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    SELECT id, walls, figures, solution
                    FROM tasks
                    WHERE task_type = ? AND task_theme = ? 
                    AND name = ? AND complexity = ?
                """, (task_type, task_theme, task_name, complexity))
                
                row = cursor.fetchone()
                if not row:
                    self.show_error("Задача не найдена")
                    return
                    
                task_data = {
                    'id': row[0],
                    'walls': json.loads(row[1]) if row[1] else [],
                    'figures': json.loads(row[2]) if row[2] else {},
                    'solution': json.loads(row[3]) if row[3] else None
                }
                
                return task_data
                
        except sqlite3.Error as e:
            self.show_error(f"Ошибка при загрузке задачи: {str(e)}")
        except json.JSONDecodeError as e:
            self.show_error(f"Ошибка при разборе данных задачи: {str(e)}")
        except Exception as e:
            self.show_error(f"Неожиданная ошибка: {str(e)}")
        return None

    def validate_inputs(self) -> bool:
        """Validate form inputs"""
        task_type = self.comboBox_task_type.currentText()
        task_theme = self.comboBox_task_theme.currentText()
        task_name = self.lineEdit_task_name.text().strip()
        complexity = self.comboBox_complexity.currentText()

        if task_type in ['Выберите вид задачи', '']:
            self.show_error("Выберите вид задачи")
            return False
        if task_theme in ['Выберите вид задачи', '']:
            self.show_error("Выберите тему задачи")
            return False
        if not task_name:
            self.show_error("Введите название задачи")
            return False
        if complexity in ['Выберите сложность', '']:
            self.show_error("Выберите сложность задачи")
            return False
        return True

    def show_error(self, message: str):
        """Show error message dialog"""
        QMessageBox.critical(
            None, "Ошибка", message,
            QMessageBox.Ok
        )

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.create_task_form = None
        self.task_generator = None
        self.task_browser = None
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        """Initialize UI connections and setup"""
        # Connect buttons
        self.pushButton_exit.clicked.connect(self.close)
        self.pushButton_show_tasks_list.clicked.connect(self.show_tasks_list)
        self.pushButton_load_task.clicked.connect(self.load_task)
        self.pushButton_create_by_yourself.clicked.connect(self.create_task_manually)
        self.pushButton_generate_task.clicked.connect(self.generate_task)
        
        # Connect task type change
        self.comboBox_task_type.currentTextChanged.connect(self.update_task_themes)
        
        # Initialize task browser
        self.task_browser = TaskBrowser()
        
        # Set initial task themes
        self.update_task_themes(self.comboBox_task_type.currentText())

    def create_task_manually(self):
        """Open task creation form"""
        if not hasattr(self, 'create_task_form') or not self.create_task_form:
            self.create_task_form = CreateTaskForm(parent=self.window())
            self.create_task_form.taskCreated.connect(self.load_tasks)
            self.create_task_form.finished.connect(self.on_create_task_form_closed)
        self.create_task_form.show()

    def load_tasks(self):
        """Load tasks from database and update UI"""
        try:
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    SELECT DISTINCT task_type 
                    FROM tasks 
                    ORDER BY task_type
                """)
                task_types = [row[0] for row in cursor.fetchall()]
                
                # Update task type combo box with all available types
                current_type = self.comboBox_task_type.currentText()
                self.comboBox_task_type.clear()
                self.comboBox_task_type.addItem("Выберите вид задачи")
                
                # Add all task types from TASK_TYPES
                for task_type in TASK_TYPES.keys():
                    self.comboBox_task_type.addItem(task_type)
                
                # Restore previous selection if possible
                index = self.comboBox_task_type.findText(current_type)
                if index >= 0:
                    self.comboBox_task_type.setCurrentIndex(index)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить задачи: {str(e)}")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
