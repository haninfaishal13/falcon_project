import falcon, json
from database import *

class Test:
    def on_get(self, req, resp):
        db = database()
        column = ('Id User','Name', 'Password')
        results = []
        query = db.select("select * from user_test")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)
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

        checking = db.check("select * from user_test where username = '%s'" % username)
        if checking:
            raise falcon.HTTPBadRequest('User already exist: {}'.format(username))
        else:
            db.commit("insert into user_test (username, password) values ('%s', '%s')" % (username, password))
            results = {
                'Message': 'Success'
            }
            resp.body = json.dumps(results)
        db.close()


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
        checking = db.check("select * from user_test where id_user = '%s'" % id_user)
        if checking:
            db.commit("delete from user_test where id_user = '%d'" % id_user)
            results = {
                'Message': 'Delete process Success'
            }
            resp.body = json.dumps(results)
        else:
            raise falcon.HTTPBadRequest('User Id is not exist: {}'.format(id_user))
        db.close()


    def on_put(self, req, resp, id_user):
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
        required = {'Username', 'Password'}
        missing = required - set(params.keys())

        if 'Username' in missing and 'Password' in missing:
            raise falcon.HTTPBadRequest('Missing parameter: {}'.format(missing))
        elif 'Username' not in missing and 'Password' not in missing:
            db.commit("update user_test set username = '%s', password = '%s' where id_user = '%s'" %
                      (params['Username'], params['Password'], id_user))
            results = {
                'Update {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
        elif 'Password' not in missing:
            db.commit("update user_test set password = '%s' where id_user = '%s'" % (params['Password'], id_user))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.value()))
            }
        elif 'Username' not in missing:
            db.commit("update user_test set username = '%s' where id_user = '%s'" % (params['Username'], id_user))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.value()))
            }
        resp.body = json.dumps(results)
        db.close()