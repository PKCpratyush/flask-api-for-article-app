from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user_name = db.Column(db.String(10), unique=True, primary_key=True)
    password = db.Column(db.String(1000))
    email = db.Column(db.String(40))
    otp = db.Column(db.String(4))
    verified = db.Column(db.Boolean(), default=False)
    logged = db.Column(db.Boolean(), default=False)

    def __init__(self, user_name, password, email, otp, verified=False, logged=False):
        self.user_name = user_name
        self.password = password
        self.email = email
        self.otp = otp
        self.verified = verified
        self.logged = logged


class Articles(db.Model):
    user = db.Column(db.ForeignKey("user.user_name", ondelete="CASCADE"))
    article_name = db.Column(db.String(), unique=True, primary_key=True)
    article = db.Column(db.String(1000))
    tags = db.Column(db.String(100))

    def __init__(self, user, article, tags, article_name):
        self.user = user
        self.article_name = article_name
        self.article = article
        self.tags = tags


class Science(db.Model):
    article = db.Column(
        db.ForeignKey("articles.article_name", ondelete="CASCADE"), primary_key=True
    )

    def __init__(self, article):
        self.article = article


class Sports(db.Model):
    article = db.Column(
        db.ForeignKey("articles.article_name", ondelete="CASCADE"), primary_key=True
    )

    def __init__(self, article):
        self.article = article


class Politics(db.Model):
    article = db.Column(
        db.ForeignKey("articles.article_name", ondelete="CASCADE"), primary_key=True
    )

    def __init__(self, article):
        self.article = article


class Entertainment(db.Model):
    article = db.Column(
        db.ForeignKey("articles.article_name", ondelete="CASCADE"), primary_key=True
    )

    def __init__(self, article):
        self.article = article