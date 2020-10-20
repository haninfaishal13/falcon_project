import falcon, psycopg2, base64


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

user_account = {
    'hanin':'hanin123'
}




class Authorize:
    def __init__(self):
        pass

    def process_request(self, req, resp):
        auth = req.get_header('Authorization')
        if auth is None:
            if(req.path == '/home' or req.path == '/login' or req.path == '/signup'):
                return True
            raise falcon.HTTPUnauthorized('Authentication required', challenges=['Basic'])
        if not self._is_valid(auth):
            raise falcon.HTTPUnauthorized('Authentication invalid',  challenges=['Basic'])

    def _is_valid(self, auth):
        return True

    def auth_basic(self, username, password):
        db = database()
        checking = db.check("select * from user_person where username = '%s'" % username)
        if(checking):
            result = []
            passwd = []
            column = ('Username', 'Password')
            query = db.select("select username, password from user_person where username = '%s'" % username)
            for row in query:
                result.append(dict(zip(column, row)))
            for value in result:
                passwd.append(value['Password'])
            decode = base64.b64decode(passwd[0].encode('utf-8')).decode('utf-8')
            if(password == decode):
                print('You have logged in')

                return username
            else:
                falcon.HTTPUnauthorized('Unauthorized', 'Your access is not allowed')
        else:
            raise falcon.HTTPUnauthorized('Unauthorized', 'Your access is not allowed')
    
    def __call__(self, req, resp, resource, params):
        print("Before trigger - class Authorize")
        auth_exp = req.auth.split(' ') 
        print(auth_exp)

        if auth_exp[0] is not None and auth_exp[0].lower() == 'basic': 
            auth = base64.b64decode(auth_exp[1]).decode('utf-8').split(':')
            username = auth[0]
            password = auth[1]
            self.auth_basic(username, password)
        else:
            raise falcon.HTTPUnauthorized('Not Implemented', 'Your auth method is not right')
    
    def getAuthentication(self, authGet):
        db = database()
        authExp = authGet
        auth = base64.b64decode(authExp[1]).decode('utf-8').split(':')
        username = auth[0]

        checking = db.check("select * from user_person where username = '%s'" % username)
        if(checking):
            result = []
            idu = []
            column = ('Id User', 'Username', 'Password')
            query = db.select("select * from user_person where username = '%s'" % username)
            for row in query:
                result.append(dict(zip(column, row)))
            for value in result:
                idu.append(value['Password'])
            decode_id = base64.b64decode(idu[0].encode('utf-8')).decode('utf-8')

        return decode_id, username
