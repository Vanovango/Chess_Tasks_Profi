from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoggingPage(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(501, 427)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(20, 10, 20, 10)
        self.verticalLayout_2.setSpacing(25)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_wind_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(18)
        self.label_wind_title.setFont(font)
        self.label_wind_title.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_wind_title.setObjectName("label_wind_title")
        self.verticalLayout_2.addWidget(self.label_wind_title)
        self.lineEdit_login = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(16)
        self.lineEdit_login.setFont(font)
        self.lineEdit_login.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(73, 168, 0);\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;")
        self.lineEdit_login.setText("")
        self.lineEdit_login.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_login.setObjectName("lineEdit_login")
        self.verticalLayout_2.addWidget(self.lineEdit_login)
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
"border: 1px solid white;")
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.lineEdit_password.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.verticalLayout_2.addWidget(self.lineEdit_password)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 40, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_registrate = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(12)
        self.pushButton_registrate.setFont(font)
        self.pushButton_registrate.setStyleSheet("QPushButton {\n"
"\n"
"color: rgb(255, 255, 255);\n"
"\n"
"padding: 8px;\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: rgb(4, 74, 0);\n"
"}")
        self.pushButton_registrate.setObjectName("pushButton_registrate")
        self.horizontalLayout_2.addWidget(self.pushButton_registrate)
        self.pushButton_enter = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(12)
        self.pushButton_enter.setFont(font)
        self.pushButton_enter.setStyleSheet("QPushButton {\n"
"\n"
"color: rgb(255, 255, 255);\n"
"\n"
"padding: 8px;\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: rgb(4, 74, 0);\n"
"}")
        self.pushButton_enter.setObjectName("pushButton_enter")
        self.horizontalLayout_2.addWidget(self.pushButton_enter)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_wind_title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Войдите или зарегистрируйтесь</p><p align=\"center\">в системе</p></body></html>"))
        self.lineEdit_login.setPlaceholderText(_translate("MainWindow", "Логин"))
        self.lineEdit_password.setPlaceholderText(_translate("MainWindow", "Пароль"))
        self.pushButton_registrate.setText(_translate("MainWindow", "Зарегистрироваться"))
        self.pushButton_enter.setText(_translate("MainWindow", "Войти"))

