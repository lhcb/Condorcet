#!/afs/cern.ch/user/g/gdujany/www/Condorcet/venv/bin/python
import sys, os
base = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
sys.path.insert(0,base+'/flup-1.0.2-py2.6.egg')
sys.path.insert(0,base)
sys.path.insert(0,base+'/Condorcet')

from flup.server.fcgi import WSGIServer
from Condorcet import app

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'].replace('cgi-bin/condorcet.fcgi','')
       return self.app(environ, start_response)

app = ScriptNameStripper(app)

if __name__ == '__main__':
    WSGIServer(app).run()
