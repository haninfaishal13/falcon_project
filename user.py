import falcon, json, hashlib, string, random
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

        required = {'username','password'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Bad Request','Missing parameter: {}'.format(missing))
        username = params['username']
        password = params['password']
        passHash = hashlib.sha256(password.encode()).hexdigest()

        checking = db.check("select * from user_person where username = '%s'" % username)
        if(checking):
            result = []
            value = []
            column = ('username', 'password')
            query = db.select("select username, password from user_person where username = '%s'" % username)
            for row in query:
                result.append(dict(zip(column, row)))
            for member in result:
                value.append(member['password'])
            if(value[0] == passHash):
                output = {
                    'success' : True,
                    'message' : 'Logged In, Welcome'
                }
                resp.status = falcon.HTTP_202
                resp.body = json.dumps(output, indent = 2)
            else:
                raise falcon.HTTPUnauthorized('Unauthorized','password not correct')
        else:
            raise falcon.HTTPUnauthorized('Unauthorized','Username not found')
        db.close()

    def on_get_signup(self, req, resp):
        db = database()
        results = []
        column = ('name', 'type', 'description')
        query = db.select("select name, type, description from hardware")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)
        db.close()

    def on_get_verification(self, req, resp):
        db = database()
        token = req.params['token']

        checking = db.check("select * from user_person where token = '%s' and status = '0'" % token)
        if checking:
            db.commit("update user_person set status = '1' where token = '%s'" % token)
            output = {
                'message': 'account has been activated successfully'
            }
        else:
            output = {
                'message': 'your account has active'
            }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        if(not isadmin):
            raise falcon.HTTPForbidden('Forbidden','You are not an admin')
        results = []
        column = ('Id User', 'Name', 'Email')
        query = db.select("select id_user, username, email from user_person")
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'success' : True,
            'message' : 'get user data',
            'user' : results
        }
        resp.body = json.dumps(output, indent=2)
        db.close()

    @falcon.before(Authorize())
    def on_get_id(self, req, resp, idu):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        id_user = authData[0]
        isadmin = authData[3]
        if(int(idu) != id_user):
            if(not isadmin):
                raise falcon.HTTPForbidden('Forbidden','You are not an admin')
        uresults = []
        nresults = []
        sresults = []
        cresults = []
        ucolumn = ('Id User','Name','Email')
        ncolumn = ('Id Node', 'Node Name', 'Location')
        scolumn = ('Id Sensor', 'Sensor Name', 'Sensor Unit')
        ccolumn = ('Time', 'Value', 'Id Sensor', 'Sensor Name', 'Sensor Unit')
        usrcheck = db.check("select id_user, username from user_person where id_user = '%s'" % idu) 
        if usrcheck: #checking id user exist or not
            uquery = db.select("select id_user, username, email from user_person where id_user = '%s'" % idu)
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
            'user' : uresults,
            'node' : nresults,
            'sensor': sresults,
            'channel' : cresults
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()
        
    def on_post_signup(self, req, resp):
        db = database()
        auth = Authorize()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        required = {'username', 'email', 'password'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        username = params['username']
        emailAddress = params['email']
        password = params['password']

        tokenOriginal = username + ' ' + emailAddress + ' ' + password
        passHash = hashlib.sha256(password.encode()).hexdigest()
        token = hashlib.sha256(tokenOriginal.encode()).hexdigest()

        emailChecking = db.check("select * from user_person where email = '%s'" % emailAddress)
        usernameChecking = db.select("select * from user_person where username = '%s'" % username)
        if emailChecking or usernameChecking:
            raise falcon.HTTPBadRequest('Bad_Request','Email or Username already used')
        else:
            db.commit("insert into user_person (username, email, password, token) values ('%s','%s', '%s', '%s')" % (username, emailAddress, passHash, token))
            auth.sendEmail(emailAddress, token)
            
        output = {
            'success' : True,
            'message' : 'add new user, check email for verification',
        }
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(output, indent = 2)
        db.close()

    def on_post_emailforget(self, req, resp):
        db = database()
        auth = Authorize()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
        required = {'email'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        mail = params['email']
        token = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
        tokenHash = hashlib.sha256(token.encode()).hexdigest()
        checking = db.check("select email from user_person where email = '%s'" % mail)
        if not checking:
            raise falcon.HTTPBadRequest('Bad Request','Email not found')

        checkToken = db.check("select token from user_person where token = '%s'" % tokenHash)
        while checkToken:
            token = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
            tokenHash = hashlib.sha256(token.encode()).hexdigest()
            checkToken = db.check("select token from user_person where token = '%s'" % tokenHash)
        auth.forgetPasswordMail(mail, token)
        db.commit("update user_person set token = '%s' where email = '%s'" % (tokenHash, mail))

        output = {
            'success' : True,
            'message' : 'send email, check email for change forgotten password'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    def on_post_tokenforget(self, req, resp):
        db = database()
        # auth = Authorize()
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
        required = {'token'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        token = params['token']
        tokenHash = hashlib.sha256(token.encode()).hexdigest()

        checking = db.check("select token from user_person where token = '%s'" % tokenHash)
        if checking:
            output = {
                'success':True,
                'message':'find token forget password'
            }
        else:
            output = {
                'success':False,
                'message':'token not correct'
            }
        resp.body = json.dumps(output, indent = 2)
        db.close()


    def on_put_passwordforget(self, req, resp):
        global results
        db = database()

        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
        required = {'token', 'password'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        token = params['token']
        password = params['password']
        tokenHash = hashlib.sha256(token.encode()).hexdigest()
        passHash = hashlib.sha256(password.encode()).hexdigest()
        checking = db.check("select token from user_person where token = '%s'" % tokenHash)
        if not checking:
            raise falcon.HTTPBadRequest('Bad Request', 'Token not correct')

        db.commit("update user_person set password = '%s' where token = '%s'" % (passHash, tokenHash))
        output = {
            'success' : True,
            'message' : 'password has been reset'
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_put_id(self, req, resp, idu):
        global results
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        id_user = authData[0]
        passwd = authData[2] #yang didapetin password hash
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
        required = {'old password', 'new password'}
        missing = required - set(params.keys())

        checking = db.check("select id_user from user_person where id_user = '%s'" % idu)

        if(id_user != idu):
            raise falcon.HTTPForbidden('Forbidden', 'you cannot edit other users data')

        if missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

        oPasswd = params['old password']
        nPasswd = params['new password']

        passHash = hashlib.sha256(oPasswd.encode()).hexdigest()
        if(passHash != passwd):
            output = {
                'success':False,
                'message': 'old password is not correct'
            }
            resp.body = json.dumps(output)
        else:
            result = []
            value = []
            newPassHash = hashlib.sha256(nPasswd.encode()).hexdigest()
            db.commit("update user_person set password = '%s' where id_user = '%s'" % (newPassHash, idu))
            output = {
                'success':True,
                'message':'change password',
            }
            resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_delete_id(self, req, resp, idu):
        auth = Authorize()
        db = database()
        authData = auth.getAuthentication(req.auth.split(' '))
        id_user = authData[0]
        isadmin = authData[3]
        if req.content_type is None:
            raise falcon.HTTPBadRequest("Empty request body")
        elif 'form' in req.content_type:
            params = req.params
        elif 'json' in req.content_type:
            params = json.load(req.bounded_stream)
        else:
            raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")

        # if(id_user != idu):
        #     raise falcon.HTTPBadRequest('Unauthorized', 'you cannot delete other users data')
        if(int(idu) != id_user):
            if not isadmin:
                raise falcon.HTTPForbidden('Forbidden', 'You are not an admin')
        checking = db.check("select * from user_person where id_user = '%s'" % idu)
        if checking:
            try:
                db.commit("delete from user_person where id_user = '%d'" % int(idu))
                output = {
                    'success' : True,
                    'message' : 'delete user',
                    'id' : '{}'.format(idu)
                }
                
            except:
                output = {
                    'success': False,
                    'message': 'cannot delete, you still using node'
                }
            resp.body = json.dumps(output)
        else:
            raise falcon.HTTPBadRequest('User Id is not exist: {}'.format(id_user))
        db.close()

