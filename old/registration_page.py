
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RegistrationPage(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(610, 647)
        MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(15, 15, 15, 15)
        self.gridLayout.setHorizontalSpacing(15)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(20)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("color: rgb(255, 255, 255);\n"
"")
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 3)
        self.label_passwword = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.label_passwword.setFont(font)
        self.label_passwword.setStyleSheet("color: rgb(255, 255, 255);\n"
"")
        self.label_passwword.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_passwword.setObjectName("label_passwword")
        self.gridLayout.addWidget(self.label_passwword, 4, 0, 1, 1)
        self.label_logging = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.label_logging.setFont(font)
        self.label_logging.setStyleSheet("color: rgb(255, 255, 255);\n"
"")
        self.label_logging.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_logging.setObjectName("label_logging")
        self.gridLayout.addWidget(self.label_logging, 3, 0, 1, 1)
        self.lineEdit_logging = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.lineEdit_logging.setFont(font)
        self.lineEdit_logging.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lineEdit_logging.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(73, 168, 0);\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;\n"
"\n"
"padding: 10px;")
        self.lineEdit_logging.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_logging.setPlaceholderText("")
        self.lineEdit_logging.setObjectName("lineEdit_logging")
        self.gridLayout.addWidget(self.lineEdit_logging, 3, 1, 1, 1)
        self.lineEdit_date_of_birth = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.lineEdit_date_of_birth.setFont(font)
        self.lineEdit_date_of_birth.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lineEdit_date_of_birth.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(73, 168, 0);\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;\n"
"\n"
"padding: 10px;")
        self.lineEdit_date_of_birth.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_date_of_birth.setPlaceholderText("")
        self.lineEdit_date_of_birth.setObjectName("lineEdit_date_of_birth")
        self.gridLayout.addWidget(self.lineEdit_date_of_birth, 2, 1, 1, 1)
        self.label_date_of_birth = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.label_date_of_birth.setFont(font)
        self.label_date_of_birth.setStyleSheet("color: rgb(255, 255, 255);\n"
"")
        self.label_date_of_birth.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_date_of_birth.setObjectName("label_date_of_birth")
        self.gridLayout.addWidget(self.label_date_of_birth, 2, 0, 1, 1)
        self.label_full_name = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.label_full_name.setFont(font)
        self.label_full_name.setStyleSheet("color: rgb(255, 255, 255);\n"
"")
        self.label_full_name.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_full_name.setObjectName("label_full_name")
        self.gridLayout.addWidget(self.label_full_name, 1, 0, 1, 1)
        self.lineEdit_full_name = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.lineEdit_full_name.setFont(font)
        self.lineEdit_full_name.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lineEdit_full_name.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(73, 168, 0);\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;\n"
"\n"
"padding: 10px;")
        self.lineEdit_full_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_full_name.setPlaceholderText("")
        self.lineEdit_full_name.setObjectName("lineEdit_full_name")
        self.gridLayout.addWidget(self.lineEdit_full_name, 1, 1, 1, 1)
        self.lineEdit_password = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lineEdit_password.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(73, 168, 0);\n"
"\n"
"border-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"border: 1px solid white;\n"
"\n"
"padding: 10px;")
        self.lineEdit_password.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_password.setPlaceholderText("")
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout.addWidget(self.lineEdit_password, 4, 1, 1, 1)
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
        self.gridLayout.addWidget(self.pushButton_reset, 8, 0, 1, 3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(30)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_back = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight")
        font.setPointSize(14)
        self.pushButton_back.setFont(font)
        self.pushButton_back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
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
        self.pushButton_registration.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
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
        self.gridLayout.addLayout(self.horizontalLayout, 11, 0, 1, 3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.functions()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Регистрация</p><p align=\"center\">нового пользователя</p></body></html>"))
        self.label_passwword.setText(_translate("MainWindow", "Пароль"))
        self.label_logging.setText(_translate("MainWindow", "Логин"))
        self.label_date_of_birth.setText(_translate("MainWindow", "Дата рождения"))
        self.label_full_name.setText(_translate("MainWindow", "ФИО"))
        self.pushButton_reset.setText(_translate("MainWindow", "Сброс"))
        self.pushButton_back.setText(_translate("MainWindow", "Назад"))
        self.pushButton_registration.setText(_translate("MainWindow", "Регистрация"))

    def functions(self):
            self.pushButton_reset.clicked.connect(self.reset_text_lines)

    def reset_text_lines(self):
        self.lineEdit_full_name.setText('')
        self.lineEdit_date_of_birth.setText('')
        self.lineEdit_logging.setText('')
        self.lineEdit_password.setText('')


