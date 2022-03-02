from celery import Celery
from flask import Blueprint
import os
from dotenv import load_dotenv

app_cel = Blueprint('mainn', __name__)

load_dotenv()
broker = os.environ.get('CELERY_BROKER_URL')
def make_celery(app):
    celery = Celery(app.import_name,backend = str(broker), broker=str(broker))
    return celery

# for creating celery object
def create_celery(app):
    celery = make_celery(app)
    return celery

celery = create_celery(app_cel)
