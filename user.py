import falcon, json
from database import *

class User:
    @falcon.before(Authorize())
    def on_get(self, req, resp):
        db = database()
        column = ('Id User','Name', 'Password')
        results = []
        query = db.select("select * from user_person")
        for row in query:
            results.append(dict(zip(column, row)))
        resp.body = json.dumps(results, indent=2)
        db.close()

    @falcon.before(Authorize())
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

        checking = db.check("select * from user_person where username = '%s'" % username)
        if checking:
            raise falcon.HTTPBadRequest('User already exist: {}'.format(username))
        else:
            db.commit("insert into user_person (username, password) values ('%s', '%s')" % (username, password))
            results = {
                'Message': 'Success'
            }
            resp.body = json.dumps(results)
        db.close()

    @falcon.before(Authorize())
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
        checking = db.check("select * from user_person where id_user = '%s'" % id_user)
        if checking:
            db.commit("delete from user_person where id_user = '%d'" % id_user)
            results = {
                'Message': 'Delete process Success'
            }
            resp.body = json.dumps(results)
        else:
            raise falcon.HTTPBadRequest('User Id is not exist: {}'.format(id_user))
        db.close()

    @falcon.before(Authorize())
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
            db.commit("update user_person set username = '%s', password = '%s' where id_user = '%s'" %
                      (params['Username'], params['Password'], id_user))
            results = {
                'Update {}'.format(set(params.keys())): '{}'.format(set(params.values()))
            }
        elif 'Password' not in missing:
            db.commit("update user_person set password = '%s' where id_user = '%s'" % (params['Password'], id_user))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.value()))
            }
        elif 'Username' not in missing:
            db.commit("update user_person set username = '%s' where id_user = '%s'" % (params['Username'], id_user))
            results = {
                'Updated {}'.format(set(params.keys())): '{}'.format(set(params.value()))
            }
        resp.body = json.dumps(results)
        db.close()
        
"""
class UserNode:
    def on_get(self, req, resp):
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
        checking = db.check("select * from user_person where id_user = '%s'" % id_user)
        if checking:
            query = db.select("select username.user_person from user_person where id_user = '%s'" % id_user)
"""
