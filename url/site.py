from tornado.web import url

from app.handlers import HomeHandler, LogoutHandler, AdminHomeHandler, \
    SearchRequestHandler, SearchResultsPageHandler

urls = [
    url(r'/$', HomeHandler, name='home'),
    url(r'/logout$', LogoutHandler, name='logout'),
    url(r'/search_request$', SearchRequestHandler, name='search-request'),
    url(r'/search_results$', SearchResultsPageHandler, name='search-results'),

    url(r'/admin$', AdminHomeHandler, name='admin-home'),
]
