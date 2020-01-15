import json
from database import database

class View_sensor:
    def on_get(self, req, resp):
        db = database()
        column = ('Name', 'Unit')
        results = []

        query = db.selet("select name, unit from sensor")
        for row in query:
            results.append(dict(zip(column, row)))

class Add_sensor:
    def on_post(self, req, resp):
        db = database()
        column = ('Id Sensor', 'Name', 'Unit', 'Id Hardware', 'Id Node')
        results = []
        params = req.params
        verify_params = True

        if 'name' not in params:
            verify_params = False
        if 'unit' not in params:
            verify_params = False
        if 'id_hardware' not in params:
            verify_params = False
        if 'id_node' not in params:
            verify_params = False

        if verify_params is True:
            db.insert("insert into sensor (name, unit, id_hardware, id_node) values ('%s','%s','%s','%s')" %
                      (params['name'], params['unit'], params['id_hardware'], params['id_node']))
            query = db.select("select * from sensor "
                              "where name = '%s' and unit = '%s' and id_hardware = '%s' and id_node = '%s'" %
                              (params['name'], params['unit'], params['id_hardware'], params['id_node']))
            for row in column:
                results.append(dict(zip(column, row)))

        else:
            result = {
                'status': 'fail',
                'message': 'Need name, node, id hardware and id node parameter'
            }
        resp.body = json.dumps(results)

class Search_sensor:
    def on_get(self, req, resp, sen_name):
        db= database()
        column = ('Name', 'Unit')
        results = []

        check = db.check("select * from sensor where lower(name) = lower('%s')" % sen_name)
        if check is True:
            query = db.select(
                "select name, unit from sensor where lower(name) = lower('%s')" % sen_name)
            for row in query:
                results.append(dict(zip(column, row)))
        elif check is False:
            results = {
                'No Content': 'There is no Sensor name %s' % sen_name
            }
        resp.body = json.dumps(results, indent=2)

