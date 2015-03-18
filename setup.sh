#!/bin/bash

export PATH=/usr/bin/:$PATH
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
wget https://pypi.python.org/packages/2.6/f/flup/flup-1.0.2-py2.6.egg
chmod 755 Condorcet/managDB.py
Condorcet/manageDB.py --init
fs setacl -dir Condorcet/databases -acl webserver:afs diklwr

