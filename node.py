import json
from database import database

class Add_node:
    def on_post(self, req, resp):
        db = database()
        results = []
        column = ('Id Node','Name','Location','Id Hardware','Id User',)
        params = req.params
        verify_params = True

        if 'name' not in params:
            verify_params = False
        if 'location' not in params:
            verify_params = False
        if 'id_hardware' not in params:
            verify_params = False
        if 'id_user' not in params:
            verify_params = False

        if verify_params is True:
            check = db.check("select * from node where lower(name) = lower('%s')" % params['name'])
            if check is False:
                db.insert("insert into node (name, location, id_hardware, id_node) values ('%s', '%s', '%s','%s')" %
                          (params['name'], params['location'], params['id_hardware'], params['id_node']))
                query = db.select("select * from node where lower(name) = lower('%s')" % params['name'])
                for row in query:
                    results.append(dict(zip(column, row)))
            elif check is True:
                results = {
                    'message': 'Node is already exist'
                }
        elif verify_params is False:
            results = {
                'status': 'fail',
                'message': 'Need name, location,id hardware and id user parameter'
            }
        resp.body = json.dumps(results, indet = 2)

class View_node:
    def on_get(self, req, resp):
        db = database()
        column = ('Name','Location')
        results = []
        query = db.select("select name, location from node")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)

class Search_node:
    def on_get(self, req, resp, node):
        db = database()
        column = ('Name','Location','Id Hardware','Id User',)
        results = []
        checking = db.check("select * from node where lower(location) = lower('%s')" % node)
        if checking is True:
            query = db.select("select * from node where lower(location) = lower('%s')" % node)
            for row in query:
                results.append(dict(zip(column, row)))
        elif checking is False:
            results = {
                'No Content': 'There is no Node location %s' % node
            }
        resp.body = json.dumps(results, indent=2)

class Delete_node:
    def on_post(self, req, resp):
        db = database()
        column = ('Name','Location','Id Hardware','Id User',)
        results = []
        params = req.params
        verify_params = True

        if 'id' not in params:
            verify_params = False

        if verify_params is True:
            check = db.check("select * from node where id_node = '%s'" % (params['id']))
            if check is True:
                db.delete("delete from node where id_node = '%s'" % params['id'])
                query = db.select("select name, location from node")
                for row in query:
                    results.append(dict(zip(column, row)))
            elif check is False:
                results = {
                    'error': 'Node not found'
                }
        if verify_params is False:
            results = {
                'No Content': 'There is no Node with id %s' % params['id']
            }
        resp.body = json.dumps(results, indent=2)