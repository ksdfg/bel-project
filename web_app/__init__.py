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


@app.route('/')
def homepage():
    if 'username' not in session:
        return redirect(url_for('login_page'), 307)  # redirect to login page
    data = loads(get(url=url + 'api/retrieve/homepage-data', data=dict(session)).text)  # get data to be displayed
    return render_template(
        'homepage.html',
        **session,
        **data
    )


@app.route('/login')
def login_page():
    if 'username' in session:
        return render_template('login.html', username=session['username'])  # just cuz i saw some other sites do this...
    return render_template('login.html')


@app.route('/login/submit', methods=['POST'])
def login_submit():
    response = loads(post(url=url + "api/login", data=dict(request.form)).text)  # login user
    print(response)
    if response['result'] == 'true':
        # save the username and role in session, then redirect to homepage
        session['username'] = request.form['username']
        session['role'] = response['role']
        return redirect(url_for('homepage'))
    return render_template('login.html', error=response['result'], username=request.form['name'])


@app.route('/register')
def register_page():
    return render_template('register.html', role=request.args.get('role'))


@app.route('/register/submit', methods=["POST"])
def register_submit():
    res = post(url + "api/register", data=dict(request.form)).text
    if res == 'done':
        return redirect(url_for('login_page'))
    else:
        return render_template('register.html', **request.form, error=res)
