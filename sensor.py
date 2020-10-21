import falcon, json
from database import *

class Sensor:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('Id Sensor', 'Name', 'Unit', 'Activity', 'Id Hardware', 'Id Node')
        results = []
        query = db.select("select * from sensor")
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'get sensor data',
            'data' : results
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

#   Sensor-Hardware Scenario
    @falcon.before(Authorize())
    def on_get_id(self, req, resp, ids):
        db = database()
        results = []
        scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        if scheck:
            column = ('Id Sensor', 'Sensor Name', 'Sensor Unit','Sensor Activity', 'Hardware Name', 'Node Name', 'Node Location')
            query = db.select("select sensor.id_sensor, sensor.name, sensor.unit, sensor.activity, hardware.name, node.name, node.location "
                              "from sensor left join hardware on sensor.id_hardware = hardware.id_hardware "
                              "left join node on sensor.id_node = node.id_node where sensor.id_sensor = '%s' " % ids)
            for row in query:
                results.append(dict(zip(column, row)))
            output = {
                'success' : True,
                'message' : 'get sensor data',
                'data' : results
            }
            resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('Id Sensor does not exist: {}'.format(ids))

        db.close()

    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]

        key = []
        type = "sensor"
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Sensor Name', 'Sensor Unit', 'Activity', 'Id Hardware', 'Id Node'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        sensor_name = params['Sensor Name']
        sensor_unit = params['Sensor Unit']
        activity = params['Activity']
        id_hardware = params['Id Hardware']
        id_node = params['Id Node']

        query = db.select("select id_user from node where id_node = '%s'" % id_node)
        value = query[0]
        id_user = value[0]
        if(id_user != idu):
            raise falcon.HTTPBadRequest('Unauthorized', 'Cannot add sensor to others user data')

        key.append(dict(zip(params.keys(), params.values())))
        hw_check = db.check("select id_hardware from hardware where id_hardware = '%s' and lower(type) = lower('Sensor')"
                            % id_hardware)
        node_check = db.check("select id_node from node where id_node = '%s'" % id_node)
        if hw_check and node_check:
            db.commit("insert into sensor (name, unit, activity, id_hardware, id_node) values ('%s', '%s', '%s', '%s', '%s')" %
                      (sensor_name, sensor_unit, activity, id_hardware, id_node))

            output = {
                'success' : True,
                'message' : 'add new sensor',
                'data' : key
            }
            resp.body = json.dumps(output)
        else:
            if not hw_check and not node_check:
                raise falcon.HTTPBadRequest('Id Hardware and Node not present: {}'.format((id_hardware, id_node)))
            elif not hw_check:
                raise falcon.HTTPBadRequest('Id Hardware not present or not valid: {}'.format(id_hardware))
            elif not node_check:
                raise falcon.HTTPBadRequest('Id Node not present: {}'.format(id_node))
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, ids):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        ids = int(ids)

        results = []
        column = ('Id Sensor', 'Sensor Name', 'Unit', 'Id Hardware', 'Id Node')
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Sensor Name', 'Sensor Unit', 'Activity'}
        missing = required - set(params.keys())

        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        value = query[0]
        id_user = value[0]
        if(id_user != idu):
            raise falcon.HTTPBadRequest('Unauthorized', 'Cannot edit others users data')

        if 'Sensor Name' in missing and 'Sensor Unit' in missing and 'Activity' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        elif 'Sensor Name' not in missing and 'Sensor Unit' not in missing and 'Activity' not in missing:
            db.commit("update sensor set name = '%s', unit = '%s', activity = '%s' where id_sensor = '%s'"
                      % (params['Sensor Name'], params['Sensor Unit'], params['Activity'], ids))
        elif 'Sensor Name' not in missing and 'Activity' not in missing:
            db.commit("update sensor set name = '%s', activity = '%s' where id_sensor = '%s'" % (params['Sensor Name'], params['Activity'], ids))
        elif 'Sensor Unit' not in missing and 'Activity' not in missing:
            db.commit("update sensor set unit = '%s', activity = '%s' where id_sensor = '%s'" % (params['Sensor Unit'],params['Activity'], ids))
        elif 'Sensor Name' not in missing and 'Sensor Unit' not in missing:
            db.commit("update sensor set name = '%s', unit = '%s' where id_sensor = '%s'" % (params['Sensor Name'], params['Sensor Unit'], ids))
        elif 'Sensor Name' not in missing:
            db.commit("update sensor set name = '%s' where id_sensor = '%s'" % (params['Sensor Name'], ids))
        elif 'Sensor Unit' not in missing:
            db.commit("update sensor set unit = '%s' where id_sensor = '%s'" % (params['Sensor Unit'], ids))
        elif 'Activity' not in missing:
            db.commit("update sensor set activity = '%s' where id_sensor = '%s'" % (params['Activity'], ids))
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
    def on_delete(self, req, resp):
        db = database()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Id Sensor'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        id_sensor = params['Id Sensor']


        checking = db.check("select * from sensor where id_sensor = '%s'" % id_sensor)
        if checking:
            db.commit("delete from sensor where id_sensor = '%s'" % id_sensor)
            output = {
                'success' : True,
                'message' : 'delete sensor data',
                'Id' : '{}'.format(id_sensor)
            }
            resp.body = json.dumps(results)
        else:
            raise falcon.HTTPBadRequest('Sensor Id not found: {}'.format(id_sensor))
        db.close()
