import uuid
import mongoengine


class TransportType(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(max_length=20, required=True)
    icon = mongoengine.StringField(max_length=200, required=True)


class FlightSegment(mongoengine.EmbeddedDocument):
    airport_start_code = mongoengine.StringField(max_length=10, required=True)
    airport_start_name = mongoengine.StringField(max_length=100, required=True)
    airport_end_code = mongoengine.StringField(max_length=10, required=True)
    airport_end_name = mongoengine.StringField(max_length=100, required=True)

    time_start = mongoengine.StringField(max_length=10, required=True)
    time_end = mongoengine.StringField(max_length=10, required=True)

    duration = mongoengine.StringField(max_length=100)
    duration_raw = mongoengine.IntField(required=True)
    airline_name = mongoengine.StringField(max_length=50, required=True)


class Flight(mongoengine.EmbeddedDocument):
    # general fields
    flight_segments = mongoengine.ListField(mongoengine.EmbeddedDocumentField(FlightSegment))
    duration = mongoengine.StringField(max_length=100)
    duration_raw = mongoengine.IntField(required=True)
    airlines = mongoengine.StringField(max_length=300, required=True)
    operating_days = mongoengine.StringField(max_length=50, required=True)

    # price fields
    price = mongoengine.StringField(required=True)
    price_raw = mongoengine.IntField(required=True)
    has_price_range = mongoengine.BooleanField(default=False)
    price_lower = mongoengine.StringField()
    price_upper = mongoengine.StringField()

    def as_dict(self):
        segments = []
        for segment in self.flight_segments:
            seg = {
                'airport_start_code': segment.airport_start_code,
                'airport_start_name': segment.airport_start_name,
                'airport_end_code': segment.airport_end_code,
                'airport_end_name': segment.airport_end_name,
                'time_start': segment.time_start,
                'time_end': segment.time_end,
                'duration': segment.duration,
                'airline': segment.airline_name,
            }
            segments.append(seg)
        return {
            'segments': segments,
            'duration': self.duration,
            'airlines': self.airlines,
            'days': self.operating_days,
            'price': self.price,
            'has_price_range': self.has_price_range,
            'price_lower': self.price_lower,
            'price_upper': self.price_upper,
        }


class Flights(mongoengine.Document):
    guid = mongoengine.StringField(required=True)
    choices = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Flight), required=True)

    def __init__(self, *args, **kwargs):
        super(Flights, self).__init__(*args, **kwargs)
        if not self.guid:
            self.guid = str(uuid.uuid4())

    @property
    def result(self):
        res = []
        for flight in self.choices:
            res.append(flight.as_dict())
        return res


class Segment(mongoengine.EmbeddedDocument):
    # general fields
    segment_type = mongoengine.StringField(choices=['air', 'surface'], required=True)
    to = mongoengine.StringField(max_length=100, required=True)
    to_full = mongoengine.StringField(max_length=200, required=True)
    transport_type = mongoengine.EmbeddedDocumentField(TransportType, required=True)
    duration = mongoengine.StringField(required=True)
    duration_raw = mongoengine.IntField(required=True)

    # price fields
    price = mongoengine.StringField(required=True)
    price_raw = mongoengine.IntField(required=True)
    has_price_range = mongoengine.BooleanField(default=False)
    price_lower = mongoengine.StringField()
    price_upper = mongoengine.StringField()

    # surface segment fields
    frequency = mongoengine.StringField(max_length=30)
    book_name = mongoengine.StringField(max_length=50)
    book_url = mongoengine.StringField(max_length=500)
    schedule_name = mongoengine.StringField(max_length=50)
    schedule_url = mongoengine.StringField(max_length=500)

    # air segment fields
    airport_start_code = mongoengine.StringField(max_length=10)
    airport_start_name = mongoengine.StringField(max_length=100)
    airport_end_code = mongoengine.StringField(max_length=10)
    airport_end_name = mongoengine.StringField(max_length=100)
    time_start = mongoengine.StringField(max_length=10)
    time_end = mongoengine.StringField(max_length=10)
    operating_days = mongoengine.StringField(max_length=50)
    flights = mongoengine.ReferenceField(Flights)


