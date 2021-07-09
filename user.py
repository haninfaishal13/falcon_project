import falcon, json, hashlib, string, random, re
from database import *

class User:
  def on_post_login(self, req, resp):
    db = database()
    if req.content_type is None:
      resp.status = falcon.HTTP_400
      resp.body = 'Emtpy request body'
      db.close()
      return
    elif 'form' in req.content_type:
      params = req.params
    elif 'json' in req.content_type:
      params = json.load(req.bounded_stream)
    else:
      resp.status = falcon.HTTP_415
      resp.body = 'Supported format: JSON or form'
      db.close()
      return

    required = {'username','password'}
    missing = required - set(params.keys())
    if missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
      db.close()
      return
    
    username = params['username']
    password = params['password']
    passHash = hashlib.sha256(password.encode()).hexdigest()

    ucheck = db.check("select * from user_person where username = '%s'" % username)
    if(ucheck):
      result = []
      column = ('username', 'password')
      query = db.select("select username, password from user_person where username = '%s'" % username)
      for row in query:
        result.append(dict(zip(column, row)))
      passwd = query[0][1]
      if(passwd == passHash):
        resp.body = 'Logged in'
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Username not found or password incorrect'
    else:
      resp.status = falcon.HTTP_400
      resp.body = 'Username not found or password incorrect'
    db.close()

  def on_post_signup(self, req, resp):
    db = database()
    auth = Authorize()
    if req.content_type is None:
      resp.status = falcon.HTTP_400
      resp.body = 'Emtpy request body'
      db.close()
      return
    elif 'form' in req.content_type:
      params = req.params
    elif 'json' in req.content_type:
      params = json.load(req.bounded_stream)
    else:
      resp.status = falcon.HTTP_415
      resp.body = 'Supported format: JSON or form'
      db.close()
      return

    required = {'username', 'email', 'password'}
    missing = required - set(params.keys())
    if missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
      db.close()
      return
    username = params['username']
    emailAddress = params['email']
    password = params['password']

    if(username == '' or emailAddress == '' or password == ''):
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter mustn\'t empty'
    else:
      regex = r'[\w!#$%&\'*+-/=?^_`{|}~.]+@[\w\.-]+'
      if(re.search(regex, str(emailAddress))): #cek format email
        tokenOriginal = username + emailAddress + password
        passHash = hashlib.sha256(password.encode()).hexdigest()
        token = hashlib.sha256(tokenOriginal.encode()).hexdigest()
        emailChecking = db.check("select email from user_person where email = '%s'" % emailAddress)
        usernameChecking = db.check("select username from user_person where username = '%s'" % username)
        if not emailChecking and not usernameChecking:
          db.commit("insert into user_person (username, email, password, token) values ('%s','%s', '%s', '%s')" % (username, emailAddress, passHash, token))
          query = db.select("select id_user, username from user_person where username = '%s'" % username)
          auth.sendEmail(str(query[0][0]), username, emailAddress, token)
          resp.status = falcon.HTTP_201
          resp.body = 'Success sign up, check email for verification'
        else:
          resp.status = falcon.HTTP_400
          resp.body = 'Email or Username already used'
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Email format is incorrect'
        db.close()
        return
    db.close()

  def on_get_activation(self, req, resp):
    db = database()
    token = req.params['token']
    # Udah aktif
    # Sebelum aktif
    # token tdak ditemukan
    token_check = db.check("select token from user_person where token = '%s'" % token)
    if token_check:
      stat_check = db.check("select * from user_person where token = '%s' and status = '0'" % token)
      if stat_check:
        db.commit("update user_person set status = '1' where token = '%s'" % token) #Tambah ubah token jadi NULL
        resp.status = falcon.HTTP_200
        resp.body = 'Your account has been activated'
      else: #respon error kalau token sudah diaktifkan
        resp.status = falcon.HTTP_400
        resp.body = 'Your account has already activated'
    else: #respon error kalau token tidak ditemukan
      resp.status = falcon.HTTP_404
      resp.body =  'Token not found'
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
    if isadmin:
      query = db.select("select id_user, username, email from user_person")
      for row in query:
        results.append(dict(zip(column, row)))
      resp.body = json.dumps(results, indent=2)
    else:
      resp.status = falcon.HTTP_403
      resp.body = 'You are not administrator'
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
    try:
      usrcheck = db.check("select id_user, username from user_person where id_user = '%s'" % idu)     
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      db.close()
      return
    if(not isadmin):    
      
      if usrcheck: #checking id user exist or not
        uquery = db.select("select id_user, username, email from user_person where id_user = '%s'" % idu)
        nquery = db.select("select id_node, name, location from node where id_user = '%s'" % idu)
        squery = db.select("select sensor.id_sensor, sensor.name, sensor.unit from sensor left join node on sensor.id_node = node.id_node "
                           "where node.id_user = '%s'" % idu)
        for row in nquery:
          nresults.append(dict(zip(ncolumn, row)))
        for row in squery:
          sresults.append(dict(zip(scolumn, row)))
        key = {
          'id_user'   : uquery[0][0],
          'username'  : uquery[0][1],
          'email'     : uquery[0][2],
          'node'      : nresults,
          'sensor'    : sresults
        }
        resp.body = json.dumps(key, indent = 2)
      else:
        resp.status = falcon.HTTP_404
        resp.body = 'Id User not found'
    else:
      resp.status = falcon.HTTP_403
      resp.body = 'You are not administrator'
    db.close()

  def on_post_forgetPassword(self, req, resp):
    db = database()
    auth = Authorize()
    if req.content_type is None:
      resp.status = falcon.HTTP_400
      resp.body = 'Emtpy request body'
      db.close()
      return
    elif 'form' in req.content_type:
      params = req.params
    elif 'json' in req.content_type:
      params = json.load(req.bounded_stream)
    else:
      resp.status = falcon.HTTP_415
      resp.body = 'Supported format: JSON or form'
      db.close()
      return
    required = {'email', 'username'}
    missing = required - set(params.keys())
    if not missing:
      if(params['email'] != '' or params['username'] != ''):
        regex = r'[\w!#$%&\'*+-/=?^_`{|}~.]+@[\w\.-]+'
        if re.search(regex, str(params['email'])):
          checking = db.check("select email, username from user_person where email = '%s' and username = '%s'" % (params['email'], params['username']))
          if checking:
            query = db.select("select status from user_person where email = '%s'" % params['email'])
            if query[0][0]:
              newPassword = ''.join(random.choice(string.ascii_lowercase) for i in range(10))        
              passHash = hashlib.sha256(newPassword.encode()).hexdigest()
              auth.forgetPasswordMail(params['email'],params['username'], newPassword)
              db.commit("update user_person set password = '%s' where email = '%s'" % (passHash, params['email']))
              resp.body = 'Forget password request sent. Check email for new password'

            else:
              resp.status = falcon.HTTP_403
              resp.body = 'Your account is inactive. Check your email for activation'
          else: 
            resp.status = falcon.HTTP_400
            resp.body = 'Username or email is incorrect'
        else:
          resp.status = falcon.HTTP_400
          resp.body = 'Email format is incorrect'
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Parameter mustn\'t empty'
    else:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
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
      resp.status = falcon.HTTP_400
      resp.body = 'Emtpy request body'
      db.close()
      return
    elif 'form' in req.content_type:
      params = req.params
    elif 'json' in req.content_type:
      params = json.load(req.bounded_stream)
    else:
      resp.status = falcon.HTTP_415
      resp.body = 'Supported format: JSON or form'
      db.close()
      return
    required = {'old password', 'new password'}
    missing = required - set(params.keys())
    if missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing Parameter: {}'.format(missing)
      db.close()
      return

    try: #antisipasi input id user tidak sesuai dengan tipe data pada database
      checking = db.check("select id_user from user_person where id_user = '%s'" % idu)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      db.close()
      return
    if checking:
      if(id_user == idu):
        if(params['old password'] != '' or params['new password'] != ''):
          oPasswd = params['old password']
          nPasswd = params['new password']
          passHash = hashlib.sha256(oPasswd.encode()).hexdigest()
          if(passHash == passwd):
            newPassHash = hashlib.sha256(nPasswd.encode()).hexdigest()
            db.commit("update user_person set password = '%s' where id_user = '%s'" % (newPassHash, idu))
            resp.body = 'Success change password'
          else:
            resp.status = falcon.HTTP_400
            resp.body = 'Old password is incorrect'
        else:
          resp.status = falcon.HTTP_400
          resp.body = 'Parameter mustn\'t empty'
      else:
        resp.status = falcon.HTTP_403
        resp.body = 'Can\'t edit another user\'s account'
    else:
      resp.status = falcon.HTTP_404
      resp.body = 'Id user not found'
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
        resp.status = falcon.HTTP_403
        resp.body = 'Can\'t delete another user\' account'
        db.close()
        return
    checking = db.check("select * from user_person where id_user = '%s'" % idu)
    if checking:
      try:
        db.commit("delete from user_person where id_user = '%d'" % int(idu))
        resp.body = 'delete user, id: {}'.format(idu)
      except:
        resp.status = falcon.HTTP_400
        resp.body = 'Can\'t delete, you still using node'
        db.close()
        return
    else:
      resp.status - falcon.HTTP_404
      resp.status = 'Id user not found'
    db.close()
