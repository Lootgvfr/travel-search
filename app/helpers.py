import hashlib
import random
import json

from tornado.httpclient import AsyncHTTPClient

from settings import base_api_url_m, headers, headers_m, base_api_url,\
    api_key, city_search_mashape

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


async def search_options(search_term):
    http_client = AsyncHTTPClient()
    search_term = search_term.replace(' ', '%20')

    if city_search_mashape:
        url = base_api_url_m + 'Geocode?countryCode=UA&languageCode=UA&query={}'.format(search_term)
        response = await http_client.fetch(url, headers=headers_m)
    else:
        url = base_api_url + 'Geocode?key={}&countryCode=UA&languageCode=UA&query={}'\
            .format(api_key, search_term)
        response = await http_client.fetch(url, headers=headers)

    response_dict = json.loads(response.body, encoding='utf-8')
    result = []
    for place in response_dict['places']:
        if place['kind'] in city_types:
            result.append({
                'city': place['shortName'],
                'country': place['countryName']
            })
    return result


def validate_search_form(required_fields, data):
    result = []
    for field in required_fields:
        if not data.get(field):
            result.append({
                'path': field,
                'text': 'This field is required',
            })

    if not any(data.get(field) for field in ['search_bus', 'search_flight', 'search_train']):
        result.append({
            'path': 'transport_types',
            'text': 'At least one transport type is required',
        })

    if data.get('price_lower') and data.get('price_upper') and int(data['price_lower']) > int(data['price_upper']):
        result.append({
            'path': 'price_upper',
            'text': 'Upper limit can not be greater than the lower'
        })

    for field in ['price_lower', 'price_upper']:
        if data.get(field) and int(data[field]) < 0:
            result.append({
                'path': field,
                'text': 'Value can not be negative',
            })

    return result
