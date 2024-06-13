import datetime
import sqlite3
from functools import wraps
from flask import Flask, render_template, request,  redirect,  url_for, session, jsonify, flash
from config import CONFIG
from user_methods import read_all_girls, read_all_photos
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase
import os
from auth import get_credentials
from googleapiclient.discovery import build


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



def get_db_connection():
    conn = sqlite3.connect('girls.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Preprocess the photos data to create a dictionary mapping girl IDs to photos
    photos = read_all_photos()
    girl_photos_dict = {}

    for photo in photos:
        # Access the 'girl_id' key within each photo dictionary
        girl_id = photo.get('girl_id')

        if girl_id is not None:
            # Check if the girl ID is already in the dictionary
            if girl_id not in girl_photos_dict:
                # If not, add the photo to the dictionary with the girl ID as the key
                girl_photos_dict[girl_id] = photo
                print("The girl dict is ", girl_photos_dict)
    return render_template('users/index.html', girls=read_all_girls(), girl_photos_dict=girl_photos_dict)


@login_required
@app.route('/search', methods=['GET'])
def search():
    conn = get_db_connection()
    query = "SELECT * FROM girls WHERE 1=1"
    parameters = []

    filters = request.args.to_dict()

    for key, value in filters.items():
        if key == '':
            pass
        elif key == 'age_min' and value:
            query += " AND age >= ?"
            parameters.append(int(value))
        elif key == 'age_max' and value:
            query += " AND age <= ?"
            parameters.append(int(value))
        elif key in ['bmi_min', 'bmi_max'] and value:
            if key == 'bmi_min':
                query += " AND bmi >= ?"
                parameters.append(float(value))
            elif key == 'bmi_max':
                query += " AND bmi <= ?"
                parameters.append(float(value))
        elif value:
            query += f" AND {key} LIKE ?"
            parameters.append(f"%{value}%")

    cursor = conn.execute(query, parameters)
    results = cursor.fetchall()
    conn.close()

    photos = read_all_photos()
    girl_photos_dict = {}

    for photo in photos:
        # Access the 'girl_id' key within each photo dictionary
        girl_id = photo.get('girl_id')

        if girl_id is not None:
            # Check if the girl ID is already in the dictionary
            if girl_id not in girl_photos_dict:
                # If not, add the photo to the dictionary with the girl ID as the key
                girl_photos_dict[girl_id] = photo
                print("The girl dict is ", girl_photos_dict)

    return render_template('users/index.html', girls=results, girl_photos_dict=girl_photos_dict), 200


@app.route('/profile/<int:girl_id>', methods=['GET', 'POST'])
def profile(girl_id):
    conn = get_db_connection()
    girl = conn.execute('SELECT * FROM girls WHERE id = ?', (girl_id,)).fetchone()
    photos = conn.execute('SELECT * FROM photos WHERE girl_id = ?', (girl_id,)).fetchall()
    conn.close()

    if girl is None:
        return "Girl not found", 404

    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        description = request.form['description']

        # Check availability and create event
        if create_event(girl['name'], start_time, end_time, description):
            flash('Booking confirmed!')
        else:
            flash('The time slot is not available. Please choose another time.')

    return render_template('users/profile.html', girl=girl, photos=photos)



def create_event(name, start_time, end_time, description):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    start_datetime = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M')

    event = {
        'summary': f'Booking with {name}',
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
    }

    # Check availability
    freebusy_query = {
        "timeMin": start_datetime.isoformat() + 'Z',
        "timeMax": end_datetime.isoformat() + 'Z',
        "items": [{"id": 'primary'}]
    }

    freebusy_result = service.freebusy().query(body=freebusy_query).execute()
    calendars = freebusy_result['calendars']

    if calendars['primary']['busy']:
        return False

    # Create event
    service.events().insert(calendarId='primary', body=event).execute()
    return True


# Route for signup (user registration)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return jsonify({"error": "Email and password are required"}), 400
            try:
                # Create user with Firebase Auth
                user = auth.create_user_with_email_and_password(email, password)
                # Add user to Firestore
                user_data = {
                    "email": email,
                    "uid": user['localId']
                }
                db.collection('users').document(user['localId']).set(user_data)
                return redirect(url_for('login')), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"error": "Content-Type must be application/json"}), 400

    return render_template('users/signup.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return jsonify({"error": "Email and password are required"}), 400
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                session['username'] = email  # Store the username in session
                return redirect(url_for('index')), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"error": "Content-Type must be application/json"}), 400

    return render_template("users/login.html")


# Route for user logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host=CONFIG["user"]["listen_ip"], port=CONFIG["user"]["port"], debug=CONFIG["user"]["debug"])
