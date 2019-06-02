import datetime
from _md5 import md5
from random import gauss
from statistics import mean

from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QAbstractItemView, QGroupBox, QFormLayout, QLabel, \
    QHeaderView

from Models.batch import Batch
from Models.standard import Standard
from Models.user import User


class StandardsTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(StandardsTableWidget, self).__init__(parent)
        self.lay = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableView()
        self.lay.addWidget(self.table)

        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable("Standards")
        self.model.setRelation(4, QtSql.QSqlRelation('Units', 'id', 'short_name'))

        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Название")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Нижний предел допуска")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Верхний предел допуска")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Единица измерения")

        self.model.select()

        self.table.setModel(self.model)
        self.table.setItemDelegateForColumn(4, QtSql.QSqlRelationalDelegate(self.table))
        self.table.hideColumn(0)

        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


class AddRowDialog(QtWidgets.QDialog):

    def __init__(self, names, parent=None):
        super(AddRowDialog, self).__init__(parent)

        self.names = names
        self.resize(300, 200)

        self.layout = QVBoxLayout(self)

        self.lines = []
        for name in names:
            label = QtWidgets.QLabel("{0}".format(name))
            line = QtWidgets.QLineEdit()
            self.lines.append(line)
            self.layout.addWidget(label)
            self.layout.addWidget(line)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @staticmethod
    def get_row_data(names, parent=None):
        dialog = AddRowDialog(names, parent)
        result = dialog.exec_()
        return list(map(lambda line: line.text(), dialog.lines)), result == QtWidgets.QDialog.Accepted


class CreateBatchDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, user=None):
        self.user = user

        super(CreateBatchDialog, self).__init__(parent)

        self.resize(600, 400)

        self.setWindowTitle("Создание партии")

        self.formGroupBox = QGroupBox()
        form_layout = QFormLayout()

        self.size = QtWidgets.QSpinBox(self)
        self.size.setRange(1, 80)
        self.size.setValue(80)
        form_layout.addRow(QLabel("Размер партии:"), self.size)

        self.formGroupBox.setLayout(form_layout)

        self.createBatchButton = QtWidgets.QPushButton('Создать', self)
        self.createBatchButton.clicked.connect(self.create_batch)

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.createBatchButton)

        self.setLayout(main_layout)

    def create_batch(self):

        try:
            size = int(self.size.text())

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

        self.accept()


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
