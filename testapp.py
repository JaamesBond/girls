from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase

app = Flask(__name__)

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


@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    db.collection('users').add(data)
    return jsonify({"success": True}), 200


@app.route('/get_data', methods=['GET'])
def get_data():
    docs = db.collection('users').stream()
    data = [doc.to_dict() for doc in docs]
    return jsonify(data), 200


@app.route('/signup', methods=['POST'])
def signup():
    email = request.json['email']
    password = request.json['password']
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return jsonify(user), 200
    except:
        return jsonify({"error": "Signup failed"}), 400


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return jsonify(user), 200
    except:
        return jsonify({"error": "Login failed"}), 400


if __name__ == '__main__':
    app.run(debug=True)
