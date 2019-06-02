class Result:

    def __init__(self, value=None, standard_id=None, batch_id=None, unit_id=None):
        self._value = value
        self._standard_id = standard_id
        self._batch_id = batch_id
        self._unit_id = unit_id

    value = property()
    standard_id = property()
    batch_id = property()
    unit_id = property()

    @value.getter
    def value(self):
        return self._value

    @standard_id.getter
    def standard_id(self):
        return self._standard_id

    @batch_id.getter
    def batch_id(self):
        return self._batch_id

    @unit_id.getter
    def unit_id(self):
        return self._unit_id
