FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN mkdir -p /data

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update && apt-get install -y git
RUN apt-get install -y build-essential python-dev git

RUN pip install Pyrebase

#RUN python -m pip install -U pip setuptools wheel # install/update build tools
RUN pip install -U nltk
RUN python -m nltk.downloader -d /usr/local/share/nltk_data wordnet

RUN pip install -U spacy
RUN python -m spacy download en_core_web_md


#COPY app.py /app.py
ADD . /main_worker
WORKDIR /main_worker
COPY . /main_worker
USER root

ENTRYPOINT celery -A tasks worker --beat --loglevel=info
#-Q celery_worker
#ENTRYPOINT ['celery','-A','test_celery', 'worker', '--loglevel=info']