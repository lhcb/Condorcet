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


def getStrOrder(choice_made):
    alphabet = [i for i in 'abcdefghi']
    dict_choices = dict((key,val) for key,val in zip(choices,alphabet))  #{key:val for key,val in zip(choices,alphabet)}
    return ''.join([dict_choices[choice] for choice in choice_made])

def create_app():
    app = Flask(__name__)

    # Add a secret key for encrypting session information
    app.secret_key = 'cH\xc5\xd9\xd2\xc4,^\x8c\x9f3S\x94Y\xe5\xc7!\x06>A'
    
    # Map SSO attributes from ADFS to session keys under session['user']
    SSO_ATTRIBUTE_MAP = {
        'ADFS_LOGIN': (True, 'username'),
        'ADFS_FULLNAME': (True, 'fullname'),
        'ADFS_PERSONID': (True, 'personid'),
        'ADFS_DEPARTMENT': (True, 'department'),
        'ADFS_EMAIL': (True, 'email')
        # There are other attributes available
        # Inspect the argument passed to the login_handler to see more
        # 'ADFS_AUTHLEVEL': (False, 'authlevel'),
        # 'ADFS_GROUP': (True, 'group'),
        # 'ADFS_ROLE': (False, 'role'),
        # 'ADFS_IDENTITYCLASS': (False, 'external'),
        # 'HTTP_SHIB_AUTHENTICATION_METHOD': (False, 'authmethod'),
        }
    app.config.setdefault('SSO_ATTRIBUTE_MAP', SSO_ATTRIBUTE_MAP)
        
    # This attaches the *flask_sso* login handler to the SSO_LOGIN_URL,
    # which essentially maps the SSO attributes to a dictionary and
    # calls *our* login_handler, passing the attribute dictionary
    ext = SSO(app=app)

    @ext.login_handler
    def login(user_info):
        session['user'] = user_info
        return redirect('/') 

   
    @app.route('/')
    def root():
        if 'user' in session:
            poll_data['Greetings'] = "Welcome {name}".format(name=session['user']['fullname'])
        else: poll_data['Greetings'] = 'Pacco'
        # return session['user']['ADFS_FULLNAME']
        return render_template('poll.html', data=poll_data)

    @app.route('/poll')
    def result():
        order = []
        for num in [str(i) for i in range(1,len(choices)+1)]:
            order.append(request.args.get(num))
        order_str = getStrOrder(order)
        if len(set(order_str)) == len(choices):
            return order_str
        else:
            poll_data['retry_str'] = 'You must rank all candidates and two element cannot share the same position, try again'
        return redirect('/')

    return app
    
    
def wsgi(*args, **kwargs):
    return create_app()(*args, **kwargs)
 
