import falcon, json, datetime
from database import *

class Channel:

  @falcon.before(Authorize())
  def on_post(self, req, resp):
    db = database()
    auth = Authorize()
    authData = auth.getAuthentication(req.auth.split(' '))
    idu = authData[0]
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
      return

    required = {'value', 'id_sensor'}
    missing = required - set(params.keys())
    if missing:
      resp.status = falcon.HTTP_400
      resp.body = 'Missing parameter: {}'.format(missing)
      return

    ch_value = params['value']
    id_sensor = params['id_sensor']
    if ch_value == '' or id_sensor == '':
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter mustn\'t empty'
      db.close()
      return
    try:
      checking = db.check("select id_sensor from sensor where id_sensor = '%s'" % id_sensor)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      return
    if not checking:
      print(id_sensor)
      resp.status = falcon.HTTP_400
      resp.body = 'Id sensor not found'
      return
    try: #antisipasi data yang diinput tidak sesuai dengan tipe data pada database
      query = db.select("select node.id_user from node left join sensor on sensor.id_node = node.id_node where id_sensor = '%s'" % id_sensor)
    except:
      resp.status = falcon.HTTP_400
      resp.body = 'Parameter is invalid'
      return
    id_user = query[0][0]
    if(id_user != idu):
      resp.status = falcon.HTTP_400
      resp.body = 'Can\'t send channel to another user\'s sensor'
      return
    time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S %Z")
    db.commit("insert into channel (time, value, id_sensor) values ('%s',%s,%s)" % (str(time), ch_value, id_sensor))
    resp.status = falcon.HTTP_201
    resp.body = 'Success add channel'

