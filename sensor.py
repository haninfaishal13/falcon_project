import falcon, json
from database import *

class Sensor:
    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('Name', 'Unit', 'Id Hardware', 'Id Node')
        results = []
        query = db.select("select name, unit from sensor")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results)

    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        type = "sensor"
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Sensor Name', 'Sensor Unit', 'Id Hardware', 'Id Node'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        sensor_name = params['Sensor Name']
        sensor_value = params['Sensor Unit']
        id_hardware = params['Id Hardware']
        id_node = params['Id Node']

        hw_check = db.check("select id_hardware from hardware where id_hardware = '%s' and lower(type) = '%s'"
                            % (id_hardware, type))
        node_check = db.check("select id_node from node where id_node = '%s'" % id_node)
        if hw_check and node_check:
            db.commit("insert into sensor (name, unit, id_hardware, id_node) values ('%s', '%s', '%s', '%s')" %
                      (sensor_name, sensor_value, id_hardware, id_node))

            results = {
                'Message': 'Success'
            }
            resp.body = json.dumps(results)
        else:
            if not hw_check and not node_check:
                raise falcon.HTTPBadRequest('Id Hardware and Node not present: {}'.format((id_hardware, id_node)))
            elif not hw_check:
                raise falcon.HTTPBadRequest('Id Hardware not present or not valid: {}'.format(id_hardware))
            elif not node_check:
                raise falcon.HTTPBadRequest('Id Node not present: {}'.format(id_node))

    @falcon.before(Authorize())
    def on_put(self, req, resp, sensor_id):
        db = database()
        global results
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Sensor Name', 'Sensor Unit'}
        missing = required - set(params.keys())
        if 'Sensor Name' in missing and 'Sensor Unit' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        elif 'Sensor Name' not in missing and 'Sensor Unit' not in missing:
            db.commit("update sensor set name = '%s', unit = '%s' where id_sensor = '%s'"
                      % (params['Sensor Name'], params['Sensor Unit'], sensor_id))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
        elif 'Sensor Name' not in missing:
            db.commit("update sensor set name = '%s' where id_sensor = '%s'" % (params['Sensor Name'], sensor_id))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
        elif 'Sensor Unit' not in missing:
            db.commit("update sensor set unit = '%s' where id_sensor = '%s'" % (params['Sensor Unit'], sensor_id))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
        resp.body = json.dumps(results)

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
            results = {
                'Messages': 'Deleted Id {} from Sensor'.format(id_sensor)
            }
            resp.body = json.dumps(results)
        else:
            raise falcon.HTTPBadRequest('Sensor Id not found: {}'.format(id_sensor))
