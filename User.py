from werkzeug.security import generate_password_hash


class SimpleUser:
    def __init__(self, name='', login='', passwd=''):
        self.name = name
        self.login = login
        self.password = passwd

    def hashed_pass(self):
        return generate_password_hash(self.password)

    def have_valid_data(self):
        return (self.name != '') and (self.login != '') and (self.password != '')
