import falcon, json
from database import *

class Hardware:
  @falcon.before(Authorize())
  def on_get(self, req, resp):
    db = database()
    column = ('id_hardware','name', 'type', 'description')
    node_result = db.getNodeHardware()
    sensor_result = db.getSensorHardware()
    
    output = {
        'node' : node_result,
        'sensor' : sensor_result
    }
    resp.body = json.dumps(output, indent=2)  
    db.close()
      
  @falcon.before(Authorize())
  def on_get_id(self, req, resp, idh):
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    id_user = authData[0]
    isadmin = authData[3]

    results = []
    try:
        idhcheck = db.check('id_hardware', 'hardware', idh)
    except:
        resp.status = falcon.HTTP_400
        resp.body = 'Parameter is invalid'
        return
    if idhcheck:
      hquery = db.getSpecificHardware(idh)
      nodecheck = db.nodeHwTypeCheck(idh)
      sensorcheck = db.sensorHwTypeCheck(idh)
      if nodecheck:
        node = db.getNodeFromHardware(idh)
        key = {
            "id_hardware"   : hquery[0]['id_hardware'],
            "name"          : hquery[0]['name'],
            "type"          : hquery[0]['type'],
            "description"   : hquery[0]['description'],
            "node"          : node
        }
      elif sensorcheck:
        sensor = db.getSensorFromHardware(idh)
        key = {
            "id_hardware"   : hquery[0]['id_hardware'],
            "name"          : hquery[0]['name'],
            "type"          : hquery[0]['type'],
            "description"   : hquery[0]['description'],
            "sensor"        : sensor
        }
      resp.body = json.dumps(key, indent = 2)
    else:
      resp.status = falcon.Http_404
      resp.body = 'Id hardware not found'
    db.close()
  @falcon.before(Authorize())
  def on_post(self, req, resp):
    db = database()
    key = []
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

    required = {'name', 'type', 'description'}
    missing = required - set(params.keys())
    if missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
      db.close()
      return
    hwname = params['name']
    tipe = params['type']
    desc = params['description']
    if(hwname == '' or tipe == '' or desc == ''):
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter mustn\'t empty'
    else:
      key.append(dict(zip(params.keys(), params.values())))
      if 'single-board computer' in tipe.lower() or 'microcontroller unit' in tipe.lower() or 'sensor' in tipe.lower():
        db.addHardware(hwname, tipe, desc)
        resp.body = 'Success add new hardware'
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Type must Single-Board Computer, Microcontroller Unit, or Sensor'
    db.close()

  @falcon.before(Authorize())
  def on_put_id(self, req, resp, idh):
    global results
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    id_user = authData[0]
    isadmin = authData[3]
    try:
      hwcheck = db.check('id_hardware', 'hardware', idh)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      db.close()
      return
    if not hwcheck:
      resp.status = falcon.Http_404
      resp.body = 'Id hardware not found'
      db.close()
      return
    results = []
    column = ('id_hardware', 'name', 'type', 'description')
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
    required = {'name', 'type', 'description'}
    missing = required - set(params.keys())
    if 'name' in missing and 'type' in missing and 'description' in missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
      db.close()
      return
    elif 'name' not in missing and 'type' not in missing and 'description' not in missing:
      if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
        db.commit("update hardware set name = '%s', type = '%s', description = '%s' where id_hardware = '%s'"
                  % (params['name'], params['type'], params['description'], idh))
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Type must Single-Board Computer, Microcontroller Unit, or Sensor'
        db.close()
        return
    #Stop kalau mau mensetting update data harus memasukkan semua required
    elif 'name' in missing and 'type' in missing: 
      db.commit("update hardware set description = '%s' where id_hardware = '%s'" % (params['description'], idh))
    elif 'name' in missing and 'description' in missing:
      if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
        db.commit("update hardware set type = '%s' where id_user = '%s'" % (params['type'], idh))
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Type must Single-Board Computer, Microcontroller Unit, or Sensor'
        return
    elif 'type' in missing and 'description' in missing:
      db.commit("update hardware set name = '%s' where id_hardware = '%s'" % (params['name'], idh))
    elif 'type' in missing:
      db.commit("update hardware set name = '%s', description = '%s' where id_hardware = '%s'"
                  % (params['name'], params['description'], idh))
    elif 'name' in missing:
      if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
        db.commit("update hardware set type = '%s', description = '%s' where id_hardware = '%s'"
                    % (params['type'], params['description'], idh))
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Type must Single-Board Computer, Microcontroller Unit, or Sensor'
        db.close()
        return
    elif 'description' in missing:
      if 'single-board computer' in params['type'].lower() or 'microcontroller unit' in params['type'].lower() or 'sensor' in params['type'].lower():
        db.commit("update hardware set name = '%s', type = '%s' where id_hardware = '%s'"
                    % (params['name'], params['type'], idh))
      else:
        resp.status = falcon.HTTP_400
        resp.body = 'Type must Single-Board Computer, Microcontroller Unit, or Sensor'
        db.close()
        return
    resp.body = 'success edit hardware'
    db.close()

  @falcon.before(Authorize())
  def on_delete_id(self, req, resp, idh):
    db = database()
    try:
      checking = db.check('id_hardware', 'hardware', idh)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      db.close()
      return
    if checking:
      try:
        db.commit("delete from hardware where id_hardware = '%s'" % idh)
        output = {
            'title' : 'Delete hardware, id: {}'.format(idh)
        }
        resp.body = 'Delete hardware, id: {}'.format(idh)
      except:
        resp.status = falcon.HTTP_400
        resp.body = 'Can\'t delete, hardware is still used'
        db.close()
        return
    else:
      resp.status = falcon.Http_404
      resp.body = 'Id hardware not found'
    db.close()

