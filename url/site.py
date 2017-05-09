from tornado.web import url

from app.handlers import HomeHandler, LogoutHandler, RegistrationHandler, \
    LoginHandler, SearchResultsPageHandler, AdminHomeHandler

urls = [
    url(r'/$', HomeHandler, name='home'),
    url(r'/login$', LoginHandler, name='login'),
    url(r'/registration$', RegistrationHandler, name='registration'),
    url(r'/logout$', LogoutHandler, name='logout'),
    url(r'/search_results/(?P<guid>[\w-]+)$', SearchResultsPageHandler, name='search-results'),

    url(r'/admin$', AdminHomeHandler, name='admin-home'),
]
