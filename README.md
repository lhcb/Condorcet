Condorcet
=========

Condorcet is a web application for voting.

Set up
------

The application uses the [Flask](http://flask.pocoo.org/) web framework and [SQLAlchemy](http://www.sqlalchemy.org/) database management packages.
To get up and running, install these dependencies and initialise the database.

```bash
$ git clone git@github.com:gdujany/Condorcet.git
$ cd Condorcet
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ chmod 755 Condorcet/managDB.py
$ Condorcet/manageDB.py --init
```

AFS
---

To set up the environment the first time [in a folder on AFS](https://espace2013.cern.ch/webservices-help/websitemanagement/ManagingWebsitesAtCERN/Pages/WebsitecreationandmanagementatCERN.aspx), just modify your `PATH` to make sure the correct Python version is used, and get a copy of the [Flup](http://www.saddi.com/software/flup/) Python module, which is used as a [WSGI](http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) bridge.

```bash
$ export PATH=/usr/bin/python:$PATH
$ wget https://pypi.python.org/packages/2.6/f/flup/flup-1.0.2-py2.6.egg
```

Go to the [CERN AFS web configuration page](https://webservices.web.cern.ch/webservices/Tools/SiteConfiguration/) and enable CGI execution.

To make the database writeable by the AFS web server one has to do:

```bash
fs setacl -dir Condorcet/databases -acl webserver:afs diklwr
chmod 0666 Condorcet/databases
chmod 0666 Condorcet/databases/*.db
```
