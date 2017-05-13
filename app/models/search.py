import uuid
import mongoengine


class SearchRequest(mongoengine.Document):
    guid = mongoengine.StringField(max_length=50, required=True, unique=True)

    req_from = mongoengine.StringField(max_length=100, required=True)
    req_to = mongoengine.StringField(max_length=100, required=True)

    search_bus = mongoengine.BooleanField(default=False)
    search_flight = mongoengine.BooleanField(default=False)
    search_train = mongoengine.BooleanField(default=False)

    price_lower_limit = mongoengine.IntField(min_value=0, default=None)
    price_upper_limit = mongoengine.IntField(min_value=0, default=None)

    no_transfers = mongoengine.BooleanField(default=False)

    result = mongoengine.StringField(required=False)
    full_response = mongoengine.StringField(required=False)
    request = mongoengine.StringField(required=False)
    dt_request = mongoengine.DateTimeField(required=False)

    def __init__(self, *args, **kwargs):
        super(SearchRequest, self).__init__(*args, **kwargs)
        self.guid = str(uuid.uuid4())