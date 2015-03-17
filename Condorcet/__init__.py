from flask import Flask, render_template, request, redirect, session, flash
import os
import sys
import random
import string
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


app = Flask(__name__)
app.config.from_object('Condorcet.config')

import manageDB
from verifyAuthors import isAuthor
import elections

alphabet = string.lowercase
name2letter = {key: val for key, val in zip(app.config['OPTIONS'], alphabet)}
letter2name = {key: val for key, val in zip(alphabet, app.config['OPTIONS'])}


def getStrOrder(choice_made):
    return ''.join([name2letter[choice] for choice in choice_made])

def getListChoice(vote):
    return [letter2name[letter] for letter in vote]


def get_environ(var):
    return request.environ(var)


@app.before_request
def set_user():
    # Set user as GD when debugging, else use CERN SSO credentials
    if app.config['DEBUG']:
        session['user'] = {
            'username': 'gdujany',
            'fullname': 'Giulio Dujany'
        }
    else:
        session['user'] = {
            'username': get_environ('ADFS_LOGIN'),
            'fullname': ' '.join([
                get_environ('ADFS_FIRSTNAME'), get_environ('ADFS_LASTNAME')
            ])
        }
    if  not isAuthor(session['user']['fullname']):
        return render_template('notAuthor.html')

def build_path(path=''):
    return os.path.join(app.config['APPLICATION_ROOT'], path)


@app.route(build_path())
@app.route('/')
def root():    
    username = session['user']['username']
    if manageDB.isInDB(username): return render_template('alreadyVoted.html')
    choices_copy = app.config['OPTIONS'][:]
    # FIXME: like this it shuffle fine but when I reload the page the votes already set change!
    random.shuffle(choices_copy)
    poll_data['fields'] = choices_copy
    return render_template('poll.html', data=poll_data)





@app.route(build_path('/poll'))
@app.route('/poll')
def confimVote():
    order = []
    if len(request.args) == len(choices):
        for num in [str(i) for i in range(1,len(choices)+1)]:
            order.append(request.args.get(num))
    choices = app.config['OPTIONS']
        vote = getStrOrder(order)
    else: vote = '' # so that fails next if
    if len(set(vote)) == len(choices):
        username = session['user']['username']
        if manageDB.isInDB(username): return render_template('alreadyVoted.html')
        session['vote'] = vote
        confirm_data = {
            'saveVote_address' : build_path('saveVote'),
            'preference' :', '.join(getListChoice(vote)),
            }
        return render_template('confirmVote.html',data=confirm_data)       
    else:
        flash('You must rank all candidates and two element cannot share the same position, try again', 'error')
    return redirect(build_path())


@app.route(build_path('/saveVote'))
@app.route('/saveVote')
def savePoll():
    username = session['user']['username']
    if manageDB.isInDB(username): return render_template('alreadyVoted.html')
    secret_key = manageDB.addVote(username, session['vote'])
    return render_template('congrats.html', secret_key=secret_key)


@app.route(build_path('/results'))
def result():
    order = []
    choices = app.config['OPTIONS']
    # Prepare page with results
    preferences = manageDB.getPreferences()
    winners = getListChoice(elections.getWinner(preferences, [i for cont,i in enumerate(alphabet) if cont< len(choices)]))
    result_data = dict(numCandidates=len(choices))
    result_data['winner_str'] = ('The winner is' if len(winners)==1 else 'The winners are')+' '+', '.join(winners)
    result_data['table_DB'] = [[i[0]]+getListChoice(i[1]) for i in manageDB.getVotes()]
    return render_template('results.html', data=result_data)
    
 
if __name__ == '__main__':
    # Always run with debugging when using `python Condorcet/__init__.py`
    app.config['DEBUG'] = True
    app.run()
