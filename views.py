from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QAbstractItemView


class PersonWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PersonWidget, self).__init__(parent)
        self.lay = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableView()
        self.lay.addWidget(self.table)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable("person")
        self.model.select()
        self.table.setModel(self.model)

        self.selectedIndex = None

        add_row_button = QtWidgets.QPushButton('Добавить строку')
        add_row_button.clicked.connect(self.add_row)
        self.lay.addWidget(add_row_button)

        remove_row_button = QtWidgets.QPushButton('Удалить выбранные строки')
        remove_row_button.clicked.connect(self.remove_row)
        self.lay.addWidget(remove_row_button)

    def remove_row(self):
        selection = self.table.selectionModel().selectedIndexes()

        if len(selection) > 0:
            for selected_row in selection:
                self.model.removeRow(selected_row.row())

            self.model.select()

    def add_row(self):
        names = []
        record = self.model.record()
        for i in range(0, record.count()):
            name = record.fieldName(i)
            if name != "id":
                names.append(name)

        values, ok = Dialog.get_row_data(names)

        for index, value in enumerate(values):
            record.setValue(index + 1, value)

        self.model.insertRecord(-1, record)
        self.model.select()

class ItemsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ItemsWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)
        view = QtWidgets.QTableView()
        lay.addWidget(view)
        model = QtSql.QSqlTableModel(self)
        model.setTable("items")
        model.select()
        view.setModel(model)


class NewTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NewTableWidget, self).__init__(parent)
        self.lay = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(5)
        self.lay.addWidget(self.table)

        add_column_button = QtWidgets.QPushButton('Добавить столбец')
        add_column_button.clicked.connect(self.add_column)
        self.lay.addWidget(add_column_button)

        remove_column_button = QtWidgets.QPushButton('Удалить столбец')
        remove_column_button.clicked.connect(self.remove_column)
        self.lay.addWidget(remove_column_button)

    def add_column(self):
        self.table.setColumnCount(self.table.columnCount() + 1)

    def remove_column(self):
        self.table.setColumnCount(max(self.table.columnCount() - 1, 0))


class Dialog(QtWidgets.QDialog):

    def __init__(self, names, parent=None):
        super(Dialog, self).__init__(parent)

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
        dialog = Dialog(names, parent)
        result = dialog.exec_()
        return list(map(lambda line: line.text(), dialog.lines)), result == QtWidgets.QDialog.Accepted
