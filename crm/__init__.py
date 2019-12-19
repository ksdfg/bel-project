from functools import wraps
from json import dumps, load
from random import choice
from re import match
from string import ascii_letters, digits
from traceback import print_exc

from flask import Flask, request, render_template
from flask_login import LoginManager, current_user, login_required
from mysql.connector import connect, IntegrityError

from crm.user import User

# create the flask app
app = Flask(__name__)
app.secret_key = ''.join([choice(ascii_letters + digits) for _ in range(32)])

# create and initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# database object, connects to mysql
with open('config.json') as json_file:
    config = load(json_file)
db = connect(**config['database'])
dbcursor = db.cursor()  # cursor that'll allow us to execute queries


# load a user given their username
@login_manager.user_loader
def load_user(username):
    dbcursor.execute(f"Select role from user where username = '{username}' and authorized = true ")  # get password
    res = dbcursor.fetchone()
    if res is None:
        return None
    return User(username=username, role=res[0])


# load a user from request
@login_manager.request_loader
def load_user_from_request(request):
    get = request.form.get if request.method == 'POST' else request.args.get
    try:
        # get password
        dbcursor.execute(f"""
            Select password, role
            from user
            where username = '{get('username')}' and authorized = true
        """)
        res = dbcursor.fetchone()
        if res is not None and get('password') in res:
            return User(username=get('username'), role=res[1])
        else:
            return None
    except Exception as e:
        print(e)
        print_exc()
        return None


# wrapper to check if currently logged in user is authorized for some function
# remember to only apply this to functions which already have login_required applied
def authorized(roles):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if current_user.role in roles:
                return func(*args, **kwargs)
            else:
                return render_template('no_access.html')  # marquee ftw

        return inner

    return outer


# post request to register a new user
@app.route('/api/add/user', methods=["POST"])
def register():
    # if password is not same in both fields
    if request.form['password'] != request.form['confirm password']:
        return "passwords don't match dummo, try again"

    # first register user
    try:
        dbcursor.execute("Insert into user values (%s, %s, %s)", (request.form['username'], request.form['password'],
                                                                  request.form['role']))
    except IntegrityError as e:
        print(e)
        return 'Username already taken'
    except Exception as e:
        print('user', e.__class__)
        return str(e)

    # now add the overall entity
    try:
        # add the respective entity
        if request.form['role'] == 'engineer':
            dbcursor.execute("Insert into engineer(Name, ContactNo, email, Region, Address, Username) values "
                             "(%s, %s, %s, %s, %s, %s)",
                             (
                                 request.form['name'], int(request.form['contact']), request.form['email'],
                                 request.form['region'], request.form['address'], request.form['username']
                             ))
        elif request.form['role'] == 'reg_mgr':
            dbcursor.execute("Insert into reg_center values (%s, %s, %s)",
                             (request.form['id'], request.form['address'], request.form['username']))
        elif request.form['role'] == 'bel_mgr':
            pass
        elif request.form['role'] == 'call_center':
            pass
        else:
            return "What role is this?"

        db.commit()  # change ought to be permanent
        return 'done'
    except Exception as e:
        print('entity', request.form['role'], e.__class__)
        return str(e)


# fire and query and make sure that date and datetime results are converted to strings
def get_data(query):
    dbcursor.execute(query)
    res = list(map(lambda x: list(x), dbcursor.fetchall()))

    for i in range(len(res)):
        for j in range(len(res[i])):
            if str(type(res[i][j])) == "<class 'datetime.date'>" or \
                    str(type(res[i][j])) == "<class 'datetime.datetime'>":
                res[i][j] = str(res[i][j])

    return res


# api call to retrieve data from db
@app.route('/api/retrieve', methods=['GET'])
@login_required
def get_data_api():
    # get values in table
    data = {'values': get_data(f"select {', '.join(request.args.getlist('fields'))} from {request.args.get('table')}")}

    # get all fields
    if len(request.args.get('table').split()) == 1:
        dbcursor.execute(f"desc {request.args.get('table')}")
        data['fields'] = list(map(lambda x: x[0], dbcursor.fetchall()))

    return dumps(data)


# to make sure values to be inserted in db are properly formatted
def parameterize(params: list):
    for i in range(len(params)):
        if len(params[i]) == 0:  # empty field, set to null
            params[i] = None
        elif match(r'\D', params[i]):  # non integer field, surround in ""
            params[i] = f'"{params[i]}"'
    return params


# add an entry in the system db
@app.route('/api/add/<table>', methods=['POST'])
@login_required
def add_to_table(table):
    try:
        dbcursor.execute(f"""
        insert into {table}({','.join(request.form.keys())}) values
        ({','.join(parameterize(list(request.form.values())))})
        """)
        db.commit()
        return 'ok'
    except IntegrityError:
        return f'{str(table).capitalize()} Already Exists'
    except Exception as e:
        return str(e)


# edit an entry in the db
@app.route('/api/edit/<table>', methods=['POST'])
@login_required
def edit_row(table):
    try:
        dbcursor.execute(f"""
            update {table}
            set {', '.join(map(lambda x: x + ' = ' + parameterize([request.form[x]])[0], list(request.form.keys())[:-2]))}
            where {request.form['primary_key']} = {parameterize([request.form[request.form['primary_key']]])[0]}
        """)
        db.commit()
        return 'ok'
    except Exception as e:
        return str(e)
