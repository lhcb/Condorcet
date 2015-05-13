from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
    send_from_directory,
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
from verifyVoters import isVoter
from updateConfig import getConfig, setConfig, getConfigDict, upConfig
import elections

alphabet = string.lowercase


def getStrOrder(choice_made):
    name2letter = dict(
        [(key, val) for key, val in zip(getConfig('OPTIONS'), alphabet)]
        )
    return ''.join([name2letter[choice] for choice in choice_made])


def getListChoice(vote):
    letter2name = dict(
        [(key, val) for key, val in zip(alphabet, getConfig('OPTIONS'))]
        )
    return [letter2name[letter] for letter in vote]


def get_environ(var):
    return request.environ[var]


@app.before_request
def set_user():
    # Set user as GD when debugging, else use CERN SSO credentials
    if app.config['DEBUG']:
        session['user'] = {
            'username': 'gdujany',
            'fullname': 'Giulio Dujany',
            'admin': True,
            'cernid': '718579',
        }
    else:
        session['user'] = {
            'username': get_environ('ADFS_LOGIN'),
            'fullname': ' '.join([
                get_environ('ADFS_FIRSTNAME'), get_environ('ADFS_LASTNAME')
            ]),
            'admin': 'lhcb-condorcet-voting' in get_environ('ADFS_GROUP'),
            'cernid': get_environ('ADFS_PERSONID')  # <- FIXME!
        }
    session['user']['voter'] = isVoter(session['user']['cernid'])


