import falcon

from database import *
from user import *
from hardware import *
from node import *
from sensor import *
from channel import *

# from test import *
# from waitress import serve

api = falcon.API(middleware=[Authorize()])
# User Route
api.add_route('/user/signup', User(), suffix='signup') #Signup
api.add_route('/user/login', User(), suffix='login') #Login
api.add_route('/user/activation', User(), suffix='activation') #Aktivasi akun
api.add_route('/user/forget-password', User(), suffix='forgetPassword') 
api.add_route('/user', User()) #
api.add_route('/user/{idu}', User(), suffix='id') 
# Hardware Route
api.add_route('/hardware', Hardware())
api.add_route('/hardware/{idh}', Hardware(), suffix='id')
# Node Route
api.add_route('/node', Node())
api.add_route('/node/{idn}', Node(), suffix='id')
# Sensor Route
api.add_route('/sensor', Sensor())
api.add_route('/sensor/{ids}', Sensor(), suffix = 'id')
#Channel Route
api.add_route('/channel', Channel())


# serve(api, host="127.0.0.1", port=8001)
