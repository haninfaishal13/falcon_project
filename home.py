import falcon, json, base64
from database import *

class Home:
    def on_get(self, req, resp):
        db = database()
        output = {
            'Success' : True,
            'Message' : 'Homepage'
        }
        resp.body = json.dumps(output, indent=2)
        db.close()

class Login:
    def on_get(self, req, resp):
        db = database()
        output = {
            'Success' : True,
            'Message' : 'Login Page'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()
    def on_post(self, req, resp):
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

class Signup:
    def on_get(self, req, resp):
        db = database()
        output = {
            'Success' : True,
            'Message' : 'Signup Page'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()
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

