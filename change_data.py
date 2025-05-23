from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChangeData(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog
        self.Dialog.setObjectName("Dialog")
        self.Dialog.resize(485, 489)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(20, 15, 20, 15)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_title = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label")
        self.verticalLayout.addWidget(self.label_title)
        self.label_full_name = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_full_name.setFont(font)
        self.label_full_name.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_full_name)
        self.lineEdit_full_name = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_full_name.setFont(font)
        self.lineEdit_full_name.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit_full_name)
        self.label_date_of_birth = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_date_of_birth.setFont(font)
        self.label_date_of_birth.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_date_of_birth)
        self.lineEdit_date_of_birth = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_date_of_birth.setFont(font)
        self.lineEdit_date_of_birth.setObjectName("lineEdit_2")
        self.verticalLayout.addWidget(self.lineEdit_date_of_birth)
        self.label_login = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_login.setFont(font)
        self.label_login.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_login)
        self.lineEdit_login = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_login.setFont(font)
        self.lineEdit_login.setObjectName("lineEdit_4")
        self.verticalLayout.addWidget(self.lineEdit_login)
        self.label_password = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_password.setFont(font)
        self.label_password.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_password)
        self.lineEdit_password = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setObjectName("lineEdit_3")
        self.verticalLayout.addWidget(self.lineEdit_password)
        self.label_pass = QtWidgets.QLabel(Dialog)
        self.label_pass.setText("")
        self.label_pass.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_pass)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(30)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_back = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_back.setFont(font)
        self.pushButton_back.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton_back)
        self.pushButton_save = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_save.setFont(font)
        self.pushButton_save.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_save)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.Dialog)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_title.setText(_translate("Dialog", "Редактирование"))
        self.label_full_name.setText(_translate("Dialog", "ФИО"))
        self.label_date_of_birth.setText(_translate("Dialog", "Дата рождения"))
        self.label_login.setText(_translate("Dialog", "Логин"))
        self.label_password.setText(_translate("Dialog", "Пароль"))
        self.pushButton_back.setText(_translate("Dialog", "Назад"))
        self.pushButton_save.setText(_translate("Dialog", "Сохранить"))

    def fill_areas(self, data):
        self.lineEdit_full_name.setText(data[1])
        self.lineEdit_date_of_birth.setText(data[2])
        self.lineEdit_login.setText(data[3])
        self.lineEdit_password.setText(data[4])

    def return_new_data(self):
        from root_main_page import UsersList

        users_list = UsersList
        users_list.new_data = {
            'full_name': self.lineEdit_full_name.text(),
            'date_of_birth': self.lineEdit_date_of_birth.text(),
            'login': self.lineEdit_login.text(),
            'password': self.lineEdit_password.text()
        }

        self.Dialog.close()

