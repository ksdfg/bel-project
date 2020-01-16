from urllib.parse import urlparse, urljoin

from flask import render_template, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from jinja2.exceptions import TemplateNotFound
from requests import get, post

from crm import app, authorized, get_data, bcrypt
from crm.user import User

url = 'http://localhost:8080/'  # url at which app is deployed


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
        # login the user, then move on to destination
        res = get_data(f"""
            select password, role, auth_token 
            from user 
            where username = '{request.form['username']}' and authorized = true
        """)

        if len(res) == 0:  # no such user
            return render_template(current_user=current_user, template_name_or_list='login.html',
                                   username=request.form['username'], error="Incorrect Username")

        if bcrypt.check_password_hash(res[0][0], request.form['password']):
            login_user(User(username=request.form['username'], role=res[0][1], auth_token=res[0][2]))
            print(request.form['username'] + " logged in!")
            dest = request.args.get("next") if request.args.get("next") else url_for('homepage')
            if not is_safe_url(dest):
                return abort(400)
            return redirect(dest)
        else:  # password does not match
            return render_template(current_user=current_user, template_name_or_list='login.html',
                                   username=request.form['username'], error="Incorrect Password")

    if current_user.is_authenticated:  # just cuz i saw some other sites do this...
        return render_template(current_user=current_user, template_name_or_list='login.html',
                               username=current_user.username)
    return render_template(current_user=current_user, template_name_or_list='login.html')


# logout a user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


# register new user upon clicking register button in register.html, or render register page (wow, so much register)
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        res = post(url + "api/add/user", data=dict(request.form)).text
        if res == 'done':
            return redirect(url_for('login', success="User Added!"))
        return render_template(current_user=current_user, template_name_or_list='register.html', **request.form,
                               error=res)  # in case of errors
    return render_template(current_user=current_user, template_name_or_list='register.html',
                           role=request.args.get('role'))


# authorize a login so the id can be used to login
@app.route('/user/authorize', methods=['POST', 'GET'])
@login_required
@authorized(['call_center'])
def authorize_user():
    if request.method == 'POST':
        # api call to edit user table; set authorized = true for given username
        res = post(url + 'api/edit/user',
                   data={'username': request.form['username'], 'authorized': True, 'primary_key': 'username'},
                   auth=(current_user.username, current_user.auth_token)).text
        if res == "ok":  # change happened smoothly
            return render_template(current_user=current_user,
                                   template_name_or_list="authorize.html",
                                   usernames=get(url + 'api/retrieve',
                                                 params={'table': 'user', 'fields': 'username',
                                                         'conditions': "authorized = false"},
                                                 auth=(current_user.username, current_user.auth_token)).json()[
                                       'values'],
                                   success=f"{request.form['username']} authorized for login"
                                   )
        # some error occurred
        return render_template(current_user=current_user,
                               template_name_or_list="authorize.html",
                               usernames=get(url + 'api/retrieve',
                                             params={'table': 'user', 'fields': 'username',
                                                     'conditions': "authorized = false"},
                                             auth=(current_user.username, current_user.auth_token)).json()['values'],
                               error=res
                               )

    # get call - display form
    return render_template(current_user=current_user,
                           template_name_or_list="authorize.html",
                           usernames=get(url + 'api/retrieve',
                                         params={'table': 'user', 'fields': 'username',
                                                 'conditions': "authorized = false"},
                                         auth=(current_user.username, current_user.auth_token)).json()['values']
                           )


