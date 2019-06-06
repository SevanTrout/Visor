import dateutil
from PyQt5 import QtSql, QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QStandardItem

from Models.batch import Batch
from report_creator import ReportCreator


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

        self.action_button = QtWidgets.QPushButton('(Выберите партию, чтобы увидеть возможные действия)', self)
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
            self.action_button.setText('(Выберите партию, чтобы увидеть возможные действия)')
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
