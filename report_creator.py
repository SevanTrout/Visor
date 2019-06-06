from statistics import mean

from PyQt5 import QtSql
from PyQt5.QtWidgets import QProgressBar

from Models.deviation import Deviation
from Models.report import Report


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

    return list(recommendations)


class ReportCreator:

    def __init__(self, batch_id=None, progress_bar=None):
        self._batch_id = batch_id
        self._progress_bar: QProgressBar = progress_bar
        self.axarr = None

    def create_report(self):
        self._progress_bar.reset()
        query = QtSql.QSqlQuery()

        result_dict = {}

        query.exec_("""SELECT * FROM Results WHERE batch_id = {0}""".format(self._batch_id))
        while query.next():
            if result_dict.get(query.value('standard_id')) is None:
                result_dict[query.value('standard_id')] = [query.value('value')]
            else:
                result_dict[query.value('standard_id')].append(query.value('value'))
        self._progress_bar.setValue(10)

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

            deviations[key] = [
                Deviation(deviation_id=1, name=deviations_dict[1], value=limit_excess_count >= 5),
                Deviation(deviation_id=2, name=deviations_dict[2], value=upper_series_length > 5),
                Deviation(deviation_id=3, name=deviations_dict[3], value=lower_series_length > 5),
                Deviation(deviation_id=4, name=deviations_dict[4], value=has_upper_trend),
                Deviation(deviation_id=5, name=deviations_dict[5], value=has_lower_trend)
            ]

        self._progress_bar.setValue(75)

        recommendations = get_recommendations(deviations)

        self.create_report_db(recommendations)
        self._progress_bar.setValue(95)

        batch_query = QtSql.QSqlQuery()
        batch_query.exec_("""UPDATE Batches SET is_checked = TRUE WHERE id = {0}""".format(self._batch_id))

        self._progress_bar.reset()
        return True

    def create_report_db(self, recommendations=None):
        report = Report(result=len(recommendations) == 0, batch_id=self._batch_id)

        report_query = QtSql.QSqlQuery()
        report_query.prepare("INSERT INTO Reports(result, batch_id) VALUES (:result, :batch_id)")
        report_query.bindValue(":result", report.result)
        report_query.bindValue(":batch_id", report.batch_id)

        if report_query.exec_():
            report_query.clear()

            report_query.prepare("SELECT last_insert_rowid() FROM Reports")
            if report_query.exec_():
                report_query.first()
                report.id = report_query.value(0)

        if report.id:
            recommendations_query = QtSql.QSqlQuery()
            pairs = []
            for recommendation in recommendations:
                pairs.append("({0}, {1})".format(recommendation, report.id))

            recommendations_query.exec_("""INSERT INTO ReportsToRecommendations(recommendation_id, report_id) 
                                           VALUES {0}""".format(", ".join(pairs)))
        return
