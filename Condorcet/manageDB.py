from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from Condorcet import app

app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///votes.db'
db = SQLAlchemy(app)


class Votes(db.Model):
    username = db.Column(db.String(80), unique=True, primary_key=True)
    vote = db.Column(db.String(15), unique=False)

    def __init__(self, username, vote):
        self.username = username
        self.vote = vote

    def __repr__(self):
        return '<User {username}, vote {vote}>'.format(**self.__dict__)

    
def initDB():
    db.create_all()

def addVote(username, vote):
    newVote = Votes(username, vote)
    if isInDB(username):
        raise KeyError(username+' already in database')
    else:
        db.session.add(newVote)
        db.session.commit()

def modifyVote(username, new_vote):
    Votes.query.filter_by(username=username).first().vote = new_vote
    db.session.commit()

def deleteVote(username):
    Votes.query.filter_by(username=username).delete()
    db.session.commit()
    

def readDB():
    print Votes.query.all()

def isInDB(username):
    return bool(Votes.query.filter_by(username=username).all())

# preferences = [i.vote for i in Votes.query.all()]


