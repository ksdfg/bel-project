from functools import wraps
from json import loads
from os import getcwd

from flask import render_template, redirect, url_for, request, session
from jinja2.exceptions import TemplateNotFound
from requests import get, post

from api import app

# set app variables for web_app
app.template_folder = getcwd() + r'\web_app\templates'
app.static_folder = getcwd() + r'\web_app\static'
app.secret_key = 'IB6TBIUKYBGF76VD'

url = "http://localhost/"  # url at which app is deployed


# set url at which app is deployed
def set_url(ip):
    global url
    url = "http://" + ip + "/"


def authorized(roles):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if 'username' in session and session['role'] in roles:
                return func(*args, **kwargs)
            else:
                return render_template('no_access.html')

        return inner

    return outer


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


# render page to add stuff to table
@app.route('/add/<table>')
@authorized(['call_center'])
def add_table_value_page(table):
    try:
        if table == 'machine':
            return render_template('add_machine.html',
                                   customers=loads(get(url + 'api/retrieve',
                                                       params={'fields': ['ID', 'Name'], 'table': 'customer'}).text)[
                                       'values'],
                                   regions=loads(get(url + 'api/retrieve',
                                                     params={'fields': ['ID', 'Name'], 'table': 'reg_center'}).text)[
                                       'values'])
        else:
            return render_template('add_' + table + '.html')
    except TemplateNotFound:
        return render_template('no_access.html')


# add customer to db
@app.route('/add/customer/submit', methods=['POST'])
@authorized(['call_center'])
def add_customer_submit():
    response = post(url + 'api/add/customer', data=dict(request.form)).text
    if response == 'ok':
        return render_template('add_customer.html', success="Customer Added")
    else:
        return render_template('add_customer.html', error=response, **request.form)


# add machine to db
@app.route('/add/machine/submit', methods=['POST'])
@authorized(['call_center'])
def add_machine_submit():
    response = post(url + 'api/add/machine', data=dict(request.form)).text
    if response == 'ok':
        return render_template('add_machine.html',
                               customers=loads(get(url + 'api/retrieve',
                                                   params={'fields': ['ID', 'Name'], 'table': 'customer'}).text)[
                                   'values'],
                               regions=loads(get(url + 'api/retrieve',
                                                 params={'table': 'reg_center', 'fields': ['ID', 'Name']}).text)[
                                   'values'],
                               success="Machine Added")
    else:
        return render_template('add_machine.html',
                               customers=loads(get(url + 'api/retrieve',
                                                   params={'fields': ['ID', 'Name'], 'table': 'customer'}).text)[
                                   'values'],
                               regions=loads(get(url + 'api/retrieve',
                                                 params={'table': 'reg_center', 'fields': ['ID', 'Name']}).text)[
                                   'values'],
                               error=response, **request.form)


# render edit details page
@app.route('/edit/<table>')
@authorized(['call_center'])
def edit_table_value_page(table):
    if table == 'machine':
        return render_template('edit_machine.html', success='test',
                               customers=loads(get(url + 'api/retrieve',
                                                   params={'fields': ['ID', 'Name'], 'table': 'customer'}).text)[
                                   'values'],
                               regions=loads(get(url + 'api/retrieve',
                                                 params={'table': 'reg_center', 'fields': ['ID', 'Name']}).text)[
                                   'values'],
                               engineers=loads(get(url + 'api/retrieve',
                                                   params={'table': 'engineer', 'fields': ['ID', 'Name']}).text)[
                                   'values'])
    else:
        return render_template('edit_' + table + '.html')


# edit customer details in db
@app.route('/edit/<table>/submit', methods=['POST'])
@authorized(['call_center'])
def edit_customer_submit(table):
    payload = dict()
    for key in request.form.keys():
        if len(request.form[key]) > 0:
            payload[key] = request.form[key]
    response = post(url + 'api/edit/<table>', data=payload).text
    if response == 'ok':
        return render_template('edit_' + table + '.html', success=table.capitalize() + " Edited")
    else:
        return render_template('edit_' + table + '.html', error=response, **request.form)


# view data of some table
@app.route('/view/<table>')
def view_table(table):
    response = loads(get(url + 'api/retrieve', params={'table': table, 'fields': '*'}).text)
    return render_template('view.html',
                           fields=response['fields'],
                           values=response['values'],
                           table=table)


# view data of machines
@app.route('/view/machine')
def view_machine():
    params = {}
    fields = ['SlNo', 'Model', 'Status', 'Location', 'Region', 'ContactPerson', 'ContactNo',
              'ContactEmail', 'InstallDate', 'AllocatedTo', 'WarrantyExp', 'AMCStart', 'AMCExp']
    params['fields'] = list(map(lambda x: 'm.' + x, fields))
    params['fields'].insert(2, 'c.Name')
    fields.insert(2, 'Customer')
    params['fields'][-4] = 'e.Name'
    params['table'] = '(machine m join engineer e on m.AllocatedTo = e.ID) join customer c on m.CustID = c.ID'
    return render_template('view.html',
                           fields=fields,
                           values=loads(get(url + 'api/retrieve', params=params).text)['values'],
                           table='machine')
