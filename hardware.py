import falcon, json
from database import *

class Hardware:
    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('id_hardware','name', 'type', 'description')
        results = []
        node_result = []
        sensor_result = []
        
        if not req.params:
            query = db.select("select id_hardware, name, type, description from hardware")
            node = db.select("select id_hardware, name, type, description from hardware where lower(type) = 'single-board computer' or lower(type) = 'microcontroller unit'")
            sensor = db.select("select id_hardware, name, type, description from hardware where lower(type) = 'sensor'")
        elif req.params:
            type = req.params['type']
            if 'sensor' in type:
                query = db.select("select id_hardware, name, type, description from hardware where lower(type) = 'sensor'")
            elif 'node' in type:
                query = db.select("select id_hardware, name, type, description from hardware where lower(type) = 'single-board computer' or lower(type) = 'microcontroller unit'")
            else:
                raise falcon.HTTPBadRequest('Bad Request', 'Params not found')

        for row in query:
            results.append(dict(zip(column, row)))
        for row in node:
            node_result.append(dict(zip(column, row)))
        for row in sensor:
            sensor_result.append(dict(zip(column, row)))
        
        output = {
            'success' : True,
            'message' : 'get hardware data',
            'node' : node_result,
            'sensor' : sensor_result
        }
        resp.body = json.dumps(output, indent=2)
        db.close()
        
    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idh):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        id_user = authData[0]
        isadmin = authData[3]

        if(not isadmin):
            raise falcon.HTTPForbidden('Forbidden', 'You are not an admin')
        results = []
        idhcheck = db.check("select * from hardware where id_hardware = '%s'" % idh)
        if idhcheck:
            hwcheck = db.check("select * from hardware where id_hardware = '%s' "
                               "and (lower(type) = lower('microcontroller unit') "
                               "or lower(type) = lower('single-board computer'))" % idh)
            if hwcheck:
                column = ('id_hardware','hardware name', 'type', 'description', 'node name', 'node location')
                query = db.select("select hardware.id_hardware, hardware.name, hardware.type, hardware.description, "
                                  "case when node.name is null then 'No Record' else node.name end, "
                                  "case when node.location is null then 'No Record' else node.location end "
                                  "from hardware left join node on hardware.id_hardware = node.id_hardware "
                                  "where hardware.id_hardware = '%s'" 
                                  % idh)
                for row in query:
                    results.append(dict(zip(column, row)))
                output = {
                    'success' : True,
                    'message' : 'get hardware data',
                    'hardware' : results
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                column = ('id_hardware','name', 'type', 'description', 'sensor name', 'sensor unit')
                query = db.select("select hardware.id_hardware, hardware.name, hardware.type, hardware.description, "
                                  "case when sensor.name is null then 'No Record' else sensor.name end, "
                                  "case when sensor.unit is null then 'No Record' else sensor.unit end "
                                  "from hardware left join sensor on hardware.id_hardware = sensor.id_hardware "
                                  "where hardware.id_hardware = '%s'" 
                                  % idh)
                for row in query:
                    results.append(dict(zip(column, row)))
                output = {
                    'success' : True,
                    'message' : 'get hardware data',
                    'hardware' : results
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
            raise falcon.HTTPUnsupportedMediatype("Supported format: JSON or form")

        required = {'name', 'type', 'description'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        hwname = params['name']
        type = params['type']
        desc = params['description']
        key.append(dict(zip(params.keys(), params.values())))
        if 'single-board computer' in type.lower() or 'microcontroller unit' in type.lower() or 'sensor' in type.lower():
            db.commit("insert into hardware (name, type, description) values ('%s', '%s', '%s')" % (hwname, type, desc))
            output = {
                'success' : True,
                'message' : 'add new hardware',
                'hardware' : key
            }

            resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idh):
        global results
        db = database()
        results = []
        column = ('id_hardware', 'name', 'type', 'description')
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediatype("Supported format: JSON or form")
        required = {'name', 'type', 'description'}
        missing = required - set(params.keys())
        if 'name' in missing and 'type' in missing and 'description' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        elif 'name' not in missing and 'type' not in missing and 'description' not in missing:
            if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
                db.commit("update hardware set name = '%s', type = '%s', description = '%s' where id_hardware = '%s'"
                          % (params['name'], params['type'], params['description'], idh))
            else:
                raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        #Stop kalau mau mensetting update data harus memasukkan semua required
        elif 'name' in missing and 'type' in missing:
            db.commit(
                "update hardware set description = '%s' where id_hardware = '%s'" % (params['description'], idh))
        elif 'name' in missing and 'description' in missing:
            if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
                db.commit("update hardware set type = '%s' where id_user = '%s'" % (params['type'], idh))
            else:
                raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        elif 'type' in missing and 'description' in missing:
            db.commit("update hardware set name = '%s' where id_hardware = '%s'" % (params['name'], idh))
        elif 'type' in missing:
            db.commit("update hardware set name = '%s', description = '%s' where id_hardware = '%s'"
                      % (params['name'], params['description'], idh))
        elif 'name' in missing:
            if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
                db.commit("update hardware set type = '%s' and set description = '%s' where id_hardware = '%s'"
                          % (params['type'], params['description'], idh))
            else:
                raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        elif 'description' in missing:
            if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
                db.commit("update hardware set name = '%s' and set type = '%s' where id_hardware = '%s'"
                          % (params['name'], params['type'], idh))
            else:
                raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        query = db.select("select * from hardware where id_hardware = '%s'" % idh)
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'update hardware data',
            'hardware' : results
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, idh):
        db = database()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediatype("Supported format: JSON or form")
        checking = db.check("select * from hardware where id_hardware = '%s'" % idh)
        if checking:
            try:
                db.commit("delete from hardware where id_hardware = '%s'" % idh)
                output = {
                    'success' : True,
                    'message': 'delete hardware',
                    'id' : '{}'.format(idh)
                }
                resp.body = json.dumps(output, indent = 2)
            except:
                output = {
                    'success' : False,
                    'message' : 'can\' delete hardware, there are nodes referenced to id hardware = {}'.format(idh) 
                }
        else:
            raise falcon.HTTPBadRequest('Hardware Id is not exist: {}'.format(idh))
        db.close()
