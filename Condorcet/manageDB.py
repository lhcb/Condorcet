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
    parser.add_argument('--csv', help='Make csv file',
                        nargs='?', const='votes.csv')
    args = parser.parse_args()

import os
import sys
import random
import string
import io
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))  # noqa

from flask.ext.sqlalchemy import SQLAlchemy

from Condorcet import app
from Condorcet.updateConfig import getConfig
from verifyVoters import listVoters
import Condorcet


def default_voters_file():
    return os.path.join(app.config['DB_DIR'], getConfig('VOTERS_LIST'))

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
    cernid = db.Column(db.String(20), unique=True, primary_key=True)
    hasVoted = db.Column(db.Boolean)

    def __init__(self, cernid):
        self.cernid = cernid
        # Set hasVoted to False on initialization
        self.hasVoted = False

    def __repr__(self):
        return '<User: {cernid}, has voted: {hasVoted}>'.format(
            **self.__dict__
        )

    def __str__(self):
        return '<{cernid}>'.format(**self.__dict__)


def populateTables(voters_file):
    """Populate voters table with voter list."""
    multiple_entries = []
    for cernid in listVoters(voters_file):
        newVoter = Voters(cernid)
        if Voters.query.filter_by(cernid=cernid).all():
            multiple_entries.append(cernid)
            continue
        db.session.add(newVoter)
    db.session.commit()
    if len(multiple_entries) != 0:
        print 'some voters appear twice in the voters list'
        with open('multiple_entries.txt', 'w') as outFile:
            outFile.write(str(multiple_entries))


def updateVoters(voters_file):
    """
    Add to the voters' database voters that are present
    in the voters_file but were not in the database
    removes voters not present in the new voter list which have not yet voted
    if someone has already voted and is not eligible any more keep
    him in the db as his vote cannot be removed
    """
    voters_list = listVoters(voters_file)
    for cernid in voters_list:
        newVoter = Voters(cernid)
        if Voters.query.filter_by(cernid=cernid).all():
            continue
        db.session.add(newVoter)
    voters_db = [voter.cernid for voter in Voters.query.all()]
    for cernid in set(voters_db) - set(voters_list):
        if not Voters.query.filter_by(cernid=cernid).first().hasVoted:
            Voters.query.filter_by(cernid=cernid).delete()
    db.session.commit()


def initDB(voters_file=None, dbdir=app.config['DB_DIR']):
    """Create voters and votes databases at database_folder.

    The voters_file is used to populate the database.
    """
    if voters_file is None:
        voters_file = default_voters_file()
    if (app.config['VOTERS_DB'] in os.listdir(dbdir) or app.config['VOTES_DB'] in os.listdir(dbdir)):  # noqa
        raise IOError(
            'Database already there, use --reset option to recreate'
        )
    db.create_all(bind='votes')
    db.create_all(bind='voters')
    os.chmod(os.path.join(dbdir, app.config['VOTES_DB']), 0666)
    os.chmod(os.path.join(dbdir, app.config['VOTERS_DB']), 0666)
    populateTables(voters_file)


def isInDB(cernid):
    try:
        return Voters.query.filter_by(cernid=cernid).first().hasVoted
    except AttributeError:
        raise KeyError(cernid + ' not in the list of possible voters')


def generateSecretKey(length=8):
    """Return a string of randomly chosen lowercase alphanumeric characters."""
    return ''.join(random.sample(string.lowercase + string.digits, length))


def addVote(cernid, vote):
    if isInDB(cernid):
        raise KeyError(cernid + ' has already voted')
    else:
        while True:
            secret_key = generateSecretKey()
            if not bool(Votes.query.filter_by(secret_key=secret_key).all()):
                break
        newPreference = Votes(secret_key, vote)
        Voters.query.filter_by(cernid=cernid).first().hasVoted = True
        db.session.add(newPreference)
        db.session.commit()
        return secret_key


def readDB():
    print 'Voters: ' + str([
        str(voter) for voter in Voters.query.all() if voter.hasVoted
    ])
    print 'Votes:  ' + str(Votes.query.all())
    print 'Number of votes: ' + str(len(Votes.query.all()))


def getVote(secret_key):
    '''return vote given secret key'''
    try:
        return Votes.query.filter_by(secret_key=secret_key).first().vote
    except AttributeError:
        return None


def getVotes():
    '''List of (secret_key, vote)'''
    return [(i.secret_key, i.vote) for i in Votes.query.all()]


def getNumVoters():
    '''Get tuple (number voters, number possible voters)'''
    return(len([voter for voter in Voters.query.all() if voter.hasVoted]),
           len(Voters.query.all()))


def makeCSV(outFile_name):
    '''
    Return list of [ secret_key, candidate1, candidate2, ..., candidateN ]
    '''
    with io.open(outFile_name, 'w',encoding='utf8') as outFile:
        outFile.write(u'Secret key,')
        for i in range(1, len(getConfig('OPTIONS'))+1):
            outFile.write(u'Choice #{0},'.format(i))
        outFile.write(u'\n')
        for vote in [[i.secret_key] + Condorcet.getListChoice(i.vote)
                     for i in Votes.query.all()]:
            outFile.write(u','.join(vote)+u'\n')


def getPreferences():
    '''List of votes'''
    return [i.vote for i in Votes.query.all()]


def rmDB(dbdir=app.config['DB_DIR']):
    votes_file = os.path.join(dbdir,
                              app.config['VOTES_DB'])
    voters_file = os.path.join(dbdir,
                               app.config['VOTERS_DB'])
    db.session.remove()
    for db_file in [votes_file, voters_file]:
        if os.path.exists(db_file):
            os.remove(db_file)


def resetDB(voters_file=None, dbdir=app.config['DB_DIR']):
    if voters_file is None:
        voters_file = default_voters_file()
    rmDB(dbdir)
    initDB(voters_file, dbdir)

if __name__ == '__main__':
    if args.rm:
        rmDB()
    if args.reset:
        resetDB(default_voters_file())
    if args.init:
        initDB(default_voters_file())
    if args.p:
        readDB()
    if args.csv:
        makeCSV(args.csv)
