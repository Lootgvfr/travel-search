import hashlib
import random
import requests

from settings import base_api_url, headers

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
city_types = ['village', 'town', 'city', 'capital']


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


def search_options(search_term):
    url = base_api_url + 'Geocode?countryCode=UA&languageCode=UA&query={}'.format(search_term)
    response = requests.get(url, headers=headers)
    response_dict = response.json()

    result = []
    for place in response_dict['places']:
        if place['kind'] in city_types:
            result.append({
                'city': place['shortName'],
                'country': place['countryName']
            })
    return result
