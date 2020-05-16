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

    def __del__(self):
        self.curr.close()
        self.conn.close()

user_account = {
    'Username':'Password'
}
class Authorize:
    def __init__(self):
        pass

    def auth_basic(self, username, password):
        if username in user_account and user_account[username] == password:
            print('you have logged in')
        else:
            raise falcon.HTTPUnauthorized('Unauthorized', 'Your access is not allowed')

    def __call__(self, req, resp, resource, params):
        print('before trigger - class: Authorize')
        auth_exp = req.auth.split(' ') if req.auth is not None else (None, None, )

        if auth_exp[0] is not None and auth_exp[0].lower() == 'basic':
            auth = base64.b64decode(auth_exp[1]).decode('utf-8').split(':')
            username = auth[0]
            password = auth[1]
            self.auth_basic(username, password)
        else:
            raise falcon.HTTPUnauthorized('Not Implemented', 'Your auth method is not right')
