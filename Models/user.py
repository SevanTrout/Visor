class User:
    def __init__(self, user_id=None, fullname=None, login=None, role_id=None):
        self._id = user_id
        self._fullname = fullname
        self._login = login
        self._role_id = role_id

    id = property()
    fullname = property()
    login = property()
    role_id = property()

    @id.getter
    def id(self):
        return self._id

    @fullname.getter
    def fullname(self):
        return self._fullname

    @login.getter
    def login(self):
        return self._login

    @role_id.getter
    def role_id(self):
        return self._role_id

    def is_admin(self):
        return self._role_id in [1]

    def is_operator(self):
        return self._role_id in [1, 2]
