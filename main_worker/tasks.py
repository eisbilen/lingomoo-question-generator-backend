from celery import Celery
from celery.utils.log import get_task_logger
from celery import chain

import random

from random_article import random_tags
from get_articles import getArticles
from create_questions import get_all
from create_images import create_images_all
from write_to_firebase import sent_all_firebase
import articles_to_sql

logger = get_task_logger(__name__)
app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

def get_random_tag():
    return random_tags[random.randint(0,len(random_tags)-1)]

def get_random_page_number():
    return random.randint(0,100)

@app.task()
def get_articles():
    print('I am in TASK1')
    return getArticles(get_random_tag(), get_random_page_number())

@app.task()
def get_data(data):
    print('I am in TASK2')
    articles_to_sql.write_to_sql(data)
    return data

@app.task()
def create_q(data):
    print('I am in TASK3')
    get_all()
    return data

@app.task()
def create_i(data):
    print('I am in TASK4')
    create_images_all()
    return 'erdem tamam'

@app.task()
def write_to_firebase():
    sent_all_firebase()

@app.task()
def workflow():
    task_chain = chain(
        # task 1: 
        get_articles.s(),
        # task 2: [ dependent on the success of task 1]
        get_data.s(),
        # task 3: [ dependent on the success of task 2]
        create_q.s(),
        # task 4: [ dependent on the success of task 3]
        create_i.s(),
        # task 5: [ dependent on the success of task 3]
        #write_to_firebase.s()
    )

    # Execute task chain in default queue
    result = task_chain.apply_async()
    return result

 #app.conf.beat_schedule = {
  #      'lingomoo-workflow-every-500-seconds': {
  #           'task': 'tasks.workflow',
   #          'schedule': 500.0,
    #     },
 #}

 #app.conf.timezone = 'UTC'