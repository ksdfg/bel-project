from json import loads

from flask import render_template, redirect, url_for, request, session
from requests import get, post

from api import app

app.template_folder = r'K:\bel-project\web_app\templates'
app.static_folder = r'K:\bel-project\web_app\static'
app.secret_key = 'IB6TBIUKYBGF76VD'

url = "http://localhost:5000/"


@app.route('/')
def homepage():
    if 'username' not in session:
        return redirect(url_for('login_page'), 307)
    data = loads(get(url=url+'api/retrieve/homepage-data', data=dict(session)).text)
    return render_template(
        'homepage.html',
        **session,
        **data
    )


@app.route('/login')
def login_page():
    if 'username' in session:
        return render_template('login.html', username=session['username'])
    return render_template('login.html')


@app.route('/login/submit', methods=['POST'])
def login_submit():
    response = loads(post(url=url + "api/login", data=dict(request.form)).text)
    if response['result'] == 'true':
        session['username'] = request.form['username']
        session['role'] = response['role']
        return redirect(url_for('homepage'))
    return render_template('login.html', error="Incorrect Password", username=request.form['name'])


@app.route('/register')
def register_page():
    return render_template('register.html', role=request.args.get('role'))


@app.route('/register/submit', methods=["POST"])
def register_submit():
    if request.form['password'] != request.form['confirm password']:
        return render_template("register.html", **request.form, error="passwords don't match dummo, try again")
    res = post(url + "api/register", data=dict(request.form)).text
    if res == 'done':
        return redirect(url_for('login_page'))
    else:
        return render_template('register.html', **request.form, error=res)
