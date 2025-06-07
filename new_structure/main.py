import sys
from PyQt5 import QtWidgets

from main_window import Ui_MainWindow


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
        return True

    def create_task(self):
        print('open create task window')

    def start(self):
        self.main_window.show()

        # main window buttons actions
        self.ui_main_window.pushButton_exit.clicked.connect(lambda: sys.exit())
        self.ui_main_window.pushButton_create_by_yourself.clicked.connect(
            lambda: self.create_task() if self.is_information_full() else print('information not full'))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    program = Program()
    program.start()

    sys.exit(app.exec_())
