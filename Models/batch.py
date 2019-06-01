from datetime import datetime


class Batch:

    def __init__(self, batch_id=None, size=None, created_at=None, is_checked=None, user_id=None):
        self._id = batch_id
        self._size = size
        self._created_at = created_at
        self._is_checked = is_checked
        self._user_id = user_id

    id = property()
    size = property()
    created_at = property()
    is_checked = property()
    user_id = property()
    iso_created_at = property()

    @size.getter
    def size(self):
        return self._size

    @created_at.getter
    def created_at(self):
        return self._created_at

    @is_checked.getter
    def is_checked(self):
        return self._is_checked

    @user_id.getter
    def user_id(self):
        return self._user_id

    @iso_created_at.getter
    def iso_created_at(self):
        return datetime.isoformat(self._created_at, sep='Z', timespec='milliseconds')

    @id.getter
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)
