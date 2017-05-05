from tornado.web import url

from app.handlers import HomeHandler, LogoutHandler

urls = [
    url(r'/$', HomeHandler, name='home'),
    url(r'/logout$', LogoutHandler, name='logout'),
]
