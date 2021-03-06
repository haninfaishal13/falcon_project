import falcon, json, datetime
from database import *

class Channel:

    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]

        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'value', 'id sensor'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        ch_value = params['value']
        id_sensor = params['id sensor']

        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % id_sensor)
        value = query[0]
        id_user = value[0]
        if(id_user != idu):
            raise falcon.HTTPBadRequest('Unauthorized', 'Cannot send channel to others user data')
        time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f %Z")
        db.commit("insert into channel (time, value, id_sensor) values ('%s',%s,%s)" % (str(time), ch_value, id_sensor))
        results = {
            'Messages': 'Success'
        }
        resp.body = json.dumps(results)
        db.close()