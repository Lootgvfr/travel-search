from tornado.web import url

from app.handlers import SearchResultsDataHandler, CityOptionsHandler,\
    SearchRequestHandler, BestOffersDataHandler, SaveOfferHandler, \
    SavedOffersDataHandler, StatisticsImgHandler, PredictionImgHandler, \
    FlightChoicesHandler

urls = [
    url(r'/ajax/search_request$', SearchRequestHandler, name='search-request'),
    url(r'/ajax/best_offers$', BestOffersDataHandler, name='best-offers-data'),
    url(r'/ajax/saved_offers$', SavedOffersDataHandler, name='saved-offers-data'),
    url(r'/ajax/search_results/(?P<guid>[\w-]+)$', SearchResultsDataHandler, name='search-results-data'),
    url(r'/ajax/city_options/(?P<search_term>[\w %,-]+)$', CityOptionsHandler, name='city-options'),
    url(r'/ajax/save_offer/(?P<guid>[\w-]+)/(?P<order>[0-9]+)$', SaveOfferHandler, name='save-offer'),
    url(r'/ajax/flights/(?P<guid>[\w-]+)$', FlightChoicesHandler, name='flights'),

    url(r'/admin/ajax/statistics/(?P<year>[0-9]+)$', StatisticsImgHandler, name='admin-statistics'),
    url(r'/admin/ajax/prediction/(?P<year>[0-9]+)$', PredictionImgHandler, name='admin-prediction'),
]
