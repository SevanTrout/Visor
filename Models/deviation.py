class Deviation:

    def __init__(self, deviation_id=None, name=None, value=None):
        self._id = deviation_id
        self._name = name
        self._value = value

    id = property()
    name = property()
    value = property()

    @id.getter
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)

    @name.getter
    def name(self):
        return self._name

    @value.getter
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
