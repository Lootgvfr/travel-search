import datetime
import json

from tornado.httpclient import AsyncHTTPClient

from settings import api_key, base_api_url, headers


class Backend:
    _base_flags = [
        'noAirLeg',
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
    ]

    _base_params = {
        'key': api_key,
        'oKind': 'City',
        'dKind': 'City',
        'currencyCode': 'UAH',
    }

    def __init__(self, search_request):
        self._search_request = search_request

    async def search(self):
        url = self._build_request()
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url, raise_error=False, headers=headers)
        response_dict = json.loads(response.body, encoding='utf-8')
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
        parameters['oName'] = self._search_request.req_from.replace(' ', '%20')
        parameters['dName'] = self._search_request.req_to.replace(' ', '%20')

        flags_str = '&'.join(flag for flag in flags)
        params_str = '&'.join('{}={}'.format(k, v) for k, v in parameters.items())

        return '{}Search?{}&{}'.format(base_api_url, params_str, flags_str)

    def _parse_response(self, response_dict):
        result = []
        for route in response_dict['routes']:
            frm = response_dict['places'][route['depPlace']]['shortName']
            to = response_dict['places'][route['arrPlace']]['shortName']

            duration_raw = route['totalDuration']
            duration = '{} hrs'.format(duration_raw // 60)
            if duration_raw % 60 > 0:
                duration += ' {} min'.format(duration_raw % 60)

            lower_price = 0
            upper_price = 0
            if route.get('indicativePrices'):
                for price in route['indicativePrices']:
                    lower_price += int(price['priceLow'])
                    upper_price += int(price['priceHigh'])
            price = '{} - {} UAH'.format(lower_price, upper_price) \
                if lower_price or upper_price else 'Unavailable'

            types_set = set()
            for segment in route['segments']:
                types_set.add(response_dict['vehicles'][segment['vehicle']]['kind'])
            types = ', '.join(tp for tp in types_set)

            result.append({
                'from': frm,
                'to': to,
                'price': price,
                'type': types,
                'duration': duration,
            })

        str_res = json.dumps(result)
        self._search_request.result = str_res
        self._search_request.full_response = json.dumps(response_dict)
        self._search_request.dt_request = datetime.datetime.now()
        self._search_request.save()
        return result
