import falcon, json
from database import *

class Sensor:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        i = 0

        results = []
        column = ('Id Sensor', 'Name', 'Unit', 'activity', 'id hardware', 'id node')
        if isadmin:
            query = db.select("select * from sensor")

            for row in query:
                results.append(dict(zip(column, row)))
            output = {
                'success' : True,
                'message' : 'get sensor data',
                'data' : results
            }
        else:
            query = db.select('''select sensor.id_sensor, sensor.name, sensor.unit, sensor.activity, 
                                sensor.id_hardware, sensor.id_node from sensor left join node
                                on sensor.id_node = node.id_node where node.id_user = '%s' ''' % idu)
            for row in query:
                results.append(dict(zip(column, row)))
            output = {
                'success' : True,
                'message' : 'get your sensor data',
                'data' : results
            }
        resp.body = json.dumps(output, indent = 2)
        db.close()

#   Sensor-Hardware Scenario
    @falcon.before(Authorize())
    def on_get_id(self, req, resp, ids):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]

        scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        if not scheck:
            raise falcon.HTTPBadRequest('Id Sensor does not exist: {}'.format(ids))
        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        value = query[0]
        id_user = value[0]
        if not isadmin:
            if(id_user != idu):
               raise falcon.HTTPForbidden('Forbidden', 'You are not admin') 

        sensor = []
        channel = []
        scolumn = ('id sensor', 'name', 'unit','activity', 'time', 'value')
        ccolumn = ('time', 'value')
        query = db.select("select id_sensor, name, unit, activity from sensor where id_sensor = '%s'" % ids)
        for row in query:
            sensor.append(dict(zip(column, row)))
        query = db.select('''select time, value from channel where id_sensor = '%s' ''' % ids)
        for row in query:
            channel.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'get sensor data',
            'data' : results,
            'channel':channel
        }
        resp.body = json.dumps(output, indent = 2)

        db.close()

    @falcon.before(Authorize())
    def on_post_add(self, req, resp, idn, type):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]

        key = []
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'name', 'unit', 'activity'}
        missing = required - set(params.keys())
        given = set(params.keys()) - required
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        if type != "sensor":
            raise falcon.HTTPBadRequest()
        name = params['name']
        unit = params['unit']
        activity = params['activity']

        if 'hardware' in given:
            id_hardware = params['id_hardware']
            db.commit("insert into sensor (name, unit, activity, id_node, id_hardware) values ('%s','%s','%s','%s','%s'" % (name, unit, activity, idn, id_hardware))
            key = {
                'name':name,
                'unit':unit,
                'activity':activity,
                'id node':idn,
                'id hardware':id_hardware
            }
            output = {
                'success':True,
                'message':'add new sensor',
                'data':key
            }
        elif 'hardware' not in given:
            db.commit("insert into sensor (name, unit, activity, id_node, id_hardware) values ('%s','%s','%s','%s',NULL)" % (name, unit, activity, idn))
            key = {
                'name':name,
                'unit':unit,
                'activity':activity,
                'id node':idn,
                'id hardware':None
            }
            output = {
                'success':True,
                'message':'add new sensor',
                'data':key
            }
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, ids):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        ids = int(ids)

        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        if not scheck:
            raise falcon.HTTPBadRequest('Id Sensor does not exist: {}'.format(ids))
        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        value = query[0]
        id_user = value[0]
        if not isadmin:
            if(id_user != idu):
               raise falcon.HTTPForbidden('Forbidden', 'You are not admin')

        results = []
        column = ('Id Sensor', 'name', 'Unit', 'id hardware', 'id node')
        required = {'name', 'unit', 'activity'}
        missing = required - set(params.keys())

        if 'name' in missing and 'unit' in missing and 'activity' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        if 'name' not in missing and 'unit' not in missing and 'activity' not in missing:
            db.commit("update sensor set name = '%s', unit = '%s', activity = '%s' where id_sensor = '%s'"
                          % (params['name'], params['unit'], params['activity'], ids))
        elif 'name' not in missing and 'activity' not in missing:
            db.commit("update sensor set name = '%s', activity = '%s' where id_sensor = '%s'" % (params['name'], params['activity'], ids))
        elif 'unit' not in missing and 'activity' not in missing:
            db.commit("update sensor set unit = '%s', activity = '%s' where id_sensor = '%s'" % (params['unit'],params['activity'], ids))
        elif 'name' not in missing and 'unit' not in missing:
            db.commit("update sensor set name = '%s', unit = '%s' where id_sensor = '%s'" % (params['name'], params['unit'], ids))
        elif 'name' not in missing:
            db.commit("update sensor set name = '%s' where id_sensor = '%s'" % (params['name'], ids))
        elif 'unit' not in missing:
            db.commit("update sensor set unit = '%s' where id_sensor = '%s'" % (params['unit'], ids))
        elif 'activity' not in missing:
            db.commit("update sensor set activity = '%s' where id_sensor = '%s'" % (params['activity'], ids))
        query = db.select("select * from sensor where id_sensor = '%s'" % ids)
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'update sensor data',
            'data' : results
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, ids):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        ids = int(ids)

        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        if not scheck:
            raise falcon.HTTPBadRequest('Id Sensor does not exist: {}'.format(ids))
        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        value = query[0]
        id_user = value[0]
        if not isadmin:
            if(id_user != idu):
               raise falcon.HTTPForbidden('Forbidden', 'You are not admin')

        db.commit("delete from sensor where id_sensor = '%s'" % ids)
        output = {
            'success' : True,
            'message' : 'delete sensor data',
            'Id' : '{}'.format(ids)
        }
        resp.body = json.dumps(output)
        db.close()

