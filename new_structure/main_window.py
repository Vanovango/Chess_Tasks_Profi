from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(15, 15, 15, 15)
        self.gridLayout.setSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox_task_type = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBox_task_type.setFont(font)
        self.comboBox_task_type.setStyleSheet("padding: 5px;")
        self.comboBox_task_type.setObjectName("comboBox_task_type")
        self.comboBox_task_type.addItem("")
        self.comboBox_task_type.addItem("")
        self.comboBox_task_type.addItem("")
        self.gridLayout.addWidget(self.comboBox_task_type, 3, 0, 1, 2)
        self.comboBox_task_theme = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBox_task_theme.setFont(font)
        self.comboBox_task_theme.setStyleSheet("padding: 5px;")
        self.comboBox_task_theme.setObjectName("comboBox_task_theme")
        self.gridLayout.addWidget(self.comboBox_task_theme, 4, 0, 1, 2)
        self.lineEdit_task_name = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_task_name.setFont(font)
        self.lineEdit_task_name.setStyleSheet("padding: 5px;")
        self.lineEdit_task_name.setObjectName("lineEdit_task_name")
        self.gridLayout.addWidget(self.lineEdit_task_name, 5, 0, 1, 2)
        self.comboBox_complexity = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBox_complexity.setFont(font)
        self.comboBox_complexity.setStyleSheet("padding: 5px;")
        self.comboBox_complexity.setObjectName("comboBox_complexity")
        self.comboBox_complexity.addItem("")
        self.comboBox_complexity.addItem("")
        self.comboBox_complexity.addItem("")
        self.comboBox_complexity.addItem("")
        self.comboBox_complexity.addItem("")
        self.gridLayout.addWidget(self.comboBox_complexity, 6, 0, 1, 2)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setLineWidth(0)
        self.line_2.setMidLineWidth(2)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 7, 0, 1, 2)
        self.pushButton_generate_task = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_generate_task.setFont(font)
        self.pushButton_generate_task.setStyleSheet("padding: 5px;")
        self.pushButton_generate_task.setObjectName("pushButton_generate_task")
        self.gridLayout.addWidget(self.pushButton_generate_task, 8, 0, 1, 1)
        self.pushButton_create_by_yourself = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_create_by_yourself.setFont(font)
        self.pushButton_create_by_yourself.setStyleSheet("padding: 5px;")
        self.pushButton_create_by_yourself.setObjectName("pushButton_create_by_yourself")
        self.gridLayout.addWidget(self.pushButton_create_by_yourself, 8, 1, 1, 1)
        self.pushButton_show_tasks_list = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_show_tasks_list.setFont(font)
        self.pushButton_show_tasks_list.setStyleSheet("padding: 5px;")
        self.pushButton_show_tasks_list.setObjectName("pushButton_show_tasks_list")
        self.gridLayout.addWidget(self.pushButton_show_tasks_list, 9, 0, 1, 1)
        self.pushButton_load_task = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_load_task.setFont(font)
        self.pushButton_load_task.setStyleSheet("padding: 5px;")
        self.pushButton_load_task.setObjectName("pushButton_load_task")
        self.gridLayout.addWidget(self.pushButton_load_task, 9, 1, 1, 1)
        self.pushButton_exit = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_exit.setFont(font)
        self.pushButton_exit.setStyleSheet("padding: 5px;")
        self.pushButton_exit.setObjectName("pushButton_exit")
        self.gridLayout.addWidget(self.pushButton_exit, 10, 0, 1, 2)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setLineWidth(0)
        self.line.setMidLineWidth(2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 2)
        self.label_title_settings = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_title_settings.setFont(font)
        self.label_title_settings.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title_settings.setObjectName("label_title_settings")
        self.gridLayout.addWidget(self.label_title_settings, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.functions()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.comboBox_task_type.setItemText(0, _translate("MainWindow", "Вид задачи"))
        self.comboBox_task_type.setItemText(1, _translate("MainWindow", " - Замкнутые"))
        self.comboBox_task_type.setItemText(2, _translate("MainWindow", " - Незамкнутые"))
        self.lineEdit_task_name.setPlaceholderText(_translate("MainWindow", "Название задачи (ваше обозначение)"))
        self.comboBox_complexity.setItemText(0, _translate("MainWindow", "Сложность задачи"))
        self.comboBox_complexity.setItemText(1, _translate("MainWindow", "Легко"))
        self.comboBox_complexity.setItemText(2, _translate("MainWindow", "Средне"))
        self.comboBox_complexity.setItemText(3, _translate("MainWindow", "Сложно"))
        self.comboBox_complexity.setItemText(4, _translate("MainWindow", "Невозможно"))
        self.pushButton_generate_task.setText(_translate("MainWindow", "Сгенерировать задачу"))
        self.pushButton_create_by_yourself.setText(_translate("MainWindow", "Сделать задачу самостоятельно"))
        self.pushButton_show_tasks_list.setText(_translate("MainWindow", "Посмотреть готовые задачи"))
        self.pushButton_load_task.setText(_translate("MainWindow", "Загрузить задачу"))
        self.pushButton_exit.setText(_translate("MainWindow", "Выход"))
        self.label_title.setText(_translate("MainWindow", "Генератор задач для обучения хашматам"))
        self.label_title_settings.setText(_translate("MainWindow", "Параметры новой задачи"))

    def functions(self):
        self.comboBox_task_type.currentTextChanged.connect(self.update_task_themes)
        self.update_task_themes(self.comboBox_task_type.currentText())

    def update_task_themes(self, current_task_type):
        self.comboBox_task_theme.clear()

        if current_task_type == " - Замкнутые":
            self.comboBox_task_theme.addItems([
                "Цикл с пустыми и закрашенными точками",
                "Цикл с закрашенными точками",
                "Замкнутый путь с перегородками",
                "Путь ладьи 1-2-3 с перегородками",
                "Несколько замкнутых циклов"
            ])
        elif current_task_type == " - Незамкнутые":
            self.comboBox_task_theme.addItems([
                "Выход для ладьи",
                "Маршрут к базе для 2 ладей",
                "Проведи ладью в правильном порядке",
                "Путь ладьи по коридорам",
                "Маршрут через клетки",
                "Простой математический лабиринт",
                "Кольцевой маршрут максимальной длины"
            ])
        else:
            self.comboBox_task_theme.addItem("Вид задачи не выбран")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
