from flask import Flask, render_template, request, redirect
import flask as fk
import os
app = Flask(__name__)

choices = ['Up', 'Down', 'Charm', 'Strange', 'Top','Beauty']


poll_data = {
'question' : 'Order the quarks as you prefer them',
'fields' : choices,
'num_choices' : [str(i) for i in range(1,len(choices)+1)],
'retry_str' : '',
}

def getStrOrder(choice_made):
    alphabet = [i for i in 'abcdefghi']
    dict_choices = {key:val for key,val in zip(choices,alphabet)}
    return ''.join([dict_choices[choice] for choice in choice_made])

@app.route('/')
def root():
    return render_template('poll.html', data=poll_data)

@app.route('/poll')
def result():
    order = []
    for num in [str(i) for i in range(1,len(choices)+1)]:
        order.append(request.args.get(num))
    order_str = getStrOrder(order)
    if len(set(order_str)) == len(order_str):
        return order_str
    else:
        poll_data['retry_str'] = 'Two element cannot share the same position, try again'
        return redirect('/')
    
    

 
