from json import dumps

from flask import Flask, request
from mysql.connector import connect, IntegrityError

# create the flask app
app = Flask('bel crm')

# database object, connects to mysql
db = connect(
    host="localhost",
    user="belmaster",
    passwd="master",
    database="beldb"
)
dbcursor = db.cursor()  # cursor that'll allow us to execute queries


# post request to login
@app.route('/api/login', methods=["POST"])
def validate_login():
    try:
        dbcursor.execute(
            "Select password, role from user where username = '{}'".format(request.form['username']))  # get password
        res = dbcursor.fetchone()
        if request.form['password'] in res:
            return dumps({'result': 'true', 'role': res[1]})
        else:
            return 'false'
    except Exception as e:
        print(e)
        return str(e)


# post request to register a new user
@app.route('/api/register', methods=["POST"])
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
            dbcursor.execute("Insert into reg_center values (%s, %s)", (request.form['id'], request.form['address']))
        elif request.form['role'] == 'bel_mgr':
            pass
        elif request.form['role'] == 'call_centre':
            pass
        else:
            return "What role is this?"

        db.commit()  # change ought to be permanent
        return 'done'
    except Exception as e:
        print('entity', request.form['role'], e.__class__)
        return str(e)


@app.route('/api/retrieve/homepage-data', methods=['GET'])
def homepage_date():
    data = dict()

    if request.form['role'] == 'bel_mgr':
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
        dbcursor.execute(
            "Select t.Machine, c.Name, m.Location, e.Name, t.MadeOn "
            "from (complaint t join engineer e on t.Engineer = e.ID) join "
            "(machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo "
            "where priority = 'High'"
        )
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
        dbcursor.execute("select count(*) from machine "
                         "where machine.AMCExp < date(now()) and machine.WarrantyExp < date(now());")  # in warranty
        res = dbcursor.fetchone()
        data['amc_warranty_out'] = res[0]

    return dumps(data)
