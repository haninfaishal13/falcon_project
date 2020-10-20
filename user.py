import falcon, json
from database import *

class User:

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        results = []
        column = ('Id User', 'Name', 'Password')
        query = db.select("select id_user, username, password from user_person")
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'Success' : True,
            'Message' : 'get user data',
            'Data' : results
        }
        resp.body = json.dumps(output, indent=2)
        db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idu):
        db = database()
        uresults = []
        cresults = []
        ucolumn = ('Id User','Name', 'Password')
        ccolumn=('Time', 'Value', 'Sensor Name', 'Sensor Unit')
        usrcheck = db.check("select * from user_person where id_user = '%s'" % idu) 
        if usrcheck: #checking id user exist or not
            uquery = db.select("select * from user_person where id_user = '%s'" % idu)
            cquery = db.select("select channel.time, channel.value, sensor.name, sensor.unit from channel "
                               "left join sensor on channel.id_sensor = sensor.id_sensor "
                               "left join node on sensor.id_node = node.id_node "
                               "left join user_person on node.id_user = user_person.id_user "
                               "where user_person.id_user = '%s'" % idu)
            for row in uquery:
                uresults.append(dict(zip(ucolumn, row)))
            for row in cquery:
                cresults.append(dict(zip(ccolumn, row)))
        else:
                raise falcon.HTTPBadRequest('Id User does not exist: {}'.format(idu))
        output = {
            'sucess' : True,
            'message' : 'get user data',
            'data' : uresults,
            'channel' : cresults
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()
    @falcon.before(Authorize())
    def on_post(self, req, resp):
        db = database()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'Username', 'Password'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        username = params['Username']
        password = params['Password']

        checking = db.check("select * from user_person where username = '%s'" % username)
        if checking:
            raise falcon.HTTPBadRequest('User already exist: {}'.format(username))
        else:
            db.commit("insert into user_person (username, password) values ('%s', '%s')" % (username, password))
            
        output = {
            'success' : True,
            'message' : 'add new user',
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

        required = {'Id User'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        id_user = params['Id User']
        checking = db.check("select * from user_person where id_user = '%s'" % id_user)
        if checking:
            db.commit("delete from user_person where id_user = '%d'" % id_user)
            output = {
                'success' : True,
                'message' : 'delete user',
                'id' : '{}'.format(id_user)
            }
            resp.body = json.dumps(output)
        else:
            raise falcon.HTTPBadRequest('User Id is not exist: {}'.format(id_user))
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idu):
        global results
        db = database()
        results = []
        column = ('Id User', 'Username', 'Password')
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
        required = {'Username', 'Password'}
        missing = required - set(params.keys())

        if 'Username' in missing and 'Password' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        elif 'Username' not in missing and 'Password' not in missing:
            db.commit("update user_person set username = '%s', password = '%s' where id_user = '%s'" %
                      (params['Username'], params['Password'], idu))
        elif 'Password' not in missing:
            db.commit("update user_person set password = '%s' where id_user = '%s'" % (params['Password'], idu))
        elif 'Username' not in missing:
            db.commit("update user_person set username = '%s' where id_user = '%s'" % (params['Username'], idu))
        query = db.select("select * from user_person where id_user = '%s'" % idu)
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'update user data',
            'data' : results
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()