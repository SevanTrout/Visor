import datetime
from _md5 import md5

import dateutil.parser
from PyQt5 import QtWidgets, QtSql, QtCore, QtGui
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QAbstractItemView, QGroupBox, QFormLayout, QLabel, \
    QHeaderView

from Models.batch import Batch
from Models.user import User
from report_creator import ReportCreator


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
        self.batch = None

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

        self.batch: Batch = Batch(user_id=self.user.id, size=size, created_at=datetime.datetime.utcnow(),
                                  is_checked=False)
        query = QtSql.QSqlQuery()
        query.prepare("""INSERT INTO Batches(size, user_id, created_at, is_checked)
                            VALUES(:size, :user_id, :created_at, :is_checked)""")
        query.bindValue(":size", self.batch.size)
        query.bindValue(":user_id", self.batch.user_id)
        query.bindValue(":created_at", self.batch.iso_created_at)
        query.bindValue(":is_checked", self.batch.is_checked)

        if not query.exec_():
            print("Error")

        query.exec_("""SELECT max(id) FROM Batches""")
        if query.isActive():
            query.first()
            self.batch.id = query.value(0)

        self.accept()

    def get_batch(self):
        return self.batch


class BatchesListWidget(QtWidgets.QListView):
    show_report_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, progress_bar=None, is_admin=None):

        self._progress_bar = progress_bar
        self._is_admin = is_admin

        self.selected_checked_item = None
        self.selected_item_index = None

        super(BatchesListWidget, self).__init__(parent)

        self.lay = QtWidgets.QVBoxLayout(self)
        self.list = QtWidgets.QListView()
        self.lay.addWidget(self.list)

        self.action_button = QtWidgets.QPushButton('(Выберете партию, чтобы увидеть возможные действия)', self)
        self.action_button.clicked.connect(self.button_action)
        self.lay.addWidget(self.action_button)

        self.update_button = QtWidgets.QPushButton('Обновить данные', self)
        self.update_button.clicked.connect(self.get_batch_list)
        self.lay.addWidget(self.update_button)

        if self._is_admin:
            self.delete_button = QtWidgets.QPushButton('Удалить выбранную партию', self)
            self.delete_button.clicked.connect(self.delete_batch)
            self.lay.addWidget(self.delete_button)

        self.model = QtGui.QStandardItemModel(self.list)
        self.list.clicked.connect(self.item_clicked)

        self.batches = []

        self.get_batch_list()

    def button_action(self):

        if self.selected_item_index is None:
            return

        batch_id = self.batches[self.selected_item_index].id
        if not self.selected_checked_item:
            reporter = ReportCreator(batch_id=batch_id, progress_bar=self._progress_bar)
            if reporter.create_report():
                self.get_batch_list()

            self.list.clearSelection()
            self.action_button.setText('(Выберете партию, чтобы увидеть возможные действия)')
        else:
            self.show_report_signal.emit(batch_id)

    def get_batch_list(self):
        batches_query = QtSql.QSqlQuery()
        self.batches = []

        self.model.clear()

        if batches_query.exec_("""SELECT * FROM Batches"""):
            while batches_query.next():
                self.batches.append(Batch(batch_id=batches_query.value(0),
                                          created_at=dateutil.parser.parse(batches_query.value(1)),
                                          size=batches_query.value(2),
                                          is_checked=batches_query.value(3),
                                          user_id=batches_query.value(4)))

        for batch in self.batches:
            batch_name = "Партия от {0} размером {1} патронов".format(batch.iso_created_at, batch.size)
            item = QStandardItem(batch_name)

            item.setCheckState(batch.is_checked)

            self.model.appendRow(item)

            self.list.update()

        self.list.setModel(self.model)

    def delete_batch(self):
        if self.selected_item_index is None:
            return

        delete_batch_query = QtSql.QSqlQuery()
        delete_batch_query.prepare("""DELETE FROM Batches WHERE id = :id""")
        delete_batch_query.bindValue(":id", self.batches[self.selected_item_index].id)
        if delete_batch_query.exec_():
            self.get_batch_list()

    def item_clicked(self, item):
        self.selected_item_index = item.row()
        self.selected_checked_item = self.model.item(self.selected_item_index, 0).checkState() == 1

        self.action_button.setText('Показать отчёт' if self.selected_checked_item else 'Создать отчёт')
