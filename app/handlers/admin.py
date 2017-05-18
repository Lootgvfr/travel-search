import datetime

from tornado.web import HTTPError

from app.models import SearchRequest
from .base import BaseHandler


class AdminHomeHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user or not user.is_superuser:
            raise HTTPError(404)

        last_hour = datetime.datetime.now() - datetime.timedelta(hours=1)
        last_hour_reqs = len(SearchRequest.objects(dt_request__gte=last_hour))
        self.render('admin/home.html', last_hour_reqs=last_hour_reqs)
        return
