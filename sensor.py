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

        results = []
        column = ('Id Sensor', 'Name', 'Unit', 'id hardware', 'id node')
        if isadmin:
            # jika pengguna adalah admin, maka pengguna dapat melihat semua sensor yang sudah diinput oleh pengguna lainnya
            query = db.select("select * from sensor")
            for row in query:
                results.append(dict(zip(column, row)))

        else:
            # jika bukan admin, maka pengguna hanya dapat melihat sensor yang sudah diinput oleh dirinya sendiri
            query = db.select('''select sensor.id_sensor, sensor.name, sensor.unit, 
                                sensor.id_hardware, sensor.id_node from sensor left join node
                                on sensor.id_node = node.id_node where node.id_user = '%s' ''' % idu)
            for row in query:
                results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, ids):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        try: 
            scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not scheck:
            raise falcon.HTTPNotFound()
        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        id_user = query[0][0]
        if(id_user != idu):
           raise falcon.HTTPForbidden('You can\'t see another user\'s sensor')
        channel = []
        ccolumn = ('time', 'value')
        squery = db.select("select id_sensor, name, unit from sensor where id_sensor = '%s'" % ids)
        channel_query = db.select('''select time, value from channel where id_sensor = '%s' ''' % ids)
        for row in channel_query:
            channel.append(dict(zip(ccolumn, row)))
        key = {
            'id_sensor' : squery[0][0],
            'name'      : squery[0][1],
            'unit'      : squery[0][2],
            'channel'   : channel
        }
        resp.body = json.dumps(key, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        function = Function()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]

        key = []
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'name', 'unit', 'id_node'}
        missing = required - set(params.keys())
        given = set(params.keys()) - required
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        name = params['name']
        unit = params['unit']
        id_node = params['id_node']
        try:
            checking = db.check("select id_node from node where id_node = '%s'" % id_node)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not checking:
            raise falcon.HTTPBadRequest('Id Node not found')
        id_user = function.nodeItem(id_node, 'id_user') #cek id user pemilik node yang akan diedit
        if(id_user != idu): #kalau bukan node miliknya dan bukan admin, dapet response error
            if(not isadmin):
                raise falcon.HTTPForbidden('You can\'t use another user\'s node')
        if 'id_hardware' in given:
            id_hardware = params['id_hardware']
            try:
                checking1 = db.check("select id_hardware from hardware where id_hardware = '%s'" % id_hardware)
            except:
                raise falcon.HTTPBadRequest('Parameter is invalid')
            if not checking1:
                raise falcon.HTTPBadRequest('Id hardware not found')
            checking2 = db.check("select type from hardware where id_hardware = '%s' and lower(type) = 'sensor'" % id_hardware)
            if not checking2:
                raise falcon.HTTPBadRequest('Hardware type not match, type should Sensor')
            try:
                db.commit("insert into sensor (name, unit, id_node, id_hardware) values ('%s','%s','%s','%s')" % (name, unit, id_node, id_hardware))
            except:
                raise falcon.HTTPBadRequest('Parameter is invalid')
        elif 'id hardware' not in given:
            try:
                db.commit("insert into sensor (name, unit, id_node, id_hardware) values ('%s','%s','%s',NULL)" % (name, unit, id_node))
            except:
                raise falcon.HTTPBadRequest('Parameter is invalid')
        output = {
            'title':'Success add new sensor'
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
        

        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        try: #antisipasi jika ada masukan id tidak sesuai dengan tipe data pada database
            ids = int(ids)
            scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not scheck:
            raise falcon.HTTPNotFound()
        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        value = query[0]
        id_user = value[0]
        if not isadmin:
            if(id_user != idu):
               raise falcon.HTTPForbidden('You can\'t edit another user\'s sensor')
        required = {'name', 'unit'}
        missing = required - set(params.keys())
        
        try: #antisipasi data pada body tidak sesuai dengan tipe data pada database
            if 'name' in missing and 'unit' in missing:
                raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
            if 'name' not in missing and 'unit' not in missing:
                db.commit("update sensor set name = '%s', unit = '%s' where id_sensor = '%s'"
                              % (params['name'], params['unit'], ids))
            elif 'name' not in missing:
                db.commit("update sensor set name = '%s' where id_sensor = '%s'" % (params['name'], ids))
            elif 'unit' not in missing:
                db.commit("update sensor set unit = '%s' where id_sensor = '%s'" % (params['unit'], ids))
            output = {
                'title' : 'Success edit sensor data'
            }
            resp.body = json.dumps(output, indent = 2)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, ids):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        try:
            scheck = db.check("select * from sensor where id_sensor = '%s'" % ids)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not scheck:
            raise falcon.HTTPNotFound()
        query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % ids)
        id_user = query[0][0]
        if not isadmin:
            if(id_user != idu):
               raise falcon.HTTPForbidden('Forbidden', 'You can\'t delete another user\'s sensor')

        db.commit("delete from sensor where id_sensor = '%s'" % ids)
        output = {
            'title' : 'Succes delete sensor data, id: {}'.format(ids)
        }
        resp.body = json.dumps(output)
        db.close()

