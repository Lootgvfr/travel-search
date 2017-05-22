import datetime
import matplotlib.pyplot as plt
import math
import heapq

from mongoengine.queryset.visitor import Q

from app.models import SearchRequest


class PredictionBackend:
    def __init__(self, year):
        self._year = year
        self.stats = None
        self.prediction = None
        self.distance_func = self._distance_euclid
        self.k = 15

    def prediction_plot(self):
        if not self.prediction:
            res = self._calculate_prediction()
            if not res:
                return None

        days = []
        counts = []
        self.prediction.sort(key=lambda r: r['day'])
        for k in self.prediction:
            days.append(k['day'])
            counts.append(k['count'])

        y_limit = max(self.stats, key=lambda r: r['count'])['count'] + 1
        fig = plt.figure(figsize=(15, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel('Дні року')
        ax.set_ylabel('Кількість запитів')
        ax.set_title('Прогноз на наступний рік')
        ax.set_ylim([0, round(y_limit)])
        ax.plot(days, counts)
        return self._save_plot(fig)

    def statistics_plot(self):
        if self.stats:
            days = []
            counts = []
            self.stats.sort(key=lambda r: r['day'])
            for k in self.stats:
                days.append(k['day'])
                counts.append(k['count'])
        else:
            result = self._get_statistics()
            if not result:
                return None
            days = result['days']
            counts = result['counts']

        y_limit = max(counts) + 1
        fig = plt.figure(figsize=(15, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_ylim([0, round(y_limit)])
        ax.set_xlabel('Дні року')
        ax.set_ylabel('Кількість запитів')
        ax.set_title('Статистика за рік {}'.format(self._year))
        ax.plot(days, counts, 'bo', markersize=2)
        return self._save_plot(fig)

    def _calculate_prediction(self):
        stat = self._get_statistics()
        if not stat:
            return None

        days = stat['days']
        counts = stat['counts']

        self.prediction = []
        self.stats = []
        for i in range(len(days)):
            self.stats.append({
                'day': days[i],
                'count': counts[i],
            })
        # end

        for i in range(len(days)):
            day = days[i]
            for j in range(len(days)):
                self.stats[j]['distance'] = self.distance_func(day, self.stats[j]['day'])
            k_smallest = heapq.nsmallest(self.k+1, self.stats, key=lambda r: r['distance'])[1:]
            self.prediction.append({
                'day': day,
                'count': sum(r['count'] for r in k_smallest)/len(k_smallest),
            })
        # end
        return True

    def _get_statistics(self):
        first_dt = datetime.datetime(year=self._year, day=1, month=1, hour=0, minute=0, second=0)
        last_dt = datetime.datetime(year=self._year, day=31, month=12, hour=23, minute=59, second=59)
        requests = SearchRequest \
            .objects(Q(dt_request__gte=first_dt) & Q(dt_request__lte=last_dt)) \
            .order_by('dt_request')
        if len(requests) == 0:
            return None

        current_day = requests[0].dt_request.timetuple().tm_yday
        days = [current_day]
        counts = [0]
        current_date = requests[0].dt_request.date()

        for request in requests:
            date_request = request.dt_request.date()

            while current_date < date_request:
                current_day += 1
                days.append(current_day)
                counts.append(0)
                current_date += datetime.timedelta(days=1)

            counts[-1] += 1
            # request.delete()
        # end

        return {
            'days': days,
            'counts': counts,
        }

    def _save_plot(self, fig):
        filename = 'static/plots/plot_{}.png'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'))
        fig.savefig(filename)
        return filename

    def _distance_euclid(self, x1, x2):
        return math.sqrt((x1 - x2)**2)

    def _distance_manhattan(self, x1, x2):
        return math.fabs(x1 - x2)
