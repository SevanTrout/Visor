from statistics import mean

import dateutil
import matplotlib.pyplot as plt
import numpy as np
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
        self.subtitle.setFont(QFont("Times", 12, QFont.Bold))
        self.lay.addWidget(self.subtitle, alignment=QtCore.Qt.AlignTop)

        self.results_dict = {}
        results_query = QtSql.QSqlQuery()
        results_query.exec_("""SELECT value, standard_id
                               FROM Results
                               WHERE Results.batch_id = {0}""".format(self._batch_id))

        while results_query.next():
            if self.results_dict.get(results_query.value(1)):
                self.results_dict[results_query.value(1)].append(results_query.value(0))
            else:
                self.results_dict[results_query.value(1)] = [results_query.value(0)]

        self.standard_dict = {}
        standard_query = QtSql.QSqlQuery()
        standard_query.exec_("""SELECT Standards.id, Standards.name, min_value, max_value, Units.short_name AS unit_name 
                                FROM Standards INNER JOIN Units on Standards.unit_id = Units.id
                                WHERE Standards.id in ({0})""".format(', '.join(map(str, self.results_dict.keys()))))

        while standard_query.next():
            self.standard_dict[standard_query.value(0)] = Standard(standard_id=standard_query.value(0),
                                                                   name=standard_query.value(1),
                                                                   min_value=standard_query.value(2),
                                                                   max_value=standard_query.value(3),
                                                                   unit=standard_query.value(4))

        self.plot_buttons = []
        for stand_id in self.standard_dict.keys():
            h_lay = QtWidgets.QHBoxLayout(self)

            pattern = "{0}: {1} ({2})".format(self.standard_dict[stand_id].name,
                                              ' - '.join(map(str, self.results_dict[stand_id])),
                                              self.standard_dict[stand_id].unit)
            recommendation = QtWidgets.QLabel(pattern)
            h_lay.addWidget(recommendation, alignment=QtCore.Qt.AlignLeft)

            button = QtWidgets.QPushButton('-|-')
            button.setMaximumWidth(50)
            self.plot_buttons.append(button)
            button_index = self.plot_buttons.index(button)
            button.setObjectName(str(button_index))
            button.clicked.connect(self.draw_plot)
            h_lay.addWidget(button, QtCore.Qt.AlignRight)

            self.lay.addLayout(h_lay)

        report_query = QtSql.QSqlQuery()
        report_query.exec_("""SELECT id, result FROM Reports WHERE batch_id = {0}""".format(self._batch_id))

        report_query.first()
        if report_query.value(1) == '1':
            self.recommendations_title = QtWidgets.QLabel("Рекомендации:")
            self.recommendations_title.setFont(QFont("Times", 12, QFont.Bold))

            self.lay.addWidget(self.recommendations_title, alignment=QtCore.Qt.AlignTop)

            rec_query = QtSql.QSqlQuery()
            rec_query.exec_("""SELECT description 
                               FROM ReportsToRecommendations RTR
                               INNER JOIN Recommendations R on RTR.recommendation_id = R.id
                               WHERE RTR.report_id = {0}""".format(report_query.value(0)))

            while rec_query.next():
                pattern = "{0}".format(rec_query.value(0))
                recommendation = QtWidgets.QLabel(pattern)
                self.lay.addWidget(recommendation, alignment=QtCore.Qt.AlignLeft)

        self.lay.addStretch()

    def draw_plot(self):
        index = int(self.sender().objectName())
        standard = self.standard_dict[index + 1]
        results = self.results_dict[index + 1]

        average_value = round(mean([standard.min_value, standard.max_value]), 4)

        results_length = len(results)
        func_range = np.array(range(1, results_length + 1))

        fig, ax = plt.subplots()

        ax.plot([1, results_length], [standard.min_value, standard.min_value], color='orange',
                linestyle='dashed')
        ax.plot([1, results_length], [average_value, average_value], 'g--')
        ax.plot([1, results_length], [standard.max_value, standard.max_value], color='orange',
                linestyle='dashed')
        ax.plot(func_range, np.array(results), color='blue', linestyle='solid', marker='.')
        ax.set_title(standard.name)
        ax.grid()

        plt.show()
