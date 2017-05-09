from tornado.web import url

from app.handlers import SearchResultsDataHandler, CityOptionsHandler,\
    SearchRequestHandler

urls = [
    url(r'/ajax/search_request$', SearchRequestHandler, name='search-request'),
    url(r'/ajax/search_results/(?P<guid>[\w-]+)$', SearchResultsDataHandler, name='search-results-data'),
    url(r'/ajax/city_options/(?P<search_term>[\w %,-]+)$', CityOptionsHandler, name='city-options')
]
