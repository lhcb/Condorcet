#!/usr/bin/env python
'''
Here I use 2 different databases, one for users to keep track of who already
voted and one for saving votes aleng with the secret keys
'''

# Options parser
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Manage databases')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--init', help='Create databases', action='store_true')
    group.add_argument('--rm', help='Remove databases', action='store_true')
    group.add_argument('--reset', help='Remove and recreate databases',
                       action='store_true')
    parser.add_argument('-p', help='Print content of databases',
                        action='store_true')
    args = parser.parse_args()

import os
import sys
import random
import string
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))  # noqa

from flask.ext.sqlalchemy import SQLAlchemy

from Condorcet import app
from Condorcet.updateConfig import getConfig
from verifyAuthors import listAuthors


def default_authors_file():
    return os.path.join(app.config['DB_DIR'], getConfig('AUTHORS_LIST'))

db = SQLAlchemy(app)


class Votes(db.Model):
    __bind_key__ = 'votes'
    secret_key = db.Column(db.String(8), unique=True, primary_key=True)
    vote = db.Column(db.String(15), unique=False)

    def __init__(self, secret_key, vote):
        self.secret_key = secret_key
        self.vote = vote

    def __repr__(self):
        return '<secret_key {secret_key}, vote {vote}>'.format(**self.__dict__)


class Voters(db.Model):
    __bind_key__ = 'voters'
    fullname = db.Column(db.String(20), unique=True, primary_key=True)
    hasVoted = db.Column(db.Boolean)

    def __init__(self, fullname):
        self.fullname = fullname
        # Set hasVoted to False on initialization
        self.hasVoted = False

    def __repr__(self):
        return '<User: {fullname}, has voted: {hasVoted}>'.format(
            **self.__dict__
        )

    def __str__(self):
        return '<{fullname}>'.format(**self.__dict__)


def populateTables(authors_file):
    """Populate voters table with author list."""
    for fullname in listAuthors(authors_file):
        newVoter = Voters(fullname)
        if Voters.query.filter_by(fullname=fullname).all():
            # raise KeyError(fullname+' appears twice in the authors list')
            print fullname+' appears twice in the authors list'
            continue
        db.session.add(newVoter)
    db.session.commit()


def initDB(authors_file=None,dbdir=app.config['DB_DIR']):
    """Create voters and votes databases at database_folder.

    The authors_file is used to populate the database.
    """
    if authors_file is None:
        authors_file = default_authors_file()
    if app.config['VOTERS_DB'] in os.listdir(dbdir) or app.config['VOTES_DB'] in os.listdir(dbdir):
        raise IOError(
            'Database already there, use --reset option to recreate'
        )
    db.create_all()
    populateTables(authors_file)
    os.chmod(os.path.join(dbdir, app.config['VOTES_DB']), 0666)
    os.chmod(os.path.join(dbdir, app.config['VOTERS_DB']), 0666)


def isInDB(fullname):
    try:
        return Voters.query.filter_by(fullname=fullname).first().hasVoted
    except AttributeError:
        raise KeyError(fullname + ' not in the list of possible voters')


def generateSecretKey(length=8):
    """Return a string of randomly chosen lowercase alphanumeric characters."""
    return ''.join(random.sample(string.lowercase + string.digits, length))


def addVote(fullname, vote):
    if isInDB(fullname):
        raise KeyError(fullname + ' has already voted')
    else:
        while True:
            secret_key = generateSecretKey()
            if not bool(Votes.query.filter_by(secret_key=secret_key).all()):
                break
        newPreference = Votes(secret_key, vote)
        Voters.query.filter_by(fullname=fullname).first().hasVoted = True
        db.session.add(newPreference)
        db.session.commit()
        return secret_key


def readDB():
    print 'Voters: ' + str([
        str(voter) for voter in Voters.query.all() if voter.hasVoted
    ])
    print 'Votes:  ' + str(Votes.query.all())


def getVotes():
    '''List of (secret_key, vote)'''
    return [(i.secret_key, i.vote) for i in Votes.query.all()]


def getPreferences():
    '''List of votes'''
    return [i.vote for i in Votes.query.all()]


def rmDB():
    votes_file = os.path.join(app.config['DB_DIR'],
                              app.config['VOTES_DB'])
    voters_file = os.path.join(app.config['DB_DIR'],
                               app.config['VOTERS_DB'])
    for db_file in [votes_file, voters_file]:
        if os.path.exists(db_file):
            os.remove(db_file)


def resetDB(authors_file=None):
    if authors_file is None:
        authors_file = default_authors_file()
    rmDB()
    initDB(authors_file)

if __name__ == '__main__':
    if args.rm:
        rmDB()
    if args.reset:
        resetDB(default_authors_file())
    if args.init:
        initDB(default_authors_file())
    if args.p:
        readDB()
