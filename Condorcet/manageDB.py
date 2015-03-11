from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app
import random, string

app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///votes.db'
db = SQLAlchemy(app)


class Votes(db.Model):
    username = db.Column(db.String(80), unique=True, primary_key=True)
    secret_key = db.Column(db.String(8), unique=True)
    vote = db.Column(db.String(15), unique=False)

    def __init__(self, username, secret_key, vote):
        self.username = username
        self.secret_key = secret_key
        self.vote = vote

    def __repr__(self):
        return '<User {username}, secret_key {secret_key}, vote {vote}>'.format(**self.__dict__)

    
def initDB():
    db.create_all()

def addVote(username, vote):   
    if isInDB(username):
        raise KeyError(username+' already in database')
    else:
        while True:
            secret_key = ''.join(random.sample(string.lowercase+string.digits,8))
            if not bool(Votes.query.filter_by(secret_key=secret_key).all()): break
        newVote = Votes(username, secret_key, vote)
        db.session.add(newVote)
        db.session.commit()
        return secret_key

def modifyVote(username, new_vote):
    Votes.query.filter_by(username=username).first().vote = new_vote
    db.session.commit()
    return Votes.query.filter_by(username=username).first().secret_key

def deleteVote(username):
    Votes.query.filter_by(username=username).delete()
    db.session.commit()

def getVote(username):
    return Votes.query.filter_by(username=username).first().vote
    
def readDB():
    print Votes.query.all()

def getVotes():
    '''List of (username, secret_key, vote)'''
    return [(i.username, i.secret_key, i.vote) for i in Votes.query.all()]

def getPreferences():
    '''List of votes'''
    return [i.vote for i in Votes.query.all()]

def isInDB(username):
    return bool(Votes.query.filter_by(username=username).all())

# preferences = [i.vote for i in Votes.query.all()]


