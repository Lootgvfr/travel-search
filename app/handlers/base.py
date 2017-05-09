from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from app.models import User


class CurrentUserMixin:
    def get_current_user(self):
        cookie = self.get_secure_cookie('auth')
        try:
            username = str(cookie, 'utf-8')
            return User.objects(username=username)[0]
        except (IndexError, TypeError) as e:
            return None


class BaseHandler(CurrentUserMixin, RequestHandler):
    pass


class BaseWebsocketHandler(CurrentUserMixin, WebSocketHandler):
    pass
