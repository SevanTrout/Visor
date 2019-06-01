class Standart:
    def __init__(self, standart_id=None, name=None, min_value=None, max_value=None, unit_id=None):
        self._id = standart_id
        self._name = name
        self._min_value = min_value
        self._max_value = max_value
        self._unit_id = unit_id

    id = property()
    name = property()
    min_value = property()
    max_value = property()
    unit_id = property()

    @id.getter
    def id(self):
        return self._id

    @name.getter
    def name(self):
        return self._name

    @min_value.getter
    def min_value(self):
        return self._min_value

    @max_value.getter
    def max_value(self):
        return self._max_value

    @unit_id.getter
    def unit_id(self):
        return self._unit_id
