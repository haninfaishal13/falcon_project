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
        
        query = db.select("select id_hardware, name, type, description from hardware")
        node = db.select("select id_hardware, name, type, description from hardware where lower(type) = 'single-board computer' or lower(type) = 'microcontroller unit'")
        sensor = db.select("select id_hardware, name, type, description from hardware where lower(type) = 'sensor'")
        for row in node:
            node_result.append(dict(zip(column, row)))
        for row in sensor:
            sensor_result.append(dict(zip(column, row)))
        
        output = {
            'title' : 'get hardware',
            'description' : {
                'node' : node_result,
                'sensor' : sensor_result
            }
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

        results = []
        try:
            idhcheck = db.check("select * from hardware where id_hardware = '%s'" % idh)
        except:
            raise falcon.HTTPBadRequest('Bad Request', 'Parameter is invalid')
        if idhcheck:
            hquery = db.select("select id_hardware, name, type, description from hardware where id_hardware = '%s'" 
                                  % idh)
            hwcheck = db.check("select * from hardware where id_hardware = '%s' "
                               "and (lower(type) = lower('microcontroller unit') "
                               "or lower(type) = lower('single-board computer'))" % idh)
            if hwcheck:
                column = ('node name', 'node location')
                nquery = db.select("select name, location from node where id_hardware = '%s'" % idh)
                for row in nquery:
                    results.append(dict(zip(column, row)))
                key = {
                    "id_hardware"   : hquery[0][0],
                    "name"          : hquery[0][1],
                    "type"          : hquery[0][2],
                    "description"   : hquery[0][3],
                    "node"          : results
                }
                output = {
                    'title' : 'get specific hardware',
                    'description' : key
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                column = ('sensor name', 'sensor unit')
                squery = db.select("select name, unit from sensor where id_hardware = '%s'" % idh)
                for row in squery:
                    results.append(dict(zip(column, row)))
                key = {
                    "id_hardware"   : hquery[0][0],
                    "name"          : hquery[0][1],
                    "type"          : hquery[0][2],
                    "description"   : hquery[0][3],
                    "sensor"          : results
                }
                output = {
                    'title' : 'get specific hardware',
                    'description' : key
                }
                resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPNotFound()
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
            raise falcon.HTTPBadRequest('Missing parameter','Parameter used is missing: {}'.format(missing))
        hwname = params['name']
        type = params['type']
        desc = params['description']
        key.append(dict(zip(params.keys(), params.values())))
        if 'single-board computer' in type.lower() or 'microcontroller unit' in type.lower() or 'sensor' in type.lower():
            db.commit("insert into hardware (name, type, description) values ('%s', '%s', '%s')" % (hwname, type, desc))
            output = {
                'title' : 'add hardware',
                'description' : 'success add new hardware'
            }

            resp.body = json.dumps(output, indent = 2)
        else:
            raise falcon.HTTPBadRequest('Invalid Type','Type must Single-Board Computer, Microcontroller Unit, or Sensor')
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idh):
        global results
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        id_user = authData[0]
        isadmin = authData[3]
        try:
            hwcheck = db.check("select * from hardware where id_hardware = '%s'" % idh)
        except:
            raise falcon.HTTPBadRequest('Bad Request', 'Parameter is invalid')
        if not hwcheck:
            raise falcon.HTTPNotFound()
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
            raise falcon.HTTPBadRequest('Missing parameter','Parameter used is missing: {}'.format(missing))
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
                db.commit("update hardware set type = '%s', description = '%s' where id_hardware = '%s'"
                          % (params['type'], params['description'], idh))
            else:
                raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        elif 'description' in missing:
            if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
                db.commit("update hardware set name = '%s', type = '%s' where id_hardware = '%s'"
                          % (params['name'], params['type'], idh))
            else:
                raise falcon.HTTPBadRequest('type must Single-Board Computer, Microcontroller Unit, or Sensor')
        output = {
            'title' : 'edit hardware',
            'description' : 'success edit hardware'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, idh):
        db = database()
        try:
            checking = db.check("select * from hardware where id_hardware = '%s'" % idh)
        except:
            raise falcon.HTTPBadRequest('Bad Request', 'Parameter is invalid')
        if checking:
            try:
                db.commit("delete from hardware where id_hardware = '%s'" % idh)
                output = {
                    'title' : 'delete hardware',
                    'message': 'delete hardware, id: {}'.format(idh)
                }
                resp.body = json.dumps(output, indent = 2)
            except:
                raise falcon.HTTPBadRequest('Bad Request', 'There\'s node or sensor referenced to it')
        else:
            raise falcon.HTTPNotFound()
        db.close()
