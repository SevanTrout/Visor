from _md5 import md5

from PyQt5 import QtWidgets, QtSql
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

from Models.user import User


class LoginWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)
        self.user = None

        self.setWindowTitle("Авторизация")

        self.formGroupBox = QGroupBox()
        form_layout = QFormLayout()

        self.login = QtWidgets.QLineEdit(self)
        form_layout.addRow(QLabel("Имя пользователя:"), self.login)

        self.password = QtWidgets.QLineEdit(self)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(QLabel("Пароль:"), self.password)

        self.formGroupBox.setLayout(form_layout)

        self.buttonLogin = QtWidgets.QPushButton('Войти', self)
        self.buttonLogin.clicked.connect(self.handle_login)

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.buttonLogin)

        self.setLayout(main_layout)

    def handle_login(self):
        login = self.login.text()
        password = self.password.text()

        if login == '' or password == '':
            QtWidgets.QMessageBox.warning(
                self, 'Внимание!', 'Введите имя пользователя и пароль!')
            return

        password_hash = md5(password.encode()).hexdigest()
        query = QtSql.QSqlQuery()
        query.exec_(
            "SELECT * FROM Users WHERE login = '{0}' AND password_hash = '{1}'".format(login, password_hash))

        if query.isActive():
            query.first()
            if query.isValid():
                self.user = User(user_id=query.value('id'),
                                 fullname=query.value('fullname'),
                                 login=query.value('login'),
                                 role_id=query.value('role_id'))
                self.accept()
            else:
                self.login.clear()
                self.password.clear()
                QtWidgets.QMessageBox.warning(self, 'Внимание!', 'Неверное имя пользователя или пароль!')
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка!', 'Произошла неизвестная ошибка, попробуйте снова')