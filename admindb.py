import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'admin.db'


def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()


def add_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()


def get_user(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


if __name__ == '__main__':
    create_tables()
    add_user('admin', 'admin')