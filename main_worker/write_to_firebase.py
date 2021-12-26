import sqlite3

import Settings
import json
import time
import random
import os

import re

from datetime import datetime

import glob
import pyrebase
import shutil

def extract__(s):
    return re.findall(r'\__(.+?)\__', s)

def extract_(s):
    return re.findall(r'\--(.+?)\--', s)

def extract___(s):
    return re.findall(r'\___(.+?)\___', s)

def moveFiletoArchive(path, filename):
    shutil.move(path + "/" + filename , "/data/archive/images/" + filename)

def getQuestion(image_filename):
    try:
        sqliteConnection = sqlite3.connect('/data/database/lingomooAPP.db')
        sqliteConnection.row_factory = sqlite3.Row  
        cursor = sqliteConnection.cursor()

        sql_select_query = """SELECT * FROM sentences WHERE image_filename = ?"""
        cursor.execute(sql_select_query, (image_filename,))
        records = cursor.fetchall()

        for row in records:
            return dict(row)

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            #print("The SQLite connection is closed")

def sent_all_firebase():
            
    firebaseConfig = {
        "apiKey": "AIzaSyD5b16Ejf5wxsaswc8qIaTBXJTLW7xp8Oc",
        "authDomain": "lingomoo.firebaseapp.com",
        "databaseURL": "https://lingomoo.firebaseio.com",
        "projectId": "lingomoo",
        "storageBucket": "lingomoo.appspot.com",
        "messagingSenderId": "886228262297",
        "appId": "1:886228262297:web:4f391f1d1b68d595974708"}

    firebase = pyrebase.initialize_app(firebaseConfig)

    # Get a reference to the auth service
    auth = firebase.auth()

    # Log the user in
    user = auth.sign_in_with_email_and_password("info@lingomoo.com", "Ece060809")

    storage = firebase.storage()
    # as admin
    db = firebase.database()
    db.child("questions")

    # ref_remove = db.child("todays_content")
    # ref_remove.remove()

    image_files = glob.glob('/data/today/question_images/*.jpg')

    print(image_files)
    print('erdem')


    for image in image_files:   
        path, filename = os.path.split(image)
        print(path)
        print(filename)
        
        question_cat = extract__(filename)
        question_word = extract_(filename)
        correct_answer = extract___(filename)

        print(filename)
    
        data_database = getQuestion(filename[0:20]+ '.jpg')
        print("database")
        print(data_database)
    
        if "missing_word_question" in filename:
            print(filename)

            data = {}
            data['correct_answer']=correct_answer[0]
            data['file_name']=filename.replace(".jpg", "")
            data['article_url']=data_database['article_url']
            data['questions_cat']=question_cat[0]
            print(data)
    
            db.child("questions/" + question_cat[0] + '/' + question_word[0]).child(filename.replace(".jpg", "")).set(data)
            db.child("questions_cat/" + question_cat[0]).child(filename.replace(".jpg", "")).set(data)
            db.child("todays_content/").child(filename.replace(".jpg", "")).set(data)
        
        storage.child("images/" + filename).put(image, user['idToken'])

        moveFiletoArchive(path, filename)

        #updateSqliteTable(filename_id, missing_word_q, correct_order_q)