# render page to add stuff to table on get; add stuff to db on post
@app.route('/<table>/add', methods=['GET', 'POST'])
@login_required
@authorized(['call_center'])
def add_table_value_page(table):
    try:
        variables = dict()  # dictionary for extra variables to pass to render template
        if table == 'machine':
            variables['customers'] = get(url + 'api/retrieve',
                                         params={'fields': ['ID', 'Name'], 'table': 'customer'},
                                         auth=(current_user.username, current_user.auth_token)).json()['values']
            variables['regions'] = get(url + 'api/retrieve',
                                       params={'fields': ['ID', 'Name'], 'table': 'reg_center'},
                                       auth=(current_user.username, current_user.auth_token)).json()['values']

        if request.method == 'POST':  # post call; api call to add tuple in db
            response = post(url + f'api/add/{table}', data=dict(request.form),
                            auth=(current_user.username, current_user.auth_token)).text
            if response == 'ok':
                return render_template(current_user=current_user, template_name_or_list='add_' + table + '.html',
                                       success=f"{table.capitalize()} Added", **variables)
            else:
                return render_template(current_user=current_user, template_name_or_list='add_' + table + '.html',
                                       error=response, **variables, **request.form)

        return render_template(current_user=current_user, template_name_or_list='add_' + table + '.html',
                               **variables)  # get call; display html form
    except TemplateNotFound:
        return render_template(current_user=current_user, template_name_or_list='no_access.html')


# render edit details page
@app.route('/<table>/edit', methods=['GET', 'POST'])
@login_required
@authorized(['call_center'])
def edit_table_value_page(table):
    try:
        variables = dict()  # dictionary for extra variables to pass to render template
        if table == 'machine':
            variables['customers'] = get(url + 'api/retrieve',
                                         params={'table': 'customer', 'fields': ['ID', 'Name']},
                                         auth=(current_user.username, current_user.auth_token)).json()['values']
            variables['regions'] = get(url + 'api/retrieve',
                                       params={'table': 'reg_center', 'fields': ['ID', 'Name']},
                                       auth=(current_user.username, current_user.auth_token)).json()['values']
            variables['engineers'] = get(url + 'api/retrieve',
                                         params={'table': 'engineer', 'fields': ['ID', 'Name']},
                                         auth=(current_user.username, current_user.auth_token)).json()['values']

        # post call; api call to edit tuple in db
        if request.method == 'POST':
            payload = dict()
            # get all fields that are not empty i.e. need to be edited
            for key in request.form.keys():
                if len(request.form[key]) > 0:
                    payload[key] = request.form[key]

            response = post(url + f'api/edit/{table}', data=payload,
                            auth=(current_user.username, current_user.auth_token)).text
            if response == 'ok':
                return render_template(current_user=current_user, template_name_or_list='edit_' + table + '.html',
                                       success=table.capitalize() + " Edited", **variables)
            else:
                return render_template(current_user=current_user, template_name_or_list='edit_' + table + '.html',
                                       error=response, **request.form, **variables)

        return render_template(current_user=current_user, template_name_or_list='edit_' + table + '.html',
                               **variables)  # get call; display html form
    except TemplateNotFound:
        return render_template(current_user=current_user, template_name_or_list='no_access.html')


# view data of some table
@app.route('/<table>/view')
@login_required
def view_table(table):
    res = get(url + 'api/retrieve', params={'table': table, 'fields': '*'},
              auth=(current_user.username, current_user.auth_token))
    response = res.json()
    return render_template(current_user=current_user, template_name_or_list='view.html',
                           fields=response['fields'],
                           values=response['values'],
                           table=table)


# view data of machines
@app.route('/machine/view')
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
    return render_template(current_user=current_user, template_name_or_list='view.html',
                           fields=fields,
                           values=get(url + 'api/retrieve', params=params,
                                      auth=(current_user.username, current_user.auth_token)).json()['values'],
                           table='machine')


