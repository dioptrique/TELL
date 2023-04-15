

# This is a telegram bot to be used as a post-lesson learning assistant for students and teachers
# Each student and teacher can register themself as a teacher or a student with the class code
# Then, teachers can upload a lesson transcript
# Upon the teacher uploading the transcript, the AI generates a set of MCQ questions based on the transcript with the correct answer. It sends the questions to each student in the class
# Once a student has responded to all the questions, the AI will generate a feedback on the students understanding with a custom remediation plan generate by the ai
# The AI will next generate MCQ questions again based on the topics that the student got mistakes in

# The AI that is used is berri.ai, which allows us to do QnA on any text

# Importing the libraries
import os
import telebot
import requests
import json
import random
import time
import datetime
import re
import string
import urllib
import dotenv

# Load the environment variables
dotenv.load_dotenv()

# Create a database with the following tables:
# classes (class_id, class_name, class_code) 
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

    # Create classes table
    c.execute('''CREATE TABLE IF NOT EXISTS classes (class_id INTEGER PRIMARY KEY, class_name TEXT, class_code TEXT)''')

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, telegram_id INTEGER, first_name TEXT, last_name TEXT, username TEXT, role TEXT, class_id TEXT)''')

    # Create user_class table, where user_id is foreign key to user's id in the users table, class_id is foreign key to class's id in the classes table, and role is the user's role in the class
    c.execute('''CREATE TABLE IF NOT EXISTS user_class (user_id INTEGER, class_id INTEGER, role TEXT, FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (class_id) REFERENCES classes(class_id))''')

    # Commit the changes
    conn.commit()

    # Check and print db schema
    res = c.execute('''SELECT name FROM sqlite_master WHERE type='table';''')\
        .fetchall()
    print(res)

    # Close the connection
    conn.close()


# Start an instance of the bot
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

def main():
    bot.infinity_polling()

# Function to explain to the user how to use the bot
@bot.message_handler(commands=['start'])
def start(message):
    # Get the user id
    telegram_user_id = message.from_user.id
    # Send a message to the user
    bot.send_message(telegram_user_id, 'Welcome to the Post-Lesson Learning Assistant Bot! This bot is used to help students and teachers with their learning. To use this bot, you will need to register as a student or a teacher with the class code. To register, type /register <student/teacher> <class_code>. To get a list of commands, type /help')

# Function to get list of commands
@bot.message_handler(commands=['help'])
def help(message):
    # Get the user id
    telegram_user_id = message.from_user.id
    # Send a message to the user
    bot.send_message(telegram_user_id, 'List of commands:\n1) /start\n2) /help\n3) /register <student/teacher> <class_code>\n4) /create_class <class_name> <class_code>\n5) /upload_transcript <lesson_name> <lesson_transcript>')

# Function to register a student or teacher with the class id
# Format: /register <student/teacher> <class_code>
# Example: /register student 131d2ws
@bot.message_handler(commands=['register'])
def register(message):
    # Get the user id
    telegram_user_id = message.from_user.id
    # Get the user's first name
    first_name = message.from_user.first_name
    # Get the user's last name
    last_name = message.from_user.last_name
    # Get the user's username
    username = message.from_user.username
    # Get the user's message
    message_text = message.text
    # Get the user's message split into a list
    message_text_list = message_text.split()
    if len(message_text_list) != 3:
        bot.send_message(telegram_user_id, 'Invalid format. Please type /register <student/teacher> <class_code>.')
        return
    # Get the user's role
    role = message_text_list[1]
    # Get the user's class id
    class_code = message_text_list[2]

    # Create a connection to the database
    conn = sqlite3.connect('database.db')

    # Create a cursor
    c = conn.cursor()

    # Check if the user is a student or a teacher
    if role == 'student' or role == 'teacher':
        # Check if the class code exists
        c.execute('''SELECT class_id FROM classes WHERE class_code = ?''', (class_code,))
        class_row = c.fetchone()
        # If the class code exists
        if class_row:
            # Get the class id
            class_id = class_row[0]
            # Check if the user is already registered
            c.execute('''SELECT user_id FROM users WHERE telegram_id = ?''', (telegram_user_id,))
            user_row = c.fetchone()
            # If the user is already registered
            if user_row:
                # Get the user id
                user_id = user_row[0]
                # Update the user's role and class id
                c.execute('''UPDATE users SET role = ?, class_id = ? WHERE user_id = ?''', (role, class_id, user_id))
                # Commit the changes
                conn.commit()
                # Send a message to the user
                bot.send_message(telegram_user_id, 'You have been registered as a ' + role + ' in class ' + class_code)
            # If the user is not registered
            else:
                # Insert the user into the users table
                c.execute('''INSERT INTO users (telegram_id, first_name, last_name, username, role, class_id) VALUES (?, ?, ?, ?, ?, ?)''', (telegram_user_id, first_name, last_name, username, role, class_id))
                # Commit the changes
                conn.commit()
                # Send a message to the user
                bot.send_message(telegram_user_id, 'You have been registered as a ' + role + ' in class ' + class_code)
        # If the class code does not exist
        else:
            # Send a message to the user
            bot.send_message(telegram_user_id, 'The class code you have entered is invalid')
    # If the user is not a student or a teacher
    else:
        # Send a message to the user
        bot.send_message(telegram_user_id, 'Please enter a valid role. The role can either be student or teacher')

    conn.close()


# Function to create a class. Returns the class code.
# Format: /create_class <class name>
# Example: /create_class Maths
@bot.message_handler(commands=['create_class'])
def create_class(message):
    # Get the user id
    telegram_user_id = message.from_user.id
    # Get the user's message
    message_text = message.text
    # Get the user's message split into a list
    message_text_list = message_text.split()

    if len(message_text_list) < 2:
        bot.send_message(telegram_user_id, 'Please enter a class name')
        return
    
    # Get the user's class name
    class_name = message_text_list[1]


    # Generate a random class code
    class_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    # Create a connection to the database
    conn = sqlite3.connect('database.db')

    # Create a cursor
    c = conn.cursor()

    # Insert the class into the classes table
    c.execute('''INSERT INTO classes (class_name, class_code) VALUES (?, ?)''', (class_name, class_code))
    # Commit the changes
    conn.commit()

    # Print inserted row in db
    if DEBUG:
        res = c.execute('''SELECT * FROM classes WHERE class_code = ?''', (class_code,))
        print(res.fetchall())

    conn.close()

    # Send a message to the user
    bot.send_message(telegram_user_id, 'The class ' + class_name + ' has been created with the class code ' + class_code)


# Function to upload a transcript of a lecture


# Run the main function
if __name__ == '__main__':
    DEBUG = True
    create_db()
    main()
