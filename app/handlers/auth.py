from app.helpers import encode_password, check_password
from app.models import User
from .base import BaseHandler


class LogoutHandler(BaseHandler):
    def get(self):
        self.set_secure_cookie('auth', '')
        self.redirect(self.reverse_url('home'))
        return


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')
        return

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
                'message': 'Логін чи пароль є невірним'
            }
        self.write(result)
        return


class RegistrationHandler(BaseHandler):
    def get(self):
        self.render('registration.html')
        return

    def post(self):
        username = self.get_argument('username')
        email = self.get_argument('email')
        password = self.get_argument('password')
        repeat_password = self.get_argument('repeat-password')
        try:
            if not password == repeat_password:
                raise ValueError('Введені паролі не співпадають')

            if User.objects(username=username) or User.objects(email=email):
                raise ValueError('Користувач з заданим ім\'ям чи поштою вже зареєстрований')

            p = encode_password(password)
            User(username=username, email=email, password=p).save()

            self.set_secure_cookie('auth', username)
            result = {
                'type': 'redirect',
                'redirect_url': self.reverse_url('home')
            }

        except Exception as e:
            result = {
                'type': 'error',
                'message': str(e)
            }
        self.write(result)
        return
