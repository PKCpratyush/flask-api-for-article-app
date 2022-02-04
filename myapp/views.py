from flask import Blueprint
from flask import jsonify, request, make_response
import jwt
import os
from functools import wraps
import datetime
from .models import db, User, Articles, Science, Sports, Entertainment, Politics
from .serializer import ArticleSerializer, TagSerializer

# from hashlib import sha256, encode
from flask_restful import Resource, Api

app = Blueprint('main', __name__)

api = Api()
#############################################3 JWT ###########################################################################################


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "token" in request.headers:
            token = request.headers["token"]

        if not token:
            return jsonify({"message": "a valid token is missing"})
        try:
            data = jwt.decode(token, str(os.environ.get('SECRET_KEY')), algorithms=["HS256"])
            current_user = User.query.filter_by(user_name=data["public_id"]).first()
            if current_user.verified == False:
                return jsonify({"message": "User still not verified with otp"})
        except:
            return jsonify({"message": "token is invalid"})

        return f(current_user, *args, **kwargs)

    return decorator


###########333 ROUTES AND VIEWS ###########################################################################################--------------------------------------------------------------------------------------

from random import randrange
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from decouple import config


def send_mail(email, msg):
    message = Mail(
        from_email="pkc.testmail@gmail.com",
        to_emails=email,
        subject="OTP verification mail",
        html_content="<strong> and easy to do anywhere, even with python </strong>"
        + "\n"
        + msg,
    )

    try:
        sg = SendGridAPIClient(config("sengridkey"))
        response = sg.send(message)
        print(response.body)

    except Exception as e:
        print(e)


@app.route("/", methods=["GET"])
def home():
    return {
        "Here is what you can do with this api": "You can have /user/, /otp/, /article/ and /tag/ urls with various methods enjoy !"
    }


class UserVerificationAndLogin(Resource):
    def get(self):

        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response(
                "could not verify",
                401,
                {"WWW.Authentication": 'Basic realm: "login required"'},
            )

        user = User.query.filter_by(
            user_name=auth.username, password=auth.password
        ).first()
        if not user:
            return {
                "msg": "No such user found! Please register yourselves on /user/ url with post request"
            }

        if user.verified == False:
            return {"msg": "User not verified! Please verify with the otp"}

        token = jwt.encode(
            {
                "public_id": user.user_name,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=50),
            },
            str(os.environ.get('SECRET_KEY')),
            "HS256",
        )

        return jsonify({"token": token})

    def post(self):
        data = request.get_json()
        username = data.get("user_name")
        email = data.get("email")
        password = data.get("password")
        print(username, email, password)
        otp = str(randrange(1000, 9999))
        if None in [username, email, password]:
            return {"msg": "missing fields! please provide all the fields"}

        ## msg generation and sending ##
        msg = "{} your one time password please verify for the registration".format(otp)

        send_mail(email, msg)

        user_object = User(user_name=username, email=email, password=password, otp=otp)

        db.session.add(user_object)
        db.session.commit()

        return {
            "username": username,
            "email": email,
            "msg": "Kindly register with the otp sent on /otp/ url",
        }


