from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, username, role, auth_token):
        self.username = username
        self.role = role
        self.auth_token = auth_token

    def get_id(self):
        return self.username

    def __repr__(self):
        return "%r" % [self.username, self.role]
