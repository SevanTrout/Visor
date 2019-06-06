import dateutil
from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtGui import QFont

from Models.batch import Batch
from Models.standard import Standard


class ReportWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, batch_id=None):
        super(ReportWidget, self).__init__(parent)

        self._batch_id = batch_id

        self.batch = None
        batch_query = QtSql.QSqlQuery()
        batch_query.exec_('SELECT * FROM Batches WHERE id = {0}'.format(batch_id))
        if batch_query.first():
            self.batch = Batch(batch_id=batch_query.value(0),
                               created_at=dateutil.parser.parse(batch_query.value(1)),
                               size=batch_query.value(2),
                               is_checked=batch_query.value(3),
                               user_id=batch_query.value(4))

        self.lay = QtWidgets.QVBoxLayout(self)

        if not self.batch:
            return

        page_title = "Партия №{0} от {1} размером {2} деталей".format(self.batch.id,
                                                                      self.batch.created_at.strftime(
                                                                          "%d.%m.%Y %H:%M:%S"),
                                                                      self.batch.size)
        self.title = QtWidgets.QLabel(page_title, self)
        self.title.setFont(QFont("Times", 18, QFont.Bold))
        self.lay.addWidget(self.title, alignment=QtCore.Qt.AlignTop)

        self.subtitle = QtWidgets.QLabel("Показатели:")
        self.lay.addWidget(self.subtitle, alignment=QtCore.Qt.AlignTop)

        results_dict = {}
        results_query = QtSql.QSqlQuery()
        results_query.exec_("""SELECT value, standard_id
                               FROM Results
                               WHERE Results.batch_id = {0}""".format(self._batch_id))

        while results_query.next():
            if results_dict.get(results_query.value(1)):
                results_dict[results_query.value(1)].append(results_query.value(0))
            else:
                results_dict[results_query.value(1)] = [results_query.value(0)]

        standard_dict = {}
        standard_query = QtSql.QSqlQuery()
        standard_query.exec_("""SELECT Standards.id, Standards.name, min_value, max_value, Units.short_name AS unit_name 
                                FROM Standards INNER JOIN Units on Standards.unit_id = Units.id
                                WHERE Standards.id in ({0})""".format(', '.join(map(str, results_dict.keys()))))

        while standard_query.next():
            standard_dict[standard_query.value(0)] = Standard(standard_id=standard_query.value(0),
                                                              name=standard_query.value(1),
                                                              min_value=standard_query.value(2),
                                                              max_value=standard_query.value(3),
                                                              unit=standard_query.value(4))

        self.plot_buttons = []
        for stand_id in standard_dict.keys():
            h_lay = QtWidgets.QHBoxLayout(self)
            pattern = "{0}: {1} ({2})".format(standard_dict[stand_id].name,
                                              ' - '.join(map(str, results_dict[stand_id])),
                                              standard_dict[stand_id].unit)
            standard = QtWidgets.QLabel(pattern)
            h_lay.addWidget(standard, alignment=QtCore.Qt.AlignLeft)
            button = QtWidgets.QPushButton('-|-')
            button.setMaximumWidth(50)
            self.plot_buttons.append(button)
            button_index = self.plot_buttons.index(button)
            button.setObjectName(str(button_index))
            button.clicked.connect(self.draw_plot)
            h_lay.addWidget(button, QtCore.Qt.AlignRight)
            self.lay.addLayout(h_lay)

        self.lay.addStretch()

    def draw_plot(self):
        index = self.sender().objectName()
