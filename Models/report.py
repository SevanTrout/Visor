class Report:
    def __init__(self, report_id=None, result=None, batch_id=None, recommendations=None):
        self._id = report_id
        self._result = result
        self._batch_id = batch_id
        self._recommendations = recommendations

    id = property()
    result = property()
    batch_id = property()
    recommendations = property()

    @id.getter
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)

    @result.getter
    def result(self):
        return self._result

    @batch_id.getter
    def batch_id(self):
        return self._batch_id

    @recommendations.getter
    def recommendations(self):
        return self._recommendations
