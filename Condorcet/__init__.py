from flask import Flask, render_template, request, redirect, session, flash
import os
import sys
import random
import string
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))


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
    if not isAuthor(session['user']['fullname']):
        return render_template('notAuthor.html')


def build_path(path=''):
    return os.path.join(app.config['APPLICATION_ROOT'], path)


@app.route(build_path())
def root():
    fullname = session['user']['fullname']
    if manageDB.isInDB(fullname):
        return render_template('alreadyVoted.html')
    try: session['candidates']
    except KeyError:
        choices_copy = app.config['OPTIONS'][:]
        random.shuffle(choices_copy)
        session['candidates'] = choices_copy
    return render_template('poll.html',
                           title=app.config['TITLE'],
                           fields=session['candidates'])


@app.route(build_path('/poll'), methods=['POST'])
def confirmVote():
    order = []
    choices = app.config['OPTIONS']
    if len(request.form) == len(choices):
        for num in [str(i) for i in range(1, len(choices) + 1)]:
            order.append(request.form.get(num))
        vote = getStrOrder(order)
    else:
        # So that fails next if
        vote = ''
    if len(set(vote)) == len(choices):
        fullname = session['user']['fullname']
        if manageDB.isInDB(fullname):
            return render_template('alreadyVoted.html')
        session['vote'] = vote
        return render_template('confirmVote.html', choices=getListChoice(vote))
    else:
        flash((
            'You must rank all candidates and two candidates cannot share the '
            'same position. Please try again.'
        ), 'error')
    return redirect(build_path())


@app.route(build_path('/saveVote'))
def savePoll():
    fullname = session['user']['fullname']
    if manageDB.isInDB(fullname):
        return render_template('alreadyVoted.html')
    secret_key = manageDB.addVote(fullname, session['vote'])
    return render_template('congrats.html', secret_key=secret_key)


@app.route(build_path('/results'))
def result():
    # Prepare page with results
    preferences = manageDB.getPreferences()
    choices = app.config['OPTIONS']
    winners = getListChoice(
        elections.getWinner(
            preferences,
            [i for cont, i in enumerate(alphabet) if cont < len(choices)]
        )
    )
    results = [
        [i[0]] + getListChoice(i[1])
        for i in manageDB.getVotes()
    ]
    return render_template('results.html',
                           winners=winners,
                           numCandidates=len(choices),
                           results=results)


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
