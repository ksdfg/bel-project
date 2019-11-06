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
        select m.Location, DATE_ADD(pm.Date, interval 3 month )
        from pm join machine m on pm.Machine = m.SlNo join engineer e on pm.Engineer = e.ID
        where e.Username = '{request.form['username']}' and
            year(DATE_ADD(pm.Date, interval 3 month )) = year(now()) and
            month(DATE_ADD(pm.Date, interval 3 month )) = month(now()) and
            (DATE_ADD(pm.Date, interval 3 month ) <= m.WarrantyExp or DATE_ADD(pm.Date, interval 3 month ) < m.AMCExp);
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

        # get all machines that are allocated to all engineers in the region which are due for pm
        dbcursor.execute(f"""
        select m.Location, e.Name, DATE_ADD(pm.Date, interval 3 month )
        from pm join machine m on pm.Machine = m.SlNo join 
            (engineer e join reg_center rc on e.Region = rc.ID) on pm.Engineer = e.ID
        where rc.username = '{request.form['username']}' and
            year(DATE_ADD(pm.Date, interval 3 month )) = year(now()) and
            month(DATE_ADD(pm.Date, interval 3 month )) = month(now()) and
            (DATE_ADD(pm.Date, interval 3 month ) <= m.WarrantyExp or DATE_ADD(pm.Date, interval 3 month ) < m.AMCExp);
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
