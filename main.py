import datetime
from hashlib import md5
from random import gauss
from statistics import mean

from PyQt5 import QtWidgets, QtSql
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

from Models.batch import Batch
from Models.standard import Standard
from Models.user import User
from connection import create_connection
from views import StandardsTableWidget, CreateBatchDialog


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
        sub1.setWidget(StandardsTableWidget())
        sub1.resize(1024, 600)
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

            batch: Batch = Batch(user_id=self.user.id, size=size, created_at=datetime.datetime.utcnow(),
                                 is_checked=False)
            query = QtSql.QSqlQuery()
            query.prepare("""INSERT INTO Batches(size, user_id, created_at, is_checked)
                            VALUES(:size, :user_id, :created_at, :is_checked)""")
            query.bindValue(":size", batch.size)
            query.bindValue(":user_id", batch.user_id)
            query.bindValue(":created_at", batch.iso_created_at)
            query.bindValue(":is_checked", batch.is_checked)

            if not query.exec_():
                print("Error")

            query.exec_("""SELECT max(id) FROM Batches""")
            if query.isActive():
                query.first()
                batch.id = query.value(0)

            if query.exec_("""SELECT id, min_value, max_value, unit_id FROM Standards"""):
                while query.next():
                    standard = Standard(standard_id=query.value(0),
                                        min_value=query.value(1),
                                        max_value=query.value(2),
                                        unit_id=query.value(3))
                    for _ in range(batch.size):
                        result_query = QtSql.QSqlQuery()
                        result_query.prepare("""INSERT INTO Results(value, standard_id, batch_id, unit_id)
                                   VALUES(:value, :standard_id, :batch_id, :unit_id)""")

                        result_value = round(gauss(round(mean([standard.min_value, standard.max_value]), 4),
                                                   round(standard.max_value - standard.min_value, 4) / 4), 4)
                        result_query.bindValue(':value', result_value)
                        result_query.bindValue(':standard_id', standard.id)
                        result_query.bindValue(':batch_id', batch.id)
                        result_query.bindValue(':unit_id', standard.unit_id)

                        if not (result_query.exec_()):
                            QtWidgets.QMessageBox.warning(self, 'Ошибка!',
                                                          'Произошла неизвестная ошибка, попробуйте снова')

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
