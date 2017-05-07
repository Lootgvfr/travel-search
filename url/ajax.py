from tornado.web import url

from app.handlers import RegistrationHandler, LoginHandler, SearchResultsDataHandler, \
    CityOptionsHandler

urls = [
    url(r'/ajax/login$', LoginHandler, name='login'),
    url(r'/ajax/registration$', RegistrationHandler, name='registration'),
    url(r'/ajax/search_results$', SearchResultsDataHandler, name='search-results-data'),
    url(r'/ajax/city_options/(?P<search_term>[\w ,%]+)$', CityOptionsHandler, name='city-options')
]
