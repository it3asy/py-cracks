# encoding: utf-8
# rdp login function
# author: 

def _login(_url, _user='', _pass=''):
  import ctypes,urlparse,os,inspect
  SELF_DIR=os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
  hydra = ctypes.cdll.LoadLibrary(SELF_DIR + "/../libs/hydra-rdp.so")   
  _up = urlparse.urlparse(_url)
  _netlocs = _up.netloc.split(':')
  _host = _netlocs[0]
  _port = int(_netlocs[1])
  _path = _up.path
  r = hydra.service_rdp(_host, _port, _path, _user, _pass)
  if r == 1:
    return (200, '')
  elif r == 0:
    return (404, '')
  else:
    return (400, '')
