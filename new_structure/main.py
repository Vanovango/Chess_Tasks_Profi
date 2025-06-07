import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from main_window import Ui_MainWindow
from create_task


class Program:
    def __init__(self):
        self.main_window = QtWidgets.QMainWindow()
        self.ui_main_window = Ui_MainWindow()
        self.ui_main_window.setupUi(self.main_window)

    def is_information_full(self):
        if self.ui_main_window.comboBox_task_type.currentText() == 'Вид задачи':
            return False
        if self.ui_main_window.comboBox_task_theme.currentText() == 'Вид задачи не выбран':
            return False
        if self.ui_main_window.lineEdit_task_name.text() == '':
            return False
        if self.ui_main_window.comboBox_complexity.currentText() == 'Сложность задачи':
            return False
        return True

    @staticmethod
    def info_not_full_error():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Ошибка ввода")
        msg.setText("Не все поля ввода информации заполнены")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def open_create_task_form(self):
        print('open create task window')

    def start(self):
        self.main_window.show()

        # main window buttons actions
        self.ui_main_window.pushButton_exit.clicked.connect(lambda: sys.exit())
        self.ui_main_window.pushButton_create_by_yourself.clicked.connect(
            lambda: self.open_create_task_form() if self.is_information_full() else self.info_not_full_error())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    program = Program()
    program.start()

    sys.exit(app.exec_())
