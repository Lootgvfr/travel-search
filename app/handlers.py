import tornado.websocket

from app.helpers import encode_password, check_password
from models import User


class CurrentUserMixin:
    def get_current_user(self):
        cookie = self.get_secure_cookie('auth')
        try:
            username = str(cookie, 'utf-8')
            return User.objects(username=username)[0]
        except (IndexError, TypeError) as e:
            return None


class BaseHandler(CurrentUserMixin, tornado.web.RequestHandler):
    pass


class BaseWebsocketHandler(CurrentUserMixin, tornado.websocket.WebSocketHandler):
    pass


class HomeHandler(BaseHandler):
    def get(self):
        self.render('home.html')


class LogoutHandler(BaseHandler):
    def get(self):
        self.set_secure_cookie('auth', '')
        self.redirect(self.reverse_url('home'))


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        try:
            user = User.objects(username=username)[0]
            if not check_password(user, password):
                raise ValueError()
            self.set_secure_cookie('auth', username)

            result = {
                'type': 'redirect',
                'redirect_url': self.reverse_url('home')
            }

        except Exception as e:
            result = {
                'type': 'error',
                'message': 'Invalid credentials'
            }
        self.write(result)


class RegistrationHandler(BaseHandler):
    def get(self):
        self.render('registration.html')

    def post(self):
        username = self.get_argument('username')
        email = self.get_argument('email')
        password = self.get_argument('password')
        repeat_password = self.get_argument('repeat-password')
        try:
            if not password == repeat_password:
                raise ValueError('Passwords do not match')

            if User.objects(username=username) or User.objects(email=email):
                raise ValueError('User with given username or email already exists')

            p = encode_password(password)
            User(username=username, email=email, password=p).save()
            self.set_secure_cookie('auth', username)

            result = {
                'type': 'redirect',
                'redirect_url': self.reverse_url('login')
            }

        except Exception as e:
            result = {
                'type': 'error',
                'message': str(e)
            }
        self.write(result)
