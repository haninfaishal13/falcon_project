import falcon, json
from database import *

class User:
    def on_get_login(self, req, resp):
        db = database()
        output = {
            'Success' : True,
            'Message' : 'Login Page'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    def on_post_login(self, req, resp):
        db = database()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Unsupported Media", "Supported format: JSON or form")

        required = {'Username', 'Password'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Bad Request','Missing parameter: {}'.format(missing))
        username = params['Username']
        password = params['Password']
        encode = base64.b64encode(password.encode('utf-8')).decode('utf-8')

        checking = db.check("select * from user_person where username = '%s'" % username)
        if(checking):
            result = []
            value = []
            column = ('Username', 'Password')
            query = db.select("select username, password from user_person where username = '%s'" % username)
            for row in query:
                result.append(dict(zip(column, row)))
            for member in result:
                value.append(member['Password'])
            decode = base64.b64decode(value[0].encode('utf-8')).decode('utf-8')
            if(password == decode):
                output = {
                    'success' : True,
                    'message' : 'Logged In',
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                raise falcon.HTTPUnauthorized('Unauthorized','Username or password is not correct')
        else:
            raise falcon.HTTPUnauthorized('Unauthorized','Username or password is not correct')
        db.close()

    def on_get_signup(self, req, resp):
        db = database()
        output = {
            'Success' : True,
            'Message' : 'Signup Page'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()
        
    def on_post_signup(self, req, resp):
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
        encode = base64.b64encode(password.encode('utf-8')).decode('utf-8')

        checking = db.check("select * from user_person where username = '%s'" % username)
        if checking:
            raise falcon.HTTPBadRequest('User already exist: {}'.format(username))
        else:
            db.commit("insert into user_person (username, password) values ('%s', '%s')" % (username, encode))
            
        output = {
            'success' : True,
            'message' : 'add new user',
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        results = []
        column = ('Id User', 'Name')
        query = db.select("select id_user, username from user_person")
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
        nresults = []
        sresults = []
        cresults = []
        ucolumn = ('Id User','Name')
        ncolumn = ('Id Node', 'Node Name', 'Location')
        scolumn = ('Id Sensor', 'Sensor Name', 'Sensor Unit')
        ccolumn = ('Time', 'Value', 'Id Sensor', 'Sensor Name', 'Sensor Unit')
        usrcheck = db.check("select id_user, username from user_person where id_user = '%s'" % idu) 
        if usrcheck: #checking id user exist or not
            uquery = db.select("select * from user_person where id_user = '%s'" % idu)
            nquery = db.select("select id_node, name, location from node where id_user = '%s'" % idu)
            squery = db.select("select sensor.id_sensor, sensor.name, sensor.unit from sensor left join node on sensor.id_node = node.id_node "
                               "where node.id_user = '%s'" % idu)
            cquery = db.select("select channel.time, channel.value, sensor.id_sensor, sensor.name, sensor.unit, "
                               "node.id_node from channel "
                               "left join sensor on channel.id_sensor = sensor.id_sensor "
                               "left join node on sensor.id_node = node.id_node "
                               "left join user_person on node.id_user = user_person.id_user "
                               "where user_person.id_user = '%s'" % idu)
            for row in uquery:
                uresults.append(dict(zip(ucolumn, row)))
            for row in nquery:
                nresults.append(dict(zip(ncolumn, row)))
            for row in squery:
                sresults.append(dict(zip(scolumn, row)))
            for row in cquery:
                cresults.append(dict(zip(ccolumn, row)))
        else:
                raise falcon.HTTPBadRequest('Id User does not exist: {}'.format(idu))
        output = {
            'sucess' : True,
            'message' : 'get user data',
            'data' : uresults,
            'node' : nresults,
            'sensor': sresults,
            'channel' : cresults
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idu):
        global results
        auth = Authorize()
        db = database()

        authData = auth.getAuthentication(req.auth.split(' '))
        id_user = authData[0]
        idu = int(idu)
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
        required = {'Old Username', 'Old Password', 'New Username', 'New Password'}
        missing = required - set(params.keys())


        if(id_user != idu):
            raise falcon.HTTPBadRequest('Unauthorized', 'you cannot edit other users data')

        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        oUname = params['Old Username']
        oPasswd = params['Old Password']
        nUname = params['New Username']
        nPasswd = params['New Password']
        checking = db.check("select * from user_person where username = '%s'" % oUname)
        if(checking):
            result = []
            value = []
            column = ('Username', 'Password')
            query = db.select("select username, password from user_person where username = '%s'" % oUname)
            for row in query:
                result.append(dict(zip(column, row)))
            for member in result:
                value.append(member['Password'])
            passDecode = base64.b64decode(value[0].encode('utf-8')).decode('utf-8')
            if(oPasswd == passDecode):
                result = []
                column = ('Id User', 'Username')
                passEncode = base64.b64encode(nPasswd.encode('utf-8')).decode('utf-8')
                db.commit("update user_person set username = '%s', password = '%s' where id_user = '%s'" % 
                    (nUname, passEncode, idu))
                query = db.select("select id_user, username from user_person where id_user = '%s'" % idu)
                for row in query:
                    result.append(dict(zip(column, row)))

                output = {
                    'success': True,
                    'message': 'Update user data',
                    'data': result
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                output = {
                    'success': False,
                    'message': 'Old username or old password is not correct'
                }
                resp.body = json.dumps(output, indent = 2)
        else:
            output = {
                'success': False,
                'message': 'Old username or old password is not correct'
            }
            resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_delete(self, req, resp):
        auth = Authorize()
        db = database()

        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
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
        if(id_user != idu):
            raise falcon.HTTPBadRequest('Unauthorized', 'you cannot delete other users data')

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

        
    # @falcon.before(Authorize())
    # def on_post(self, req, resp):
    #     db = database()
    #     if req.content_type is None:
    #         raise falcon.HTTPBadRequest("Empty request body")
    #     elif 'form' in req.content_type:
    #         params = req.params
    #     elif 'json' in req.content_type:
    #         params = json.load(req.bounded_stream)
    #     else:
    #         raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

    #     required = {'Username', 'Password'}
    #     missing = required - set(params.keys())
    #     if missing:
    #         raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
    #     username = params['Username']
    #     password = params['Password']

    #     checking = db.check("select * from user_person where username = '%s'" % username)
    #     if checking:
    #         raise falcon.HTTPBadRequest('User already exist: {}'.format(username))
    #     else:
    #         db.commit("insert into user_person (username, password) values ('%s', '%s')" % (username, password))
            
    #     output = {
    #         'success' : True,
    #         'message' : 'add new user',
    #     }
    #     resp.body = json.dumps(output, indent = 2)
    #     db.close()

    


# class Index:
#     def on_get():
#         db = database()
#         auth = Authorize()
#         authData = auth.getAuthentication(req.auth.spli(' '))
#         idu = authData[0]

#         nNode = []
#         nrow = ('Id Node', 'Node Name', 'Node Location', 'Id Sensor')
#         nquery = db.select("select node.id_node, node.name, node.location, sensor.id_sensor, sensor.name, sensor.unit from node left join sensor on node.id_node = sensor.id_node where node.id_user = '%s'" % idu)
#         for row in nquery:
