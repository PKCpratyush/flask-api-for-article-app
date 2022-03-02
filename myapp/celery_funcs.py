from .celery_task import celery
from time import sleep

@celery.task()
def testing_f():
    sleep(5)
    # return {"msg":"Celery return"}