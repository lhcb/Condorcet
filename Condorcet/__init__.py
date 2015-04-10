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
from updateConfig import getConfig, setConfig, getConfigDict, upConfig
import elections

alphabet = string.lowercase

def getStrOrder(choice_made):
    name2letter = dict([(key, val) for key, val in zip(getConfig('OPTIONS'), alphabet)])
    return ''.join([name2letter[choice] for choice in choice_made])


def getListChoice(vote):
    letter2name = dict([(key, val) for key, val in zip(alphabet, getConfig('OPTIONS'))])
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
                getConfig('VIEW_RESULTS')
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
def admin():
    #setConfig('CLOSE_ELECTION','28/03/2013 12.47')
    #return 'Congrats, you are an admin'
    current_config = getConfigDict()
    return render_template('admin.html',
                           current_config=current_config)

@app.route('/updateConfig', methods=['POST'])
@admin_required
def updateConfig():
    #return request.form.get('START_ELECTION_date')+' '+request.form.get('START_ELECTION_time')
    new_config = {}
    new_config['TITLE'] = request.form.get('TITLE')
    new_config['OPTIONS'] = [i.lstrip() for i in request.form.get('OPTIONS').split(',')]
    new_config['START_ELECTION'] = time.strptime(request.form.get('START_ELECTION_date')+' '+request.form.get('START_ELECTION_time'), '%Y-%m-%d %H:%M')
    new_config['CLOSE_ELECTION'] = time.strptime(request.form.get('CLOSE_ELECTION_date')+' '+request.form.get('CLOSE_ELECTION_time'), '%Y-%m-%d %H:%M')
    new_config['VIEW_RESULTS'] = time.strptime(request.form.get('VIEW_RESULTS_date')+' '+request.form.get('VIEW_RESULTS_time'), '%Y-%m-%d %H:%M')
    current_config = getConfigDict()
    for key in new_config:
        if new_config[key] != current_config[key]:
            if key in ['OPTIONS']:
                # So that I can check immediately if the candidates have changed
                try:
                    del session['candidates']
                except KeyError:
                    pass
                flash(('You changed the candidates so you probably want to reset the databases'), 'error')
            setConfig(key,new_config[key])
    return redirect(url_for('admin'))
    #return time.strftime('%d %B %Y at %H.%M',new_config['START_ELECTION'])

@app.route('/resetDatabases', methods=['POST'])
@admin_required
def resetDatabases():
    manageDB.resetDB(authors_file=getConfig('AUTHORS_LIST'))
    flash(('Databases correcly reset'), 'success')
    return redirect(url_for('admin'))

@app.route('/resetConfiguration', methods=['POST'])
@admin_required
def resetDefaultConfiguration():
    old_config = getConfigDict()
    upConfig()
    flash(('Default configuration correcly reset'), 'success')
    new_config = getConfigDict()
    if old_config['OPTIONS'] != new_config['OPTIONS']:
        flash(('You changed the candidates so you probably want to reset the databases'), 'error')
    return redirect(url_for('admin'))

 


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
