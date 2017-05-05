from tornado.web import url

from app.handlers import RegistrationHandler, LoginHandler

urls = [
    url(r'/ajax/login$', LoginHandler, name='login'),
    url(r'/ajax/registration$', RegistrationHandler, name='registration'),
]
