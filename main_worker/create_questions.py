import json
import spacy
from spacy.matcher import Matcher

from add_options import AddOptions
import question_rules as qr
import tag_list as tag_list

import sqlite3

import json
from datetime import datetime
import time

nlp = spacy.load('en_core_web_md')
taglist = tag_list.taglist

def filename_generator():
    time.sleep(1)
    file_name = '' + \
        str(datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")) + '.jpg'
    return file_name

class QuestionFilter:
    def __init__(self, taglist, my_doc) -> None:
        self.taglist = taglist
        self.my_doc = my_doc
        self.__rule = list()
        self.__matcher = list()

        for i in range(len(taglist)):
            self.__rule.append(qr.rules[taglist[i]])
            self.__matcher.append(Matcher(nlp.vocab))
            self.__matcher[i].add(taglist[i], self.__rule[i])

    def __call__(self):
        return self.write_linguistic_features()
        
    def write_linguistic_features(self):
        lf_dict = {}
        comp_lf_dict = {}

        for i in range(len(taglist)):
            matches = self.__matcher[i](self.my_doc)
            question_list = []
            option_list = []
            for match_id, start, end in matches:
                
                lf_dict = {}
                # Get the string representation
                string_id = nlp.vocab.strings[match_id]
                span = self.my_doc[start:end]  # The matched span
                lf_dict[string_id] = span.text

                option2 = 0

                if self.taglist[i]=="VERB":
                    option2 = 1
                    vaa = 'v'

                if self.taglist[i]=="ADVERB":
                    option2 = 1
                    vaa = 'r'

                if self.taglist[i]=="ADJECTIVE":
                    option2 = 1
                    vaa = 'a'

                if self.taglist[i]=="NOUN":
                    option2 = 1
                    vaa = 'n'

                if lf_dict:
                    question_list.append(lf_dict)
                    temp = AddOptions(self.taglist[i], lf_dict)

                    if option2 == 0:
                        option_list.append(temp.add_options()) 
                    else:
                        option_list.append(temp.add_options_vocab(nlp, vaa))         
                
            question_list.insert(0, option_list)
            comp_lf_dict[self.taglist[i]] = question_list

        return comp_lf_dict
    
    def include_options(self, item, vocab):
        temp = AddOptions(self.tag, self)

        if vocab==0:
            item.insert(0,item.add_options())
        else:
            item.insert(0, item.add_options_vocab(nlp, vocab))
        return


def update_sentence_processed(sentence, image_filename):
    try:
        sqliteConnection = sqlite3.connect('/data/database/lingomooAPP.db')
        sqliteConnection.row_factory = sqlite3.Row  
        cursor = sqliteConnection.cursor()

        print("Connected to SQLite")
        
        sql_update_query = "UPDATE sentences SET sentence_processed = 1, image_filename = ? WHERE sentence = ?"
        cursor.execute(sql_update_query, (image_filename, sentence,))
        sqliteConnection.commit()
        
        print("Record Updated successfully")

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")


def get_all():
    try:
        sqliteConnection = sqlite3.connect('/data/database/lingomooAPP.db')
        sqliteConnection.row_factory = sqlite3.Row  
        cursor = sqliteConnection.cursor()

        print("Connected to SQLite")


        sql_select_query = """SELECT * FROM sentences WHERE sentence_processed = ?"""
        cursor.execute(sql_select_query, (0,))
        records = cursor.fetchall()

        data = list()
        with open('/data/data.json', 'w', encoding='utf-8') as f:
            for row in records:
                item = dict()
                sentence = dict(row)['sentence']
                article_image_src = dict(row)['article_image_src']
                article_image_basename = dict(row)['article_image_basename']

                my_doc = nlp(sentence)
                print(my_doc)
                item['sentence'] = sentence
                item['article_image_src'] = article_image_src
                item['article_image_basename'] = article_image_basename
                item['image_filename'] = filename_generator()
                item.update(QuestionFilter(taglist, my_doc)())  
                print(item)
                data.append(item)
                update_sentence_processed(sentence, item['image_filename'])

            cursor.close()
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")