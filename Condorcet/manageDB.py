#!/usr/bin/env python
'''
Here I use 2 different databases, one for users to keep track of who already voted and one for saving votes aleng with the secret keys
'''

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'Manage databases')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--init',help='create databases',action='store_true')
    group.add_argument('--rm',help='remove databases',action='store_true')
    group.add_argument('--reset',help='remove databases and create them again',action='store_true')
    parser.add_argument('-p',help='print content of databases',action='store_true')
    args = parser.parse_args()
##########################

import os, sys, random, string
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))

from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app

db = SQLAlchemy(app)

class Votes(db.Model):
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
        self.hasVoted = False # at initialization is set to False
        
    def __repr__(self):
        return '<User: {fullname}, has voted: {hasVoted}>'.format(**self.__dict__)

    def __str__(self):
        return '<{fullname}>'.format(**self.__dict__)

from verifyAuthors import listAuthors

    
def initDB():
    if 'voters.db' in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),'databases')) or 'votes.db' in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),'databases')):
        raise IOError('Database already there, use --reset option if you want to substitute it')
    db.create_all()
    for fullname in listAuthors():
        newVoter = Voters(fullname)
        db.session.add(newVoter)
    db.session.commit()
    os.chmod(os.path.join(os.path.dirname(os.path.realpath(__file__)),'databases/votes.db'),0666)
    os.chmod(os.path.join(os.path.dirname(os.path.realpath(__file__)),'databases/voters.db'),0666)
    

def isInDB(fullname):
    try:
        return Voters.query.filter_by(fullname=fullname).first().hasVoted
    except AttributeError:
        raise KeyError(fullname+' not in the list of possible voters')

def addVote(fullname, vote):   
    if isInDB(fullname):
        raise KeyError(fullname+' has already voted')
    else:
        while True:
            secret_key = ''.join(random.sample(string.lowercase+string.digits,8))
            if not bool(Votes.query.filter_by(secret_key=secret_key).all()): break
        newPreference = Votes(secret_key, vote)
        Voters.query.filter_by(fullname=fullname).first().hasVoted = True
        db.session.add(newPreference)
        db.session.commit()
        return secret_key

def readDB():
    print 'Voters: '+ str([str(voter) for voter in Voters.query.all() if voter.hasVoted])
    print 'Votes:  '+ str(Votes.query.all())

def getVotes():
    '''List of (secret_key, vote)'''
    return [(i.secret_key, i.vote) for i in Votes.query.all()]

def getPreferences():
    '''List of votes'''
    return [i.vote for i in Votes.query.all()]


if __name__ == '__main__':
    
    if args.rm or args.reset:
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)),'databases/votes.db'))
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)),'databases/voters.db'))
    if args.init or args.reset:
        initDB()
    if args.p:
        readDB()
