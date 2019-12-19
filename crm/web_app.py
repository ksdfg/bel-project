from json import loads
from urllib.parse import urlparse, urljoin

from flask import render_template, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from jinja2.exceptions import TemplateNotFound
from requests import get, post

from crm import app, login_manager, authorized, dbcursor

url = "http://localhost/"  # url at which app is deployed


# set url at which app is deployed
def set_url(ip):
    global url
    url = "http://" + ip + "/"


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# render login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = login_manager.request_callback(request)
        if user is not None:
            # login the user, then move on to destination
            login_user(user)
            print(request.form['username'] + " logged in!")
            dest = request.args.get("next")
            if not is_safe_url(dest):
                return abort(400)
            return redirect(dest or url_for("homepage"))

        # in case there was an error while logging in
        return render_template('login.html', username=request.form['username'], error="Check Credentials and try again")

    if current_user.is_authenticated:  # just cuz i saw some other sites do this...
        return render_template('login.html', username=current_user.username)
    return render_template('login.html')


# logout a user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


# render register page
@app.route('/register')
def register_page():
    if request.method == 'POST':
        res = post(url + "api/add/user", data=dict(request.form)).text
        if res == 'done':
            return redirect(url_for('login'))
        return render_template('register.html', **request.form, error=res)  # in case of errors
    return render_template('register.html', role=request.args.get('role'), current_user=current_user)


# register new user upon clicking register button in register.html (wow, so much register)
@app.route('/register/submit', methods=["POST"])
def register_submit():
    res = post(url + "api/add/user", data=dict(request.form)).text
    if res == 'done':
        return redirect(url_for('login'))
    return render_template('register.html', **request.form, error=res)  # in case of errors


# render page to add stuff to table
@app.route('/add/<table>')
@login_required
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
@login_required
@authorized(['call_center'])
def add_customer_submit():
    response = post(url + 'api/add/customer', data=dict(request.form)).text
    if response == 'ok':
        return render_template('add_customer.html', success="Customer Added")
    else:
        return render_template('add_customer.html', error=response, **request.form)


# add machine to db
@app.route('/add/machine/submit', methods=['POST'])
@login_required
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
@login_required
@authorized(['call_center'])
def edit_table_value_page(table):
    if table == 'machine':
        return render_template('edit_machine.html',
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
@login_required
def view_table(table):
    response = loads(get(url + 'api/retrieve', params={'table': table, 'fields': '*'}).text)
    return render_template('view.html',
                           fields=response['fields'],
                           values=response['values'],
                           table=table)


# view data of machines
@app.route('/view/machine')
@login_required
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


# render homepage
@app.route('/')
@login_required
def homepage():
    data = dict()

    if current_user.role == 'bel_mgr' or current_user.role == 'call_center':
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

    elif current_user.role == 'engineer':
        # get all open complaints assigned to the engineer
        dbcursor.execute(f"""
            Select t.Machine, c.Name, m.Location, t.MadeOn
            from (complaint t join engineer e on t.Engineer = e.ID) join
            (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where e.username = '{current_user.username}' and t.Status = 'Open'
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['complaints'] = res

        # get all machines that are allocated to engineer which are due for pm
        dbcursor.execute(f"""
        select m.Location, next_pm(m.SlNo)
        from machine m join engineer e on m.AllocatedTo = e.ID
        where e.username = '{current_user.username}' and
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
            where e.username = '{current_user.username}'
        """)
        res = dbcursor.fetchall()
        data['materials'] = res

        # get all scrap materials that the regional center has
        dbcursor.execute(f"""
            Select m.Desc, em.Qty
            from material m join (eng_scrap em join engineer e on em.Engineer = e.ID) on m.PartNo = em.PartNo
            where e.username = '{current_user.username}'
        """)
        res = dbcursor.fetchall()
        data['scrap'] = res

    elif current_user.role == 'reg_mgr':
        # get all open complaints assigned to all engineers in the region
        dbcursor.execute(f"""
            Select t.Machine, c.Name, m.Location, e.Name, t.MadeOn
            from (complaint t join (engineer e join reg_center rc on e.Region = rc.ID) on t.Engineer = e.ID) join
                (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where rc.username = '{current_user.username}' and t.Status = 'Open' and t.Priority = 'High'
        """)
        res = list(map(list, dbcursor.fetchall()))  # convert tuples to lists
        for i in res:
            i[-1] = str(i[-1])  # convert datetime to string, since datetime is not serializable
        data['complaints'] = res

        # get all machines that are to be installed assigned to the region
        dbcursor.execute(f"""
            Select m.SlNo, c.Name, m.Location
            from (machine m join customer c on m.CustID = c.ID) join reg_center rc on m.Region = rc.ID
            where rc.username = '{current_user.username}' and m.Status = 'Installation Pending'
        """)
        data['installations'] = dbcursor.fetchall()

        # get all machines that are allocated to all engineers in the region which are due for pm
        dbcursor.execute(f"""
        select m.Location, e.Name, next_pm(m.SlNo)
        from machine m join (engineer e join reg_center rc on e.Region = rc.ID) on m.AllocatedTo = e.ID
        where rc.username = '{current_user.username}' and
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
            where rc.username = '{current_user.username}'
        """)
        res = dbcursor.fetchall()
        data['materials'] = res

        # get all scrap materials that the regional center has
        dbcursor.execute(f"""
            Select m.Desc, rm.Qty
            from material m join (reg_scrap rm join reg_center rc on rm.Region = rc.ID) on m.PartNo = rm.PartNo
            where rc.username = '{current_user.username}'
        """)
        res = dbcursor.fetchall()
        data['scrap'] = res

    return render_template(
        'homepage.html',
        **current_user.__dict__,
        **data
    )
