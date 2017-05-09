import json


class Backend:
    def __init__(self, search_request):
        self._search_request = search_request

    def search(self):
        return self._parse_response()

    def _build_request(self):
        return

    def _parse_response(self):
        result = json.dumps({
            'type': 'success',
            'records': [
                {
                    'from': 'Kiev',
                    'to': 'Moscow',
                    'price': '100 UAH',
                    'type': 'train',
                },
                {
                    'from': 'Kiev',
                    'to': 'Moscow',
                    'price': '200 UAH',
                    'type': 'bus',
                },
                {
                    'from': 'Kiev',
                    'to': 'Moscow',
                    'price': '1000 UAH',
                    'type': 'flight',
                },
            ]
        })
        self._search_request.result = result
        self._search_request.save()
        return result
