import datetime
from hashlib import md5

from PyQt5 import QtWidgets, QtSql
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

from Models.batch import Batch
from Models.user import User
from connection import create_connection
from views import PersonWidget, CreateBatchDialog


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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, user=None):
        super(MainWindow, self).__init__(parent)
        self.user = user

        self.setWindowTitle("Visor. Сессия пользователя {0}".format(
            user.fullname if user is not None else 'Неизвестный пользователь'))

        bar = self.menuBar()
        conveyor = bar.addMenu("&Конвейер")
        create_batch_action = conveyor.addAction("&Создать партию")
        create_batch_action.triggered.connect(self.create_batch)

        load_data_action = conveyor.addAction("&Загрузить данные")
        load_data_action.triggered.connect(self.load_data)

        if user.is_operator():
            settings = bar.addMenu("&Настройки")

        if user.is_admin():
            admin = bar.addMenu("&Администрирование")

            create_user_action = admin.addAction("&Добавить пользователя")
            create_user_action.triggered.connect(self.create_user)

        self.mdiarea = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdiarea)

        sub1 = QtWidgets.QMdiSubWindow()
        sub1.setWidget(PersonWidget())
        sub1.resize(800, 600)
        self.mdiarea.addSubWindow(sub1)
        sub1.show()

    def create_batch(self):
        create_batch_dialog = CreateBatchDialog()
        if create_batch_dialog.exec_():
            try:
                size = int(create_batch_dialog.get_size())

                if size < 1 or size > 80:
                    raise ValueError()

            except ValueError:
                QtWidgets.QMessageBox.warning(self, 'Внимание!',
                                              'Указано недопустимое значение параметра "Рамер партии"!')

            batch = Batch(user_id=self.user.id, size=size, created_at=datetime.datetime.utcnow(), is_checked=False)
            query = QtSql.QSqlQuery()
            query_body = """INSERT INTO Batches(size, user_id, created_at, is_checked) 
                            VALUES({batch.size}, {batch.user_id}, '{batch.iso_created_at}', {batch.is_checked})"""\
                .format(batch=batch)

            query.exec_(query_body)

            if not (query.isActive()):
                print("Error")

    def create_user(self):
        print("User")

    def load_data(self):
        print("Load")


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    if not create_connection():
        sys.exit(-1)

    login_window = Login()

    if login_window.exec_() == QtWidgets.QDialog.Accepted:
        w = MainWindow(user=login_window.user)
        w.show()
        sys.exit(app.exec_())
