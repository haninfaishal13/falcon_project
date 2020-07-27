import falcon

from database import *
from user import *
from hardware import *
from node import *
from sensor import *
from channel import *

from test import *
# from waitress import serve

api = falcon.API(middleware=[Authorize()])
api.add_route('/user', User())
api.add_route('/user/{idu}', User(), suffix='id') 
api.add_route('/hardware', Hardware())
api.add_route('/hardware/{idh}', Hardware(), suffix='id')
api.add_route('/node', Node())
api.add_route('/node/{idn}', Node(), suffix='id')
api.add_route('/sensor', Sensor())
api.add_route('/sensor/{ids}', Sensor(), suffix = 'id')
api.add_route('/channel', Channel())
api.add_route('/channel/{ids}', Channel(), suffix = 'id')


# serve(api, host="127.0.0.1", port=8001)
