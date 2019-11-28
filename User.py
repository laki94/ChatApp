class SimpleUser:
    def __init__(self, us_id=0, login='', name='', passwd=''):
        self.us_id = us_id
        self.name = name
        self.login = login
        self.password = passwd

    def have_valid_data(self):
        return (self.name != '') and (self.login != '') and (self.password != '')
