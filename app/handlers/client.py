from tornado.web import HTTPError

from app.helpers import search_options, validate_search_form
from app.models import SearchRequest, SavedOffer
from app.search_backend import Backend
from .base import BaseHandler


class HomeHandler(BaseHandler):
    def get(self):
        self.render('home.html')
        return


class SearchRequestHandler(BaseHandler):
    required_fields = ['from', 'to']

    def post(self):
        data = {
            k: str(v[0], encoding='utf-8') for k, v in self.request.arguments.items()
        }

        val_result = validate_search_form(self.required_fields, data)
        if val_result:
            self.write({
                'type': 'error',
                'errors': val_result
            })
            return

        s_request = SearchRequest(
            req_from=data['from'],
            req_to=data['to'],
            search_bus=data.get('search_bus'),
            search_train=data.get('search_train'),
            search_flight=data.get('search_flight'),
            price_lower_limit=data['price_lower'] if data.get('price_lower') else None,
            price_upper_limit=data['price_upper'] if data.get('price_upper') else None,
        )
        if self.current_user:
            s_request.user = self.current_user

        s_request.save()
        self.write({
            'type': 'redirect',
            'redirect_url': self.reverse_url('search-results', s_request.guid)
        })
        return


class SearchResultsPageHandler(BaseHandler):
    def get(self, guid):
        if len(SearchRequest.objects(guid=guid)) != 1:
            raise HTTPError(404)
        self.render('search_results.html', guid=guid, best_offers=False)
        return


class SearchResultsDataHandler(BaseHandler):
    async def get(self, guid):
        req = SearchRequest.objects(guid=guid)
        if len(req) != 1:
            raise HTTPError(404)

        search = req[0]
        if search.result:
            self.write({
                'type': 'success',
                'records': search.result,
            })
        else:
            backend = Backend(search)
            self.write({
                'type': 'success',
                'records': await backend.search(),
            })
        return


class BestOffersPageHandler(BaseHandler):
    def get(self):
        self.render('best_offers.html', best_offers=True)
        return


class BestOffersDataHandler(BaseHandler):
    def get(self):
        routes = []

        for offer in SavedOffer.objects(type='best').order_by('-dt_created')[:10]:
            routes.append(offer.route.as_dict())

        self.write({
                'type': 'success',
                'records': routes,
            })
        return


class CityOptionsHandler(BaseHandler):
    async def get(self, search_term):
        self.write({
            'type': 'success',
            'options': await search_options(search_term),
        })
        return


class SaveOfferHandler(BaseHandler):
    def get(self, guid, order):
        if not self.current_user:
            raise HTTPError(404)

        req = SearchRequest.objects(guid=guid)
        if len(req) != 1:
            raise HTTPError(404)
        search = req[0]

        found = False
        for route in search.routes:
            if route.order == int(order):
                found = True
                existing = SavedOffer.objects(pl_from=route.pl_from, pl_to=route.pl_to,
                                              user=self.current_user, price=route.price_raw)
                if len(existing) == 0:
                    SavedOffer(
                        type='by_user',
                        user=self.current_user,
                        pl_from=route.pl_from,
                        pl_to=route.pl_to,
                        price=route.price_raw,
                        route=route
                    ).save()
                else:
                    self.write({
                        'type': 'already_saved'
                    })
                    return
            # end
        # end

        if not found:
            raise HTTPError(404)

        self.write({
            'type': 'success',
        })
        return


class CabinetHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            raise HTTPError(404)

        requests = SearchRequest.objects(user=self.current_user).order_by('-dt_request')
        self.render('cabinet.html', best_offers=True, requests=requests)
        return


class SavedOffersDataHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            raise HTTPError(404)

        routes = []

        for offer in SavedOffer.objects(user=self.current_user).order_by('-dt_created'):
            routes.append(offer.route.as_dict())

        self.write({
            'type': 'success',
            'records': routes,
        })
        return