class OTPVerification(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("user_name")
        otp = data.get("otp")
        if None in [username, otp]:
            return {"msg": "Invalid Credentials provided"}

        user = User.query.filter_by_by(user_name=username).first()
        if not user:
            return {"msg": "User not found"}

        if user.otp != otp:
            return {"msg": "OTP not matched"}
        user.verified = True
        db.session.add(user)
        db.session.commit()

        return {"msg": "User verified successfully"}


class ArticleCRUD(Resource):
    decorators = [token_required]

    def get(self, user):
        articles = Articles.query.all()
        if articles:
            serialized_data = ArticleSerializer(many=True).dump(articles)
            return serialized_data
        return jsonify({"msg": "No articles available"})

    def post(self, user):
        data = request.get_json()
        article_name = data.get("article_name")
        article = data.get("article")
        tags = data.get("tags")
        if None in [article_name, article, tags]:
            return {"msg": "Please provide complete details please"}
        article_object = Articles(
            user=user.user_name, article_name=article_name, article=article, tags=tags
        )
        db.session.add(article_object)
        db.session.commit()

        tag_list = list(tags.split(","))
        for i in tag_list:
            if "Science" in i:
                tag_object = Science(article=article_name)
                db.session.add(tag_object)
                db.session.commit()

            elif "Entertainment" in i:
                tag_object = Entertainment(article=article_name)
                db.session.add(tag_object)
                db.session.commit()

            elif "Sports" in i:
                tag_object = Sports(article=article_name)
                db.session.add(tag_object)
                db.session.commit()

            elif "Politics" in i:
                tag_object = Politics(article=article_name)
                db.session.add(tag_object)
                db.session.commit()

        return {"msg": "Your Article is saved successfully"}

    def delete(self, user):
        data = request.get_json()
        article_name = data.get("article_name")

        if article_name is None:
            return {"msg": "Please provide article name to delete"}

        article = Articles.query.filter_by(article_name=article_name).first()
        if article is None:
            return {"msg": "article not found"}

        if article.user != user.user_name:
            return {"msg", "You are not authorized to delete this article"}

        db.session.delete(article)
        db.session.commit()
        return {"msg": "Your article has been deleted"}

    def put(self, user):
        data = request.get_json()
        article_name = data.get("article_name")
        article = data.get("article")

        if None in [article_name, article]:
            return {"msg": "Important parameters missing"}

        article_object = Articles.query.filter_by(article_name=article_name).first()
        if article_object is None:
            return {"msg": "article not found"}

        if article_object.user != user.user_name:
            return {"msg", "You are not authorized to edit this article"}

        article_object.article = article
        db.session.commit()

        return {"msg": "Articles updated successfully"}


class TagBasedView(Resource):
    decorators = [token_required]

    def get(self, user):
        data = request.get_json()
        tag_name = data.get("tag")

        if tag_name in ["Science", "Entertainment", "Politics", "Sports"]:
            if tag_name == "Science":
                articles = Science.query.all()

                if not articles:
                    return {"msg": "No articles of this tag"}

                serialized_data = TagSerializer(many=True).dump(articles)

                json_data_to_return = {}
                for article in serialized_data:
                    article_name = article.get("article")
                    json_data_to_return[
                        "{}".format(article_name)
                    ] = ArticleSerializer().dump(
                        Articles.query.filter_by(article_name=article_name).first()
                    )
                return jsonify(json_data_to_return)

            elif tag_name == "Sports":
                articles = Sports.query.all()

                if not articles:
                    return {"msg": "No articles of this tag"}
                # print(articles)
                serialized_data = TagSerializer(many=True).dump(articles)
                # print(type(serialized_data), serialized_data)
                json_data_to_return = {}
                for article in serialized_data:
                    article_name = article.get("article")
                    json_data_to_return[
                        "{}".format(article_name)
                    ] = ArticleSerializer().dump(
                        Articles.query.filter_by(article_name=article_name).first()
                    )
                return jsonify(json_data_to_return)

            elif tag_name == "Entertainment":
                articles = Entertainment.query.all()

                if not articles:
                    return {"msg": "No articles of this tag"}

                serialized_data = TagSerializer(many=True).dump(articles)

                json_data_to_return = {}
                for article in serialized_data:
                    article_name = article.get("article")
                    json_data_to_return[
                        "{}".format(article_name)
                    ] = ArticleSerializer().dump(
                        Articles.query.filter_by(article_name=article_name).first()
                    )
                return jsonify(json_data_to_return)

            elif tag_name == "Politics":
                articles = Politics.query.all()

                if not articles:
                    return {"msg": "No articles of this tag"}

                serialized_data = TagSerializer(many=True).dump(articles)

                json_data_to_return = {}
                for article in serialized_data:
                    article_name = article.get("article")
                    json_data_to_return[
                        "{}".format(article_name)
                    ] = ArticleSerializer().dump(
                        Articles.query.filter_by(article_name=article_name).first()
                    )
                return jsonify(json_data_to_return)
        return {"msg": "No such tag found"}


################### ROUTES ########################################################################################################################

api.add_resource(OTPVerification, "/otp/")
api.add_resource(UserVerificationAndLogin, "/user/")
api.add_resource(ArticleCRUD, "/article/")
api.add_resource(TagBasedView, "/tag/")