from statistics import mean

from PyQt5 import QtSql


class ReportCreater:

    def __init__(self, batch_id=None):
        self._batch_id = batch_id

    def create_report(self):
        query = QtSql.QSqlQuery()

        result_dict = {}

        query.exec_("""SELECT * FROM Results WHERE batch_id = {0}""".format(self._batch_id))
        while query.next():
            if result_dict.get(query.value('standard_id')) is None:
                result_dict[query.value('standard_id')] = [query.value('value')]
            else:
                result_dict[query.value('standard_id')].append(query.value('value'))

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
