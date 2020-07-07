import falcon

from database import *
from user import *
from hardware import *
from node import *
from sensor import *
from channel import *
# from waitress import serve

api = falcon.API(middleware=[Authorize()])
api.add_route('/user', User())
api.add_route('/hardware', Hardware())
api.add_route('/node', Node())
api.add_route('/sensor', Sensor())
api.add_route('/channel', Channel())

# serve(api, host="127.0.0.1", port=8001)
