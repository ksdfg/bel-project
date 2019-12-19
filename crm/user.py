from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, username, role):
        self.username = username
        self.role = role

    def get_id(self):
        return self.username

    def __repr__(self):
        return "%r" % [self.username, self.role]
