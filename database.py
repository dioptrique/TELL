
# Create a database with the following tables:
# classes (class_id, class_name, class_code, lesson_transcript, created_by) 
# users (user_id, first_name, last_name, username)
# user_class (user_id, class_id, role)

# Use sqlite3 for the database

# Importing the libraries
import sqlite3


def create_db():
    # Create a connection to the database
    conn = sqlite3.connect('database.db')

    # Create a cursor
    c = conn.cursor()

    # drop all tables
    c.execute('''DROP TABLE IF EXISTS classes''')
    c.execute('''DROP TABLE IF EXISTS users''')
    c.execute('''DROP TABLE IF EXISTS user_class''')

    # Create classes table
    c.execute('''CREATE TABLE IF NOT EXISTS classes (class_id INTEGER PRIMARY KEY, class_name TEXT, class_code TEXT, lesson_transcript TEXT, created_by INTEGER, FOREIGN KEY (created_by) REFERENCES users(user_id))''')

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, telegram_id INTEGER UNIQUE, first_name TEXT, last_name TEXT, username TEXT)''')

    # Create user_class table, where user_id is foreign key to user's id in the users table, class_id is foreign key to class's id in the classes table, and role is the user's role in the class
    c.execute('''CREATE TABLE IF NOT EXISTS user_class (user_id INTEGER, class_id INTEGER, role TEXT, PRIMARY KEY (user_id, class_id), FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (class_id) REFERENCES classes(class_id))''')

    # Commit the changes
    conn.commit()

    # Check and print db schema
    res = c.execute('''SELECT name FROM sqlite_master WHERE type='table';''')\
        .fetchall()
    print(res)

    # Close the connection
    conn.close()