from json import loads
from os import getcwd

from flask import render_template, redirect, url_for, request, session
from requests import get, post

from api import app

# set app variables for web_app
app.template_folder = getcwd() + r'\web_app\templates'
app.static_folder = getcwd() + r'\web_app\static'
app.secret_key = 'IB6TBIUKYBGF76VD'

url = "http://localhost:5000/"  # url at which app is deployed


# render homepage
@app.route('/')
def homepage():
    if 'username' not in session:
        return redirect(url_for('login_page'), 307)  # redirect to login page if user not already logged in
    data = loads(get(url=url + 'api/retrieve/homepage-data', data=dict(session)).text)  # get data to be displayed
    return render_template(
        'homepage.html',
        **session,
        **data
    )


# render login page
@app.route('/login')
def login_page():
    if 'username' in session:  # just cuz i saw some other sites do this...
        return render_template('login.html', username=session['username'])
    return render_template('login.html')


# login user upon clicking login button in login.html
@app.route('/login/submit', methods=['POST'])
def login_submit():
    response = loads(post(url=url + "api/login", data=dict(request.form)).text)  # login user
    if response['result'] == 'true':
        # save the username and role in session, then redirect to homepage
        session['username'] = request.form['username']
        session['role'] = response['role']
        print(request.form['username'] + " logged in!")
        return redirect(url_for('homepage'))
    # in case there was an error while logging in
    return render_template('login.html', username=request.form['username'], error=response['result'])


# logout a user
@app.route('/logout')
def logout():
    last_user = ""
    if 'username' in session.keys():
        last_user = session['username']
        del session['username']
        del session['role']
    return render_template('login.html', username=last_user)


# render register page
@app.route('/register')
def register_page():
    return render_template('register.html', role=request.args.get('role'), session=session)


# register new user upon clicking register button in register.html (wow, so much register)
@app.route('/register/submit', methods=["POST"])
def register_submit():
    res = post(url + "api/add/user", data=dict(request.form)).text
    if res == 'done':
        return redirect(url_for('login_page'))
    return render_template('register.html', **request.form, error=res)  # in case of errors


# render add machine page
@app.route('/add-machine')
def add_machine_page():
    return render_template('add_machine.html', customers=loads(get(url + 'api/retrieve/customers').text))


# add machine to db
@app.route('/add-machine/submit', methods=['POST'])
def add_machine_submit():
    response = post(url + 'api/add/machine', data=dict(request.form)).text
    if response == 'ok':
        return render_template('add_machine.html', customers=loads(get(url + 'api/retrieve/customers').text),
                               success="Machine Added")
    else:
        return render_template('add_machine.html', customers=loads(get(url + 'api/retrieve/customers').text),
                               error=response, **request.form)


# render add customer page
@app.route('/add-customer')
def add_customer_page():
    return render_template('add_customer.html')


# add customer to db
@app.route('/add-customer/submit', methods=['POST'])
def add_customer_submit():
    response = post(url + 'api/add/customer', data=dict(request.form)).text
    if response == 'ok':
        return render_template('add_customer.html', success="Customer Added")
    else:
        return render_template('add_customer.html', error=response, **request.form)
