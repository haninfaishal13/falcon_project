import json
from database import database


class Add_hardware:
    def on_post(self, req, resp):
        db = database()
        results = []
        column = ('Id Hardware', 'Hardware Name', 'Type', 'Description')
        params = req.params
        verify_params = True

        if 'name' not in params:
            verify_params = False
        if 'type' not in params:
            verify_params = False
        if 'description' not in params:
            verify_params = False

        if verify_params is True:
            check = db.check("select * from hardware where lower(name) = lower('%s') "
                             "and lower(type) = lower('%s') and lower(description) = lower('%s')" %
                             (params['name'], params['type'], params['description']))
            if check is False:
                db.insert("insert into hardware (name, type, description) values ('%s', '%s', '%s')" %
                          (params['name'], params['type'], params['description']))
                query = db.select("select * from hardware where lower(name) = lower('%s') "
                                  "and lower(type) = lower('%s') and lower(description) = lower('%s')" %
                                  (params['name'], params['type'], params['description']))
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
        resp.body = json.dumps(results, indent=2)


class Search_hardware:
    def on_get(self, req, resp, hw_id):
        db = database()
        column = ('Hardware Name', 'Type', 'Description')
        results = []

        checking = db.check("select * from hardware where id_hardware = '%s'" % hw_id)
        if checking is True:
            query = db.select("select name, type, description from hardware where id_hardware = '%s'" % hw_id)
            for row in query:
                results.append(dict(zip(column, row)))
        elif checking is False:
            results = {
                'No Content': 'There is no Hardware id_hardware %s' % hw_id
            }
        resp.body = json.dumps(results, indent=2)


class Delete_hardware:
    def on_post(self, req, resp):
        db = database()
        column = ('Hardware Name', 'Type', 'Description')
        results = []
        params = req.params
        verify_params = True

        if 'id' not in params:
            verify_params = False
        # if 'name' not in params:
        #     verify_params = False
        # if 'type' not in params:
        #     verify_params = False
        # if 'description' not in params:
        #     verify_params = False

        if verify_params is True:
            # check = db.check("select * from hardware where lower(name) = lower('%s') "
            #                  "and lower(type) = lower('%s') and lower(description) = lower('%s')" %
            #                  (params['name'], params['type'], params['description']))
            check = db.check("select * from hardware where id_hardware = '%s'" % params['id'])
            if check is True:
                # db.delete("delete from hardware where lower(name) = lower('%s') "
                #           "and lower(type) = lower('%s') and lower(description) = lower('%s')" %
                #           (params['name'], params['type'], params['description']))
                db.delete("delete from hardware where id_hardware'%s'" % params['id'])
                query = db.select("select name, type, description from hardware")
                for row in query:
                    results.append(dict(zip(column, row)))
            elif check is False:
                results = {
                    'error': 'hardware not found'
                }
        if verify_params is False:
            results = {
                'No Content': 'There is no Hardware name %s' % params['name']
            }
        resp.body = json.dumps(results, indent=2)


class Edit_hardware:
    def on_post(self, req, resp, hw_id):
        db = database()
        results = []
        column = ('Hardware Name', 'Type', 'Description')
        params = req.params
        type_params = True
        desc_params = True

        if 'type' not in params:
            type_params = False
        if 'description' not in params:
            desc_params = False

        check = db.check("select * from hardware where id_hardware = '%s'" % hw_id)

        if check is True:
            if type_params is True and desc_params is True:
                db.update("update hardware set type = '%s' and description = '%s'" %
                          (params['type'], params['description']))
            elif type_params is True and desc_params is False:
                db.update("update hardware set type = '%s'" % params['type'])
            elif type_params is False and desc_params is True:
                db.update("update hardware set description = '%s'" % params['description'])
            elif type_params is False and desc_params is False:
                results = {
                    'error': 'need type or description for edit'
                }
            query = db.select("select name, type, description")
            for row in query:
                results.append(dict(zip(column, row)))
        elif check is False:
            results = {
                'No Content': 'There is no name %s' % hw_id
            }
        resp.body = json.dumps(results, indent = 2)
