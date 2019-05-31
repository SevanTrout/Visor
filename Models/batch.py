class Batch:
    def __init__(self, size=None, created_at=None, is_checked=None, user_id=None):
        self._size = size
        self._created_at = created_at
        self._is_checked = is_checked
        self._user_id = user_id

    size = property()
    created_at = property()
    is_checked = property()
    user_id = property()

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
