import json
from database import database

class Add_channel:
    def on_post(self, req, resp):
        db = database()
        params = req.params
        verify_params = True

        if 'value' not in params:
            verify_params = False
        if 'id_sensor' not in params:
            verify_params = False

        if verify_params is True:
            db.insert("insert into channel (value, id_sensor) values ('%s', '%s')" %
                      (params['value'], params['id_sensor']))
        