from flask import Flask, render_template, request, redirect, session, flash
import os, sys, random

choices = ['Up', 'Down', 'Charm', 'Strange', 'Top','Beauty']

alphabet = [i for i in 'abcdefghi']
name2letter = dict((key,val) for key,val in zip(choices,alphabet))
letter2name = dict((key,val) for key,val in zip(alphabet,choices))

def getStrOrder(choice_made):
    return ''.join([name2letter[choice] for choice in choice_made])

def getListChoice(vote):
    return [letter2name[letter] for letter in vote]

app = Flask(__name__)
app.config['DEBUG'] = __name__ == '__main__'
#app.config['ROOT'] = '/' if app.config['DEBUG'] else '/gdujany/Condorcet'
app.config['ROOT'] = '/' if __name__ == '__main__' else '/gdujany/Condorcet'
#app.config['APPLICATION_ROOT'] = None if __name__ == '__main__' else '/gdujany/Condorcet' # not sure yet what it does, it may be usefull

# Add a secret key for encrypting session information
app.secret_key = 'cH\xc5\xd9\xd2\xc4,^\x8c\x9f3S\x94Y\xe5\xc7!\x06>A'

sys.path.append(os.getcwd())
import manageDB
from verifyAuthors import isAuthor
import elections

@app.before_request
def set_user():
    # TODO (AP): check that the user is on the author list, else redirect, (GD) done partially: still miss fancy page
    if app.config['DEBUG']:
        session['user'] = {
            'username': 'gdujany',
            'fullname': 'Giulio Dujany'
        }
    else:
        session['user'] = {
            'username': request.environ['ADFS_LOGIN'],
            'fullname': ' '.join([
                request.environ['ADFS_FIRSTNAME'], request.environ['ADFS_LASTNAME']
            ])
        }
    if  not isAuthor(session['user']['fullname']):
        return 'It would seems that you are not an LHCb author hence you are not eligible to vote for the Physics coordinator, in case you think this is a mistake send an email to ...'

def build_path(path=''):
    return os.path.join(app.config['ROOT'], path)

poll_data = {
    'question' : 'Order the quarks in the order you prefer them',
    'fields' : choices,
    'num_choices' : [str(i) for i in range(1,len(choices)+1)],
    'poll_address' : build_path('poll'),
    }

@app.route(build_path())
@app.route('/')
def root():
    if 'user' in session:
        poll_data['Greetings'] = "Welcome {name}! ".format(name=session['user']['fullname'])
        username = session['user']['username']
        if manageDB.isInDB(username):
            vote = manageDB.getVote(username)
            poll_data['Greetings'] += 'It seems that you have already voted and your preference was '+', '.join(getListChoice(vote))+'. If you want to modify your vote fill the form again.'
        else:
            poll_data['Greetings'] +='To vote fill the form below, select only one element per row and column.'
        choices_copy = choices[:]
        # FIXME: like this it shuffle fine but when I reload the page the votes already set change!
        random.shuffle(choices_copy)
        poll_data['fields'] = choices_copy
        return render_template('poll.html', data=poll_data)

    else: # now not possible any more probably!
        poll_data['Greetings'] = 'Pacco'
        return render_template('first.html')#'Sorry you did not succesfully log in' 

@app.route(build_path('/poll'))
@app.route('/poll')
def savePoll():
    #return str(request.args)
    if 'user' in session:
        order = []
        if len(request.args) == len(choices):
            for num in [str(i) for i in range(1,len(choices)+1)]:
                order.append(request.args.get(num))
            vote = getStrOrder(order)
        else: vote = '' # so that fails next if
        if len(set(vote)) == len(choices):
            username = session['user']['username']
            if manageDB.isInDB(username):
                secret_key = manageDB.modifyVote(username, vote)
            else:
                secret_key = manageDB.addVote(username, vote)
            congrats_data = dict(secret_key=secret_key)
            return render_template('congrats.html', data=congrats_data)
        else:
            flash('You must rank all candidates and two element cannot share the same position, try again', 'error')
        return redirect(build_path())
    else: 
        return redirect(build_path())

@app.route(build_path('/results'))
def result():
    if 'user' in session:
        order = []
        # Prepare page with results
        preferences = manageDB.getPreferences()
        winners = getListChoice(elections.getWinner(preferences, [i for cont,i in enumerate(alphabet) if cont< len(choices)]))
        result_data = dict(numCandidates=len(choices))
        result_data['winner_str'] = ('The winner is' if len(winners)==1 else 'The winners are')+' '+', '.join(winners)
        result_data['table_DB'] = [[i[0],i[1]]+getListChoice(i[2]) for i in manageDB.getVotes()]
        return render_template('results.html', data=result_data)
    else: # In theory this case should never happen
        return redirect(build_path())
 
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
