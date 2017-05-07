import mongoengine


class User(mongoengine.Document):
    username = mongoengine.StringField(max_length=50, min_length=3, regex='[a-zA-Z0-9-_.]{3,50}',
                                       required=True, unique=True)
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField(max_length=500, required=True)
    is_superuser = mongoengine.BooleanField(default=False)
    is_moderator = mongoengine.BooleanField(default=False)
