import textwrap
import random
import Settings
import json
import time
import random
import sqlite3
import string

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from datetime import datetime

def is_sentence_processed(sentence):
    try:
        sqliteConnection = sqlite3.connect('/data/database/lingomooAPP.db')
        sqliteConnection.row_factory = sqlite3.Row  
        cursor = sqliteConnection.cursor()

        print("Connected to SQLite")

        sql_select_query = """SELECT * FROM sentences WHERE sentence = ?"""
        cursor.execute(sql_select_query, (sentence,))
        records = cursor.fetchall()

        for row in records:
            dict(row)['sentence_processed']

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")

def filename_generator(question):
    if question:
        suffix = "_question"
    else:
        suffix = "_answer"

    file_name = '_' + \
        str(datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")) + suffix + '.jpg'
    return file_name

def convert_to_words(lst):
    return ' '.join(lst).split()

class CreateImage:
    """ This class generates question/answer Image Sets """
    
    # Initializer / Instance Attributes
    def __init__(self, question_type, question_category, text, text_org, answer_options, missing_word, missing_word_definition, image_file_name, bg):
        self.question_type = question_type
        self.question_category = question_category
        self.text = text
        self.text_org = text_org
        self.bg = bg
        self.option1 = answer_options[0]
        self.option2 = answer_options[1]
        self.option3 = answer_options[2]
        self.option4 = answer_options[3]
        self.missing_word = missing_word
        self.missing_word_definition = missing_word_definition
        self.image_file_name = image_file_name
        self.img, self.save_image = self.random_background_generator(self.bg)

    def random_background_generator(self, bg):
        ##background = Image.open('background_' + str(random.randint(1, 2)) + '.jpg')           
        background = Image.open(bg)   
        transparent_layer = Image.open('transparent_layer_' + self.question_category + '.png')
        background.paste(transparent_layer, (0, 0), transparent_layer)

        lingomoo_icon = Image.open('lingomoo.png')
        lingomoo_icon = lingomoo_icon.resize((int(lingomoo_icon.size[0]/2),int(lingomoo_icon.size[1]/2)), 0)
        background.paste(lingomoo_icon, (850, 1000), lingomoo_icon)
        
        img = ImageDraw.Draw(background) 
        
        return img, background
    
    def option_lines(self, question_or_answer):
        if self.question_type=="missing_word":
            self.img.text((150, 350), self.option1, font=Settings.FONT_BODY, fill=(0, 115, 255))
            self.img.text((150, 450), self.option2, font=Settings.FONT_BODY, fill=(0, 115, 255))
            self.img.text((150, 550), self.option3, font=Settings.FONT_BODY, fill=(0, 115, 255))
            self.img.text((150, 650), self.option4, font=Settings.FONT_BODY, fill=(0, 115, 255))

            self.img.text((50, 350), "(A)", font=Settings.FONT_BODY, fill=(255, 140, 0))
            self.img.text((50, 450), "(B)", font=Settings.FONT_BODY, fill=(255, 140, 0))
            self.img.text((50, 550), "(C)", font=Settings.FONT_BODY, fill=(255, 140, 0))
            self.img.text((50, 650), "(D)", font=Settings.FONT_BODY, fill=(255, 140, 0))
        
        if question_or_answer=="answer":
            tick = Image.open('correct.png')     
            if self.option1==self.missing_word:
                self.save_image.paste(tick, (50, 350), tick)
            if self.option2==self.missing_word:
                self.save_image.paste(tick, (50, 450), tick)
            if self.option3==self.missing_word:
                self.save_image.paste(tick, (50, 550), tick)
            if self.option4==self.missing_word:
                 self.save_image.paste(tick, (50, 650), tick)

        return self.img
    
    def first_line(self, question_or_answer):
        if question_or_answer == "question":
            self.img.text((50, 10), Settings.FIRST_LINE[self.question_type], 
                font=Settings.FONT_TITLE, fill=(255, 140, 0))
            
            #rect_20 = Image.open('rect20.png')
            #self.save_image.paste(rect_20, (50, 990), rect_20)
        
            #self.img.text((90, 1000), self.question_category, 
            #    font=Settings.FONT_CAT, fill=(0, 115, 255))       
    
        if question_or_answer == "answer":
            self.img.text((50, 10), "Correct Answer: " ,
                font=Settings.FONT_TITLE, fill=(255, 140, 0))
            self.img.text((550, 10), self.missing_word,
                font=Settings.FONT_TITLE, fill=(0, 115, 255)) 
    
        self.img.text((50, 30), "_________________________________",
            font=Settings.FONT_TITLE, fill=(255, 140, 0))
                
        return self.img
    
    def question_or_answer_line(self, question_or_answer):
        text_keep_org = self.text_org
        
        self.text_org = self.text_org.split()
        random.shuffle(self.text_org)
        separator = ' '
        unordered_text = separator.join(self.text_org)
        
        if question_or_answer == "answer":
            if self.question_type == "correct_order":
                self.text = text_keep_org
            if self.question_type == "missing_word":
                self.text = text_keep_org   
        else:
            if self.question_type == "correct_order":
                self.text = unordered_text
            
        lines = textwrap.wrap(self.text, width=35)
        y_text = 100

        for line in lines:
            self.img.text((50, y_text), line, font = Settings.FONT_BODY, fill=(0, 115, 255))
            y_text += 50

        return self.img
    
    def meaning_text_line(self):
        self.img.text((50, 780), "Meaning of '" + self.missing_word + "':",
            font=Settings.FONT_TITLE, fill=(0, 115, 255)) 
        lines = textwrap.wrap(self.missing_word_definition, width=35)
        y_text = 840
        
        for line in lines:
            self.img.text((50, y_text), line, font = Settings.FONT_BODY, fill=(255, 140, 0))
            y_text += 50
        return self.img
    
    def question_generator(self, correct_answer):
        self.img = self.first_line("question")
        self.img = self.question_or_answer_line( "question")
        self.img = self.option_lines("question")
        self.save_image.save('/data/today/question_images/'  +  self.image_file_name.replace(".", "__" + self.question_category + "__" +  "--" + self.missing_word + "--" + "___" + str(correct_answer) + "___missing_word_question.") , quality=80)
    
    def answer_generator(self, correct_answer):
        self.img = self.first_line("answer")
        self.img = self.question_or_answer_line( "answer")
        self.img = self.option_lines("answer")
        #self.img = self.meaning_text_line()
        self.save_image.save('/data/today/question_images/'  +  self.image_file_name.replace(".", "__" + self.question_category + "__" + "--" + self.missing_word + "--" + "___" + str(correct_answer) + "___missing_word_answer.")  , quality=80)
                     
def create_images_all():

    with open(Settings.ARTICLE_SENTENCES_PROCESSED_JSON_FILE) as json_file:
        data = json.load(json_file)

        for p in data:
            text_org = p['sentence']
            sentence = p['sentence']

            if is_sentence_processed(sentence):
                break

            image_name = p["image_filename"]
            bg = '/data/today/images/' + p["article_image_basename"]

            for question_cat in Settings.QUESTION_CAT_LIST:
                question = p[question_cat]
      
                if len(question) > 1:
                    print('question0', question)
                    for question in question[0]:
                        
                        if question is None:
                            break
                        if question.get('base') is None:
                            print ('it is null')
                            break

                        answers = []
                        text_adj = []
                        
                        print('question', question)
                        missing_word = question["base"]
                                         
                        for word in sentence.split():   
                            print('word', word)
                            word_org = word                     
                            word = word.translate(str.maketrans('','',string.punctuation))
                         
                            if word == missing_word:
                                text_adj.append("____")
                            else:
                                text_adj.append(word_org)
                        
                        text = ' '.join(map(str, text_adj))
                          
                        #text = text_org.replace(str(missing_word), "_____")
                        
                        answers.append(question["base"])
                        answers.append(question["option1"])
                        answers.append(question["option2"])
                        answers.append(question["option3"])              
                        random.shuffle(answers)
                        
                        for i, answer in enumerate(answers):
                            if answer == missing_word:
                                correct_answer = i
                            
                        print ('answers', answers)
                        image = CreateImage("missing_word", question_cat.upper(), text, text_org, answers, missing_word, 'missing_word_definition', image_name, bg)
                        image.question_generator(correct_answer)
                      
                        image_a = CreateImage("missing_word", question_cat.upper(), text, text_org, answers, missing_word, 'missing_word_definition', image_name, bg)
                        image_a.answer_generator(correct_answer)
            time.sleep(1)