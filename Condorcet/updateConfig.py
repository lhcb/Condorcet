#!/usr/bin/env python
"""
Put some Condorcet voting configuration in a database
so that it is possible to modify them in real time.
"""

# Options parser
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Update Config database sincronizing it with config.py')  # noqa
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--update', help='update config database reading from the CONFIG_FILE',  # noqa
                       action='store_true')
    group.add_argument('--reset', help='Remove and recreate config database',
                       action='store_true')
    parser.add_argument('--key', help='Key used to store new config, leave default "default"',  # noqa
                        default='default')
    parser.add_argument('--config_file', help='Config file to use',
                        default='config.py')
    parser.add_argument('-p', help='Print content of databases',
                        action='store_true')
    args = parser.parse_args()
    default_config_file = args.config_file
    default_key = args.key
else:
    default_config_file = 'config.py'
    default_key = 'default'

import os
import sys
import time
this_files_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_files_dir, '..'))

_fields = ['KEY', 'TITLE', 'OPTIONS', 'CONTACT', 'DATE_FORMAT',
           'START_ELECTION', 'CLOSE_ELECTION', 'VIEW_RESULTS', 'VOTERS_LIST']

from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app
db = SQLAlchemy(app)


class Config(db.Model):
    KEY = db.Column(db.String(20), unique=True, primary_key=True)
    TITLE = db.Column(db.String(100), unique=False)
    OPTIONS = db.Column(db.String(100), unique=False)
    CONTACT = db.Column(db.String(100), unique=False)
    DATE_FORMAT = db.Column(db.String(100), unique=False)
    START_ELECTION = db.Column(db.String(100), unique=False)
    CLOSE_ELECTION = db.Column(db.String(100), unique=False)
    VIEW_RESULTS = db.Column(db.String(100), unique=False)
    VOTERS_LIST = db.Column(db.String(100), unique=False)

    def __init__(self, KEY, TITLE, OPTIONS, CONTACT, DATE_FORMAT,
                 START_ELECTION, CLOSE_ELECTION, VIEW_RESULTS, VOTERS_LIST):
        for field in _fields:
            exec 'self.{0} = {0}'.format(field)

    def __repr__(self):
        ret_str = '\n'
        for field in _fields:
            ret_str += '''{0} = {1}\n'''.format(field, getattr(self, field))
        return ret_str


def getConfig(field, KEY='default'):
    """
    Get configuration from database
    field: which configuration, eg. TITLE
    KEY: if I have multiple configurations may be useful
    """
    try:
        ret = getattr(Config.query.filter_by(KEY=KEY).first(), field)
        if field == 'OPTIONS':
            ret = [i.lstrip() for i in ret.split(',')]
    # if there is no database I fallback to reading conf from config file  # noqa
    except:
        if field == 'KEY':
            return KEY
        exec 'from config import '+field+' as ret'

    if field in ('START_ELECTION', 'CLOSE_ELECTION', 'VIEW_RESULTS'):
        ret = time.strptime(ret, getConfig('DATE_FORMAT', KEY))
    return ret


def getConfigDict(KEY='default'):
    return dict((field, getConfig(field, KEY=KEY)) for field in _fields)


def setConfig(field, value, KEY='default'):
    """
    Modify configuration in the database but without changing
    the defaults values in config.py
    N.B. If I run uptdateConfig.py the defaults will be set back again
    """
    if field == 'OPTIONS':
        value = ','.join(value)
    elif field in ('START_ELECTION', 'CLOSE_ELECTION', 'VIEW_RESULTS'):
        value = time.strftime(getConfig('DATE_FORMAT', KEY), value)
    setattr(Config.query.filter_by(KEY=KEY).first(), field, value)

    # TODO: Check if field is a date in which format I get it  # noqa
    db.session.commit()


def resetConfig(KEY='default', config_file=default_config_file):
    """
    Create a new database for Config, removing the old and call updateConfig
    """
    config_db = os.path.join(app.config['DB_DIR'],
                             app.config['CONFIG_DB'])
    if os.path.exists(config_db):
        os.remove(config_db)
    db.create_all(bind=None)
    os.chmod(os.path.join(app.config['DB_DIR'], config_db), 0666)
    upConfig(KEY, config_file)


def upConfig(KEY='default', config_file=default_config_file):
    '''
    Update the KEY config reading the values from config.py
    '''
    sys.path.append(os.path.dirname(config_file))
    config_name = os.path.basename(os.path.splitext(config_file)[0])
    _fields.remove('KEY')
    for field in _fields:
        exec 'from {0} import {1}'.format(config_name, field)
    _fields.insert(0, 'KEY')
    KEY = default_key
    OPTIONS = ','.join(locals()['OPTIONS'])
    config_file = os.path.join(app.config['DB_DIR'],
                               app.config['CONFIG_DB'])

    newConfig = Config(**dict([(field, locals()[field]) for field in _fields]))
    # if Config.query.filter_by(KEY=KEY).all():
    #     print 'Qui'
    #     Config.query.filter_by(KEY=KEY).delete()
    # db.session.add(newConfig)
    if Config.query.filter_by(KEY=KEY).all():
        for field in _fields:
            exec 'Config.query.filter_by(KEY=KEY).first().'+field+' = '+field
    else:
        db.session.add(newConfig)
    db.session.commit()


if __name__ == '__main__':

    if args.update:
        print 'Updating database using '+args.config_file
        upConfig(args.key)
    elif args.reset:
        print 'Resetting database using '+args.config_file
        resetConfig()

    if args.p:
        print Config.query.all()

# N.B.
# If I change OPTIONS or VOTERS_LIST I want also to reset the voters/votes databases  # noqa
