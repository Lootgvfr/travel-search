from tornado.web import url

from app.handlers import RegistrationHandler, LoginHandler, SearchResultsDataHandler

urls = [
    url(r'/ajax/login$', LoginHandler, name='login'),
    url(r'/ajax/registration$', RegistrationHandler, name='registration'),
    url(r'/ajax/search_results$', SearchResultsDataHandler, name='search-results-data'),
]
