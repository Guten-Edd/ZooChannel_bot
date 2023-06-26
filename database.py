"""Модуль для общения с базой данных."""

import sqlite3


def check_create_bd():
    """Проверка наличия базы данных или создание ее."""
    try:
        sqlite_connection = sqlite3.connect('db_urls')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = "select sqlite_version();"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchall()
        print("Версия базы данных SQLite: ", record)
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
            return True
        else:
            raise False


def add_url(url):
    """Добавление записи адресса в базу."""
    try:
        con = sqlite3.connect('db_urls')
        cur = con.cursor()

        cur.execute('''
        CREATE TABLE IF NOT EXISTS URLS(
            id INTEGER PRIMARY KEY,
            url TEXT
        );
            ''')
        query_count = cur.execute("""SELECT * from URLS""")
        print(query_count)
        cur.execute('INSERT INTO URLS VALUES(?, ?);',
                    (len(query_count.fetchall())+1, url))

        con.commit()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if con:
            con.close()
            print("Соединение с SQLite закрыто")
            return True
        else:
            return False


def check_existing_url(test_url):
    """Проверяет наличие переданного URL."""
    try:
        con = sqlite3.connect('db_urls')
        cur = con.cursor()
        query_select = """SELECT id from URLS WHERE url = ?"""
        query_exist = cur.execute(query_select, (test_url,))
        query_exist_fe = query_exist.fetchall()
        print(query_exist_fe)
        num_raws = len(query_exist.fetchall())
        print(num_raws)
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if con:
            con.close()
            print("Соединение с SQLite закрыто")

        if num_raws > 0:
            return True
        else:
            return False
