import json
from database import database

class Add_hardware:
    def on_post(self, req, resp):
        db = database()
        results = []
        column = ('Id Hardware','Hardware Name', 'Type', 'Description')
        params = req.params
        verify_params = True

        if 'name' not in params:
            verify_params = False
        if 'type' not in params:
            verify_params = False
        if 'description' not in params:
            verify_params = False

        if verify_params is True:
            check = db.check("select * from hardware where lower(name) = lower('%s')" % params['name'])
            if check is False:
                db.insert("insert into hardware (name, type, description) values ('%s', '%s', '%s')" %
                          (params['name'], params['type'], params['description']))
                query = db.select("select * from hardware where lower(name) = lower('%s')" % params['name'])
                for row in query:
                    results.append(dict(zip(column, row)))
            elif check is True:
                results = {
                    'message': 'Hardware is already exist'
                }
        elif verify_params is False:
            results = {
                'status': 'fail',
                'message': 'Need name, type, and description parameter'
            }
        resp.body = json.dumps(results, indent=2)

class View_hardware:
    def on_get(self, req, resp):
        db = database()
        column = ('Hardware Name', 'Type', 'Description')
        results = []
        query = db.select("select name, type, description from hardware")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent = 2)

class Search_hardware:
    def on_get(self,req, resp, hwname):
        db = database()
        column = ('Hardware Name', 'Type', 'Description')
        results = []

        checking = db.check("select * from hardware where lower(name) = lower('%s')" % hwname)
        if checking is True:
            query = db.select("select name, type, description from hardware where lower(name) = lower('%s')" % hwname)
            for row in query:
                results.append(dict(zip(column, row)))
        elif checking is False:
            results = {
                'No Content':'There is no Hardware name %s' % hwname
            }
        resp.body = json.dumps(results, indent = 2)