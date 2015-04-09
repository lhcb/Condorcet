#!/bin/bash

export PATH=/usr/bin/:$PATH
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
wget https://pypi.python.org/packages/2.6/f/flup/flup-1.0.2-py2.6.egg
chmod 755 Condorcet/manageDB.py
Condorcet/manageDB.py --init
chmod 755 Condorcet/updateConfig.py
Condorcet/updateConfig.py --reset
fs setacl -dir Condorcet/databases -acl webserver:afs diklwr
chmod +x cgi-bin/condorcet.fcgi

# Change first line in cgi-bin/condorcet.fcgi
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo $DIR
cat cgi-bin/condorcet.fcgi | sed -e "s;/afs/cern.ch/user/g/gdujany/www/Condorcet;$DIR;" > cgi-bin/tmp.fcgi
mv cgi-bin/tmp.fcgi cgi-bin/condorcet.fcgi
chmod 755 cgi-bin/condorcet.fcgi

