import falcon, json, hashlib, string, random, re
from database import *

class User:
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
            column = ('username', 'password')
            query = db.select("select username, password from user_person where username = '%s'" % username)
            for row in query:
                result.append(dict(zip(column, row)))
            passwd = query[0][1]
            if(passwd == passHash):
                output = {
                    'title' : True,
                    'description' : 'Logged in, Welcome'
                }
                resp.body = json.dumps(output, indent = 2)
            else:
                raise falcon.HTTPBadRequest('Unauthorized','Username not found or password incorrect')
        else:
            raise falcon.HTTPBadRequest('Unauthorized','Username not found or password incorrect')
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
            raise falcon.HTTPBadRequest('Missing parameter','Parameter used is missing: {}'.format(missing))
        username = params['username']
        emailAddress = params['email']
        password = params['password']

        regex = r'[\w!#$%&\'*+-/=?^_`{|}~.]+@[\w\.-]+'
        if(re.search(regex, str(emailAddress))): #cek format email
            tokenOriginal = username + emailAddress + password
            passHash = hashlib.sha256(password.encode()).hexdigest()
            token = hashlib.sha256(tokenOriginal.encode()).hexdigest()
        else:
            raise falcon.HTTPBadRequest('Bad Request', 'email format is not correct') 

        emailChecking = db.check("select * from user_person where email = '%s'" % emailAddress)
        usernameChecking = db.select("select * from user_person where username = '%s'" % username)
        if emailChecking or usernameChecking:
            raise falcon.HTTPBadRequest('Bad_Request','Email or Username already used')
        else:
            auth.sendEmail(username, emailAddress, token)
            db.commit("insert into user_person (username, email, password, token) values ('%s','%s', '%s', '%s')" % (username, emailAddress, passHash, token))
            
        output = {
            'title' : "Sign up",
            'description' : 'Success sign up, check email for verification'
        }
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(output, indent = 2)
        db.close()

    def on_get_verification(self, req, resp):
        db = database()
        token = req.params['token']
        # Udah aktif
        # Sebelum aktif
        # token tdak ditemukan
        token_check = db.check("select token from user_person where token = '%s'" % token)
        if not token_check:
            raise falcon.HTTPNotFound()
        checking = db.check("select * from user_person where token = '%s' and status = '0'" % token)
        if checking:
            db.commit("update user_person set status = '1' where token = '%s'" % token) #Tambah ubah token jadi NULL
            output = {
                'title':'Activate account',
                'description': 'Account has been activated'
            }
        else:
            raise falcon.HTTPBadRequest('Bad Request','You Account has been activated')
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output, indent = 2)
        db.close()

    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        auth = Authorize()
        authData = auth.getAuthentication(req.auth.split(' '))
        idu = authData[0]
        isadmin = authData[3]
        results = []
        column = ('Id User', 'Name', 'Email')
        if(not isadmin):
            raise falcon.HTTPForbidden('Forbidden', 'You are not administrator')
        query = db.select("select id_user, username, email from user_person")
        for row in query:
            results.append(dict(zip(column, row)))
        output = {
            'title' : "get user data",
            'description' : results
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
        
        nresults = []
        sresults = []
        ncolumn = ('Id Node', 'Node Name', 'Location')
        scolumn = ('Id Sensor', 'Sensor Name', 'Sensor Unit')
        if(not isadmin):    
            if(idu != str(id_user)):
                raise falcon.HTTPForbidden('Forbidden','You are not an admin')
        try:
            usrcheck = db.check("select id_user, username from user_person where id_user = '%s'" % idu)     
        except:
            raise falcon.HTTPBadRequest('Bad Request', 'Parameter is invalid')
        if usrcheck: #checking id user exist or not
            uquery = db.select("select id_user, username, email from user_person where id_user = '%s'" % idu)
            nquery = db.select("select id_node, name, location from node where id_user = '%s'" % idu)
            squery = db.select("select sensor.id_sensor, sensor.name, sensor.unit from sensor left join node on sensor.id_node = node.id_node "
                               "where node.id_user = '%s'" % idu)
            for row in nquery:
                nresults.append(dict(zip(ncolumn, row)))
            for row in squery:
                sresults.append(dict(zip(scolumn, row)))
        else:
            raise falcon.HTTPNotFound()
        key = {
            'id_user'   : uquery[0][0],
            'username'  : uquery[0][1],
            'email'     : uquery[0][2],
            'node'      : nresults,
            'sensor'    : sresults
        }
        output = {
            'title' : 'get user specific data',
            'description' : key
        }
        resp.body = json.dumps(output, indent = 2)
        db.close()

    # def on_post_emailforget(self, req, resp):
    #     db = database()
    #     auth = Authorize()
    #     if req.content_type is None:
    #         raise falcon.HTTPBadRequest("Empty request body")
    #     elif 'form' in req.content_type:
    #         params = req.params
    #     elif 'json' in req.content_type:
    #         params = json.load(req.bounded_stream)
    #     else:
    #         raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
    #     required = {'email'}
    #     missing = required - set(params.keys())
    #     if missing:
    #         raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

    #     mail = params['email']
    #     token = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
    #     tokenHash = hashlib.sha256(token.encode()).hexdigest()
    #     checking = db.check("select email from user_person where email = '%s'" % mail)
    #     if not checking:
    #         raise falcon.HTTPBadRequest('Bad Request','Email not found')

    #     checkToken = db.check("select token from user_person where token = '%s'" % tokenHash)
    #     while checkToken:
    #         token = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
    #         tokenHash = hashlib.sha256(token.encode()).hexdigest()
    #         checkToken = db.check("select token from user_person where token = '%s'" % tokenHash)
    #     auth.forgetPasswordMail(mail, token)
    #     db.commit("update user_person set token = '%s' where email = '%s'" % (tokenHash, mail))

    #     output = {
    #         'success' : True,
    #         'message' : 'send email, check email for change forgotten password'
    #     }
    #     resp.body = json.dumps(output, indent = 2)
    #     db.close()

    # def on_put_passwordforget(self, req, resp):
    #     global results
    #     db = database()

    #     if req.content_type is None:
    #         raise falcon.HTTPBadRequest("Empty request body")
    #     elif 'form' in req.content_type:
    #         params = req.params
    #     elif 'json' in req.content_type:
    #         params = json.load(req.bounded_stream)
    #     else:
    #         raise falcon.HTTPUnsupportedMediaType("Supported format: JSON or form")
    #     required = {'token', 'password'}
    #     missing = required - set(params.keys())
    #     if missing:
    #         raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))

    #     token = params['token']
    #     password = params['password']
    #     tokenHash = hashlib.sha256(token.encode()).hexdigest()
    #     passHash = hashlib.sha256(password.encode()).hexdigest()
    #     checking = db.check("select token from user_person where token = '%s'" % tokenHash)
    #     if not checking:
    #         raise falcon.HTTPBadRequest('Bad Request', 'Token not correct')

    #     db.commit("update user_person set password = '%s' where token = '%s'" % (passHash, tokenHash))
    #     output = {
    #         'success' : True,
    #         'message' : 'password has been reset'
    #     }
    #     resp.body = json.dumps(output, indent = 2)
    #     db.close()
    def on_post_forgetPassword(self, req, resp):
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
        required = {'email', 'username'}
        missing = required - set(params.keys())
        if missing:
            raise falcon.HTTPBadRequest('Missing parameter','Parameter used is missing: {}'.format(missing))
        regex = r'[\w!#$%&\'*+-/=?^_`{|}~.]+@[\w\.-]+'
        if not re.search(regex, str(params['email'])):
            raise falcon.HTTPBadRequest('Bad Request', 'email format is not correct')
        checking = db.check("select email, username from user_person where email = '%s' and username = '%s'" % (params['email'], params['username']))
        if not checking:
            raise falcon.HTTPBadRequest('Bad Request', 'Username or Email not correct')
        query = db.select("select status from user_person where email = '%s'" % params['email'])
        if not query[0][0]:
           raise falcon.HTTPForbidden('Forbidden', 'Your account is inactive. Check your email for activation') 
        newPassword = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        
        passHash = hashlib.sha256(newPassword.encode()).hexdigest()
            
        auth.forgetPasswordMail(params['email'],params['username'], newPassword)
        db.commit("update user_person set password = '%s' where email = '%s'" % (passHash, params['email']))
        output = {
            'title':'forget password',
            'description':'Forget password request sent. Check email for new password'
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
        
        try: #antisipasi input id user tidak sesuai dengan tipe data pada database
            checking = db.check("select id_user from user_person where id_user = '%s'" % idu)
        except:
            raise falcon.HTTPBadRequest('Bad Request', 'Parameter is invalid')
        if not checking:
            raise falcon.HTTPNotFound()
        if(id_user != idu):
            raise falcon.HTTPForbidden('Forbidden', 'you cannot edit other users data')

        if missing:
            raise falcon.HTTPBadRequest('Missing parameter','Parameter used is missing: {}'.format(missing))

        oPasswd = params['old password']
        nPasswd = params['new password']

        passHash = hashlib.sha256(oPasswd.encode()).hexdigest()
        if(passHash != passwd):
            raise falcon.HTTPBadRequest('Bad Request', 'Old password is not correct')
        else:
            newPassHash = hashlib.sha256(nPasswd.encode()).hexdigest()
            db.commit("update user_person set password = '%s' where id_user = '%s'" % (newPassHash, idu))
            output = {
                'title':'Change Password',
                'description':'success change password',
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

        if(idu != id_user):
            if not isadmin:
                raise falcon.HTTPForbidden('Forbidden', 'You are not an admin')
        checking = db.check("select * from user_person where id_user = '%s'" % idu)
        if checking:
            try:
                db.commit("delete from user_person where id_user = '%d'" % int(idu))
                output = {
                    'title':'delete user',
                    'description': 'delete user, id: {}'.format(idu)
                }
                resp.body = json.dumps(output)
            except:
                raise falcon.HTTPBadRequest('Bad Request', 'cannot delete, you still using node')
        else:
            raise falcon.HTTPNotFound()
        db.close()

