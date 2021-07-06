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

        required = {'value', 'id_sensor'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        ch_value = params['value']
        id_sensor = params['id_sensor']
        try:
            checking = db.check("select id_sensor from sensor where id_sensor = '%s'" % id_sensor)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not checking:
            print(id_sensor)
            raise falcon.HTTPBadRequest('Id Sensor not found')
        try: #antisipasi data yang diinput tidak sesuai dengan tipe data pada database
            query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % id_sensor)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        id_user = query[0][0]
        if(id_user != idu):
            raise falcon.HTTPForbidden('Cannot send channel to another user\'s data')
        time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S %Z")
        db.commit("insert into channel (time, value, id_sensor) values ('%s',%s,%s)" % (str(time), ch_value, id_sensor))
        results = {
            'title': 'add channel',
            'description': 'success add channel'
        }
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(results)
        db.close()

