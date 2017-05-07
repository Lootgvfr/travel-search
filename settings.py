import os
import uuid

settings = {
    'debug': True,
    'login_url': '/login',
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'xsrf_cookies': True,
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'cookie_secret': '6dc43f7a-ffc2-4197-92e8-f858c1ead695',
    'autoreload': False
}

mongo_db_name = 'travel-search'
port = 8891
host = '0.0.0.0:' + str(port)

with open(os.path.join(os.path.dirname(__file__), 'api.key')) as file:
    api_key = file.readline()
base_api_url = 'https://rome2rio12.p.mashape.com/'
headers = {
    'Accept': 'application/json',
    'X-Mashape-Key': api_key,
}
