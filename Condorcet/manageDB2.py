'''
Here I use 2 different databases, one for users to keep track of who already voted and one for saving votes aleng with the secret keys
'''

if __name__ == '__main__':
    import sys
    sys.path.append('..')

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app
import random, string


app.config['SQLALCHEMY_DATABASE_URI'] =  r'sqlite:///databases/preferences.db'
app.config['SQLALCHEMY_BINDS'] = {
    'voters' : r'sqlite:///databases/voters.db',
    }
db = SQLAlchemy(app)


class Preferences(db.Model):
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

def addVote(username, vote):   
    if isInDB(username):
        raise KeyError(username+' already in database')
    else:
        while True:
            secret_key = ''.join(random.sample(string.lowercase+string.digits,8))
            if not bool(Preferences.query.filter_by(secret_key=secret_key).all()): break
        newVoter = Voters(username)
        newPreference = Preferences(secret_key, vote)
        db.session.add(newVoter)
        db.session.add(newPreference)
        db.session.commit()
        return secret_key

# def modifyVote(username, new_vote):
#     #Votes.query.filter_by(username=username).first().vote = new_vote
#     #db.session.commit()
#     return "Sorry but this operation is not permitted" #Votes.query.filter_by(username=username).first().secret_key

# def deleteVote(username):
#     Votes.query.filter_by(username=username).delete()
#     db.session.commit()

# def getVote(username):
#     return Votes.query.filter_by(username=username).first().vote
    
def readDB():
    print Voters.query.all()
    print Preferences.query.all()

def getVotes():
    '''List of (secret_key, vote)'''
    return [(i.secret_key, i.vote) for i in Preferences.query.all()]

def getPreferences():
    '''List of votes'''
    return [i.vote for i in preferences.query.all()]

def isInDB(username):
    return bool(Voters.query.filter_by(username=username).all())
