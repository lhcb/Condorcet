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

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app

app.config['SQLALCHEMY_DATABASE_URI'] =  r'sqlite:///databases/votes.db'
app.config['SQLALCHEMY_BINDS'] = {
    'voters' : r'sqlite:///databases/voters.db',
    }
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
    username = db.Column(db.String(20), unique=True, primary_key=True)
    
    def __init__(self, username):
        self.username = username
        
    def __repr__(self):
        return '<User {username}>'.format(**self.__dict__)

    
def initDB():
    db.create_all()

def isInDB(username):
    return bool(Voters.query.filter_by(username=username).all())

def addVote(username, vote):   
    if isInDB(username):
        raise KeyError(username+' already in database')
    else:
        while True:
            secret_key = ''.join(random.sample(string.lowercase+string.digits,8))
            if not bool(Votes.query.filter_by(secret_key=secret_key).all()): break
        newVoter = Voters(username)
        newPreference = Votes(secret_key, vote)
        db.session.add(newVoter)
        db.session.add(newPreference)
        db.session.commit()
        return secret_key

def readDB():
    print 'Voters: '+ str(Voters.query.all())
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
