from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtSql

from Models.deviation import Deviation
from Models.standard import Standard


def get_recommendations(deviations=None):
    if deviations is None:
        return

    recommendations = set()

    for key, value in deviations.items():
        rules_query = QtSql.QSqlQuery()
        rules_query.prepare("SELECT deviation_id, recommendation_id FROM Rules WHERE standard_id = :standard_id")
        rules_query.bindValue(':standard_id', key)

        if rules_query.exec_():
            while rules_query.next():
                for deviation in value:
                    if deviation.id == rules_query.value('deviation_id') and deviation.value:
                        recommendations.add(rules_query.value('recommendation_id'))

    recommendations_query = QtSql.QSqlQuery()
    recommendations_query.exec_("""SELECT description FROM Recommendations WHERE id IN ({0})"""
                                .format(", ".join(map(str, recommendations))))

    recommendations_description = []
    while recommendations_query.next():
        recommendations_description.append(recommendations_query.value(0))

    print(list(recommendations_description))


class ReportCreator:

    def __init__(self, batch_id=None):
        self._batch_id = batch_id
        self.axarr = None

    def create_report(self):
        query = QtSql.QSqlQuery()

        result_dict = {}

        query.exec_("""SELECT * FROM Results WHERE batch_id = {0}""".format(self._batch_id))
        while query.next():
            if result_dict.get(query.value('standard_id')) is None:
                result_dict[query.value('standard_id')] = [query.value('value')]
            else:
                result_dict[query.value('standard_id')].append(query.value('value'))

        deviations_dict = {}

        deviation_query = QtSql.QSqlQuery()
        deviation_query.exec_("""SELECT * FROM Deviations""")
        while deviation_query.next():
            deviations_dict[deviation_query.value('id')] = deviation_query.value('name')

        deviations = {}

        for key in result_dict.keys():
            standard_query = QtSql.QSqlQuery()
            standard_query.exec_("""SELECT * FROM Standards WHERE id = {0}""".format(key))
            standard_query.first()
            current_min_value = standard_query.value(2)
            current_max_value = standard_query.value(3)
            current_average = round(mean([current_max_value, current_min_value]), 4)

            current_results = result_dict[key]

            state_list = list(map(lambda x: 1 if x > current_average else (-1 if x < current_average else 0),
                                  current_results))
            series_state_list = state_list[:]

            if len(current_results) > 1:
                for i in range(1, len(current_results)):
                    series_state_list[i] += series_state_list[i - 1] if series_state_list[i] == \
                                                                        series_state_list[i - 1] else 0

            has_upper_trend = False
            has_lower_trend = False
            upper_trend_index = 0
            lower_trend_index = 0
            trend_size = 4

            if len(current_results) >= trend_size:
                for i in range(0, len(current_results) - trend_size):
                    if len(set(state_list[i:i + trend_size])) > 1:
                        continue

                    zipped_arr = list(zip(current_results[i:i + trend_size], current_results[i + 1:i + trend_size]))
                    has_upper_trend = has_upper_trend or (state_list[0] == 1
                                                          and (all(map(lambda z: z[1] > z[0], zipped_arr))
                                                               or all(map(lambda z: z[1] < z[0], zipped_arr))))
                    has_lower_trend = has_lower_trend or (state_list[0] == -1
                                                          and (all(map(lambda z: z[1] > z[0], zipped_arr))
                                                               or all(map(lambda z: z[1] < z[0], zipped_arr))))

                    upper_trend_index = i if has_upper_trend and upper_trend_index == 0 else upper_trend_index
                    lower_trend_index = i if has_lower_trend and lower_trend_index == 0 else lower_trend_index

            upper_series_length = max(series_state_list)
            lower_series_length = abs(min(series_state_list))
            limit_excess_count = len(list(filter(lambda x: x > current_max_value or x < current_min_value,
                                                 current_results)))

            print('Standard number {0}'.format(key))

            print('Lower at {0}: {1}, Upper at {2}: {3}'.format(lower_trend_index,
                                                                has_lower_trend,
                                                                upper_trend_index,
                                                                has_upper_trend))

            print('Upper series length: {0}. Lower series length: {1}'.format(upper_series_length,
                                                                              lower_series_length))

            print("Limit excess count: {0}".format(limit_excess_count))

            deviations[key] = [
                Deviation(deviation_id=1, name=deviations_dict[1], value=limit_excess_count >= 5),
                Deviation(deviation_id=2, name=deviations_dict[2], value=upper_series_length > 5),
                Deviation(deviation_id=3, name=deviations_dict[3], value=lower_series_length > 5),
                Deviation(deviation_id=4, name=deviations_dict[4], value=has_upper_trend),
                Deviation(deviation_id=5, name=deviations_dict[5], value=has_lower_trend)
            ]

        get_recommendations(deviations)

        batch_query = QtSql.QSqlQuery()
        batch_query.exec_("""UPDATE Batches SET is_checked = TRUE WHERE id = {0}""".format(self._batch_id))

        self.draw_plots(result_dict)
        return True

    def draw_plots(self, result_dict):
        standards_query = QtSql.QSqlQuery()
        standards_query.exec_("""SELECT Standards.id, Standards.name, min_value, max_value, Units.short_name As unit 
                                 FROM Standards INNER JOIN Units on Standards.unit_id = Units.id 
                                 WHERE Standards.id in ({0})""".format(', '.join(map(str, result_dict.keys()))))

        standards_dict = {}
        while standards_query.next():
            standards_dict[standards_query.value('id')] = Standard(standard_id=standards_query.value('id'),
                                                                   name=standards_query.value('name'),
                                                                   min_value=standards_query.value('min_value'),
                                                                   max_value=standards_query.value('max_value'),
                                                                   unit=standards_query.value('unit'))

        plt.close('all')

        row_count = round(len(standards_dict) / 2)
        f, self.axarr = plt.subplots(row_count, 2, figsize=(30, 20))

        for key, results in result_dict.items():
            y_index = (key - 1) // 2
            x_index = (key - 1) % 2

            self.draw_plot(standards_dict.get(key), results, x_index, y_index)

        plt.savefig('Партия_{0}.png'.format(self._batch_id), bbox_inches='tight', pad_inches=0)
        plt.close('all')

    def draw_plot(self, standard=None, results=None, x_index=None, y_index=None):
        average_value = round(mean([standard.min_value, standard.max_value]), 4)

        results_length = len(results)
        func_range = np.array(range(1, results_length + 1))

        self.axarr[y_index, x_index].plot([1, results_length], [standard.min_value, standard.min_value], color='orange',
                                          linestyle='dashed')
        self.axarr[y_index, x_index].plot([1, results_length], [average_value, average_value], 'g--')
        self.axarr[y_index, x_index].plot([1, results_length], [standard.max_value, standard.max_value], color='orange',
                                          linestyle='dashed')
        self.axarr[y_index, x_index].plot(func_range, np.array(results), color='blue', linestyle='solid', marker='.')
        # self.axarr[y_index, x_index].axis([1, results_length, standard.min_value * 1.5, standard.max * 1.5])
        self.axarr[y_index, x_index].set_title(standard.name)
