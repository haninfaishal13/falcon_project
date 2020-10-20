import falcon, json
from database import *

class Node:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('Id Node', 'Name', 'Location', 'Id Hardware', 'Id User')
        results = []
        query = db.select("select * from node")
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'get node data',
            'data' : results
        }
        resp.body = json.dumps(output, indent=2)
        db.close()

#   Node-Sensor Scenario
    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idn):
        db = database()
        results = []
        column = ('Id Node', 'Node Name', 'Location', 'Hardware Name', 'User')
        ncheck = db.check("select * from node where id_node = '%s'" % idn)
        if ncheck:
            query = db.select('''select node.id_node, node.name, node.location, hardware.name, user_person.username
                                 from node left join hardware on node.id_hardware = hardware.id_hardware
                                 left join user_person on node.id_user = user_person.id_user
                                 where node.id_node = %s ''' % idn)
            for row in query:
                results.append(dict(zip(column, row)))
            output = {
                'success':True,
                'message':'get node data',
                'data':results
            }
            resp.body = json.dumps(output, indent=2)

        else:
            raise falcon.HTTPBadRequest('Id Node does not exist: {}'.format(idn))
        db.close()

    @falcon.before(Authorize())
    def on_post(self, req, resp):
        auth = Authorize()
        db = database()

        authData = auth.getAuthentication(req.auth.spli(' '))
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

        required = {'Node Name', 'Location', 'Id Hardware', 'Id User'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        node_name = params['Node Name']
        location = params['Location']
        id_hardware = params['Id Hardware']
        id_user = idu

        key.append(dict(zip(params.keys(), params.values())))
        hwcheck = db.check("select id_hardware from hardware where id_hardware = '%s'" % id_hardware)
        usrcheck = db.check("select id_user from user_person where id_user = '%s'" % id_user)
        if hwcheck is True and usrcheck is True:
            hwtcheck = db.check("select id_hardware from hardware where id_hardware = '%s' and (lower(type) = lower('Microcontroller Unit') or lower(type) = lower('Single-Board Computer'))" % id_hardware)
            if hwtcheck:
                db.commit("insert into node (name, location, id_hardware, id_user) values ('%s', '%s', '%s', '%s')" %
                          (node_name, location, id_hardware, id_user))
                output = {
                    'success': True, 
                    'message':'add new node',
                    'data':key
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                raise falcon.HTTPBadRequest('Hardware type not valid, required type: Microcontroller Unit or Single-Board Computer')
        else:
            if not usrcheck and not hwcheck:
                raise falcon.HTTPBadRequest('Id User and Hardware not present: {}'.format((id_user, id_hardware)))
            elif not usrcheck:
                raise falcon.HTTPBadRequest('Id User not present: {}'.format(id_user))
            elif not hwcheck:
                raise falcon.HTTPBadRequest('Id Hardware not present or not valid: {}'.format(id_hardware))
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idn):
        db = database()
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
        required = {'Node Name', 'Location'}
        missing = required - set(params.keys())

        if 'Node Name' in missing and 'Location' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        elif 'Node Name' not in missing and 'Location' not in missing:
            db.commit("update node set name = '%s', location = '%s' where id_node = '%s'"
                      % (params['Node Name'], params['Location'], idn))
        elif 'Location' not in missing:
            db.commit("update node set location = '%s' where id_node = '%s'" % (params['Location'], idn))
        elif 'Node Name' not in missing:
            db.commit("update node set name = '%s' where id_node = '%s'" % (params['Node Name'], idn))
        query = db.select("select * from node where id_node = '%s'" % idn)
        for row in query:
            results.append(dict(zip(column,row)))
        output = {
            'success':True,
            'message':'update node',
            'data':results
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

        required = {'Id Node'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        id_node = params['Id Node']

        checking = db.check("select * from node where id_node = '%s'" % id_node)

        if checking:
            db.commit("delete from node where id_node = '%s'" % id_node)
            output = {
                'success' : True,
                'message': 'delete node',
                'id' : '{}'.format(id_node)
            }
            resp.body = json.dumps(output)

        elif not checking:
            raise falcon.HTTPBadRequest('Node Id is not exist: {}'.format(id_node))
        db.close()