def voter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['user']['voter']:
            return redirect(url_for('notVoter'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['user']['admin']:
            # TODO: put a nice page here
            return 'You appear not to be an admin so you cannot access this content'  # noqa
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
                                   message=message,
                                   printResultsLink=False)
        if time.localtime() > getConfig('CLOSE_ELECTION'):
            # TODO factor out long string to view
            close = time.strftime(
                '%d %B %Y at %H.%M',
                getConfig('CLOSE_ELECTION')
            )
            message = 'The closing date of the election was the ' + close
            return render_template('notCorrectDate.html',
                                   title='Too late to vote',
                                   message=message,
                                   printResultsLink=True)
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
                    message = 'The election is still on until '+close+' so even if you are an admin you must at least wait for the election to be closed, the results will be pubblically availabe on ' + results  # noqa

            return render_template('notCorrectDate.html',
                                   title='Too early to see the results',
                                   message=message)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@during_elections
@voter_required
def root():
    cernid = session['user']['cernid']
    if manageDB.isInDB(cernid):
        return render_template('alreadyVoted.html')
    try:
        session['candidates']
        if sorted(session['candidates']) != sorted(getConfig('OPTIONS')):
            raise KeyError('Want to exit the try')
    except KeyError:
        choices_copy = getConfig('OPTIONS')[:]
        random.shuffle(choices_copy)
        session['candidates'] = choices_copy
    return render_template('poll.html',
                           title=getConfig('TITLE'),
                           fields=session['candidates'])


@app.route('/poll', methods=['POST'])
@during_elections
@voter_required
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
        cernid = session['user']['cernid']
        if manageDB.isInDB(cernid):
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
@voter_required
def savePoll():
    if not session.get('vote'):
        return redirect(url_for('root'))
    cernid = session['user']['cernid']
    if manageDB.isInDB(cernid):
        return render_template('alreadyVoted.html')
    secret_key = manageDB.addVote(cernid, session['vote'])
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
    numVoters = manageDB.getNumVoters()
    assert len(results) == numVoters[0]
    return render_template('results.html',
                           winners=winners,
                           numCandidates=len(choices),
                           numVoters=numVoters,
                           results=results)


@app.route('/votes.csv', methods=['GET', 'POST'])
@publish_results
def getCSV():
    manageDB.makeCSV(os.path.join(app.config['DB_DIR'], 'votes.csv'))
    return send_from_directory(directory=app.config['DB_DIR'],
                               filename='votes.csv')


@app.route('/unauthorised')
def notVoter():
    # Voters shouldn't see this page
    if session['user']['voter']:
        return redirect(url_for('root'))
    return render_template('notVoter.html',
                           voterList=getConfig('VOTERS_LIST')), 403


@app.route('/admin')
@admin_required
def admin():
    current_config = getConfigDict()
    if current_config['CLOSE_ELECTION'] > current_config['VIEW_RESULTS']:
        flash(('The publish date is before the close election date'), 'error')  # noqa
    if current_config['START_ELECTION'] > current_config['VIEW_RESULTS']:
        flash(('The publish date is before the start election date'), 'error')  # noqa
    if current_config['START_ELECTION'] > current_config['CLOSE_ELECTION']:
        flash(('The start date is after the close election date'), 'error')  # noqa
    return render_template('admin.html',
                           current_config=current_config)


@app.route('/updateConfiguration', methods=['POST'])
@admin_required
def updateConfiguration():
    new_config = {}
    new_config['TITLE'] = request.form.get('TITLE')
    new_config['OPTIONS'] = [i.lstrip() for i in request.form.get('OPTIONS').split(',')]  # noqa
    new_config['START_ELECTION'] = time.strptime(request.form.get('START_ELECTION_date')+' '+request.form.get('START_ELECTION_time'), '%Y-%m-%d %H:%M')  # noqa
    new_config['CLOSE_ELECTION'] = time.strptime(request.form.get('CLOSE_ELECTION_date')+' '+request.form.get('CLOSE_ELECTION_time'), '%Y-%m-%d %H:%M')  # noqa
    new_config['VIEW_RESULTS'] = time.strptime(request.form.get('VIEW_RESULTS_date')+' '+request.form.get('VIEW_RESULTS_time'), '%Y-%m-%d %H:%M')  # noqa
    current_config = getConfigDict()
    for key in new_config:
        if new_config[key] != current_config[key]:
            if key in ['OPTIONS']:
                # So that I can check immediately if the candidates have changed  # noqa
                try:
                    del session['candidates']
                except KeyError:
                    pass
                flash(('You changed the candidates so you probably want to reset the databases'), 'error')  # noqa
            setConfig(key, new_config[key])
    return redirect(url_for('admin'))


@app.route('/setToNow/<timeDate>', methods=['GET', 'POST'])
@admin_required
def setToNow(timeDate):
    setConfig(timeDate,
              time.localtime())
    flash((timeDate+' set to now'), 'success')
    return redirect(url_for('admin'))


@app.route('/resetDatabases', methods=['POST'])
@admin_required
def resetDatabases():
    manageDB.resetDB(voters_file=os.path.join(app.config['DB_DIR'],
                                              getConfig('VOTERS_LIST')))
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
        flash(('You changed the candidates so you probably want to reset the databases'), 'error')  # noqa
    if old_config['VOTERS_LIST'] != new_config['VOTERS_LIST']:
        flash(('You changed the list of voters so you probably want to reset the databases'), 'error')  # noqa
    return redirect(url_for('admin'))


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    if filename[-3:] == '.db':
        return 'Not authorized to download a database'
    return send_from_directory(directory=app.config['DB_DIR'],
                               filename=filename)


@app.route('/uploadVotersList', methods=['GET', 'POST'])
@admin_required
def uploadVotersList():
    inFile = request.files['filename']
    inFile_name = inFile.filename
    if not inFile_name:
        flash(('No file updated'), 'error')
    else:
        inFile.save(os.path.join(app.config['DB_DIR'], inFile_name))
        setConfig('VOTERS_LIST', inFile_name)
        manageDB.updateVoters(voters_file=os.path.join(app.config['DB_DIR'],
                              getConfig('VOTERS_LIST')))
        flash(('New list of voters correcly uploaded'), 'success')
        flash(('You changed the list of voters so you probably want to reset the databases'), 'error')  # noqa
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
