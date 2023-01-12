from sqlite3 import IntegrityError
import sqlite3
import time


def get_active_target(target_list: list):
    for target in target_list:
        if float(target) != 0:
            return [(target_list.index(target) + 1), target]
    return 0


class User:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def register(self, symbol, current_price, target_1, target_2, target_3, type):
        with self.connection as con:
            con.execute("INSERT INTO SIGNALS (symbol, target_1, target_2, target_3, date, current_price, type) ""VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (symbol, target_1, target_2, target_3, time.time(), current_price, type))

    def close_target(self, symbol, target_number):
        with self.connection:
            self.cursor.execute(f"UPDATE SIGNALS SET target_{target_number}=? WHERE symbol=?", ('0', symbol,))

    def get_symbol(self, symbol):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM SIGNALS WHERE symbol=?", (symbol,)).fetchall()
            for i in result:
                return [i[2], i[3], i[4], i[5], i[6], i[7]]
            return False

    def get_list(self):
        with self.connection:
            result = self.cursor.execute("SELECT symbol FROM SIGNALS").fetchall()
            tg_list = []
            for i in result:
                tg_list.append(i[0])
            return tg_list

    def check_symbol(self, symbol):
        with self.connection:
            result = self.cursor.execute("SELECT id FROM SIGNALS WHERE symbol=?", (symbol,)).fetchall()
            if len(result) == 1:
                return True
            elif len(result) == 0:
                return False

    def delete_symbol(self, symbol):
        with self.connection:
            self.cursor.execute(f"DELETE FROM SIGNALS WHERE symbol=?", (symbol,))


if __name__ == '__main__':
    db = User('db.db')
    print(db.register('ETCUSDT', '38.42', '38.804', '39.188', '39.573', 'LONG'))
    #print(db.register('SNXUSDT', '4.016', '3.815', '3.614', '3.414'))
    # try:
    #     print(db.register(14))
    # except IntegrityError:
    #     print('Такой юзер уже есть')
    # for user in db.get_active_list_with_time():
    #     if time.time() - float(user[1]) > 60*60*24*30:
    #          db.update_status(user[0])
    # print(db.get_active_list())
    # print(db.get_active_list_with_time())
