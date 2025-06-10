from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
import sys
import os
import json

from config import UI_COLORS, TASK_TYPES, COMPLEXITY_SETTINGS
from task_generator import TaskGenerator
from create_task import CreateTaskForm
from task_browser import TaskBrowser

class Ui_MainWindow(object):
    def __init__(self, task_browser=None):
        self.task_browser = task_browser
        self.task_types = list(TASK_TYPES.keys())

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
        if task_type in TASK_TYPES:
            self.comboBox_task_theme.addItems(TASK_TYPES[task_type])
        else:
            self.comboBox_task_theme.addItem("Выберите вид задачи")

    def generate_task(self):
        """Generate a new task"""
        if not self.validate_inputs():
            return

        try:
            generator = TaskGenerator(
                self.comboBox_task_type.currentText(),
                self.comboBox_task_theme.currentText(),
                self.comboBox_complexity.currentText()
            )
            
            task = generator.generate_task()
            if not task or not generator.validate_task(task):
                self.show_error("Не удалось сгенерировать валидную задачу. Попробуйте еще раз.")
                return

            # Open task editor with generated task
            self.open_task_editor(task)
            
        except Exception as e:
            self.show_error(f"Ошибка при генерации задачи: {str(e)}")

    def create_task_manually(self):
        """Open task editor for manual creation"""
        if not self.validate_inputs():
            return

        task = {
            'task_type': self.comboBox_task_type.currentText(),
            'task_theme': self.comboBox_task_theme.currentText(),
            'name': self.lineEdit_task_name.text(),
            'complexity': self.comboBox_complexity.currentText(),
            'walls': [],
            'figures': {}
        }
        
        self.open_task_editor(task)

    def open_task_editor(self, task: dict):
        """Open the task editor window"""
        editor = CreateTaskForm(
            task_id=task.get('task_id'),
            task_type=task['task_type'],
            task_theme=task['task_theme'],
            name=task['name'],
            complexity=task['complexity'],
            walls=task.get('walls', []),
            figures=task.get('figures', {})
        )
        editor.show()

    def show_tasks_list(self):
        """Show the task browser window (single instance)"""
        if self.task_browser is not None:
            self.task_browser.show()
            self.task_browser.raise_()
            self.task_browser.activateWindow()
            self.task_browser.load_tasks()

    def load_task(self):
        """Load a task from file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Загрузить задачу",
            os.path.expanduser("~/Desktop"),
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                
                # Validate task data
                required_fields = ['task_type', 'task_theme', 'name', 'complexity']
                if not all(field in task_data for field in required_fields):
                    raise ValueError("Неверный формат файла задачи")
                
                # Open task editor with loaded task
                self.open_task_editor(task_data)
                
            except Exception as e:
                self.show_error(f"Ошибка при загрузке задачи: {str(e)}")

    def validate_inputs(self) -> bool:
        """Validate all input fields"""
        if self.comboBox_task_type.currentText() == "Выберите вид задачи":
            self.show_error("Выберите вид задачи")
            return False
        if self.comboBox_task_theme.currentText() == "Выберите вид задачи":
            self.show_error("Выберите тему задачи")
            return False
        if not self.lineEdit_task_name.text().strip():
            self.show_error("Введите название задачи")
            return False
        if self.comboBox_complexity.currentText() == "Выберите сложность":
            self.show_error("Выберите сложность задачи")
            return False
        return True

    def show_error(self, message: str):
        """Show error message dialog"""
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("Ошибка")
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {UI_COLORS['background']};
            }}
            QMessageBox QLabel {{
                color: {UI_COLORS['text']};
            }}
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
        """)
        msg.exec_()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
