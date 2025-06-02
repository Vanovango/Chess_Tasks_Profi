import sys
from PyQt5 import QtWidgets


from loggin_page import Ui_LoggingPage
from root_main_page import Ui_RootMainPage
from user_main_page import Ui_UserMainPage
from registration_page import Ui_RegistrationPage

from verify_user import Verify
import init


class StartApp:
    # =========================== init main variables ===============================
    def __init__(self):
        init.init_db()

        self.verify = Verify()

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
        self.ui_root_main_page = Ui_RootMainPage(self)  # передаём ссылку на StartApp
        self.ui_root_main_page.setupUi(self.root_main_page)

        self.root_main_page.show()
        self.logging_page.close()

    def logout(self):
        self.logging_page.show()
        self.root_main_page.close()

    def open_user_main(self):
        self.user_main_page = QtWidgets.QMainWindow()
        self.ui_user_main_page = Ui_UserMainPage()
        self.ui_user_main_page.setupUi(self.user_main_page)

        self.user_main_page.show()
        self.logging_page.close()

    def open_registration_page(self, from_root=False):
        self.registration_page = QtWidgets.QMainWindow()
        self.ui_registration_page = Ui_RegistrationPage()
        self.ui_registration_page.setupUi(self.registration_page)

        self.logging_page.close()
        self.registration_page.show()

        if not from_root:
            self.ui_registration_page.pushButton_back.clicked.connect(
                lambda: (self.registration_page.close(), self.logging_page.show())
            )
            self.ui_registration_page.pushButton_registration.clicked.connect(
                lambda: self.registration_new_user(
                    self.ui_registration_page.lineEdit_full_name.text(),
                    self.ui_registration_page.lineEdit_date_of_birth.text(),
                    self.ui_registration_page.lineEdit_logging.text(),
                    self.ui_registration_page.lineEdit_password.text()
                ))
        else:
            self.ui_registration_page.pushButton_back.clicked.connect(
                lambda: self.registration_page.close()
            )
            self.ui_registration_page.pushButton_registration.clicked.connect(
                lambda: self.registration_new_user(
                    self.ui_registration_page.lineEdit_full_name.text(),
                    self.ui_registration_page.lineEdit_date_of_birth.text(),
                    self.ui_registration_page.lineEdit_logging.text(),
                    self.ui_registration_page.lineEdit_password.text(),
                    from_root
                ))

    # ======================= logically functions ===========================
    def entering_into_system(self, logging, password):
        if self.verify.check_user(logging, password) == 'admin_access':
            self.open_root_main()
        elif self.verify.check_user(logging, password):
            self.open_user_main()
        else:
            print('Пользователь не найден')

    def registration_new_user(self, full_name, date_of_birth, logging, password, from_root=False):
        user_data = {
            'full_name': full_name,
            'date_of_birth': date_of_birth,
            'logging': logging,
            'password': password
        }
        self.verify.add_new_user(user_data)

        self.registration_page.close()

        if not from_root:
            self.logging_page.show()

    #=========================== run app ===============================
    def run(self):
        app = QtWidgets.QApplication(sys.argv)

        self.open_logging_page()

        sys.exit(app.exec_())


if __name__ == "__main__":
    app = StartApp()
