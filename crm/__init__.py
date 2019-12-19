from json import dumps, load
from random import choice
from re import match
from string import ascii_letters, digits

from flask import Flask, request
from mysql.connector import connect, IntegrityError

# create the flask app
app = Flask(__name__)
app.secret_key = ''.join([choice(ascii_letters + digits) for _ in range(32)])

# database object, connects to mysql
with open('config.json') as json_file:
    config = load(json_file)
db = connect(**config['database'])
dbcursor = db.cursor()  # cursor that'll allow us to execute queries


# post request to login
@app.route('/api/login', methods=["POST"])
def validate_login():
    try:
        dbcursor.execute(
            f"Select password, role from user where username = '{request.form['username']}'")  # get password
        res = dbcursor.fetchone()
        if res is None:
            return dumps({'result': "No such Username"})
        elif request.form['password'] in res:  # since fetchone returns tuple
            return dumps({'result': 'true', 'role': res[1]})
        else:
            return dumps({'result': "Wrong Password"})
    except Exception as e:
        print(e)
        return dumps({'result': str(e)})


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


# get request to retrieve data to be displayed on homepage from database
@app.route('/api/retrieve/homepage-data', methods=['GET'])
def homepage_date():
    data = dict()

    if request.form['role'] == 'bel_mgr' or request.form['role'] == 'call_center':
        # get total scrap value
        dbcursor.execute(
            "Select round(sum(m.price * e.Qty), 3) from eng_scrap e join material m on e.PartNo = m.PartNo")
        res = dbcursor.fetchone()
        data['scrap_money'] = res[0]
        dbcursor.execute(
            "Select round(sum(m.price * r.Qty), 3) from reg_scrap r join material m on r.PartNo = m.PartNo")
        res = dbcursor.fetchone()
        data['scrap_money'] += res[0]

        # get high priority complaints
        dbcursor.execute(f"""
            Select t.Machine, c.Name, m.Location, e.Name, t.MadeOn
            from (complaint t join engineer e on t.Engineer = e.ID) join
            (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where t.Priority = 'High' and t.Status = 'Open'
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['complaints'] = res

        # get number of machines under warranty
        dbcursor.execute("select count(*) from machine where machine.WarrantyExp >= date(now());")  # in warranty
        res = dbcursor.fetchone()
        data['warranty_in'] = res[0]
        dbcursor.execute("select count(*) from machine where machine.AMCExp >= date(now());")  # in warranty
        res = dbcursor.fetchone()
        data['amc_in'] = res[0]

        # get number of machines out of amc and warranty
        dbcursor.execute("""
            select count(*) from machine 
            where machine.AMCExp < date(now()) and machine.WarrantyExp < date(now());
        """)  # in warranty
        res = dbcursor.fetchone()
        data['amc_warranty_out'] = res[0]

    elif request.form['role'] == 'engineer':
        # get all open complaints assigned to the engineer
        dbcursor.execute(f"""
            Select t.Machine, c.Name, m.Location, t.MadeOn
            from (complaint t join engineer e on t.Engineer = e.ID) join
            (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where e.username = '{request.form['username']}' and t.Status = 'Open'
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['complaints'] = res

        # get all machines that are allocated to engineer which are due for pm
        dbcursor.execute(f"""
        select m.Location, next_pm(m.SlNo)
        from machine m join engineer e on m.AllocatedTo = e.ID
        where e.username = '{request.form['username']}' and
            (next_pm(m.SlNo) <= m.WarrantyExp or next_pm(m.SlNo) between m.AMCStart and m.AMCExp) and 
            next_pm(m.SlNo) >= date(now()) and
            year(next_pm(m.SlNo)) = year(now()) and month(next_pm(m.SlNo)) = month(now());
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['pm'] = res

        # get all materials that the engineer has
        dbcursor.execute(f"""
            Select m.Desc, em.Qty
            from material m join (eng_material em join engineer e on em.Engineer = e.ID) on m.PartNo = em.PartNo
            where e.username = '{request.form['username']}'
        """)
        res = dbcursor.fetchall()
        data['materials'] = res

        # get all scrap materials that the regional center has
        dbcursor.execute(f"""
            Select m.Desc, em.Qty
            from material m join (eng_scrap em join engineer e on em.Engineer = e.ID) on m.PartNo = em.PartNo
            where e.username = '{request.form['username']}'
        """)
        res = dbcursor.fetchall()
        data['scrap'] = res

    elif request.form['role'] == 'reg_mgr':
        # get all open complaints assigned to all engineers in the region
        dbcursor.execute(f"""
            Select t.Machine, c.Name, m.Location, e.Name, t.MadeOn
            from (complaint t join (engineer e join reg_center rc on e.Region = rc.ID) on t.Engineer = e.ID) join
                (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where rc.username = '{request.form['username']}' and t.Status = 'Open' and t.Priority = 'High'
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['complaints'] = res

        # get all machines that are to be installed assigned to the region
        dbcursor.execute(f"""
            Select m.SlNo, c.Name, m.Location
            from (machine m join customer c on m.CustID = c.ID) join reg_center rc on m.Region = rc.ID
            where rc.username = '{request.form['username']}' and m.Status = 'Installation Pending'
        """)
        data['installations'] = dbcursor.fetchall()

        # get all machines that are allocated to all engineers in the region which are due for pm
        dbcursor.execute(f"""
        select m.Location, e.Name, next_pm(m.SlNo)
        from machine m join (engineer e join reg_center rc on e.Region = rc.ID) on m.AllocatedTo = e.ID
        where rc.username = '{request.form['username']}' and
            (next_pm(m.SlNo) <= m.WarrantyExp or next_pm(m.SlNo) between m.AMCStart and m.AMCExp) and 
            next_pm(m.SlNo) >= date(now()) and
            year(next_pm(m.SlNo)) = year(now()) and month(next_pm(m.SlNo)) = month(now());
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['pm'] = res

        # get all materials that the regional center has
        dbcursor.execute(f"""
            Select m.Desc, rm.Qty
            from material m join (reg_materials rm join reg_center rc on rm.Region = rc.ID) on m.PartNo = rm.PartNo
            where rc.username = '{request.form['username']}'
        """)
        res = dbcursor.fetchall()
        data['materials'] = res

        # get all scrap materials that the regional center has
        dbcursor.execute(f"""
            Select m.Desc, rm.Qty
            from material m join (reg_scrap rm join reg_center rc on rm.Region = rc.ID) on m.PartNo = rm.PartNo
            where rc.username = '{request.form['username']}'
        """)
        res = dbcursor.fetchall()
        data['scrap'] = res

    return dumps(data)


# just retrieve data from db
@app.route('/api/retrieve', methods=['GET'])
def get_data():
    data = {}

    # get values in table
    dbcursor.execute(f"select {', '.join(request.args.getlist('fields'))} from {request.args.get('table')}")
    data['values'] = list(map(lambda x: list(x), dbcursor.fetchall()))
    for i in range(len(data['values'])):
        for j in range(len(data['values'][i])):
            if str(type(data['values'][i][j])) == "<class 'datetime.date'>" or \
                    str(type(data['values'][i][j])) == "<class 'datetime.datetime'>":
                data['values'][i][j] = str(data['values'][i][j])

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
