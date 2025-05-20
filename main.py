import sys
from PyQt5 import QtCore, QtGui, QtWidgets


from loggin_page import Ui_LoggingPage
from root_main_page import Ui_RootMainPage
from user_main_page import Ui_UserMainPage
from registration_page import Ui_RegistrationPage


class StartApp:
    # =========================== init main variables ===============================
    def __init__(self):
        self.logging_page = None
        self.ui_logging_page = None

        self.root_main_page = None
        self.ui_root_main_page = None

        self.user_main_page = None
        self.ui_user_main_page = None

        self.registration_page = None
        self.ui_registration_page = None

        self.run()

    # ======================= open windows ===========================
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
        self.ui_logging_page.pushButton_registrate.clicked.connect(self.open_registration_page)

    def open_root_main(self):
        self.root_main_page = QtWidgets.QMainWindow()
        self.ui_root_main_page = Ui_RootMainPage()
        self.ui_root_main_page.setupUi(self.root_main_page)

        self.root_main_page.show()

    def open_user_main(self):
        self.user_main_page = QtWidgets.QMainWindow()
        self.ui_user_main_page = Ui_UserMainPage()
        self.ui_user_main_page.setupUi(self.user_main_page)

        self.user_main_page.show()

    def open_registration_page(self):
        self.registration_page = QtWidgets.QMainWindow()
        self.ui_registration_page = Ui_RegistrationPage()
        self.ui_registration_page.setupUi(self.registration_page)

        self.logging_page.close()
        self.registration_page.show()

        self.ui_registration_page.pushButton_back.clicked.connect(
            lambda: (self.registration_page.close(), self.logging_page.show())
        )
        self.ui_registration_page.pushButton_registration.clicked.connect(
            lambda: self.registration_new_user(
                self.ui_registration_page.lineEdit_logging.text(),
                self.ui_registration_page.lineEdit_password.text()
            ))

    # ======================= logically functions ===========================
    def entering_into_system(self, logging, password):
        print(f"logging - {logging} \npassword - {password}")

        if any(logging == i for i in ['root', 'admin']):
            self.open_root_main()
        elif any(logging == i for i in ['user', 'Ivan']):
            self.open_user_main()
        else:
            print('Пользователь не найден')

    def registration_new_user(self, logging, password):
        print(f"logging - {logging}\npassword - {password}")

    #=========================== run app ===============================
    def run(self):
        app = QtWidgets.QApplication(sys.argv)

        self.open_logging_page()

        sys.exit(app.exec_())

if __name__ == "__main__":
    app = StartApp()

