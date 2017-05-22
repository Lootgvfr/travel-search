import datetime

from tornado.web import HTTPError

from app.prediction_backend import PredictionBackend
from app.models import SearchRequest, User
from .base import BaseHandler


class AdminHomeHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user or not user.is_superuser:
            raise HTTPError(404)

        last_hour = datetime.datetime.now() - datetime.timedelta(hours=1)
        last_hour_reqs = len(SearchRequest.objects(dt_request__gte=last_hour))

        map_f = "function map(){ emit(this.req_from + ' - ' + this.req_to, 1); }"
        reduce_f = "function reduce(key, values){ return Array.sum(values); }"
        routes = sorted(list(SearchRequest.objects.map_reduce(map_f, reduce_f, "routes")),
                        key=lambda r: r.value, reverse=True)
        most_popular_route = routes[0].key if len(routes) > 0 else 'Немає'

        pipeline = [
            {'$match': {'is_superuser': False}},
            {
                '$lookup': {
                    'from': 'saved_offer',
                    'localField': '_id',
                    'foreignField': 'user',
                    'as': 'saved_offers'
                }
            },
            {
                '$project': {
                    'has_saved': {
                        '$cond': {
                            'if': {'$gte': [{'$size': "$saved_offers"}, 1]},
                            'then': True,
                            'else': False
                        }
                    }
                }
            },
            {'$match': {'has_saved': True}},
            {'$count': "users_with_saved"}
        ]
        aggregation = list(User.objects.aggregate(*pipeline))
        user_saved = aggregation[0]['users_with_saved'] if len(aggregation) > 0 else 0

        data = {
            'last_hour_reqs': last_hour_reqs,
            'most_popular_route': most_popular_route,
            'user_saved': user_saved,
            'user_total': User.objects(is_superuser=False).count(),
        }

        self.render('admin/home.html', **data)
        return


class StatisticsImgHandler(BaseHandler):
    def get(self, year):
        user = self.get_current_user()
        if not user or not user.is_superuser:
            raise HTTPError(404)

        backend = PredictionBackend(int(year))
        statistics_url = backend.statistics_plot()

        if statistics_url:
            self.write({
                'type': 'success',
                'statistics_url': statistics_url,
            })
        else:
            self.write({
                'type': 'error',
                'message': 'Результатів для заданого року не знайдено',
            })
        return


class PredictionImgHandler(BaseHandler):
    def get(self, year):
        user = self.get_current_user()
        if not user or not user.is_superuser:
            raise HTTPError(404)

        backend = PredictionBackend(int(year))
        prediction_url = backend.prediction_plot()

        if prediction_url:
            self.write({
                'type': 'success',
                'prediction_url': prediction_url,
                'statistics_url': backend.statistics_plot(),
            })
        else:
            self.write({
                'type': 'error',
                'message': 'Результатів для заданого року не знайдено',
            })
