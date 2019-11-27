from flaskext.mysql import MySQL
from User import SimpleUser


class MSQLConn:
    def __init__(self, app):
        self.mysql = MySQL(app)
        app.config['MYSQL_DATABASE_USER'] = 'root'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
        app.config['MYSQL_DATABASE_DB'] = 'BucketList'
        app.config['MYSQL_DATABASE_HOST'] = 'localhost'
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def have_room_with_title(self, title):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM tbl_room WHERE room_title = %s"
            cursor.execute(query, (title,))
            return len(cursor.fetchall()) > 0
        finally:
            cursor.close()

    def create_room(self, title):
        cursor = self.conn.cursor()
        try:
            query = "INSERT INTO tbl_room (room_title) VALUES (%s)"
            result = cursor.execute(query, (title,))
            if result:
                self.conn.commit()
            return result
        finally:
            cursor.close()

    def get_rooms(self):
        result = []
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM tbl_room"
            cursor.execute(query)
            data = cursor.fetchall()
        finally:
            cursor.close()

        for room in data:
            room_dict = {
                'Title': room[1],
            }
            result.append(room_dict)
        return result

    def clear_joined_room(self, user_id):
        self.join_room(user_id, '')

    def join_room(self, user_id, room_name):
        cursor = self.conn.cursor()
        try:
            query = "UPDATE tbl_user SET user_last_visited_room = %s WHERE user_id = %s"
            result = cursor.execute(query, (room_name, user_id))
            if result:
                self.conn.commit()
            return result
        finally:
            cursor.close()

    def have_user_with_email(self, email):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM tbl_user WHERE user_username = %s"
            cursor.execute(query, (email,))
            return len(cursor.fetchall()) > 0
        finally:
            cursor.close()

    def have_user_with_name(self, name):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM tbl_user WHERE user_name = %s"
            cursor.execute(query, (name,))
            return len(cursor.fetchall()) > 0
        finally:
            cursor.close()

    def add_new_user(self, user):
        cursor = self.conn.cursor()
        try:
            query = "INSERT INTO tbl_user (user_name, user_username, user_password) VALUES (%s, %s, %s)"
            result = cursor.execute(query, (user.name, user.login, user.hashed_pass))
            if result:
                self.conn.commit()
            return result
        finally:
            cursor.close()

    def get_user_with_login(self, login):
        cursor = self.conn.cursor()
        try:
            query = "SELECT * FROM tbl_user WHERE user_username = %s"
            cursor.execute(query, (login,))
            tmp_user = cursor.fetchone()
            if len(tmp_user) > 0:
                return SimpleUser(tmp_user[0], tmp_user[1], tmp_user[2], tmp_user[3])
        finally:
            cursor.close()
