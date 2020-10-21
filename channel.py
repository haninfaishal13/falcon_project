import falcon, json, datetime
from database import *

class Channel:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        results = []
        column = ('Time','Channel Value', 'Sensor Id')
        query = db.select("select time, value, id_sensor from channel")
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'get channel data',
            'data' : results
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, ids): #Channel sensor
        db = database()
        results = []
        column = ('Time', 'Value', 'Sensor Name', 'Sensor Unit')
        scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        if scheck:
            query = db.select('''select channel.time, channel.value, sensor.name, sensor.unit 
                                 from channel left join sensor on channel.id_sensor = sensor.id_sensor
                                 where channel.id_sensor = %s ''' % ids)
            for row in query:
                results.append(dict(zip(column, row)))
            output = {
                'success' : True,
                'message' : 'get channel data',
                'data' : results
            }
            resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('Channel in this sensor not fount, Id: {}'.format(ids))
        db.close()
    
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

        required = {'Value', 'Id Sensor'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        ch_value = params['Value']
        id_sensor = params['Id Sensor']

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