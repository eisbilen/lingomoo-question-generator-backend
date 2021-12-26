import sqlite3
import re

def remove_puct(sentence):
    sentence_wo_punct = re.sub('[^A-Za-z0-9 ]+', '', sentence)
    return sentence_wo_punct

def sentence_length_calc(sentence):
    sentence_length = len(sentence.split())
    return sentence_length

def write_to_sql(data):
    connection = sqlite3.connect("/data/database/lingomooAPP.db")
    cursor = connection.cursor()

    command1 = """CREATE TABLE IF NOT EXISTS
    sentences(sentence_id INTEGER PRIMARY KEY, date_scrapped TEXT, article_tag TEXT, article_url TEXT, article_image_src TEXT, article_image_basename TEXT, image_filename TEXT, website TEXT, sentence TEXT, sentence_length INTEGER, difficulty_score FLOAT, sentence_processed INTEGER)"""

    cursor.execute(command1)

    for l in data:
        date_scrapped = l['datetime']
        article_tag = l['tag']
        article_url = l['article_url']
        article_image_src = l['article_image_src']
        article_image_basename = l['article_image_basename']
        image_filename = ''
        website = l['website']

        for sentence_article in l['article']:
            sentence = sentence_article.replace("READ MORE:", "")
            sentence = sentence.replace('"', '')
            sentence = sentence.lstrip()
                
            sentence_length = sentence_length_calc(remove_puct(sentence_article))
            difficulty_score = 0
            sentence_processed = 0
            print(sentence)

            # only adding the sentences with the word count between 7 and 15
            if sentence_length > 7 and sentence_length < 15:
                cursor.execute("INSERT INTO sentences (date_scrapped, article_tag, article_url, article_image_src, article_image_basename, image_filename, website, sentence, sentence_length, difficulty_score, sentence_processed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (date_scrapped, article_tag, article_url, article_image_src, article_image_basename, image_filename, website, sentence, sentence_length, difficulty_score, sentence_processed))
                connection.commit()

    # deletes the dublicate lines containing the same sentece
    cursor.execute("DELETE FROM sentences WHERE sentence_id NOT IN (SELECT min(sentence_id) FROM sentences GROUP BY sentence)")
    connection.commit() 
    cursor.close()