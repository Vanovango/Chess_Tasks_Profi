import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QDialog, QVBoxLayout,
    QLineEdit, QPushButton, QMessageBox, QAbstractItemView
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QStandardItemModel, QStandardItem


class Ui_RootMainPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(621, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setGeometry(QtCore.QRect(130, 40, 331, 281))
        self.label_title.setObjectName("label_title")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 621, 26))
        self.menuBar.setObjectName("menuBar")
        self.menu_tasks = QtWidgets.QMenu(self.menuBar)
        self.menu_tasks.setObjectName("menu_tasks")
        self.menu_users = QtWidgets.QMenu(self.menuBar)
        self.menu_users.setObjectName("menu_users")
        MainWindow.setMenuBar(self.menuBar)
        self.action_tasks_list = QtWidgets.QAction(MainWindow)
        self.action_tasks_list.setObjectName("action_tasks_list")
        self.action_create_task = QtWidgets.QAction(MainWindow)
        self.action_create_task.setObjectName("action_create_task")
        self.action_import_task = QtWidgets.QAction(MainWindow)
        self.action_import_task.setObjectName("action_import_task")
        self.action_export_task = QtWidgets.QAction(MainWindow)
        self.action_export_task.setObjectName("action_export_task")
        self.action_users_list = QtWidgets.QAction(MainWindow)
        self.action_users_list.setObjectName("action_users_list")
        self.action_create_user = QtWidgets.QAction(MainWindow)
        self.action_create_user.setObjectName("action_create_user")
        self.action_users_statistics = QtWidgets.QAction(MainWindow)
        self.action_users_statistics.setObjectName("action_users_statistics")
        self.menu_tasks.addAction(self.action_tasks_list)
        self.menu_tasks.addAction(self.action_create_task)
        self.menu_tasks.addSeparator()
        self.menu_tasks.addAction(self.action_import_task)
        self.menu_tasks.addAction(self.action_export_task)
        self.menu_users.addAction(self.action_users_list)
        self.menu_users.addAction(self.action_create_user)
        self.menu_users.addSeparator()
        self.menu_users.addAction(self.action_users_statistics)
        self.menuBar.addAction(self.menu_tasks.menuAction())
        self.menuBar.addAction(self.menu_users.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.functions()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:24pt;\">Вы</span></p><p align=\"center\"><span style=\" font-size:24pt;\">вошли как</span></p><p align=\"center\"><span style=\" font-size:24pt;\">ROOT</span></p></body></html>"))
        self.menu_tasks.setTitle(_translate("MainWindow", "Задачи"))
        self.menu_users.setTitle(_translate("MainWindow", "Участники"))
        self.action_tasks_list.setText(_translate("MainWindow", "Список задач"))
        self.action_create_task.setText(_translate("MainWindow", "Создать задачу"))
        self.action_import_task.setText(_translate("MainWindow", "Импорт"))
        self.action_export_task.setText(_translate("MainWindow", "Экспорт"))
        self.action_users_list.setText(_translate("MainWindow", "Список всех"))
        self.action_create_user.setText(_translate("MainWindow", "Новый пользователь"))
        self.action_users_statistics.setText(_translate("MainWindow", "Статистика"))


    def functions(self):
        # сразу показываем список задач
        self.show_tasks_list()

        # вкладка с параметрами задач
        self.action_tasks_list.triggered.connect(self.show_tasks_list)
        self.action_create_task.triggered.connect(self.crate_task)
        self.action_import_task.triggered.connect(self.import_task)
        self.action_export_task.triggered.connect(self.export_task)

        # вкладка с параметрами пользователей
        self.action_users_list.triggered.connect(self.show_users_list)
        self.action_create_user.triggered.connect(self.create_user)
        self.action_users_statistics.triggered.connect(self.show_statistics)

    # ===================== action triggers functions =========================
    # tasks menu bar
    def show_tasks_list(self):
        self.label_title.setText('show_tasks_list')

    def crate_task(self):
        self.label_title.setText('crate_task')

    def import_task(self):
        self.label_title.setText('import_task')

    def export_task(self):
        self.label_title.setText('export_task')

    # tasks menu bar
    def show_users_list(self):
        UsersList(self.centralwidget)

    def create_user(self):
        self.label_title.setText('create_user')

    def show_statistics(self):
        self.label_title.setText('show_statistics')

    #====================== special functions ==========================


class UsersList(QMainWindow):
    def __init__(self, centralwidget):
        super().__init__()

        self.new_data = None

        self.centralwidget = centralwidget

        self.connection = sqlite3.connect('database.db')
        self.cursor =  self.connection.cursor()

        self.init_ui()

    def init_ui(self):
        self.cursor.execute("SELECT * FROM users_list")
        rows = self.cursor.fetchall()
        print(rows)

        self.model = QStandardItemModel()
        # Установка заголовков
        headers = ["ID", "ФИО", "Дата рождения", "Логин", "Пароль"]
        self.model.setHorizontalHeaderLabels(headers)

        # Заполнение модели
        for row in rows:
            items = [QStandardItem(str(cell)) for cell in row]
            self.model.appendRow(items)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.doubleClicked.connect(lambda index: self.edit_selected_row(index))

        # Устанавливаем layout на centralwidget
        layout = QtWidgets.QVBoxLayout(self.centralwidget)
        layout.addWidget(self.table)
        self.centralwidget.setLayout(layout)

    def edit_selected_row(self, index):
        from change_data import Ui_ChangeData

        row = index.row()
        data = []
        for column in range(self.model.columnCount()):
            item = self.model.item(row, column)
            data.append(item.text())

        # открываем окно редактирования по конкретной строке
        edit_dialog = QtWidgets.QDialog()
        ui_edit_dialog = Ui_ChangeData()
        ui_edit_dialog.setupUi(edit_dialog)

        ui_edit_dialog.fill_areas(data)
        edit_dialog.show()

        def return_new_data(id):
            self.new_data = {
                'id': id,
                'full_name': ui_edit_dialog.lineEdit_full_name.text(),
                'date_of_birth': ui_edit_dialog.lineEdit_date_of_birth.text(),
                'logging': ui_edit_dialog.lineEdit_login.text(),
                'password': ui_edit_dialog.lineEdit_password.text()
            }
            self.save_new_data()
            edit_dialog.close()


        def close():
            edit_dialog.close()

        ui_edit_dialog.pushButton_back.clicked.connect(lambda: close())
        ui_edit_dialog.pushButton_save.clicked.connect(lambda: return_new_data(data[0]))

    def save_new_data(self):
        self.cursor.execute(f"""
            UPDATE users_list
            SET full_name = '{self.new_data['full_name']}',
                date_of_birth = '{self.new_data['date_of_birth']}',
                logging = '{self.new_data['logging']}',
                password = '{self.new_data['password']}'
            WHERE id = {self.new_data['id']};
        """)
        self.connection.commit()
        self.update_table()

    def update_table(self):
        new_data = list(i for i in self.new_data.values())
        print(new_data)

        for column, value in enumerate(new_data[1:]):
            item = QStandardItem(str(value))
            self.model.setItem(int(new_data[0]) - 1, column + 1, item)