class Route(mongoengine.EmbeddedDocument):
    order = mongoengine.IntField(required=True)
    pl_from = mongoengine.StringField(max_length=100, required=True)
    pl_to = mongoengine.StringField(max_length=100, required=True)
    from_seg = mongoengine.StringField(max_length=100, required=True)

    transfers = mongoengine.IntField(min_value=0, required=True)
    duration = mongoengine.StringField(required=True)
    duration_raw = mongoengine.IntField(required=True)
    transport_types = mongoengine.ListField(mongoengine.EmbeddedDocumentField(TransportType))
    segments = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Segment))

    price = mongoengine.StringField(required=True)
    price_raw = mongoengine.IntField(required=True)
    has_price_range = mongoengine.BooleanField(default=False)
    price_lower = mongoengine.StringField()
    price_upper = mongoengine.StringField()

    def as_dict(self):
        segments = []
        for segment in self.segments:
            seg = {
                'segment_type': segment.segment_type,
                'to': segment.to,
                'to_full': segment.to_full,
                'transport_type': {
                    'name': segment.transport_type.name,
                    'icon': segment.transport_type.icon,
                },
                'duration': segment.duration,
                'duration_raw': segment.duration_raw,
                'price': segment.price,
                'price_raw': segment.price_raw,
                'has_price_range': segment.has_price_range,
                'price_lower': segment.price_lower,
                'price_upper': segment.price_upper,
            }

            if segment.segment_type == 'surface':
                seg['frequency'] = segment.frequency
                seg['book_name'] = segment.book_name
                seg['book_url'] = segment.book_url
                seg['schedule_name'] = segment.schedule_name
                seg['schedule_url'] = segment.schedule_url
            else:
                seg['airport_start_code'] = segment.airport_start_code
                seg['airport_start_name'] = segment.airport_start_name
                seg['airport_end_code'] = segment.airport_end_code
                seg['airport_end_name'] = segment.airport_end_name
                seg['time_start'] = segment.time_start
                seg['time_end'] = segment.time_end
                seg['days'] = segment.operating_days
                seg['flights_id'] = segment.flights.guid

            segments.append(seg)

        transport_types = []
        for transport_type in self.transport_types:
            transport_types.append({
                'name': transport_type.name,
                'icon': transport_type.icon,
            })

        return {
            'from': self.pl_from,
            'to': self.pl_to,
            'from_seg': self.from_seg,
            'transfers': self.transfers,
            'duration': self.duration,
            'duration_raw': self.duration_raw,
            'segments': segments,
            'order': self.order,
            'transport_types': transport_types,
            'price': self.price,
            'price_raw': self.price_raw,
            'has_price_range': self.has_price_range,
            'price_lower': self.price_lower,
            'price_upper': self.price_upper,
        }


class SearchRequest(mongoengine.Document):
    guid = mongoengine.StringField(max_length=50, required=True, unique=True)
    user = mongoengine.ReferenceField('User')

    req_from = mongoengine.StringField(max_length=100, required=True)
    req_to = mongoengine.StringField(max_length=100, required=True)

    search_bus = mongoengine.BooleanField(default=False)
    search_flight = mongoengine.BooleanField(default=False)
    search_train = mongoengine.BooleanField(default=False)

    price_lower_limit = mongoengine.IntField(min_value=0, default=None)
    price_upper_limit = mongoengine.IntField(min_value=0, default=None)

    no_transfers = mongoengine.BooleanField(default=False)

    routes = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Route))
    full_response = mongoengine.StringField()
    request = mongoengine.StringField()
    dt_request = mongoengine.DateTimeField()

    def __init__(self, *args, **kwargs):
        super(SearchRequest, self).__init__(*args, **kwargs)
        if not self.guid:
            self.guid = str(uuid.uuid4())

    @property
    def result(self):
        if not self.routes:
            return None

        res = []
        for route in self.routes:
            res.append(route.as_dict())
        return res
