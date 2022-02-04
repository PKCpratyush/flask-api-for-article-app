from flask import Flask, Blueprint
import os
from .models import db
from .serializer import ma
from .views import app, api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api

# db = SQLAlchemy()
# ma = Marshmallow()
# api = Api()

def create_app():
    app1 = Flask(__name__)
    DB_URL = "postgresql://mr_pkc:pratyush@127.0.0.1/flask_db"

    app1.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app1.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app1.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
    db.init_app(app1)
    ma.init_app(app1)
    api.init_app(app1)
    app1.register_blueprint(app)
    
    return app1




# if __name__ == '__main__':
#     app.run(debug=True)