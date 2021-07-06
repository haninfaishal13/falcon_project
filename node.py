import falcon, json
from database import *

class Node:

    @falcon.before(Authorize())
    def on_get(self, req, resp): #tambah error node 
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]

        column = ('id_node', 'name', 'location', 'id_hardware', 'id_user')
        results = []
        if isadmin:
            query = db.select("select * from node")
            for row in query:
                results.append(dict(zip(column, row)))
            resp.body = json.dumps(output, indent=2)
        else:
            query = db.select("select * from node where id_user = '%s'" % idu)
            for row in query:
                results.append(dict(zip(column, row)))
            
        resp.body = json.dumps(results, indent=2)
        db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idn):
        db = database()
        function = Function()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        try:
            ncheck = db.check("select * from node where id_node = '%s'" % idn)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not ncheck:
            raise falcon.HTTPNotFound()

        id_user = function.nodeItem(idn, 'id_user')
        if(id_user != idu):
            if(not isadmin):
                raise falcon.HTTPForbidden('You are not an admin')

        hardware = []
        sensor = []
        hcolumn = ('name', 'type')
        scolumn = ('id_sensor','name', 'unit')
        nquery = db.select('''select node.id_node, node.name, node.location, user_person.id_user, user_person.username 
                             from node left join user_person on node.id_user = user_person.id_user
                              where node.id_node = '%s' ''' % idn)
        hquery = db.select(''' select hardware.name, hardware.type from hardware 
                              left join node on hardware.id_hardware = node.id_hardware 
                              where id_node = '%s' ''' % idn)
        for row in hquery:
            hardware.append(dict(zip(hcolumn, row)))
        squery = db.select('''select sensor.id_sensor, sensor.name, sensor.unit from sensor
                             left join node on sensor.id_node = node.id_node 
                             where sensor.id_node = '%s' ''' % idn)
        for row in squery:
            sensor.append(dict(zip(scolumn, row)))
        key = {
            'id_node'   : nquery[0][0],
            'name'      : nquery[0][1],
            'location'  : nquery[0][2],
            'id_user'   : nquery[0][3],
            'username'  : nquery[0][4],
            'hardware'  : hardware,
            'sensor'    : sensor
        }
        resp.body = json.dumps(key, indent=2)
            
        db.close()

    @falcon.before(Authorize())
    def on_post(self, req, resp):
        auth = Authorize()
        db = database()
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

        required = {'name', 'location'}
        missing = required - set(params.keys())
        notgiven = set(params.keys()) - required
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        
        node_name = params['name']
        location = params['location']
        id_user = idu
        if 'id_hardware' in notgiven:
            id_hardware = params['id_hardware']
            try:
                checking1 = db.check("select id_hardware from hardware where id_hardware = '%s'" % id_hardware)
            except:
                raise falcon.HTTPBadRequest('Parameter is invalid')
            if not checking1:
                raise falcon.HTTPBadRequest('Id hardware not found')
            checking2 = db.check("select type from hardware where id_hardware = '%s' and (lower(type) = 'single-board computer' or lower(type) = 'microcontroller unit')" % id_hardware)
            if not checking2:
                raise falcon.HTTPBadRequest('Hardware type not match, type should Microcontroller Unit or Single-Board Computer')
            db.commit("insert into node(name, location, id_hardware, id_user) values ('%s','%s', '%s', '%s')" % (node_name, location, id_hardware, id_user))

        elif 'id hardware' not in notgiven:
            db.commit("insert into node(name, location, id_hardware, id_user) values ('%s','%s', NULL, '%s')" % (node_name, location, id_user))
        
        output = {
            'title': 'Success add new node'
        }
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(output, indent = 2)
        
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idn):
        db = database()
        function = Function()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]

        results = []
        column = ('Id Node', 'Name', 'Location', 'Id Hardware', 'Id User')
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
        
        try: #antisipasi jika input id node tidak sesuai dengan tipe data pada database
            ncheck = db.check("select * from node where id_node = '%s'" % idn)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not ncheck:
            raise falcon.HTTPNotFound()

        id_user = function.nodeItem(idn, 'id_user') #cek id user pemilik node yang akan diedit
        if(id_user != idu): #kalau bukan node miliknya dan bukan admin, dapet response error
            if(not isadmin):
                raise falcon.HTTPForbidden('You can\'t edit another user\'s node')

        required = {'name', 'location'}
        missing = required - set(params.keys())
        try: #antisipasi jika masukan pada body tidak sesuai dengan tipe data pada database
            if 'name' in missing and 'location' in missing:
                raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
            elif 'name' not in missing and 'location' not in missing:
                db.commit("update node set name = '%s', location = '%s' where id_node = '%s'"
                          % (params['name'], params['location'], idn))
            elif 'location' not in missing:
                db.commit("update node set location = '%s' where id_node = '%s'" % (params['location'], idn))
            elif 'name' not in missing:
                db.commit("update node set name = '%s' where id_node = '%s'" % (params['name'], idn))
            output = {
                'title':'Success edit node'
            }
            resp.body = json.dumps(output, indent = 2)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, idn):
        db = database()
        auth = Authorize()
        function = Function()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]

        try: #antisipasi input id node tidak sesuai dengan tipe data pada database 
            ncheck = db.check("select * from node where id_node = '%s'" % idn)
        except:
            raise falcon.HTTPBadRequest('Parameter is invalid')
        if not ncheck:
            raise falcon.HTTPNotFound()
        id_user = function.nodeItem(idn,'id_user')
        if(id_user != idu):
            raise falcon.HTTPForbidden('You cannot delete another user\'s data')
        
        checking = db.check("select * from node where id_node = '%s'" % idn)
        if checking:
            db.commit("delete from node where id_node = '%s'" % idn)
            output = {
                'title' : 'Success delete node, id: {}'.format(idn)
            }
            resp.body = json.dumps(output)

        elif not checking:
            raise falcon.HTTPNotFound()
        db.close()
