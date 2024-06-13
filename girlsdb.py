import sqlite3
import sys

from config import CONFIG


class GirlsDB:
    @staticmethod

    def create_database(database_connection: sqlite3.Connection):
        cursor = database_conncetion.cursor()
        
        
        # Connect to or create the database
        conn = sqlite3.connect('girls.db')
        c = conn.cursor()

        # Encode data with UTF8
        c.execute('PRAGMA encoding = "UTF-8";')

        # Create a table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS girls (
                     id INTEGER PRIMARY KEY,
                     name TEXT NOT NULL,
                     age INTEGER NOT NULL,
                     hair_colour TEXT NOT NULL,
                     phone TEXT NOT NULL,
                     boobs TEXT,
                     ass TEXT,
                     race TEXT,
                     orientation TEXT,
                     bmi INTEGER,
                     personality TEXT,
                     services TEXT
                     )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY,
        girl_id INTEGER,
        photo_url TEXT,
        FOREIGN KEY (girl_id) REFERENCES girls(id)
    );
        ''')

        # Commit changes and close connection
        conn.commit()
        conn.close()


def insert_data(name, age, hair_colour, phone, boobs=None, ass=None, race=None, orientation=None, bmi=None,
                personality=None, services=None):
    conn = sqlite3.connect('girls.db')
    c = conn.cursor()

    # Insert a new row into the table
    c.execute('''INSERT INTO girls (name, age, hair_colour, phone, boobs, ass, race, orientation, bmi, personality, services)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, age, hair_colour, phone, boobs, ass, race, orientation, bmi, personality, services))

    # Commit changes and close connection
    conn.commit()
    conn.close()


def clear_database():
    conn = sqlite3.connect('girls.db')
    c = conn.cursor()

    # Delete all rows from the table
    c.execute('''DELETE FROM girls''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Create the database and table
    create_database()
    print("Database 'girls' and table 'girls' created successfully.")

    clear_database()
    print("Database cleared successfully.")

