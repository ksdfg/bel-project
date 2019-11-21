from waitress import serve

from web_app import app, set_url

set_url('localhost')  # url at which app is deployed

# app.run('localhost', port=80)
serve(app, host='localhost', port=80)
