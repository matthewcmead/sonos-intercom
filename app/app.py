#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import abort
from flask import send_file
import uuid
from expiringdict import ExpiringDict
import soco
import io
import os
import subprocess
import pathlib



def get_or_def(thedict, key, default=None):
  if key in thedict.keys():
    return thedict[key]
  else:
    return default

host = get_or_def(os.environ, 'LISTEN_HOST', '0.0.0.0')
port = int(get_or_def(os.environ, 'LISTEN_PORT', '2020'))
tmp =  get_or_def(os.environ, 'TRANSCODE_DIR', '/dev/shm/sonos_intercomm')
deployed_host = get_or_def(os.environ, 'EXTERNAL_HOST', 'localhost')

app = Flask(__name__)

audio_cache = ExpiringDict(max_len=5, max_age_seconds=3600, items=None)

@app.route('/sonosplay', methods = ['POST'])
def sonosplay():
  global host, port, deployed_host, tmp

  content_type = request.headers['Content-Type']
  if content_type != 'audio/aiff':
    return abort(404, 'Please send aiff.')

  intercomm_data = request.stream.read()

  media_id = uuid.uuid4().hex

  if not os.path.isdir(tmp):
    pathlib.Path(tmp).mkdir(parents=True, exist_ok=True)

  aiff_filename = os.path.join(tmp, '{}.aiff'.format(media_id))
  with open(aiff_filename, 'wb') as outf:
    outf.write(intercomm_data)
  mp3_filename = os.path.join(tmp, '{}.mp3'.format(media_id))

  completion = subprocess.run(['ffmpeg', '-i', aiff_filename, mp3_filename], capture_output=False)
  if completion.returncode != 0:
    return abort(404, 'Failed to convert audio.')
  with open(mp3_filename, 'rb') as inf:
    intercomm_data = inf.read()

  os.remove(aiff_filename)
  os.remove(mp3_filename)
  

  audio_cache[media_id] = { 'content-type': 'audio/mp3', 'data': intercomm_data }

  for zone in soco.discover(timeout=.5):
    try:
      zone.play_uri('http://{}:{}/getintercom/{}.mp3'.format(deployed_host, port, media_id))
    except soco.exceptions.SoCoException:
      pass
    

  return 'file uploaded successfully as {}'.format(media_id)

@app.route('/getintercom/<media_id>.mp3')
def getintercom(media_id):
  global audio_cache
  if media_id in audio_cache.keys():
    intercomm_obj = audio_cache[media_id]
    return send_file(io.BytesIO(intercomm_obj['data']),
                     attachment_filename='{}.mp3'.format(media_id),
                     mimetype=intercomm_obj['content-type'])
  else:
    return abort(404, 'Invalid media_id.')

if __name__ == '__main__':
  app.run(host=host, port=port)
