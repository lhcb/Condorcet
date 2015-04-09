from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)
from functools import wraps
import os
import sys
import random
import string
import time
# Add this directory and the one above to PYTHONPATH
this_files_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_files_dir)
sys.path.append(os.path.join(this_files_dir, '..'))


app = Flask(__name__)
app.config.from_object('Condorcet.config')

import manageDB
from verifyAuthors import isAuthor, isAdmin
from updateConfig import getConfig, setConfig
import elections

alphabet = string.lowercase
name2letter = dict([
    (key, val) for key, val in zip(getConfig('OPTIONS'), alphabet)
])
letter2name = dict([
    (key, val) for key, val in zip(alphabet, getConfig('OPTIONS'))
])


def getStrOrder(choice_made):
    return ''.join([name2letter[choice] for choice in choice_made])


def getListChoice(vote):
    return [letter2name[letter] for letter in vote]


def get_environ(var):
    return request.environ[var]


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
    session['user']['author'] = isAuthor(session['user']['fullname'])
    session['user']['admin'] = isAdmin(session['user']['fullname'])


def author_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['user']['author']:
            return redirect(url_for('notAuthor'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['user']['admin']:
            return 'You appear not to be an admin so you cannot access this content' #redirect(url_for('notAuthor'))
        return f(*args, **kwargs)
    return decorated_function


def during_elections(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if time.localtime() < getConfig('START_ELECTION'):
            # TODO factor out long string to view
            start = time.strftime(
                '%d %B %Y at %H.%M',
                getConfig('START_ELECTION')
            )
            message = 'The election will be begin on ' + start
            return render_template('notCorrectDate.html',
                                   title='Too early to vote',
                                   message=message)
        if time.localtime() > getConfig('CLOSE_ELECTION'):
            # TODO factor out long string to view
            close = time.strftime(
                '%d %B %Y at %H.%M',
                getConfig('CLOSE_ELECTION')
            )
            message = 'The closing date of the election was the ' + close
            return render_template('notCorrectDate.html',
                                   title='Too late to vote',
                                   message=message)
        return f(*args, **kwargs)
    return decorated_function


def publish_results(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if time.localtime() < getConfig('VIEW_RESULTS'):
            results = time.strftime(
                '%d %B %Y at %H.%M',
                getConfig('START_ELECTION')
            )
            message = 'The results will be availabe on ' + results
            if session['user']['admin']:
                if time.localtime() > getConfig('CLOSE_ELECTION'):
                    return f(*args, **kwargs)
                else:
                    close = time.strftime(
                        '%d %B %Y at %H.%M',
                        getConfig('CLOSE_ELECTION')
                        )
                    message = 'The election is still on until '+close+' so even if you are an admin you must at least wait for the election to be closed, the results will be pubblically availabe on ' + results
            
            return render_template('notCorrectDate.html',
                                       title='Too early to see the results',
                                       message=message)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@during_elections
@author_required
def root():
    fullname = session['user']['fullname']
    if manageDB.isInDB(fullname):
        return render_template('alreadyVoted.html')
    try:
        session['candidates']
    except KeyError:
        choices_copy = getConfig('OPTIONS')[:]
        random.shuffle(choices_copy)
        session['candidates'] = choices_copy
    return render_template('poll.html',
                           title=getConfig('TITLE'),
                           fields=session['candidates'])


@app.route('/poll', methods=['POST'])
@during_elections
@author_required
def confirmVote():
    order = []
    choices = getConfig('OPTIONS')
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
    return redirect(url_for('root'))


@app.route('/saveVote')
@during_elections
@author_required
def savePoll():
    fullname = session['user']['fullname']
    if manageDB.isInDB(fullname):
        return render_template('alreadyVoted.html')
    secret_key = manageDB.addVote(fullname, session['vote'])
    return render_template('congrats.html', secret_key=secret_key)


@app.route('/results')
@publish_results
def result():
    # Prepare page with results
    preferences = manageDB.getPreferences()
    choices = getConfig('OPTIONS')
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


@app.route('/unauthorised')
def notAuthor():
    # Authors shouldn't see this page
    if session['user']['author']:
        return redirect(url_for('root'))
    return render_template('notAuthor.html'), 403


@app.route('/admin')
@admin_required
def adminPage():
    return 'Congrats, you are an admin'
    


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
