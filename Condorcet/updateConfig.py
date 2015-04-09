#!/usr/bin/env python
"""
Put some Condorcet voting configuration in a database so that it is possible to modify them in real time.
"""

# Options parser
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Update Config database sincronizing it with config.py')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--update', help='update config database reading from the CONFIG_FILE',
                       action='store_true')
    group.add_argument('--reset', help='Remove and recreate config database',
                       action='store_true')
    parser.add_argument('--key', help='Key used to store new config, leave default "default"',
                       default='default')
    parser.add_argument('--config_file', help='Config file to use',default='config.py')
    parser.add_argument('-p', help='Print content of databases',
                        action='store_true')
    args = parser.parse_args()


import os
import sys
this_files_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_files_dir, '..'))

_fields = ['TITLE', 'OPTIONS', 'CONTACT', 'DATE_FORMAT', 'START_ELECTION', 'CLOSE_ELECTION', 'VIEW_RESULTS', 'AUTHORS_LIST']

# for field in _fields:
#     exec 'from config import {0}'.format(field)

#if args.config_file:


import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))
from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app
db = SQLAlchemy(app)

sys.path.append(os.path.dirname(args.config_file))
config_name = os.path.basename(os.path.splitext(args.config_file)[0])
for field in _fields:
    exec 'from {0} import {1}'.format(config_name, field)

_fields.insert(0,'KEY')
KEY = 'default'

class Config(db.Model):
    KEY = db.Column(db.String(20), unique=True, primary_key=True)
    TITLE = db.Column(db.String(100), unique=False)
    OPTIONS = db.Column(db.String(100), unique=False)
    CONTACT = db.Column(db.String(100), unique=False)
    DATE_FORMAT = db.Column(db.String(100), unique=False)
    START_ELECTION = db.Column(db.String(100), unique=False)
    CLOSE_ELECTION = db.Column(db.String(100), unique=False)
    VIEW_RESULTS = db.Column(db.String(100), unique=False)
    AUTHORS_LIST = db.Column(db.String(100), unique=False)
    

    def __init__(self, KEY, TITLE, OPTIONS, CONTACT, DATE_FORMAT, START_ELECTION, CLOSE_ELECTION, VIEW_RESULTS, AUTHORS_LIST):
        for field in _fields:
            exec 'self.{0} = {0}'.format(field)
        

    def __repr__(self):
        ret_str = '\n'
        for field in _fields:
            ret_str += '''{0} = {1}\n'''.format(field,getattr(self,field))
        return ret_str

def getConfig(field,KEY='default'):
    """
    Get configuration from database
    field: which configuration, eg. TITLE
    KEY: if I have multiple configurations may be useful
    """
    ret = getattr(Config.query.filter_by(KEY=KEY).first(),field)
    if field == 'OPTIONS':
        ret = ret.split('|')
    return ret

def setConfig(field,value,KEY='default'):
    """
    Modify configuration in the database but without changing the defaults values in config.py
    N.B. If I run uptdateConfig.py the defaults will be set back again
    """
    if field == 'OPTIONS':
        value = '|'.join(value)
    setattr(Config.query.filter_by(KEY=KEY).first(), field, value)
    db.session.commit()

def resetConfig(KEY='default'):
    """
    Create a new database for Config, removing the old and call updateConfig
    """
    config_db = os.path.join(app.config['DB_DIR'],
                                  app.config['CONFIG_DB'])
    if os.path.exists(config_db):
        os.remove(config_db)
    db.create_all(bind=None)
    os.chmod(os.path.join(database_folder, config_db), 0666)
    updateConfig(KEY)
    

def updateConfig(KEY='default'):
    '''
    Update the KEY config reading the values from config.py
    '''
    # Convert OPTIONS to a single string
    for field in _fields:
        locals()[field] = globals()[field]
    OPTIONS = '|'.join(globals()['OPTIONS'])
    config_file = os.path.join(app.config['DB_DIR'],
                               app.config['CONFIG_DB'])

    newConfig = Config(**dict([(field,locals()[field]) for field in _fields]))
    if Config.query.filter_by(KEY=KEY).all():
        Config.query.filter_by(KEY=KEY).delete()
    db.session.add(newConfig)
    db.session.commit()
    

if __name__ == '__main__':

    if args.update:
        print 'Updating database using '+args.config_file
        updateConfig(args.key)
    elif args.reset:
        print 'Resetting database using '+args.config_file
        resetConfig()

    if args.p:
        print Config.query.all()

    

# N.B.
# If I change OPTIONS or AUTHORS_LIST I want also to reset the voters/votes databases

