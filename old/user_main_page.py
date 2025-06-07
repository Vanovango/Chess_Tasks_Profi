from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
from datetime import datetime

from init import DB_PATH


class TaskSolver(QtWidgets.QDialog):
    def __init__(self, user_id, task_id, task_name):
        super().__init__()
        self.user_id = user_id
        self.task_id = task_id
        self.task_name = task_name
        self.path_cells = []  # Список клеток пути (например, ["A1", "B1", ...])
        self.setWindowTitle(f"Решение задачи: {task_name}")
        self.resize(400, 400)

        self.grid_size = 6  # Размер поля (например 6x6)
        self.cell_size = 50

        self.setMinimumSize(self.grid_size * self.cell_size + 20, self.grid_size * self.cell_size + 70)

        self.canvas = QtWidgets.QLabel()
        self.canvas.setFixedSize(self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid black;")
        self.canvas.mousePressEvent = self.on_canvas_click

        self.info_label = QtWidgets.QLabel("Кликните по клеткам для построения пути. Потом нажмите 'Сохранить'.")

        self.btn_save = QtWidgets.QPushButton("Сохранить решение")
        self.btn_save.clicked.connect(self.save_solution)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.info_label)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

        self.update_canvas()

    def update_canvas(self):
        pixmap = QtGui.QPixmap(self.canvas.size())
        pixmap.fill(QtCore.Qt.white)
        painter = QtGui.QPainter(pixmap)

        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)

        # Рисуем сетку
        for i in range(self.grid_size + 1):
            # Горизонтальные линии
            painter.drawLine(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size)
            # Вертикальные линии
            painter.drawLine(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size)

        # Рисуем линию пути, если есть
        if self.path_cells:
            pen = QtGui.QPen(QtCore.Qt.blue)
            pen.setWidth(4)
            painter.setPen(pen)

            points = []
            for cell in self.path_cells:
                col = ord(cell[0]) - ord('A')
                row = int(cell[1]) - 1
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                points.append(QtCore.QPoint(x, y))
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

        painter.end()
        self.canvas.setPixmap(pixmap)

    def on_canvas_click(self, event):
        x = event.pos().x()
        y = event.pos().y()
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= col < self.grid_size and 0 <= row < self.grid_size:
            cell = f"{chr(ord('A') + col)}{row + 1}"
            if cell not in self.path_cells:
                self.path_cells.append(cell)
            else:
                # Если кликнули на уже добавленную клетку - удалим её из пути
                self.path_cells.remove(cell)
            self.update_canvas()

    def save_solution(self):
        if len(self.path_cells) < 2:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Путь должен содержать минимум 2 клетки.")
            return
        path_str = '-'.join(self.path_cells)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_results (user_id, task_id, path, timestamp)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, self.task_id, path_str, timestamp))
            conn.commit()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить решение:\n{e}")
            return

        QtWidgets.QMessageBox.information(self, "Успех", f"Решение задачи '{self.task_name}' сохранено.")
        self.accept()  # Закрыть окно


class UserMainPage(object):
    def __init__(self):
        self.user_id = None

    def setupUi(self, MainWindow, user_id):
        self.user_id = user_id
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Заголовок
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setGeometry(QtCore.QRect(200, 20, 400, 40))
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setText("<h2>Добро пожаловать, пользователь</h2>")

        # Таблица задач
        self.table_tasks = QtWidgets.QTableWidget(self.centralwidget)
        self.table_tasks.setGeometry(QtCore.QRect(50, 80, 700, 300))
        self.table_tasks.setColumnCount(3)
        self.table_tasks.setHorizontalHeaderLabels(["ID", "Название", "Сложность"])
        self.table_tasks.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table_tasks.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_tasks.doubleClicked.connect(self.open_task_solver)

        # Кнопка личного кабинета
        self.button_account = QtWidgets.QPushButton("Личный кабинет", self.centralwidget)
        self.button_account.setGeometry(QtCore.QRect(50, 400, 150, 40))
        self.button_account.clicked.connect(self.open_account_window)

        MainWindow.setCentralWidget(self.centralwidget)

        self.load_tasks()

    def load_tasks(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, complexity FROM tasks")
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить задачи:\n{e}")
            return

        self.table_tasks.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(val))
                self.table_tasks.setItem(i, j, item)

    def open_task_solver(self):
        selected_row = self.table_tasks.currentRow()
        if selected_row < 0:
            return
        task_id = int(self.table_tasks.item(selected_row, 0).text())
        task_name = self.table_tasks.item(selected_row, 1).text()

        dialog = TaskSolver(self.user_id, task_id, task_name)
        dialog.exec_()

    def open_account_window(self):
        dialog = AccountDialog(self.user_id)
        dialog.exec_()


class AccountDialog(QtWidgets.QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Личный кабинет")
        self.resize(400, 350)

        self.layout = QtWidgets.QVBoxLayout()

        # Поля для данных пользователя
        self.input_full_name = QtWidgets.QLineEdit()
        self.input_date_of_birth = QtWidgets.QLineEdit()
        self.input_login = QtWidgets.QLineEdit()
        self.input_password = QtWidgets.QLineEdit()
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("ФИО:", self.input_full_name)
        form_layout.addRow("Дата рождения (ГГГГ-ММ-ДД):", self.input_date_of_birth)
        form_layout.addRow("Логин:", self.input_login)
        form_layout.addRow("Пароль:", self.input_password)

        self.layout.addLayout(form_layout)

        # Статистика
        self.label_tasks_done = QtWidgets.QLabel()
        self.label_last_task = QtWidgets.QLabel()
        self.layout.addWidget(self.label_tasks_done)
        self.layout.addWidget(self.label_last_task)

        # Кнопки
        self.btn_save = QtWidgets.QPushButton("Сохранить изменения")
        self.btn_save.clicked.connect(self.save_user_data)
        self.btn_close = QtWidgets.QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_close)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)

        self.load_user_data()

    def load_user_data(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, date_of_birth, logging, password FROM users_list WHERE id = ?", (self.user_id,))
            user_data = cursor.fetchone()

            cursor.execute("SELECT COUNT(*), MAX(timestamp) FROM task_results WHERE user_id = ?", (self.user_id,))
            stats = cursor.fetchone()

            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{e}")
            return

        if user_data:
            self.input_full_name.setText(user_data[0])
            self.input_date_of_birth.setText(user_data[1])
            self.input_login.setText(user_data[2])
            self.input_password.setText(user_data[3])

            self.label_tasks_done.setText(f"Решено задач: {stats[0]}")
            self.label_last_task.setText(f"Последнее решение: {stats[1] or 'Нет'}")

    def save_user_data(self):
        full_name = self.input_full_name.text().strip()
        dob = self.input_date_of_birth.text().strip()
        login = self.input_login.text().strip()
        password = self.input_password.text().strip()

        if not full_name or not dob or not login or not password:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users_list SET full_name = ?, date_of_birth = ?, logging = ?, password = ? WHERE id = ?
            """, (full_name, dob, login, password, self.user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные:\n{e}")
            return

        QtWidgets.QMessageBox.information(self, "Успех", "Данные сохранены.")


# Пример запуска:
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UserMainPage()
    ui.setupUi(MainWindow, user_id=1)  # здесь user_id должен быть реальным после логина
    MainWindow.show()
    sys.exit(app.exec_())
