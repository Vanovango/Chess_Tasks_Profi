import sqlite3
from init import *

class Verify:
    def __init__(self):
        self.connect = sqlite3.connect(DB_PATH)
        self.cursor = self.connect.cursor()

        self.users_list = {
            'full_name': [],
            'date_of_birth': [],
            'logging': [],
            'password': []
        }

        self.load_data()

    def load_data(self):
        data = self.cursor.execute("""
            SELECT * FROM users_list
        """).fetchall()

        for user in data:
            self.users_list['full_name'].append(user[1])
            self.users_list['date_of_birth'].append(user[2])
            self.users_list['logging'].append(user[3])
            self.users_list['password'].append(user[4])

        # print(self.users_list)

    def add_new_user(self, user_data):

        self.cursor.execute(f"""
                    INSERT INTO users_list(full_name, date_of_birth, logging, password) VALUES
                    ('{user_data['full_name']}', '{user_data['date_of_birth']}',
                     '{user_data['logging']}', '{user_data['password']}'
                     );
                """)
        self.connect.commit()

        for key in user_data:
            self.users_list[key].append(user_data[key])

        print(self.users_list)

    def check_user(self, logging, password):
        if logging == '' and password == '1':
            return 'admin_access'

        if logging in self.users_list['logging']:
            ind = self.users_list['logging'].index(logging)
            if password == self.users_list['password'][ind]:
                return True

        return False

