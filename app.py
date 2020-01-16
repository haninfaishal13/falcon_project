import falcon
from user import *
from hardware import *
from node import *
from sensor import *
from waitress import serve

api = falcon.API()

api.add_route('/user', View_user())
api.add_route('/user/add', Add_user())
api.add_route('/user/search/{username}', Search_user())
api.add_route('/user/delete', Delete_user())
# api.add_route('/user/edit/{username}', Edit_user())

api.add_route('/hardware', View_hardware())
api.add_route('/hardware/add', Add_hardware())
api.add_route('/hardware/search/{hw_id}', Search_hardware())
api.add_route('/hardware/edit/{hw_id}', Edit_hardware())
api.add_route('/hardware/delete', Delete_hardware())

api.add_route('/node', View_node())
api.add_route('/node/add', Add_node())
api.add_route('/node/search/{node}', Search_node())
api.add_route('/node/delete', Delete_node())
# api.add_route('/node/edit/{node}', Edit_node())

api.add_route('/sensor', View_sensor())
api.add_route('/sensor/add', Add_sensor())
api.add_route('/sensor/search/{sensor}', Search_sensor())
api.add_route('/sensor/delete', Delete_sensor())
# api.add_route('/sensor/edit/{sensor}', Edit_sensor())

# api.add_route('/add_channel', Add_channel())

serve(api, host="127.0.0.1", port=8001)