# render homepage
@app.route('/')
@login_required
def homepage():
    data = dict()

    if current_user.role == 'bel_mgr' or current_user.role == 'call_center':
        # get total scrap value
        data['scrap_money'] = get_data(
            "Select round(sum(m.price * e.Qty), 3) from eng_scrap e join material m on e.PartNo = m.PartNo")[0][0]
        data['scrap_money'] += get_data(
            "Select round(sum(m.price * r.Qty), 3) from reg_scrap r join material m on r.PartNo = m.PartNo")[0][0]

        data['warranty_in'] = get_data(
            "select count(*) from machine where machine.WarrantyExp >= date(now());")[0][0]  # in warranty
        data['amc_in'] = get_data(
            "select count(*) from machine where machine.AMCExp >= date(now());")[0][0]  # in amc

        # get number of machines out of amc and warranty
        data['amc_warranty_out'] = get_data("""
            select count(*) from machine 
            where machine.AMCExp < date(now()) and machine.WarrantyExp < date(now());
        """)[0][0]

        # get high priority complaints
        data['complaints'] = get_data(f"""
            Select t.Machine, c.Name, m.Location, e.Name, t.MadeOn
            from (complaint t join engineer e on t.Engineer = e.ID) join
            (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where t.Priority = 'High' and t.Status = 'Open'
        """)

    elif current_user.role == 'engineer':
        # get all open complaints assigned to the engineer
        data['complaints'] = get_data(f"""
            Select t.Machine, c.Name, m.Location, t.MadeOn
            from (complaint t join engineer e on t.Engineer = e.ID) join
            (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where e.username = '{current_user.username}' and t.Status = 'Open'
        """)

        # get all machines that are allocated to engineer which are due for pm
        data['pm'] = get_data(f"""
        select m.Location, next_pm(m.SlNo)
        from machine m join engineer e on m.AllocatedTo = e.ID
        where e.username = '{current_user.username}' and
            (next_pm(m.SlNo) <= m.WarrantyExp or next_pm(m.SlNo) between m.AMCStart and m.AMCExp) and 
            next_pm(m.SlNo) >= date(now()) and
            year(next_pm(m.SlNo)) = year(now()) and month(next_pm(m.SlNo)) = month(now());
        """)

        # get all materials that the engineer has
        data['materials'] = get_data(f"""
            Select m.Desc, em.Qty
            from material m join (eng_material em join engineer e on em.Engineer = e.ID) on m.PartNo = em.PartNo
            where e.username = '{current_user.username}'
        """)

        # get all scrap materials that the regional center has
        data['scrap'] = get_data(f"""
            Select m.Desc, em.Qty
            from material m join (eng_scrap em join engineer e on em.Engineer = e.ID) on m.PartNo = em.PartNo
            where e.username = '{current_user.username}'
        """)

    elif current_user.role == 'reg_mgr':
        # get all open complaints assigned to all engineers in the region
        data['complaints'] = get_data(f"""
            Select t.Machine, c.Name, m.Location, e.Name, t.MadeOn
            from (complaint t join (engineer e join reg_center rc on e.Region = rc.ID) on t.Engineer = e.ID) join
                (machine m join customer c on c.ID = m.CustID) on t.Machine = m.SlNo
            where rc.username = '{current_user.username}' and t.Status = 'Open' and t.Priority = 'High'
        """)

        # get all machines that are to be installed assigned to the region
        data['installations'] = get_data(f"""
            Select m.SlNo, c.Name, m.Location
            from (machine m join customer c on m.CustID = c.ID) join reg_center rc on m.Region = rc.ID
            where rc.username = '{current_user.username}' and m.Status = 'Installation Pending'
        """)

        # get all machines that are allocated to all engineers in the region which are due for pm
        data['pm'] = get_data(f"""
        select m.Location, e.Name, next_pm(m.SlNo)
        from machine m join (engineer e join reg_center rc on e.Region = rc.ID) on m.AllocatedTo = e.ID
        where rc.username = '{current_user.username}' and
            (next_pm(m.SlNo) <= m.WarrantyExp or next_pm(m.SlNo) between m.AMCStart and m.AMCExp) and 
            next_pm(m.SlNo) >= date(now()) and
            year(next_pm(m.SlNo)) = year(now()) and month(next_pm(m.SlNo)) = month(now());
        """)

        # get all materials that the regional center has
        data['materials'] = get_data(f"""
            Select m.Desc, rm.Qty
            from material m join (reg_materials rm join reg_center rc on rm.Region = rc.ID) on m.PartNo = rm.PartNo
            where rc.username = '{current_user.username}'
        """)

        # get all scrap materials that the regional center has
        data['scrap'] = get_data(f"""
            Select m.Desc, rm.Qty
            from material m join (reg_scrap rm join reg_center rc on rm.Region = rc.ID) on m.PartNo = rm.PartNo
            where rc.username = '{current_user.username}'
        """)

    return render_template(current_user=current_user,
                           template_name_or_list='homepage.html',
                           **data
                           )
