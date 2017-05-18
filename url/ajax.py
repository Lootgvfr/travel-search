from tornado.web import url

from app.handlers import SearchResultsDataHandler, CityOptionsHandler,\
    SearchRequestHandler, BestOffersDataHandler, SaveOfferHandler, \
    SavedOffersDataHandler

urls = [
    url(r'/ajax/search_request$', SearchRequestHandler, name='search-request'),
    url(r'/ajax/best_offers$', BestOffersDataHandler, name='best-offers-data'),
    url(r'/ajax/saved_offers$', SavedOffersDataHandler, name='saved-offers-data'),
    url(r'/ajax/search_results/(?P<guid>[\w-]+)$', SearchResultsDataHandler, name='search-results-data'),
    url(r'/ajax/city_options/(?P<search_term>[\w %,-]+)$', CityOptionsHandler, name='city-options'),
    url(r'/ajax/save_offer/(?P<guid>[\w-]+)/(?P<order>[0-9]+)$', SaveOfferHandler, name='save-offer'),
]
