from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QAbstractItemView, QGroupBox, QFormLayout, QLabel


class PersonWidget(QtWidgets.QWidget):
    selectedIndex = None

    def __init__(self, parent=None):
        super(PersonWidget, self).__init__(parent)
        self.lay = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableView()
        self.lay.addWidget(self.table)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable("Roles")
        self.model.select()
        self.table.setModel(self.model)

        add_row_button = QtWidgets.QPushButton('Добавить строку')
        add_row_button.clicked.connect(self.add_row)
        self.lay.addWidget(add_row_button)

        remove_row_button = QtWidgets.QPushButton('Удалить выбранные строки')
        remove_row_button.clicked.connect(self.remove_row)
        self.lay.addWidget(remove_row_button)

    def remove_row(self):
        selected_row_indexes = set(map(lambda item: item.row(), self.table.selectionModel().selectedIndexes()))
        for selected_row_index in selected_row_indexes:
            self.model.removeRow(selected_row_index)

        self.model.select()

    def add_row(self):
        record = self.model.record()

        names = [record.fieldName(i) for i in range(0, record.count()) if record.fieldName(i) != "id"]

        values, ok = AddRowDialog.get_row_data(names)

        for index, value in enumerate(values):
            record.setValue(index + 1, value)

        self.model.insertRecord(-1, record)
        self.model.select()


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
    def __init__(self, parent=None):
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
        self.createBatchButton.clicked.connect(self.accept)

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.createBatchButton)

        self.setLayout(main_layout)

    def get_size(self):
        return self.size.text()
