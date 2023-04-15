

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
from database import create_db
from utils import parse_user_details, parse_arguments
import sqlite3

# Load the environment variables
dotenv.load_dotenv()



# Start an instance of the bot
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

def main():
    bot.infinity_polling()


# Function to explain to the user how to use the bot
@bot.message_handler(commands=['start'])
def start(message):
    print(message)
    # Get the user details
    first_name, last_name, username, telegram_user_id = parse_user_details(message)
    # Send a message to the user
    bot.send_message(telegram_user_id, f'Hi {first_name} {last_name} Welcome to the Post-Lesson Learning Assistant Bot! \n This bot is used to help students and teachers with their learning.\nTo get a list of commands, type /help')

    # Register user in the database
    # Create a connection to the database
    conn = sqlite3.connect(os.getenv('DB_URL'))
    # Create a cursor
    c = conn.cursor()
    # Check if user exists
    user_exists = c.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_user_id,)).fetchone()
    if user_exists is None:
        # Insert user into the database
        c.execute('''INSERT INTO users (telegram_id, first_name, last_name, username) VALUES (?, ?, ?, ?)''', (telegram_user_id, first_name, last_name, username))
        print(f'User {username} registered successfully')
        # Commit the changes
        conn.commit()
    # Close the connection
    conn.close()


# Function to get list of commands
@bot.message_handler(commands=['help'])
def help(message):
    # Get the user details
    first_name, last_name, username, telegram_user_id = parse_user_details(message)
    # Send a message to the user
    bot.send_message(telegram_user_id, 'List of commands:\n1) /start\n2) /help\n3) /register <class_code>\n4) /create_class <class_name>\n5) /upload_transcript <class_code> <lesson_transcript>')

# Function to register a student for a class
# Format: /register <class_code>
# Example: /register 131d2ws
@bot.message_handler(commands=['register'])
def register(message):
    # Get the user details
    first_name, last_name, username, telegram_user_id = parse_user_details(message)
    arg_list = parse_arguments(message)
    if len(arg_list) != 1:
        bot.send_message(telegram_user_id, 'Invalid format. Please type /register <class_code>.')
        return

    # Get the user's class id
    class_code = arg_list[0]

    # Create a connection to the database
    conn = sqlite3.connect('database.db')

    # Create a cursor
    c = conn.cursor()

    role = 'student'

    # Check if the user is a student or a teacher
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
        if not user_row:
            bot.send_message(telegram_user_id, 'You are not registered. Please type /start to register.')
            return
        user_id = user_row[0]
        # Add user to class as a student
        c.execute('''INSERT INTO user_class (class_id, user_id, role) VALUES (?, ?, ?)''', (class_id, user_id, role))
        # Commit the changes
        conn.commit()
        # Send a message to the user
        bot.send_message(telegram_user_id, 'You have successfully registered as a student for the class code ' + class_code)
    
    # If the class code does not exist
    else:
        # Send a message to the user
        bot.send_message(telegram_user_id, 'The class code you have entered is invalid')

    conn.close()


# Function to create a class. Returns the class code. Creator of class becomes the teacher of the class.
# Format: /create_class <class name>
# Example: /create_class Maths
@bot.message_handler(commands=['create_class'])
def create_class(message):
    # Get the user details
    first_name, last_name, username, telegram_user_id = parse_user_details(message)
    message_text_list = parse_arguments(message)


    if len(message_text_list) < 1:
        bot.send_message(telegram_user_id, 'Please enter a class name')
        return

    class_name = message_text_list[0]

    # Generate a random class code
    class_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    # Create a connection to the database
    conn = sqlite3.connect(os.getenv('DB_URL'))

    # Create a cursor
    c = conn.cursor()

    # Get the id of the user
    c.execute('''SELECT user_id FROM users WHERE telegram_id = ?''', (telegram_user_id,))
    user_row = c.fetchone()
    # If the user is not registered
    if not user_row:
        # Send a message to the user
        bot.send_message(telegram_user_id, 'You are not registered. Please run /start command first.')
        return
    # Get the user id
    user_id = user_row[0]
    
    # Insert the class into the classes table
    res = c.execute('''INSERT INTO classes (class_name, class_code, created_by) VALUES (?, ?, ?)''', (class_name, class_code, user_id))
    # Get the class id of the inserted class
    class_id = res.lastrowid

    # Insert class and user into the user_class table
    c.execute('''INSERT INTO user_class (user_id, class_id, role) VALUES (?, ?, ?)''', (user_id, class_id, 'teacher'))

    # Commit the changes
    conn.commit()

    conn.close()

    # Send a message to the user
    bot.send_message(telegram_user_id, 'The class ' + class_name + ' has been created with the class code ' + class_code + ' You are the teacher of this class. Share this class code with your students so they can join your class.')


# Function to upload a transcript of a lecture
# Format: /upload_transcript <class_code> <lesson_transcript>
@bot.message_handler(commands=['upload_transcript'])
def upload_transcript(message):
    # Get the user id
    pass

# Run the main function
if __name__ == '__main__':
    DEBUG = True
    create_db()
    main()
