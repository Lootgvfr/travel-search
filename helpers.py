import hashlib
import random

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_password(password):
    salt = ''.join(random.choice(ALPHABET) for _ in range(16))
    h = hashlib.sha512()
    h.update(salt.encode('utf-8'))
    h.update(password.encode('utf-8'))
    return '$'.join((salt, h.hexdigest()))


def check_password(user, password):
    salt, hashed_pass = user.password.split('$')
    h = hashlib.sha512()
    h.update(salt.encode('utf-8'))
    h.update(password.encode('utf-8'))
    return hashed_pass == h.hexdigest()
