from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RegistrationPage(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 590)
        MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(30, 20, 30, 20)
        self.verticalLayout.setSpacing(25)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(20)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("color: rgb(255, 255, 255);\n"
                                       "")
        self.label_title.setObjectName("label_title")
        self.verticalLayout.addWidget(self.label_title)
        self.lineEdit_logging = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(16)
        self.lineEdit_logging.setFont(font)
        self.lineEdit_logging.setStyleSheet("color: rgb(255, 255, 255);\n"
                                            "background-color: rgb(73, 168, 0);\n"
                                            "\n"
                                            "border-color: rgb(255, 255, 255);\n"
                                            "border-radius: 10px;\n"
                                            "border: 1px solid white;\n"
                                            "\n"
                                            "padding: 10px;")
        self.lineEdit_logging.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_logging.setObjectName("lineEdit_logging")
        self.verticalLayout.addWidget(self.lineEdit_logging)
        self.lineEdit_password = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(16)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setStyleSheet("color: rgb(255, 255, 255);\n"
                                             "background-color: rgb(73, 168, 0);\n"
                                             "\n"
                                             "border-color: rgb(255, 255, 255);\n"
                                             "border-radius: 10px;\n"
                                             "border: 1px solid white;\n"
                                             "\n"
                                             "padding: 10px;")
        self.lineEdit_password.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.verticalLayout.addWidget(self.lineEdit_password)
        self.pushButton_reset = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(12)
        self.pushButton_reset.setFont(font)
        self.pushButton_reset.setStyleSheet("QPushButton {\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "\n"
                                            "padding: 5px;\n"
                                            "\n"
                                            "border-color: rgb(255, 255, 255);\n"
                                            "border-radius: 10px;\n"
                                            "border: 1px solid white;\n"
                                            "\n"
                                            "\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:hover {\n"
                                            "background-color: rgb(4, 74, 0);\n"
                                            "}")
        self.pushButton_reset.setObjectName("pushButton_reset")
        self.verticalLayout.addWidget(self.pushButton_reset)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout.setSpacing(50)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_back = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight")
        font.setPointSize(14)
        self.pushButton_back.setFont(font)
        self.pushButton_back.setStyleSheet("QPushButton {\n"
                                           "color: rgb(255, 255, 255);\n"
                                           "\n"
                                           "padding: 10px;\n"
                                           "\n"
                                           "border-color: rgb(255, 255, 255);\n"
                                           "border-radius: 15px;\n"
                                           "border: 1px solid white;\n"
                                           "\n"
                                           "}\n"
                                           "\n"
                                           "QPushButton:hover {\n"
                                           "background-color: rgb(4, 74, 0);\n"
                                           "}")
        self.pushButton_back.setObjectName("pushButton_back")
        self.horizontalLayout.addWidget(self.pushButton_back)
        self.pushButton_registration = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight")
        font.setPointSize(14)
        self.pushButton_registration.setFont(font)
        self.pushButton_registration.setStyleSheet("QPushButton {\n"
                                                   "color: rgb(255, 255, 255);\n"
                                                   "\n"
                                                   "padding: 10px;\n"
                                                   "\n"
                                                   "border-color: rgb(255, 255, 255);\n"
                                                   "border-radius: 15px;\n"
                                                   "border: 1px solid white;\n"
                                                   "\n"
                                                   "}\n"
                                                   "\n"
                                                   "QPushButton:hover {\n"
                                                   "background-color: rgb(4, 74, 0);\n"
                                                   "}")
        self.pushButton_registration.setObjectName("pushButton_registration")
        self.horizontalLayout.addWidget(self.pushButton_registration)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.functions()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_title.setText(_translate("MainWindow",
                                            "<html><head/><body><p align=\"center\">Регистрация</p><p align=\"center\">нового пользователя</p></body></html>"))
        self.lineEdit_logging.setPlaceholderText(_translate("MainWindow", "Введите логин"))
        self.lineEdit_password.setPlaceholderText(_translate("MainWindow", "Введите пароль"))
        self.pushButton_reset.setText(_translate("MainWindow", "Сброс"))
        self.pushButton_back.setText(_translate("MainWindow", "Назад"))
        self.pushButton_registration.setText(_translate("MainWindow", "Регистрация"))

    def functions(self):
        self.pushButton_reset.clicked.connect(self.reset)

    def reset(self):
        self.lineEdit_logging.setText('')
        self.lineEdit_password.setText('')
