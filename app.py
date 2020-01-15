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

api.add_route('/hardware', View_hardware())
api.add_route('/hardware/add', Add_hardware())
api.add_route('/hardware/search/{hwname}', Search_hardware())
# api.add_route('/view_related_hardware/{hardware}', View_related_hardware())

api.add_route('/node', View_node())
api.add_route('/node/add', Add_node())
api.add_route('/node/search/{loc_node}', Search_node())
# api.add_route('/view_related_node/{node}', View_related_node())

api.add_route('/sensor', View_sensor())
api.add_route('/sensor/add', Add_sensor())
api.add_route('/sensor/search/{sensor}', Search_sensor())
# api.add_route('/view_sensor_channel/{sensor}', View_sensor_channel())

# api.add_route('/add_channel', Add_channel())

serve(api, host="127.0.0.1", port=8001)
