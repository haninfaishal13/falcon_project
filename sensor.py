import falcon, json
from database import *

class Sensor:

  @falcon.before(Authorize())
  def on_get(self, req, resp):
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    idu = authData[0]
    isadmin = authData[3]

    results = []
    column = ('Id Sensor', 'Name', 'Unit', 'id hardware', 'id node')
    if isadmin:
      # jika pengguna adalah admin, maka pengguna dapat melihat semua sensor yang sudah diinput oleh pengguna lainnya
      results = db.adminGetSensor()
    else:
      # jika bukan admin, maka pengguna hanya dapat melihat sensor yang sudah diinput oleh dirinya sendiri
      results = db.userGetSensor(idu)
    resp.body = json.dumps(results, indent = 2)
    db.close()

  @falcon.before(Authorize())
  def on_get_id(self, req, resp, ids):
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    idu = authData[0]
    isAdmin = authData[3]
    try: 
      scheck = db.check('id_sensor', 'sensor', ids)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Id sensor is invalid'
      db.close()
      return
    if scheck:
      id_user = db.getSensorUserId(ids)
      if(id_user != idu):
        if not isAdmin:
          resp.status = falcon.HTTP_403
          resp.body = 'You can\'t see another user\'s sensor'
          db.close()
          return
      sensor = db.getSpecificSensor(ids)
      channel = db.getChannel('id_sensor', ids)
      key = {
        'id_sensor' : sensor[0]['Id Sensor'],
        'name'      : sensor[0]['Name'],
        'unit'      : sensor[0]['Unit'],
        'channel'   : channel
      }
      resp.body = json.dumps(key, indent = 2)
    else:
      resp.status = falcon.HTTP_404
      resp.body = 'Id sensor not found'
    db.close()

  @falcon.before(Authorize())
  def on_post(self, req, resp):
    db = database()
    function = Function()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    idu = authData[0]
    isadmin = authData[3]

    if req.content_type is None:
      resp.status = falcon.HTTP_400
      resp.body = 'Emtpy request body'
      db.close()
      return
    elif 'form' in req.content_type:
      params = req.params
    elif 'json' in req.content_type:
      params = json.load(req.bounded_stream)
    else:
      resp.status = falcon.HTTP_415
      resp.body = 'Supported format: JSON or form'
      db.close()
      return

    required = {'name', 'unit', 'id_node'}
    missing = required - set(params.keys())
    given = set(params.keys()) - required
    if missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
      db.close()
      return
    name = params['name']
    unit = params['unit']
    id_node = params['id_node']
    if(name =='' or unit == '' or id_node == ''):
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter mustn\'t empty'
      db.close()
      return
    try:
      checking = db.check('id_node', 'node', id_node)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Id node is invalid'
      db.close()
      return
    if checking:
      id_user = function.nodeItem(id_node, 'id_user') #cek id user pemilik node yang akan diedit
      if not isadmin:
        if id_user != idu:
          resp.status = falcon.HTTP_403
          resp.body = 'You can\'t use another user\'s node'
          db.close()
          return
      if 'id_hardware' in given:
        id_hardware = params['id_hardware']
        if id_hardware == '':
          db.addSensorNoHardware(name, unit, id_node)
          resp.status = falcon.HTTP_201
          resp.body = 'Success add new sensor'
          db.close()
          return
        try:
          idhcheck = db.check('id_hardware', 'hardware', id_hardware)
        except:
          resp.status = falcon.HTTP_400
          resp.body = 'Id hardware is invalid'
          db.close()
          return
        if idhcheck:
          typecheck = db.sensorHwTypeCheck(id_hardware)
          if typecheck:
            db.addSensor(name, unit, id_node, id_hardware)
            resp.status = falcon.HTTP_201
            resp.body = 'Success add new sensor'
          else:
            resp.status = falcon.HTTP_400
            resp.body = 'Hardware type not match, type should Sensor'
        else:
          resp.status = falcon.HTTP_400
          resp.body = 'Id hardware not exist'
      elif 'id_hardware' not in given:
        db.addSensorNoHardware(name, unit, id_node)
        resp.status = falcon.HTTP_201
        resp.body = 'Success add new sensor'
    else:
      resp.status = falcon.HTTP_400
      resp.body = 'Id node not exist'  
    db.close()

  @falcon.before(Authorize())
  def on_put_id(self, req, resp, ids):
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    idu = authData[0]
    isadmin = authData[3]
    if req.content_type is None:
      resp.status = falcon.HTTP_400
      resp.body = 'Emtpy request body'
      return
    elif 'form' in req.content_type:
      params = req.params
    elif 'json' in req.content_type:
      params = json.load(req.bounded_stream)
    else:
      resp.status = falcon.HTTP_415
      resp.body = 'Supported format: JSON or form'
      db.close()
      return
    try: #antisipasi jika ada masukan id tidak sesuai dengan tipe data pada database
      ids = int(ids)
      scheck = db.check('id_sensor', 'sensor', ids)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      db.close()
      return
    if not scheck:
      resp.status = falcon.HTTP_404
      resp.body = 'Id sensor not found'
      db.close()
      return
    id_user = db.getSensorUserId(ids)
    if not isadmin:
      if(id_user != idu):
        resp.status = falcon.HTTP_403
        resp.body = 'You can\'t edit another user\'s sensor'
        db.close()
        return
    required = {'name', 'unit'}
    missing = required - set(params.keys())
    try: #antisipasi data pada body tidak sesuai dengan tipe data pada database
      if 'name' in missing and 'unit' in missing:
        resp.status = falcon.HTTP_400
        resp.body = 'Missing parameter: {}'.format(missing)
        db.close()
        return
      if 'name' not in missing and 'unit' not in missing:
        db.commit("update sensor set name = '%s', unit = '%s' where id_sensor = '%s'"
                        % (params['name'], params['unit'], ids))
      elif 'name' not in missing:
        db.commit("update sensor set name = '%s' where id_sensor = '%s'" % (params['name'], ids))
      elif 'unit' not in missing:
        db.commit("update sensor set unit = '%s' where id_sensor = '%s'" % (params['unit'], ids))
      resp.body = 'Success edit sensor data'
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
    db.close()

  @falcon.before(Authorize())
  def on_delete_id(self, req, resp, ids):
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    idu = authData[0]
    isadmin = authData[3]
    try:
      scheck = db.check('id_sensor', 'sensor', ids)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      db.close()
      return
    if not scheck:
      resp.status = falcon.HTTP_404
      resp.body = 'Id sensor not found'
      db.close()
      return
    id_user = db.getSensorUserId(ids)
    if not isadmin:
      if(id_user != idu):
        resp.status = falcon.HTTP_403
        resp.body = 'You can\'t delete another user\'s sensor'
        db.close()
        return
    db.commit("delete from sensor where id_sensor = '%s'" % ids)
    resp.body = 'Succes delete sensor data, id: {}'.format(ids)
    db.close()

