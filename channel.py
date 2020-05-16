import falcon, json
from database import *

class Channel:
    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Channel Value', 'Id Sensor'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        ch_value = params['Channel Value']
        id_sensor = params['Id Sensor']
        db.commit("insert into channel (value, id_sensor) values ('%s', '%s')" % (ch_value, id_sensor))
        results = {
            'Messages': 'Success'
        }
        resp.body = json.dumps(results)