from PyQt5 import QtWidgets, QtSql
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

from Models.user import User
from connection import create_connection
from views import PersonWidget


class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
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

        query = QtSql.QSqlQuery()
        query.exec_(
            "SELECT * FROM Users WHERE login = '{0}' AND password = '{1}'".format(login, password))

        if query.isActive():
            query.first()
            if query.isValid() and query.value('login') == login and query.value('password') == password:
                self.user = User(fullname=query.value('fullname'),
                                 login=query.value('login'),
                                 role_id=query.value('role_id'))
                self.accept()
            else:
                self.login.clear()
                self.password.clear()
                QtWidgets.QMessageBox.warning(self, 'Внимание!', 'Неверное имя пользователя или пароль!')
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка!', 'Произошла неизвестная ошибка, попробуйте снова')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, user=None):
        super(MainWindow, self).__init__(parent)
        self.user = user

        self.setWindowTitle("Visor. Сессия пользователя {0}".format(
            user.fullname if user is not None else 'Неизвестный пользователь'))

        bar = self.menuBar()
        conveyor = bar.addMenu("&Конвейер")
        if user.is_operator():
            settings = bar.addMenu("&Настройки")
        if user.is_admin():
            admin = bar.addMenu("&Администрирование")

        self.mdiarea = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdiarea)

        sub1 = QtWidgets.QMdiSubWindow()
        sub1.setWidget(PersonWidget())
        sub1.resize(800, 600)
        self.mdiarea.addSubWindow(sub1)
        sub1.show()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    if not create_connection():
        sys.exit(-1)

    login = Login()

    if login.exec_() == QtWidgets.QDialog.Accepted:
        w = MainWindow(user=login.user)
        w.show()
        sys.exit(app.exec_())
