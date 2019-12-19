from waitress import serve

from crm.web_app import app, set_url

set_url('localhost')  # url at which app is deployed

# deploy web app on http port
serve(app, host='localhost', port=80)
