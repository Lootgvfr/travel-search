import hashlib
import random
import json

from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape

from app.models import CityCache, RequestCache
from settings import base_api_url_m, headers, headers_m, base_api_url,\
    api_key, city_search_mashape, geonames_base_url, geonames_username

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
city_types = ['village', 'town', 'city', 'capital', 'metropolis']


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
    srch = await translate_request(search_term)
    search_term = url_escape(srch)

    if city_search_mashape:
        url = base_api_url_m + 'Geocode?countryCode=UA&languageCode=UA&query={}'.format(search_term)
        response = await http_client.fetch(url, headers=headers_m)
    else:
        url = base_api_url + 'Geocode?key={}&countryCode=UA&languageCode=UA&query={}'\
            .format(api_key, search_term)
        response = await http_client.fetch(url, headers=headers)

    response_dict = json.loads(response.body, encoding='utf-8')
    result = []
    futures = []

    for place in response_dict['places']:
        if place['kind'] in city_types:
            futures.append(translate_place(place['shortName'], place['countryName']))

    caches = []
    for future in futures:
        caches.append(await future)

    for cache in caches:
        result.append({
            'city': cache.name_uk,
            'country': cache.country_uk,
        })
    return result


async def translate_place(city, country):
    cache = CityCache.objects(name_en=city, country_en=country)
    if len(cache) == 1:
        return cache[0]

    url = '{}searchJSON?username={}&maxRows=1&lang=uk&q={}'.format(
        geonames_base_url,
        geonames_username,
        url_escape(', '.join(c for c in (city, country))),
    )
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(url, headers=headers)
    response_dict = json.loads(response.body, encoding='utf-8')
    if len(response_dict['geonames']) > 0:
        name_uk = response_dict['geonames'][0]['name']
        country_uk = response_dict['geonames'][0]['countryName']
    else:
        name_uk = city
        country_uk = country

    cache = CityCache(
        name_en=city,
        country_en=country,
        name_uk=name_uk,
        country_uk=country_uk,
    ).save()
    return cache


async def translate_request(request):
    cache = RequestCache.objects(request_uk=request)
    if len(cache) == 1:
        return cache[0].request_en

    url = '{}searchJSON?username={}&maxRows=1&lang=en&q={}'.format(
        geonames_base_url,
        geonames_username,
        url_escape(request),
    )
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(url, headers=headers)
    response_dict = json.loads(response.body, encoding='utf-8')
    if len(response_dict['geonames']) > 0:
        cache = RequestCache(
            request_uk=request,
            request_en=response_dict['geonames'][0]['name']
        ).save()
        return cache.request_en
    else:
        return request


def validate_search_form(required_fields, data):
    result = []
    for field in required_fields:
        if not data.get(field):
            result.append({
                'path': field,
                'text': 'Це поле є обов\'язковим',
            })

    for field in ['from', 'to']:
        if data.get(field):
            try:
                city, country = data[field].split(', ')
                CityCache.objects(name_uk=city, country_uk=country)[0]
            except Exception as e:
                print(e)
                result.append({
                    'path': field,
                    'text': 'Виберіть значення зі списку',
                })

    if not any(data.get(field) for field in ['search_bus', 'search_flight', 'search_train']):
        result.append({
            'path': 'transport_types',
            'text': 'Виберіть хоча б один вид транспорту',
        })

    if data.get('price_lower') and data.get('price_upper') and int(data['price_lower']) > int(data['price_upper']):
        result.append({
            'path': 'price_upper',
            'text': 'Верхня межа не може бути меньше нижньої'
        })

    for field in ['price_lower', 'price_upper']:
        if data.get(field) and int(data[field]) < 0:
            result.append({
                'path': field,
                'text': 'Значення не може бути від\'ємним',
            })

    return result
