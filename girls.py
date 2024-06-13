import sqlite3
from flask import jsonify
from config import CONFIG


def girl_id_exists(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM girls WHERE id = ?", (id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists


def dict_factory(cursor, row):
    fields = [ column[0] for column in cursor.description ]
    return {key: value for key, value in zip(fields, row)}


def get_db_connection():
    db_conn = sqlite3.connect(CONFIG["database"]["name"])
    db_conn.row_factory = dict_factory
    return db_conn


def read_all():
    ALL_GIRLS = "SELECT * FROM girls"

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(ALL_GIRLS)
    result = cursor.fetchall()
    db_conn.close()

    return jsonify(result)


def create(girl):
    INSERT_GIRL = ("INSERT INTO girls (name, age, hair_colour, phone, boobs, ass, race, orientation, bmi, personality, services) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    if girl["age"] < 18 or girl["age"] > 65:
        return jsonify({"error": "Age must be between 18 and 65"}), 400
    if girl["name"] is None or girl["name"] == "":
        return jsonify({"error": "Name is required"}), 400
    if girl["hair_colour"] is None:
        return jsonify({"error": "Hair_colour is required"}), 400
    if girl["phone"] is None or girl["phone"] == "":
        return jsonify({"error": "Phone is required"}), 400

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(INSERT_GIRL, (girl["name"], girl["age"], girl["hair_colour"], girl["phone"], girl["boobs"], girl["ass"], girl["race"], girl["orientation"], girl["bmi"], girl["personality"], girl["services"]))
    db_conn.commit()
    new_girl_id = cursor.lastrowid
    cursor.close()

    return new_girl_id, 201


def read_girlById(id):
    ONE_GIRL = "SELECT * FROM girls WHERE id = ?"

    if id > 9223372036854775807 or id < -9223372036854775807:
        return jsonify({"error": "ID too large"}), 400

    if not girl_id_exists(id):
        return jsonify({"error": "Girl not found"}), 404

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(ONE_GIRL, (id,))
    result = cursor.fetchall()
    db_conn.close()

    if len(result) < 1:
        return "Not Found", 404
    elif len(result) > 2:
        return "Too many girls!", 500

    return jsonify(result[0]), 200


def update_girlById(id, girl):
    UPDATE_GIRL = """
    UPDATE girls
    SET age = ?,
    hair_colour = ?,
    phone = ?,
    boobs = ?,
    ass = ?,
    race = ?,
    orientation = ?,
    bmi = ?,
    personality = ?,
    services = ?
    WHERE id = ?
    """

    if id > 9223372036854775807 or id < -9223372036854775807:
        return jsonify({"error": "ID too large"}), 401

    if not girl_id_exists(id):
        return jsonify({"error": "Girl not found"}), 404

    if girl["age"] < 18 or girl["age"] > 65:
        return jsonify({"error": "Age must be between 18 and 65"}), 400
    if girl["name"] is None or girl["name"] == "" or not girl["name"].isalpha:
        return jsonify({"error": "Name is required"}), 400
    if girl["hair_colour"] is None or girl["hair_colour"] or not girl["hair_colour"].isalpha == "":
        return jsonify({"error": "Hair_colour is required"}), 400
    if girl["phone"] is None or girl["phone"] == "" or not girl["phone"]:
        return jsonify({"error": "Phone is required"}), 400

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(UPDATE_GIRL, (girl['age'], girl['hair_colour'], girl['phone'], girl['boobs'], girl['ass'], girl['race'], girl['orientation'], girl['bmi'], girl['personality'], girl['services'], id))
    db_conn.commit()

    return read_girlById(id)


def delete_girlById(id):
    DELETE_GIRL = "DELETE FROM girls WHERE id = ?"

    if id > 9223372036854775807 or id < -9223372036854775807:
        return jsonify({"error": "ID too large"}), 400

    if not girl_id_exists(id):
        return jsonify({"error": "Girl not found"}), 404

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(DELETE_GIRL, (id,))
    db_conn.commit()

    return "Successfully deleted", 204