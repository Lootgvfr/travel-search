import mongoengine
import datetime


class User(mongoengine.Document):
    username = mongoengine.StringField(max_length=50, min_length=3, regex='[a-zA-Z0-9-_.]{3,50}',
                                       required=True, unique=True)
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField(max_length=500, required=True)


class Message(mongoengine.Document):
    author = mongoengine.ReferenceField(User, required=True)
    dt_sent = mongoengine.DateTimeField(required=True)
    text = mongoengine.StringField(required=True)

    @property
    def html_text(self):
        return self.text.replace('\n', '<br/>')

    @property
    def html_dt_sent(self):
        return self.dt_sent.strftime('%H:%M - %d %b %Y')
