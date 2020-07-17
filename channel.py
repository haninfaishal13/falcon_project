import falcon, json, datetime
from json import JSONEncoder
from database import *

class Channel:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('Time','Channel Value', 'Sensor Id')
        results = []
        query = db.select("select time, value, id_sensor from channel")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)
        db.close()
    
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

        required = {'Value', 'Id Sensor'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        ch_value = params['Value']
        id_sensor = params['Id Sensor']
        time = datetime.datetime.now()
        db.commit("insert into channel (time, value, id_sensor) values ('%s','%s', '%s')" % (str(time), ch_value, id_sensor))
        results = {
            'Messages': 'Success'
        }
        resp.body = json.dumps(results)
        db.close()