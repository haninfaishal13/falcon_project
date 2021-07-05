import falcon, psycopg2, base64, smtplib, email.message, hashlib


class database:
    host = "localhost"
    database = "postgres"
    user = "postgres"
    password = "postgres"
    port = "5432"

    def __init__(self):
        self.conn = psycopg2.connect(database=self.database,
                                     user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)
        self.curr = self.conn.cursor()

    def check(self, query):
        conn = self.conn
        curr = self.curr
        self.curr.execute(query)
        checking = bool(self.curr.rowcount)

        return checking

    def select(self, query):
        conn = self.conn
        curr = self.curr
        self.curr.execute(query)

        return curr.fetchall()

    def commit(self, query):
        self.curr.execute(query)
        self.conn.commit()

    def close(self):
        self.curr.close()
        self.conn.close()


class Authorize:
    def __init__(self):
        pass

    def process_request(self, req, resp):
        auth = req.get_header('Authorization')
        if auth is None:
            if(
                req.path == '/user/verification' 
                or req.path == '/user/login' 
                or req.path == '/user/signup'
                or req.path == '/user/forget-password'):
                return True
            if(req.method == 'OPTIONS'):
                return True
            raise falcon.HTTPUnauthorized('Authentication required', challenges=['Basic'])
        if not self._is_valid(auth):
            raise falcon.HTTPUnauthorized('Authentication invalid',  challenges=['Basic'])

    def _is_valid(self, auth):
        return True

    def auth_basic(self, username, password):
        db = database()
        checking = db.check("select * from user_person where username = '%s'" % username) #cek kesesuaian username
        if(checking):
            query = db.select("select username, password, status from user_person where username = '%s'" % username)
            uname = query[0][0]   #ambil kolom username
            passwd = query[0][1]  #ambil kolom password
            status = query[0][2]  #ambil kolom status
            passHash = hashlib.sha256(password.encode()).hexdigest()  #hash password dari auth
            if(not status):       #cek keaktifan user
                raise falcon.HTTPForbidden('Forbidden', 'Your account is inactive. Check your email for activation')
            if(passwd==passHash): #cek kesesuaian password
                print('you have loggedin, welcome ' + uname)
            else:
                raise falcon.HTTPUnauthorized('Unauthorized', 'password incorrect')
        else:
            raise falcon.HTTPUnauthorized('Unauthorized', 'username not found')
    
    def __call__(self, req, resp, resource, params):
        print("Before trigger - class Authorize")
        auth_exp = req.auth.split(' ') 

        if auth_exp[0] is not None and auth_exp[0].lower() == 'basic': 
            auth = base64.b64decode(auth_exp[1]).decode('utf-8').split(':')
            username = auth[0]
            password = auth[1]
            self.auth_basic(username, password)
        else:
            raise falcon.HTTPUnauthorized('Not Implemented', 'Your auth method is not right')

    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Access-Control-Allow-Origin', '*')

        if (req_succeeded
            and req.method == 'OPTIONS'
            and req.get_header('Access-Control-Request-Method')
        ):
            # NOTE: This is a CORS preflight request. Patch the
            #   response accordingly.

            allow = resp.get_header('Allow')
            resp.delete_header('Allow')

            allow_headers = req.get_header(
                'Access-Control-Request-Headers',
                default='*'
            )

            resp.set_headers((
                ('Access-Control-Allow-Methods', allow),
                ('Access-Control-Allow-Headers', allow_headers),
                ('Access-Control-Max-Age', '86400'),  # 24 hours
            ))
    
    def getAuthentication(self, authGet):
        db = database()
        authExp = authGet
        auth = base64.b64decode(authExp[1]).decode('utf-8').split(':')
        username = auth[0]

        checking = db.check("select * from user_person where username = '%s'" % username)
        if(checking):
            query = db.select("select id_user, username, password, isadmin from user_person where username = '%s'" % username)
            id_user = query[0][0]
            uname = query[0][1]
            passwd = query[0][2]
            isadmin = query[0][3]
            # decode_id = base64.b64decode(idu[0].encode('utf-8')).decode('utf-8')
        return id_user, username, passwd, isadmin

    def sendEmail(self, username, emailAddress, token):
      server = smtplib.SMTP('smtp.gmail.com:587')
      urlCode = "http://127.0.0.1:8000/user/verification?token="+token
      email_content = """ 
      <html>              
       
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Activation Message</title>
      </head>
      <body>
      <table width="100%" cellpadding="0" cellspacing="0" bgcolor="e4e4e4"><tr><td>
          <table id="top-message" cellpadding="20" cellspacing="0" width="600" align="center">
              <tr>
                <td align="center">
                  
                </td>
              </tr>
          </table>
           
          <table id="main" width="600" align="center" cellpadding="0" cellspacing="15" bgcolor="ffffff">
              <tr>
                <td>
                  <table id="header" cellpadding="10" cellspacing="0" align="center" bgcolor="8fb3e9">
                    <tr>
                      <td width="600" align="left"  bgcolor="#2BA6CB"><h1>Activation Message</h1></td>
                    </tr>
                    <tr>
                      <td width="600" align="left" bgcolor="#2BA6CB"><p>Administrator</p></td>
                    </tr>
                  </table>
                </td>
              </tr>   
              <tr>
                <td>
                  <table id="content-4" cellpadding="5" cellspacing="0" align="center">
                    <tr>
                      <td width="500" valign="top" >
                        <h5>Dear """+username+"""</h5>
                        <p>We have accepted your registration. Please click button below to activate your account.</p>
                      </td>
                    </tr>
                    <tr>
                      <td width="500" valign="top">
                        <p><a href="""+urlCode+"""><button type="button" class="btn btn-primary">Activate</button></a>
                      </td>
                    </tr>
                    <tr>
                      <td width = "500" valign="top">
                        <p><h5>Thank you</h5></p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
          </table>
      </td></tr>
      </table><!-- wrapper -->
       
      </body>
      </html> 
      """
       
      msg = email.message.Message()
      msg['Subject'] = 'Activation Message'
       
       
      msg['From'] = 'haninfaishal13@gmail.com'
      msg['To'] = emailAddress
      password = "hidupmulia45"
      msg.add_header('Content-Type', 'text/html') 
      msg.set_payload(email_content)
       
      s = smtplib.SMTP('smtp.gmail.com: 587')
      s.starttls()
       
      # Login Credentials for sending the mail
      s.login(msg['From'], password) #pastikan email udah dikonfigurasi keamanannya
       
      s.sendmail(msg['From'], [msg['To']], msg.as_string())

    def forgetPasswordMail(self, mail, username, password):
        server = smtplib.SMTP('smtp.gmail.com:587')
        # urlCode = "http://127.0.0.1:8000/login/forget"
        email_content = """
        <html>
          <head>
          </head>
          <body>
            <h3>Dear """+username+""". </h3>

            <p>We have accepted your forget password request. Use this password for log in.</p>

            <p><h4>"""+password+"""</h4></p>

            <p>Thank You</p>
          </body
        </html>
        """
         
        msg = email.message.Message()
        msg['Subject'] = 'New Password'
         
         
        msg['From'] = 'haninfaishal13@gmail.com'
        msg['To'] = mail
        password = "hidupmulia45"
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(email_content)
         
        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
         
        # Login Credentials for sending the mail
        s.login(msg['From'], password)
         
        s.sendmail(msg['From'], [msg['To']], msg.as_string())

class Function:
    def userItem(self, idu, item):
        db = database()
        result = []
        value = []
        column = (item,)
        query = db.select("select %s from user_person where id_user = '%s'" % (item, idu))
        for row in query:
            result.append(dict(zip(column, row)))
            value.append(member[0][item])
        return value[0]
    def nodeItem(self, idn, item):
        db = database()
        result = []
        value = []
        column = (item,)
        query = db.select("select %s from node where id_node = '%s'" % (item, idn))
        for row in query:
            result.append(dict(zip(column, row)))
            value.append(result[0][item])
        return value[0]
    def sensorItem(self, ids, item):
        db = database()
        result = []
        value = []
        column = (item,)
        query = db.select("select %s from node where id_sensor = '%s'" % (item, ids))
        for row in query:
            result.append(dict(zip(column, row)))
            value.append(result[0][item])
        return value[0]