import datetime
import json

from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape

from app.models import CityCache, Route, Segment, Flight, \
    FlightSegment, TransportType, SavedOffer, Flights
from settings import api_key, base_api_url, headers


class SearchBackend:
    _base_flags = [
        'noFerry',
        'noCar',
        'noBikeshare',
        'noRideshare',
        'noTowncar',
        'noCommuter',
        'noSpecial',
        'noMinorStart',
        'noMinorEnd',
        'noPath',
        'noStop',
    ]

    _base_params = {
        'key': api_key,
        'oKind': 'City',
        'dKind': 'City',
        'currencyCode': 'UAH',
    }

    _weekdays = {
        0: 'Нд',
        1: 'Пн',
        2: 'Вт',
        3: 'Ср',
        4: 'Чт',
        5: 'Пт',
        6: 'Сб',
    }

    _icons = {
        'bus': '/static/images/bus-active.png',
        'train': '/static/images/train-active.png',
        'plane': '/static/images/plane-active.png',
        'foot': '/static/images/walk.png',
        'tram': '/static/images/tram.png',
        'subway': '/static/images/train-active.png',
    }

    _names = {
        'bus': 'Автобус',
        'train': 'Потяг',
        'plane': 'Літак',
        'foot': 'Пішки',
        'tram': 'Трамвай',
        'subway': 'Метро',
    }

    _max_place_name_len = 20

    def __init__(self, search_request):
        self._search_request = search_request

    async def search(self):
        url = self._build_request()

        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url, raise_error=False, headers=headers)
        response_dict = json.loads(response.body, encoding='utf-8')

        self._search_request.full_response = str(response.body, encoding='utf-8')
        self._search_request.request = url
        self._search_request.dt_request = datetime.datetime.now()
        self._search_request.save()

        return self._parse_response(response_dict)

    def _build_request(self):
        flags = self._base_flags[:]
        if not self._search_request.search_bus:
            flags.append('noBus')
        if not self._search_request.search_train:
            flags.append('noRail')
        if not self._search_request.search_flight:
            flags.append('noAir')

        parameters = self._base_params.copy()
        try:
            city_from, country_from = self._search_request.req_from.split(', ')
            city_to, country_to = self._search_request.req_to.split(', ')
            cache_from = CityCache.objects(name_uk=city_from, country_uk=country_from)[0]
            cache_to = CityCache.objects(name_uk=city_to, country_uk=country_to)[0]

            parameters['oName'] = url_escape('{}, {}'.format(cache_from.name_en, cache_from.country_en))
            parameters['dName'] = url_escape('{}, {}'.format(cache_to.name_en, cache_to.country_en))
        except Exception as e:
            print(e)
            parameters['oName'] = url_escape(self._search_request.req_from)
            parameters['dName'] = url_escape(self._search_request.req_to)

        flags_str = '&'.join(flag for flag in flags)
        params_str = '&'.join('{}={}'.format(k, v) for k, v in parameters.items())

        return '{}Search?{}&{}'.format(base_api_url, params_str, flags_str)

    def _parse_response(self, response_dict):
        routes = []
        for i, route in enumerate(response_dict['routes']):
            # filter by transfers
            if self._search_request.no_transfers and len(route['segments']) > 1:
                continue

            # create route obj
            rt = Route(
                order=i,
                pl_from=self._search_request.req_from,
                pl_to=self._search_request.req_to,
                from_seg=response_dict['places'][route['depPlace']]['shortName'],
                transfers=len(route['segments']) - 1,
                duration=self._parse_duration(route['totalDuration']),
                duration_raw=route['totalDuration'],
            )

            # filter by total price
            if not route.get('indicativePrices'):
                continue
            else:
                pr = route['indicativePrices'][-1]
                if self._search_request.price_lower_limit and \
                        int(pr['price']) < self._search_request.price_lower_limit:
                    continue

                if self._search_request.price_upper_limit and \
                        int(pr['price']) > self._search_request.price_upper_limit:
                    continue

            # parse total price
            self._parse_price(route, rt)

            # parse segments
            segments = []
            types_set = set()
            for segment in route['segments']:
                transport_type = response_dict['vehicles'][segment['vehicle']]['kind']
                types_set.add(transport_type)

            if any(not self._names.get(tr) for tr in types_set):
                continue

            for segment in route['segments']:
                # create segment dict
                transport_type = response_dict['vehicles'][segment['vehicle']]['kind']
                seg = Segment(
                    to=self._limit_name(response_dict['places'][segment['arrPlace']]['shortName']),
                    to_full=response_dict['places'][segment['arrPlace']]['shortName'],
                    transport_type=TransportType(
                        name=self._names[transport_type],
                        icon=self._icons[transport_type],
                    ),
                )

                # parse segment price
                if segment.get('indicativePrices'):
                    self._parse_price(segment, seg)
                else:
                    seg.price = '-'
                    seg.price_raw = 0

                # parsing specific segment type
                if segment['segmentKind'] == 'surface':
                    seg.segment_type = 'surface'
                    seg.duration = self._parse_duration(segment['transitDuration'] + segment['transferDuration'])
                    seg.duration_raw = segment['transitDuration'] + segment['transferDuration']
                    if segment.get('agencies'):
                        seg.frequency = self._parse_frequency(segment['agencies'][0]['frequency'])
                        links = segment['agencies'][0]['links']
                        for link in links:
                            if link['text'] == 'Book at':
                                seg.book_name = link['displayUrl']
                                seg.book_url = link['url']
                            elif link['text'] == 'Schedules at':
                                seg.schedule_name = link['displayUrl']
                                seg.schedule_url = link['url']
                # end
                else:
                    seg.segment_type = 'air'
                    if segment.get('outbound'):
                        duration = 0
                        leg = segment['outbound'][0]

                        start_index = leg['hops'][0]['depPlace']
                        time_start = leg['hops'][0]['depTime']
                        for hop in leg['hops']:
                            end_index = hop['arrPlace']
                            duration += hop['duration']
                            time_end = hop['arrTime']

                        seg.airport_start_code = response_dict['places'][start_index]['code']
                        seg.airport_start_name = response_dict['places'][start_index]['shortName']
                        seg.airport_end_code = response_dict['places'][end_index]['code']
                        seg.airport_end_name = response_dict['places'][end_index]['shortName']
                        seg.time_start = time_start
                        seg.time_end = time_end
                        seg.duration = self._parse_duration(duration)
                        seg.duration_raw = duration
                        seg.operating_days = self._parse_days(leg['operatingDays'])

                        flights = []
                        for leg in segment['outbound']:
                            flight = Flight(
                                operating_days=self._parse_days(leg['operatingDays'])
                            )
                            if leg.get('indicativePrices'):
                                self._parse_price(leg, flight)

                            duration = 0
                            hops = []
                            airlines = []
                            for hop in leg['hops']:
                                duration += hop['duration']
                                start_index = hop['depPlace']
                                end_index = hop['arrPlace']
                                hp = FlightSegment(
                                    airport_start_code=response_dict['places'][start_index]['code'],
                                    airport_start_name=response_dict['places'][start_index]['shortName'],
                                    airport_end_code=response_dict['places'][end_index]['code'],
                                    airport_end_name=response_dict['places'][end_index]['shortName'],
                                    time_start=hop['depTime'],
                                    time_end=hop['arrTime'],
                                    duration=self._parse_duration(hop['duration']),
                                    duration_raw=hop['duration'],
                                    airline_name=response_dict['airlines'][hop['airline']]['name'],
                                )
                                hops.append(hp)
                                airlines.append(response_dict['airlines'][hop['airline']]['name'])

                            flight.flight_segments = hops
                            flight.duration_raw = duration
                            flight.duration = self._parse_duration(duration)
                            flight.airlines = ', '.join(a for a in set(airlines))
                            flights.append(flight)

                        flights_obj = Flights(choices=flights).save()
                        seg.flights = flights_obj
                # end
                segments.append(seg)
            # end

            # parse transport types
            transport_types = [TransportType(
                name=self._names[tp],
                icon=self._icons[tp],
            ) for tp in types_set]

            rt.segments = segments
            rt.transport_types = transport_types
            routes.append(rt)

        self._save_best_route(routes)
        self._search_request.routes = routes
        self._search_request.save()
        return self._search_request.result

    def _parse_duration(self, duration):
        hrs = duration // 60
        mins = duration % 60

        result = ''
        if hrs:
            result += '{} год. '.format(hrs)
        if mins:
            result += '{} хв.'.format(mins)

        return result

    def _parse_days(self, days):
        bits = str(bin(days))
        days = list(reversed(bits.split('b')[1][:-1]))
        days.insert(0, bits[-1])

        if '0' not in days and len(days) == 7:
            result = 'Кожен день'
        else:
            weekdays = [self._weekdays[i] for i, day in enumerate(days) if day == '1']
            if weekdays[0] == 'Нд':
                weekdays = weekdays[1:]
                weekdays.append('Нд')
            result = ', '.join(day for day in weekdays)

        return result

    def _parse_price(self, element, obj):
        p = element['indicativePrices'][-1]
        has_price_range = bool(p.get('priceLow'))

        obj.price = '{} {}'.format(p['price'], 'грн')
        obj.has_price_range = has_price_range
        obj.price_raw = p['price']

        if has_price_range:
            obj.price_lower = '{} {}'.format(p['priceLow'], 'грн')
            obj.price_upper = '{} {}'.format(p['priceHigh'], 'грн')
        return

    def _parse_frequency(self, frequency):
        if 0.9 < frequency < 1.1:
            return 'Кожен тиждень'

        period = 1 / frequency
        days_period = period * 7
        if days_period >= 1.1:
            return 'Кожні {} днів'.format(int(days_period))
        elif 0.9 < days_period < 1.1:
            return 'Кожен день'

        hours_period = days_period * 24
        if hours_period >= 1.1:
            return 'Кожні {} годин'.format(int(hours_period))
        elif 0.9 < hours_period < 1.1:
            return 'Кожну годину'

        minutes_period = hours_period * 60
        return 'Кожні {} хвилин'.format(int(minutes_period))

    def _limit_name(self, name):
        if len(name) > self._max_place_name_len:
            return '{}..'.format(name[:self._max_place_name_len])
        else:
            return name

    def _save_best_route(self, routes):
        best_route = min(
            filter(lambda r: all(s.price_raw > 0 for s in r.segments), routes),
            key=lambda r: r.price_raw
        )

        current_best = SavedOffer.objects(type='best', pl_from=best_route.pl_from, pl_to=best_route.pl_to)
        if len(current_best) == 0:
            SavedOffer(
                type='best',
                pl_from=best_route.pl_from,
                pl_to=best_route.pl_to,
                price=best_route.price_raw,
                route=best_route,
            ).save()

        elif current_best[0].price >= best_route.price_raw:
            cur = current_best[0]
            cur.price = best_route.price_raw
            cur.route = best_route
            cur.dt_created = datetime.datetime.now()
            cur.save()

        return
