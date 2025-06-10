import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from main_window import Ui_MainWindow
from create_task import CreateTaskForm
from task_browser import TaskBrowser
from task_generator import TaskGenerator
from config import init_db, DB_PATH, TASK_TYPES

class Program:
    def __init__(self):
        # Initialize database
        self.conn, self.cursor = init_db()
        
        # Create main window
        self.main_window = QtWidgets.QMainWindow()
        self.task_browser = TaskBrowser()  # Create one instance
        self.ui_main_window = Ui_MainWindow(task_browser=self.task_browser)  # Pass it to UI
        self.ui_main_window.setupUi(self.main_window)
        
        # Initialize task generator with default values
        self.task_generator = None  # Will be initialized when needed
        
        # Connect signals
        self.setup_connections()

    def setup_connections(self):
        """Setup all signal connections"""
        # Main window buttons
        self.ui_main_window.pushButton_exit.clicked.connect(self.exit_application)
        self.ui_main_window.pushButton_create_by_yourself.clicked.connect(self.open_create_task_form)
        self.ui_main_window.pushButton_generate_task.clicked.connect(self.show_generate_task)
        self.ui_main_window.pushButton_show_tasks_list.clicked.connect(self.show_tasks_list)
        self.ui_main_window.pushButton_load_task.clicked.connect(self.load_task)
        
        # Task type change
        self.ui_main_window.comboBox_task_type.currentTextChanged.connect(self.update_task_themes)

    def update_task_themes(self, task_type: str):
        """Update available themes based on selected task type"""
        self.ui_main_window.comboBox_task_theme.clear()
        if task_type in TASK_TYPES:
            self.ui_main_window.comboBox_task_theme.addItems(TASK_TYPES[task_type])

    def is_information_full(self) -> bool:
        """Check if all required task information is provided"""
        if self.ui_main_window.comboBox_task_type.currentText() == 'Вид задачи':
            return False
        if self.ui_main_window.comboBox_task_theme.currentText() == 'Вид задачи не выбран':
            return False
        if not self.ui_main_window.lineEdit_task_name.text().strip():
            return False
        if self.ui_main_window.comboBox_complexity.currentText() == 'Сложность задачи':
            return False
        return True

    def show_error(self, message: str):
        """Show error message dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Ошибка")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def open_create_task_form(self):
        """Open the task creation form"""
        if not self.is_information_full():
            self.show_error("Не все поля ввода информации заполнены")
            return
            
        task_type = self.ui_main_window.comboBox_task_type.currentText()
        task_theme = self.ui_main_window.comboBox_task_theme.currentText()
        task_name = self.ui_main_window.lineEdit_task_name.text().strip()
        complexity = self.ui_main_window.comboBox_complexity.currentText()
        
        self.create_task_form = CreateTaskForm(
            task_type=task_type,
            task_theme=task_theme,
            name=task_name,
            complexity=complexity
        )
        self.create_task_form.show()

    def show_generate_task(self):
        """Show task generator with current settings"""
        task_type = self.ui_main_window.comboBox_task_type.currentText()
        task_theme = self.ui_main_window.comboBox_task_theme.currentText()
        complexity = self.ui_main_window.comboBox_complexity.currentText()
        
        # Check for default/empty values
        if task_type in ['Вид задачи', ''] or task_theme in ['Вид задачи не выбран', ''] or complexity in ['Сложность задачи', '']:
            QMessageBox.warning(self.main_window, "Предупреждение", 
                               "Выберите тип задачи, тему и сложность")
            return
            
        self.task_generator = TaskGenerator(
            task_type=task_type,
            task_theme=task_theme,
            complexity=complexity
        )
        self.task_generator.show()

    def show_tasks_list(self):
        """Show the task browser window (single instance)"""
        if not hasattr(self, 'task_browser') or self.task_browser is None:
            self.task_browser = TaskBrowser()
        self.task_browser.show()
        self.task_browser.raise_()
        self.task_browser.activateWindow()
        self.task_browser.load_tasks()

    def load_task(self):
        """Load an existing task"""
        if not self.is_information_full():
            self.show_error("Не все поля ввода информации заполнены")
            return
            
        # TODO: Implement task loading from database
        pass

    def exit_application(self):
        """Safely exit the application"""
        try:
            self.conn.close()
        except:
            pass
        sys.exit()

    def start(self):
        """Start the application"""
        self.main_window.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and start program
    program = Program()
    program.start()
    
    sys.exit(app.exec_())
