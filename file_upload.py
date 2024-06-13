import sqlite3
import os
from werkzeug.utils import secure_filename  # For secure file name handling
from config import CONFIG
from flask import jsonify, request


UPLOAD_FOLDER = 'static/girls'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def dict_factory(cursor, row):
    fields = [ column[0] for column in cursor.description ]
    return {key: value for key, value in zip(fields, row)}


def get_db_connection():
    db_conn = sqlite3.connect(CONFIG["database"]["name"])
    db_conn.row_factory = dict_factory
    return db_conn


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def insert_photo(girl_id, girl_name):
    print("Girl ID:", girl_id)
    print("Girl Name:", girl_name)

    if 'file' not in request.files:
        print("No file part in the request")
        # No file part in the request
        return None

    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        # No selected file
        return None

    if file and allowed_file(file.filename):
        # Generate a secure filename and save the file to the girl's folder
        filename = secure_filename(file.filename)
        girl_folder_name_and_id = str(girl_name) + "_" + str(girl_id)
        girl_folder = os.path.join(UPLOAD_FOLDER, girl_folder_name_and_id)
        print("Girl Folder:", girl_folder)
        if not os.path.exists(girl_folder):
            os.makedirs(girl_folder)
        file_path = os.path.join(girl_folder, filename)
        print("File Path:", file_path)
        file.save(file_path)

        # Insert the file path into the database
        INSERT_PHOTO = "INSERT INTO photos (girl_id, photo_url) VALUES (?, ?)"
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute(INSERT_PHOTO, (girl_id, file_path))
        db_conn.commit()
        cursor.close()

        return file_path  # Return the file path if insertion is successful
    else:
        # Invalid file type
        print("Invalid file type")
        return None



def update_girl_photo_url(girl_id, photo_url):
    UPDATE_photo_url = "UPDATE girls SET photo_url = ? WHERE id = ?"
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(UPDATE_photo_url, (photo_url, girl_id))
    db_conn.commit()
    cursor.close()


def delete_girl_photos(girl_id):
    # Retrieve photo URLs associated with the girl from the database
    SELECT_PHOTOS_QUERY = "SELECT photo_url FROM photos WHERE girl_id = ?"
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(SELECT_PHOTOS_QUERY, (girl_id,))
    photo_urls = cursor.fetchall()
    cursor.close()

    # Delete photos from the file system and remove photo URL records from the database
    for photo_url in photo_urls:
        url = photo_url["photo_url"]
        # Delete photo file from the file system
        if os.path.exists(url):
            os.remove(url)
        # Remove photo URL record from the database
        DELETE_PHOTO_QUERY = "DELETE FROM photos WHERE photo_url = ?"
        cursor = db_conn.cursor()
        cursor.execute(DELETE_PHOTO_QUERY, (url,))
        db_conn.commit()
        cursor.close()
    # Delete the folder associated with the girl's photos
    girl_folder = os.path.dirname(photo_urls[0]["photo_url"])  # Get the folder containing the photos
    if os.path.exists(girl_folder):
        os.rmdir(girl_folder)
    return True  # Return True if deletion is successful


def read_all_photos():
    ALL_PHOTOS = "SELECT * FROM photos"

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(ALL_PHOTOS)
    result = cursor.fetchall()
    db_conn.close()
    print(result)
    return result