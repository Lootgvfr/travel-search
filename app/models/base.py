import mongoengine
import datetime

from .search import Route


class User(mongoengine.Document):
    username = mongoengine.StringField(max_length=50, min_length=3, regex='[a-zA-Z0-9-_.]{3,50}',
                                       required=True, unique=True)
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField(max_length=500, required=True)
    is_superuser = mongoengine.BooleanField(default=False)
    is_moderator = mongoengine.BooleanField(default=False)


class CityCache(mongoengine.Document):
    name_en = mongoengine.StringField(max_length=500, required=True)
    country_en = mongoengine.StringField(max_length=500, required=True)
    name_uk = mongoengine.StringField(max_length=500, required=True)
    country_uk = mongoengine.StringField(max_length=500, required=True)


class RequestCache(mongoengine.Document):
    request_en = mongoengine.StringField(max_length=500, required=True)
    request_uk = mongoengine.StringField(max_length=500, required=True)


class SavedOffer(mongoengine.Document):
    dt_created = mongoengine.DateTimeField(required=True)
    type = mongoengine.StringField(choices=['best', 'by_user'], required=True)
    user = mongoengine.ReferenceField(User)

    pl_from = mongoengine.StringField(max_length=100, required=True)
    pl_to = mongoengine.StringField(max_length=100, required=True)
    price = mongoengine.IntField(required=True)
    route = mongoengine.EmbeddedDocumentField(Route)

    def __init__(self, *args, **kwargs):
        super(SavedOffer, self).__init__(*args, **kwargs)
        self.dt_created = datetime.datetime.now()
