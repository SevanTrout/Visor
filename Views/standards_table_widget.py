from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView


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