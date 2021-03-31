import falcon, json
from database import *

class Node:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
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
            output = {
                'success' : True,
                'message' : 'get node data',
                'node' : results
            }
            resp.body = json.dumps(output, indent=2)
        else:
            query = db.select("select * from node where id_user = '%s'" % idu)
            for row in query:
                results.append(dict(zip(column, row)))
            output = {
                'success' : True,
                'message' : 'get node data',
                'node' : results
            }
            resp.body = json.dumps(output, indent=2)
        db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idn):
        db = database()
        function = Function()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]

        ncheck = db.check("select * from node where id_node = '%s'" % idn)
        if not ncheck:
            raise falcon.HTTPBadRequest('Id Node does not exist: {}'.format(idn))

        id_user = function.nodeItem(idn, 'id_user')
        if(id_user != idu):
            if(not isadmin):
                raise falcon.HTTPForbidden('Forbidden', 'You are not an admin')

        user = []
        node = []
        hardware = []
        sensor = []
        ucolumn = ('id_user','name')
        ncolumn = ('id_node', 'name', 'location', 'username')
        hcolumn = ('name', 'type')
        scolumn = ('id_sensor','name', 'unit', 'activity')
        query = db.select('''select user_person.id_user, user_person.username 
                             from user_person left join node on user_person.id_user = node.id_user 
                             where node.id_node = '%s' ''' % idn)
        for row in query:
            user.append(dict(zip(ucolumn, row)))
        query = db.select('''select node.id_node, node.name, node.location, user_person.username 
                             from node left join user_person on node.id_user = user_person.id_user
                              where node.id_node = '%s' ''' % idn)
        for row in query:
            node.append(dict(zip(ncolumn, row)))
        query = db.select(''' select hardware.name, hardware.type from hardware 
                              left join node on hardware.id_hardware = node.id_hardware 
                              where id_node = '%s' ''' % idn)
        for row in query:
            hardware.append(dict(zip(hcolumn, row)))
        query = db.select('''select sensor.id_sensor, sensor.name, sensor.unit, sensor.activity from sensor
                             left join node on sensor.id_node = node.id_node 
                             where sensor.id_node = '%s' ''' % idn)
        for row in query:
            sensor.append(dict(zip(scolumn, row)))
        output = {
            'success':True,
            'message':'get data',
            'node':node,
            'user':user,
            'hardware':hardware,
            'sensor':sensor
        }
        resp.body = json.dumps(output, indent=2)
            
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
        
        if 'id hardware' in notgiven:
            id_hardware = params['id hardware']
            db.commit("insert into node(name, location, id_hardware, id_user) values ('%s','%s', '%s', '%s')" % (node_name, location, id_hardware, id_user))
            key = {
                'name': node_name,
                'location': location,
                'id_hardware': id_hardware,
                'id_user': id_user
            }
            output = {
                'success': True, 
                'message':'add new node',
                'node':key
            }

        elif 'id hardware' not in notgiven:
            db.commit("insert into node(name, location, id_hardware, id_user) values ('%s','%s', NULL, '%s')" % (node_name, location, id_user))
            key = {
                'Node Name': node_name,
                'Location': location,
                'Id Hardware': None,
                'Id User': id_user
            }
            output = {
                'success': True, 
                'message':'add new node',
                'node':key
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
        
        ncheck = db.check("select * from node where id_node = '%s'" % idn)
        if not ncheck:
            raise falcon.HTTPBadRequest('Id Node does not exist: {}'.format(idn))

        id_user = function.nodeItem(idn, 'id_user')
        if(id_user != idu):
            if(not isadmin):
                raise falcon.HTTPForbidden('Forbidden', 'You cannot edit other user\'s data')

        required = {'name', 'location'}
        missing = required - set(params.keys())

        if 'name' in missing and 'location' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        elif 'name' not in missing and 'location' not in missing:
            db.commit("update node set name = '%s', location = '%s' where id_node = '%s'"
                      % (params['name'], params['location'], idn))
        elif 'location' not in missing:
            db.commit("update node set location = '%s' where id_node = '%s'" % (params['location'], idn))
        elif 'name' not in missing:
            db.commit("update node set name = '%s' where id_node = '%s'" % (params['name'], idn))
        query = db.select("select * from node where id_node = '%s'" % idn)
        for row in query:
            results.append(dict(zip(column,row)))
        output = {
            'success':True,
            'message':'update node',
            'node':results
        }
        resp.body = json.dumps(output, indent = 2)
        
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, idn):
        db = database()
        auth = Authorize()
        function = Function()
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

        ncheck = db.check("select * from node where id_node = '%s'" % idn)
        if not ncheck:
            raise falcon.HTTPBadRequest('Id Node does not exist: {}'.format(idn))

        id_user = function.nodeItem(idn,'id_user')
        if(id_user != idu):
            raise falcon.HTTPForbidden('Forbidden', 'You cannot delete other user\'s data')
        
        checking = db.check("select * from node where id_node = '%s'" % idn)
        if checking:
            db.commit("delete from node where id_node = '%s'" % idn)
            output = {
                'success' : True,
                'message': 'delete node',
                'id' : '{}'.format(idn)
            }
            resp.body = json.dumps(output)

        elif not checking:
            raise falcon.HTTPBadRequest('Node Id is not exist: {}'.format(idn))
        db.close()
