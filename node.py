import falcon, json
from database import *

class Node:

    def on_get(self, req, resp):
        db = database()
        column = ('Name', 'Location', 'Id Hardware', 'Id User')
        results = []
        query = db.select("select name, location, id_hardware, id_user from node")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)
        db.close()

    def on_post(self, req, resp):
        db = database()
        type = 'node'
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
        id_user = params['Id User']

        hw_check = db.check("select id_hardware from hardware where id_hardware = '%s' and lower(type) = '%s'"
                            % (id_hardware, type))
        usr_check = db.check("select id_user from user_person where id_user = '%s'" % id_user)
        if hw_check and usr_check:
            db.commit("insert into node (name, location, id_hardware, id_user) values ('%s', '%s', '%s', '%s')" %
                      (node_name, location, id_hardware, id_user))
            results = {
                'Message': 'Success'
            }
            resp.body = json.dumps(results)
        else:
            if not usr_check and not hw_check:
                raise falcon.HTTPBadRequest('Id user and hardware not present: {}'.format((id_user, id_hardware)))
            elif not usr_check:
                raise falcon.HTTPBadRequest('Id user not present: {}'.format(id_user))
            elif not hw_check:
                raise falcon.HTTPBadRequest('Id hardware not present or not valid: {}'.format(id_hardware))
        db.close()

    def on_put(self, req, resp, node):
        db = database()
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
                      % (params['Node Name'], params['Location'], node))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
            resp.body = json.dumps(results)
        elif 'Location' not in missing:
            db.commit("update node set location = '%s' where id_node = '%s'" % (params['Location'], node))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
            resp.body = json.dumps(results)
        elif 'Name' not in missing:
            db.commit("update node set name = '%s' where id_node = '%s'" % (params['Node Name'], node))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
            resp.body = json.dumps(results)
        db.close()

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
            results = {
                'Message': 'Deleted'
            }
            resp.body = json.dumps(results)

        elif not checking:
            raise falcon.HTTPBadRequest('Node Id is not exist: {}'.format(id_node))
        db.close()
