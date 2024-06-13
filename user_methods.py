import sqlite3
from flask import jsonify
from config import CONFIG


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db_connection():
    db_conn = sqlite3.connect(CONFIG["database"]["name"])
    db_conn.row_factory = dict_factory
    return db_conn


def get_usersdb_conncection():
    db_conn = sqlite3.connect(CONFIG["usersdb"]["name"])
    db_conn.row_factory = dict_factory
    return db_conn


def read_all_photos():
    ALL_PHOTOS = "SELECT * FROM photos"

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(ALL_PHOTOS)
    result = cursor.fetchall()
    db_conn.close()
    print(result)
    return result


def read_all_girls():
    ALL_GIRLS = "SELECT * FROM v_girls"

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(ALL_GIRLS)
    result = cursor.fetchall()
    db_conn.close()
    return result


def insert_message(user_id, sender, receiver, message):
    INSERT_MESSAGE = ("INSERT INTO messages (user_id, sender, receiver, message)"
                      "VALUES (?, ?, ?, ?)")

    db_conn = get_usersdb_conncection()
    cursor = db_conn.cursor()
    cursor.execute(INSERT_MESSAGE, (user_id, sender, receiver, message))
    db_conn.commit()
    cursor.close()
