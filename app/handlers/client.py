import json

from tornado.web import HTTPError

from app.helpers import search_options, validate_search_form
from app.models import SearchRequest
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
        ).save()

        self.write({
            'type': 'redirect',
            'redirect_url': self.reverse_url('search-results', s_request.guid)
        })
        return


class SearchResultsPageHandler(BaseHandler):
    def get(self, guid):
        if len(SearchRequest.objects(guid=guid)) != 1:
            raise HTTPError(404)
        self.render('search_results.html', guid=guid)
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
                'records': json.loads(search.result, encoding='utf-8'),
            })
        else:
            backend = Backend(search)
            self.write({
                'type': 'success',
                'records': await backend.search(),
            })
        return


class CityOptionsHandler(BaseHandler):
    async def get(self, search_term):
        self.write({
            'type': 'success',
            'options': await search_options(search_term),
        })
        return
