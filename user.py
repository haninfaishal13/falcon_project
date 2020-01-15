import falcon, json
from database import database


class Add_user:
    def on_post(self, req, resp):
        db = database()
        results = []
        column = ('Id User', 'Name', 'Password')
        params = req.params  # ?
        verify_params = True

        if 'name' not in params:
            verify_params = False
        if 'password' not in params:
            verify_params = False

        if verify_params is True:
            check = db.check("select * from user_person where lower(username) = lower('%s') and password = '%s'" %
                             (params['name'], params['password']))
            if check is False:
                db.insert("insert into user_person (username, password) values ('%s', '%s')" %
                          (params['name'], params['password']))
                query = db.select("select * from user_person where lower(username) = lower('%s') and password = '%s'"
                                  % (params['name'], params['password']))
                for row in query:
                    results.append(dict(zip(column, row)))
            elif check is True:
                results = {
                    'message': 'Username is already exist'
                }
        elif verify_params is False:
            results = {
                'status': 'fail',
                'message': 'Need name and password parameter'
            }
        resp.body = json.dumps(results)


class View_user:
    def on_get(self, req, resp):
        db = database()
        column = ('Name', 'Password')
        results = []
        query = db.select("select username, password from user_person")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)


class Search_user:
    def on_get(self, req, resp, username):
        db = database()
        column = ('Name', 'Password')
        results = []
        check = db.check("select * from user_person where lower(username) = lower('%s')" % username)
        if check is True:
            query = db.select(
                "select username, password from user_person where lower(username) = lower('%s')" % username)
            for row in query:
                results.append(dict(zip(column, row)))
        elif check is False:
            results = {
                'No Content': 'There is no username %s' % username
            }
        resp.body = json.dumps(results, indent=2)
