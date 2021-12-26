from flask import Flask
from celery import Celery

app = Flask(__name__)
simple_app = Celery('simple_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@app.route('/simple_start_task')
def call_method():
    app.logger.info("Invoking Method ")
    r = simple_app.send_task('tasks.workflow', kwargs={})
    app.logger.info(r.backend)
    return r.id

@app.route('/write_to_firebase')
def write_method():
    app.logger.info("Invoking Method ")
    r = simple_app.send_task('tasks.write_to_firebase', kwargs={})
    app.logger.info(r.backend)
    return r.id

@app.route('/simple_task_status/<task_id>')
def get_status(task_id):
    status = simple_app.AsyncResult(task_id, app=simple_app)
    print("Invoking Method ")
    return "Status of the Task " + str(status.state)

@app.route('/simple_task_result/<task_id>')
def task_result(task_id):
    result = simple_app.AsyncResult(task_id).result
    return "Result of the Task " + str(result)