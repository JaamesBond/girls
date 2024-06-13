"""The admin dashboard"""
from functools import wraps
from flask import Flask, render_template, request, make_response, redirect, jsonify, url_for, session
import os
from config import CONFIG
from werkzeug.security import check_password_hash
from admindb import get_user
from admin_methods import *
from file_upload import insert_photo, update_girl_photo_url, delete_girl_photos, read_all_photos

import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase


app = Flask(__name__.split('.')[0], template_folder='/home/matei/PycharmProjects/Lesbiene_dev/Templates')
app.config['SECRET_KEY'] = 'Pula mea'


# Initialize Firebase Admin SDK
cred = credentials.Certificate('/home/matei/PycharmProjects/Lesbiene/firebase_sdk.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Firebase SDK configuration snippet
firebase_config = {
    "apiKey": "AIzaSyAd5uJKABU1eBtZVUVhgKdqlb0BhDtZqI8",
    "authDomain": "projectv2-631e7.firebaseapp.com",
    "databaseURL": "https://projectv2-631e7.firebaseio.com",
    "projectId": "projectv2-631e7",
    "storageBucket": "projectv2-631e7.appspot.com",
    "messagingSenderId": "954061641289",
    "appId": "1:954061641289:web:b544cd45714b8cf84d1198"
}
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


# Custom decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# A method displaying the home page
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("girls/index.html", girls=list_of_girls(), photos=read_all_photos())


# A methode to import js safely
@app.template_global()
@login_required
def static_include(filename):
    fullpath = os.path.join(app.static_folder, filename)
    with open(fullpath, 'r') as f:
        return f.read()


# A method that adds a new girl
@app.route("/new/", methods=["GET", "POST"])
@login_required
def newgirl():
    if request.method == "GET":
        return render_template("girls/new_girl.html")
    elif request.method == "POST":
        girl = {}
        for key, value in request.form.items():
            if key == "age" or key == "bmi":
                if value.strip():
                    girl[key] = int(value)
                else:
                    girl[key] = None
            else:
                if value.strip():
                    girl[key] = value
                else:
                    girl[key] = None

        # Add girl to the database
        girl_id = add_girl(girl["name"], girl["age"], girl["hair_colour"], girl["phone"], girl["boobs"], girl["ass"],
                           girl["race"], girl["orientation"], girl["bmi"], girl["personality"], girl["services"])

        if girl_id:
            # If girl is successfully added, handle photo upload
            print("The girl's id is {}".format(girl_id))
            if 'file' in request.files:
                print("It found the file")
                file = request.files['file']
                if file.filename != '':
                    # Upload the photo and get its file path
                    photo_url = insert_photo(girl_id, girl["name"])
            return render_template("girls/new_girl.html", girl=girl)

    return make_response("Invalid request", 400)

@app.route("/deletegirl/<int:id>", methods=["GET"])
@login_required
def deletegirl(id):
    delete_girl(id)
    delete_girl_photos(id)
    return redirect("/")


@app.route("/editgirl/<int:id>", methods=["GET", "POST"])
@login_required
def editgirl(id):
    if request.method == "GET":
        girl = get_girl_by_id(id)
        return render_template("girls/edit_girl.html", girl=girl)
    elif request.method == "POST":
        girl = {}
        girl["id"] = id
        for key, value in request.form.items():
            if key == "age" or key == "bmi":
                if value.strip():
                    girl[key] = int(value)
                else:
                    girl[key] = None
            else:
                if value.strip():
                    girl[key] = value
                else:
                    girl[key] = None
        update_girl(girl)
        if id:
            # If girl is successfully added, handle photo upload
            print("The girl's id is {}".format(id))
            if 'file' in request.files:
                print("It found the file")
                file = request.files['file']
                if file.filename != '':
                    # Upload the photo and get its file path
                    photo_url = insert_photo(id, girl["name"])
        return render_template("girls/edit_girl.html", girl=girl, girl_updated=girl)
    return make_response("Invalid request", 400)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("girls/login.html")
    else:
        username = request.form['username']
        password = request.form['password']

        user = get_user(username)

        if user and check_password_hash(user[2], password):
            # Successful login
            session['username'] = username  # Store the username in session
            return redirect(url_for('index'))
        else:
            return "Username or password incorrect"


# Route for admin logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host=CONFIG["frontend"]["listen_ip"], port=CONFIG["frontend"]["port"], debug=CONFIG["frontend"]["debug"])
