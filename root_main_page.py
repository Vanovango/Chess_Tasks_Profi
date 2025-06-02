import sqlite3
import sys
import json
import ast

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout,
    QMessageBox, QWidget, QAbstractItemView
)

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt, pyqtSignal

from new_task_settings import Ui_NewTaskSettings
from change_data import Ui_ChangeData
from create_task import CreateTaskForm


class Ui_RootMainPage(QMainWindow):
    def __init__(self, app_reference=None):
        super().__init__()
        self.app = app_reference
        self.db = None

        self.new_task_settings = QtWidgets.QMainWindow()
        self.ui_new_task_settings = Ui_NewTaskSettings()
        self.ui_new_task_settings.setupUi(self.new_task_settings)

        self.current_widget = None
        self.content_layout = None

        self.table_title_font = QFont()
        self.table_title_font.setPointSize(14)
        self.table_title_font.setBold(True)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(621, 600)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.main_layout = QVBoxLayout(self.centralwidget)

        self.label_title = QtWidgets.QLabel()
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setText("<h2>Вы вошли как ROOT</h2>")
        self.main_layout.addWidget(self.label_title)

        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.main_layout.addWidget(self.content_container)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 621, 26))
        MainWindow.setMenuBar(self.menuBar)

        self.menu_tasks = QtWidgets.QMenu("Задачи", self.menuBar)
        self.menu_users = QtWidgets.QMenu("Участники", self.menuBar)
        self.menu_exit = QtWidgets.QMenu("Выход", self.menuBar)

        self.action_tasks_list = QtWidgets.QAction("Список задач", self)
        self.action_create_task = QtWidgets.QAction("Создать задачу", self)
        self.action_import_task = QtWidgets.QAction("Импорт", self)
        self.action_export_task = QtWidgets.QAction("Экспорт", self)

        self.action_users_list = QtWidgets.QAction("Список всех", self)
        self.action_create_user = QtWidgets.QAction("Новый пользователь", self)
        self.action_users_statistics = QtWidgets.QAction("Статистика", self)

        self.action_logout = QtWidgets.QAction("Выйти", self)
        self.action_close_app = QtWidgets.QAction("Закрыть приложение", self)

        self.menu_tasks.addActions([
            self.action_tasks_list,
            self.action_create_task,
            self.action_import_task,
            self.action_export_task
        ])
        self.menu_users.addActions([
            self.action_users_list,
            self.action_create_user,
            self.action_users_statistics
        ])
        self.menu_exit.addActions([
            self.action_logout,
            self.action_close_app
        ])

        self.menuBar.addMenu(self.menu_tasks)
        self.menuBar.addMenu(self.menu_users)
        self.menuBar.addMenu(self.menu_exit)

        self.functions()

    def functions(self):
        self.action_tasks_list.triggered.connect(self.show_tasks_list)
        self.action_create_task.triggered.connect(self.crate_task)
        self.action_import_task.triggered.connect(lambda: self.label_title.setText(""))
        self.action_export_task.triggered.connect(lambda: self.label_title.setText(""))

        self.action_users_list.triggered.connect(self.show_users_list)
        self.action_create_user.triggered.connect(lambda: self.app.open_registration_page(True))
        self.action_users_statistics.triggered.connect(lambda: self.label_title.setText(""))

        self.action_logout.triggered.connect(self.logout)
        self.action_close_app.triggered.connect(self.close_app)

        self.show_tasks_list()

    def set_content_widget(self, widget):
        if self.current_widget:
            self.content_layout.removeWidget(self.current_widget)
            self.current_widget.setParent(None)
        self.current_widget = widget
        self.content_layout.addWidget(widget)

    def show_tasks_list(self):
        self.label_title.setText("Список всех задач")
        self.label_title.setFont(self.table_title_font)

        table_widget = CreateTaskTable()
        table_widget.task_double_clicked.connect(self.edit_existing_task)
        self.set_content_widget(table_widget)

    def crate_task(self):
        self.new_task_settings.show()

        self.ui_new_task_settings.pushButton_back.clicked.connect(lambda: self.new_task_settings.close())
        self.ui_new_task_settings.pushButton_create.clicked.connect(lambda: self.open_create_form(
            None,
            self.ui_new_task_settings.lineEdit_theme.text(),
            self.ui_new_task_settings.lineEdit_name.text(),
            self.ui_new_task_settings.comboBox_complexity.currentText()
        ))

    def open_create_form(self, task_id, theme, name, complexity):
        self.new_task_settings.close()
        new_task_form = CreateTaskForm(task_id, theme, name, complexity)
        new_task_form.run()

    def edit_existing_task(self, task_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT theme, name, complexity, walls, figures FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            theme, name, complexity, walls_json, figures_json = row
            loaded_walls = json.loads(walls_json)
            loaded_figures = json.loads(figures_json)
            # Преобразуем ключи фигур из строк в кортежи
            fixed_figures = {}
            for key, value in loaded_figures.items():
                if isinstance(key, str):
                    fixed_figures[tuple(ast.literal_eval(key))] = value
                else:
                    fixed_figures[key] = value
            task_form = CreateTaskForm(task_id, theme, name, complexity)
            task_form.walls = {tuple(w): True for w in loaded_walls}
            task_form.figures = fixed_figures
            task_form.run()

    def show_users_list(self):
        self.label_title.setText("Список пользователей")
        self.label_title.setFont(self.table_title_font)

        table_widget = UsersListTable()
        self.set_content_widget(table_widget)

    def logout(self):
        if self.app:
            self.app.logout()

    @staticmethod
    def close_app():
        sys.exit()


class CreateTaskTable(QWidget):
    task_double_clicked = pyqtSignal(int)  # ID задачи

    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.table = QTableView()
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

        self.init_ui()

    def init_ui(self):
        self.update_table()
        layout = QVBoxLayout(self)
        self.table.setModel(self.model)
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        self.table.doubleClicked.connect(self.row_double_clicked)

    def update_table(self):
        self.model.clear()
        self.cursor.execute("SELECT id, theme, name, complexity FROM tasks")
        rows = self.cursor.fetchall()
        headers = ["ID", "Тема", "Название", "Сложность"]
        self.model.setHorizontalHeaderLabels(headers)
        for row in rows:
            items = [QStandardItem(str(cell)) for cell in row]
            self.model.appendRow(items)

    def row_double_clicked(self, index):
        row = index.row()
        task_id = int(self.model.item(row, 0).text())
        self.task_double_clicked.emit(task_id)


class UsersListTable(QWidget):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.table = QTableView()
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

        self.edit_dialog = QtWidgets.QDialog()
        self.ui_edit_dialog = Ui_ChangeData()
        self.ui_edit_dialog.setupUi(self.edit_dialog)

        self.init_ui()

    def init_ui(self):
        self.update_table()
        layout = QVBoxLayout(self)
        self.table.setModel(self.model)
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        self.table.doubleClicked.connect(self.edit_selected_row)

    def update_table(self):
        self.model.clear()
        self.cursor.execute("SELECT * FROM users_list")
        rows = self.cursor.fetchall()
        headers = ["ID", "ФИО", "Дата рождения", "Логин", "Пароль"]
        self.model.setHorizontalHeaderLabels(headers)
        for row in rows:
            items = [QStandardItem(str(cell)) for cell in row]
            self.model.appendRow(items)

    def edit_selected_row(self, index):
        row = index.row()
        data = [self.model.item(row, col).text() for col in range(self.model.columnCount())]

        self.ui_edit_dialog.fill_areas(data)
        self.edit_dialog.show()

        self.ui_edit_dialog.pushButton_back.clicked.connect(self.edit_dialog.close)
        self.ui_edit_dialog.pushButton_save.clicked.connect(lambda: self.save_new_data(data[0]))
        self.ui_edit_dialog.pushButton_delete.clicked.connect(lambda: self.del_user(data[0]))

    def save_new_data(self, id):
        self.cursor.execute(f"""
            UPDATE users_list SET
                full_name = ?,
                date_of_birth = ?,
                logging = ?,
                password = ?
            WHERE id = ?
        """, (
            self.ui_edit_dialog.lineEdit_full_name.text(),
            self.ui_edit_dialog.lineEdit_date_of_birth.text(),
            self.ui_edit_dialog.lineEdit_login.text(),
            self.ui_edit_dialog.lineEdit_password.text(),
            id
        ))
        self.connection.commit()
        self.edit_dialog.close()
        self.update_table()

    def del_user(self, id):
        self.cursor.execute("DELETE FROM users_list WHERE id = ?", (id,))
        self.connection.commit()
        self.edit_dialog.close()
        self.update_table()
