from .models import Articles
from flask_marshmallow import Marshmallow

ma = Marshmallow()


class ArticleSerializer(ma.Schema):
    class Meta:
        model = Articles
        fields = ("user", "article_name", "article", "tags")


class TagSerializer(ma.Schema):
    class Meta:
        fields = ("article",)
