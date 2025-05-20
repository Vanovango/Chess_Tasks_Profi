import sys
from PyQt5 import QtCore, QtGui, QtWidgets


from loggin_page import Ui_LoggingPage


class StartApp:
    def __init__(self):
        self.logging_page = None
        self.ui_logging_page = None

        self.run()


    def open_logging_page(self):
        # open logging window
        self.logging_page = QtWidgets.QMainWindow()
        self.ui_logging_page = Ui_LoggingPage()
        self.ui_logging_page.setupUi(self.logging_page)

        self.logging_page.show()

        self.ui_logging_page.pushButton_enter.clicked.connect(lambda: self.entering_into_system(
            self.ui_logging_page.lineEdit_login.text(),
            self.ui_logging_page.lineEdit_password.text())
        )

    def entering_into_system(self, logging, enter_pass):
        print(f"logging - {logging} \npassword - {enter_pass}")

    def run(self):
        app = QtWidgets.QApplication(sys.argv)

        self.open_logging_page()

        sys.exit(app.exec_())

if __name__ == "__main__":
    app = StartApp()

