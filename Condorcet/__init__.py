from flask import Flask, render_template, request, redirect, session
from flask_sso import SSO
import os

choices = ['Up', 'Down', 'Charm', 'Strange', 'Top','Beauty']

poll_data = {
    'question' : 'Order the quarks in the order you prefer them',
    'fields' : choices,
    'num_choices' : [str(i) for i in range(1,len(choices)+1)],
    'retry_str' : '',
    }

alphabet = [i for i in 'abcdefghi']
name2letter = dict((key,val) for key,val in zip(choices,alphabet))
letter2name = dict((key,val) for key,val in zip(alphabet,choices))

def getStrOrder(choice_made):
    return ''.join([name2letter[choice] for choice in choice_made])

def getListChoice(vote):
    return [letter2name[letter] for letter in vote]

#def create_app():
app = Flask(__name__)

import manageDB
from verifyAuthors import isAuthor
import elections

# Add a secret key for encrypting session information
app.secret_key = 'cH\xc5\xd9\xd2\xc4,^\x8c\x9f3S\x94Y\xe5\xc7!\x06>A'

# Map SSO attributes from ADFS to session keys under session['user']
SSO_ATTRIBUTE_MAP = {
    'ADFS_LOGIN': (True, 'username'),
    'ADFS_FULLNAME': (True, 'fullname'),
    'ADFS_PERSONID': (True, 'personid'),
    'ADFS_DEPARTMENT': (True, 'department'),
    'ADFS_EMAIL': (True, 'email'),
    'ADFS_GROUP': (True, 'group'),  
    }
app.config.setdefault('SSO_ATTRIBUTE_MAP', SSO_ATTRIBUTE_MAP)
app.config.setdefault('SSO_LOGIN_URL', '/login')
ext = SSO(app=app)


@ext.login_handler
def login(user_info):
    session['user'] = user_info
    return redirect('/') 

@app.route('/')
def root():
    if 'user' in session:
        fullname = session['user']['fullname']
        if isAuthor(fullname):
            poll_data['Greetings'] = "Welcome {name}! ".format(name=session['user']['fullname'])
            username = session['user']['username']
            if manageDB.isInDB(username):
                vote = manageDB.getVote(username)
                poll_data['Greetings'] += 'It seems that you have already voted and your preference was '+', '.join(getListChoice(vote))+'. If you want to modify your vote fill the form again.'
            else:
                poll_data['Greetings'] +='To vote fill the form below, select only one element per row and column.'
            return render_template('poll.html', data=poll_data)
        else:
            return 'It would seems that you are not an LHCb author hence you are not eligible to vote for the Physics coordinator, in case you think this is a mistake send an email to ...'
    else:
        poll_data['Greetings'] = 'Pacco'
        return render_template('first.html')#'Sorry you did not succesfully log in' 



@app.route('/poll')
def result():
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
                manageDB.modifyVote(username, vote)
            else:
                manageDB.addVote(username, vote)
            # Prepare page with results
            preferences = manageDB.getPreferences()
            winners = getListChoice(elections.getWinner(preferences, [i for cont,i in enumerate(alphabet) if cont< len(choices)]))
            result_data = dict(numCandidates=len(choices))
            result_data['winner_str'] = ('The winner is' if len(winners)==1 else 'The winners are')+' '+', '.join(winners)
            result_data['table_DB'] = [[i[0]]+getListChoice(i[1]) for i in manageDB.getVotes()]
            #return "{0} {1}".format(result_data['winner_str'],result_data['table_DB'])
            return render_template('results.html', data=result_data)
        else:
            poll_data['retry_str'] = 'You must rank all candidates and two element cannot share the same position, try again'
        return redirect('/')
    else: # In theory this case should never happen
        return redirect('/')

#return app
    
def wsgi(*args, **kwargs):
    return app(*args, **kwargs)
 
