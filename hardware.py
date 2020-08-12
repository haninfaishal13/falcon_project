import falcon, json
from database import *

class Hardware:
    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('Id Hardware','Hardware Name', 'Type', 'Description')
        results = []
        query = db.select("select id_hardware, name, type, description from hardware")
        for row in query:
            results.append(dict(zip(column, row)))
        
        output = {
            'success' : True,
            'message' : 'get hardware data',
            'data' : results
        }
        resp.body = json.dumps(output, indent=2)
        db.close()

    # @falcon.before(Authorize())
    # def on_get_id(self, req, resp, idh):
    #     db = database()
    #     results = []
    #     idhcheck = db.check("select * from hardware where id_hardware = '%s'" % idh)
    #     if idhcheck:
    #         hwcheck = db.check("select * from hardware where lower(type) = lower('microcontroller unit') or lower(type) = lower('single-board computer')")
    #         if hwcheck:
    #             column = ('Id Hardware', 'Hardware Name', 'Type', 'Description', 'Node Name', 'Node Location')
    #             query = db.select("select hardware.id_hardware, hardware.name, hardware.type, hardware.description, "
    #                                 "node.name, node.location from hardware, node "
    #                                 "where hardware.id_hardware = '%s' and lower(hardware.type) = lower('microcontroller unit') or lower(type) = lower('single-board computer')" % idh)
    #             for row in query:
    #                 results.append(dict(zip(column, row)))
    #             output = {
    #                 'success' : True,
    #                 'message' : 'get hardware data',
    #                 'data' : results
    #             }
    #             resp.body = json.dumps(output, indent = 2)
    #         else:
    #             column = ('Id Hardware', 'Hardware Name', 'Type', 'Description', 'Sensor Name', 'Sensor Unit')
    #             query = db.select("select hardware.id_hardware, hardware.name, hardware.type, hardware.description, "
    #                 "sensor.name, sensor.unit from hardware, sensor where id_hardware = '%s' and lower(type) = 'sensor'" % idh)
    #             for row in query:
    #                 results.append(dict(zip(column, row)))
    #             output = {
    #                 'success' : True,
    #                 'message' : 'get hardware data',
    #                 'data' : results
    #             }
    #             resp.body = json.dumps(output, indent = 2)
    #     else:
    #         raise falcon.HTTPBadRequest('Id Hardware does not exist: {}'.format(idh))
    #     db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idh):
        db = database()
        results = []
        column = ('Id Hardware','Hardware Name', 'Type', 'Description')
        ncolumn = ('Id Node', 'Node Name', 'Location')
        scolumn = ('Id Sensor', 'Sensor Name', 'Sensor Unit')
        idhcheck = db.check("select * from hardware where id_hardware = '%s'" % idh)
        if idhcheck:
            query = db.select("select * from hardware where id_hardware = '%s'" % idh)
            for row in query:
                results.append(dict(zip(column, row)))
            hwcheck = db.check("select * from hardware where id_hardware = '%s' and (lower(type) = lower('microcontroller unit') or lower(type) = lower('single-board computer'))" % idh)
            if hwcheck:
                nresults = []
                query = db.select("select id_node, name, location from node where id_hardware = '%s')" % idh)
                for row in query:
                    nresults.append(dict(zip(column, row)))
                output = {
                    'success' : True,
                    'message' : 'get hardware data',
                    'hardware' : results,
                    'node' : nresults
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                sresults = []
                query = db.select("select id_sensor, name, unit from sensor where id_hardware = '%s'" % idh)
                for row in query:
                    sresults.append(dict(zip(column, row)))
                output = {
                    'success' : True,
                    'message' : 'get hardware data',
                    'hardware' : results,
                    'sensor' : sresults 
                }
                resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('Id Hardware does not exist: {}'.format(idh))
        db.close()
    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        key = []
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Hardware Name', 'Type', 'Description'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        hwname = params['Hardware Name']
        type = params['Type']
        desc = params['Description']
        key.append(dict(zip(params.keys(), params.values())))
        if 'single-board computer' in type.lower() or 'microcontroller unit' in type.lower() or 'sensor' in type.lower():
            db.commit("insert into hardware (name, type, description) values ('%s', '%s', '%s')" % (hwname, type, desc))
            output = {
                'success' : True,
                'message' : 'add new hardware',
                'data' : key
            }

            resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('Type must Single-Board Computer, Microcontroller Unit, or Sensor')
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idh):
        global results
        db = database()
        results = []
        column = ('Id Hardware', 'Hardware Name', 'Type', 'Description')
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
        required = {'Hardware Name', 'Type', 'Description'}
        missing = required - set(params.keys())
        if 'Hardware Name' in missing and 'Type' in missing and 'Description' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        elif 'Hardware Name' not in missing and 'Type' not in missing and 'Description' not in missing:
            if 'single-board computer' in params['Type'].lower() or 'microcontroller unit' in params['Type'].lower() or 'sensor' in params['Type'].lower():
                db.commit("update hardware set name = '%s', type = '%s', description = '%s' where id_hardware = '%s'"
                          % (params['Hardware Name'], params['Type'], params['Description'], idh))
            else:
                raise falcon.HTTPBadRequest('Type must Single-Board Computer, Microcontroller Unit, or Sensor')
        elif 'Hardware Name' in missing and 'Type' in missing:
            db.commit(
                "update hardware set description = '%s' where id_hardware = '%s'" % (params['Description'], idh))
        elif 'Hardware Name' in missing and 'Description' in missing:
            if 'single-board computer' in params['Type'].lower() or 'microcontroller unit' in params['Type'].lower() or 'sensor' in params['Type'].lower():
                db.commit("update hardware set type = '%s' where id_user = '%s'" % (params['Type'], idh))
            else:
                raise falcon.HTTPBadRequest('Type must Single-Board Computer, Microcontroller Unit, or Sensor')
        elif 'Type' in missing and 'Description' in missing:
            db.commit("update hardware set name = '%s' where id_hardware = '%s'" % (params['Hardware Name'], idh))
        elif 'Type' in missing:
            db.commit("update hardware set name = '%s', description = '%s' where id_hardware = '%s'"
                      % (params['Hardware Name'], params['Description'], idh))
        elif 'Hardware Name' in missing:
            if 'single-board computer' in params['Type'].lower() or 'microcontroller unit' in params['Type'].lower() or 'sensor' in params['Type'].lower():
                db.commit("update hardware set type = '%s' and set description = '%s' where id_hardware = '%s'"
                          % (params['Type'], params['Description'], idh))
            else:
                raise falcon.HTTPBadRequest('Type must Single-Board Computer, Microcontroller Unit, or Sensor')
        elif 'Description' in missing:
            if 'single-board computer' in params['Type'].lower() or 'microcontroller unit' in params['Type'].lower() or 'sensor' in params['Type'].lower():
                db.commit("update hardware set name = '%s' and set type = '%s' where id_hardware = '%s'"
                          % (params['Hardware Name'], params['Type'], idh))
            else:
                raise falcon.HTTPBadRequest('Type must Single-Board Computer, Microcontroller Unit, or Sensor')
        query = db.select("select * from hardware where id_hardware = '%s'" % idh)
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'update hardware data',
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
        required = {'Id Hardware'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        id_hardware = params['Id Hardware']
        checking = db.check("select * from hardware where id_hardware = '%s'" % id_hardware)
        if checking:
            db.commit("delete from hardware where id_hardware = '%s'" % id_hardware)
            output = {
                'success' : True,
                'message': 'delete hardware',
                'id' : '{}'.format(id_hardware)
            }
            resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('Hardware Id is not exist: {}'.format(id_hardware))
        db.close()
