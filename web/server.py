from flask import Flask, redirect
from authlib.flask.client import OAuth

import sys
import os
import config
import requests


app = Flask(__name__)
env = os.environ

app.debug = env.get('ENVIRONMENT', 'development') == 'development'


@app.route('/_zero/callback')
def handle_callback():
    resp = auth0.authorize_access_token()
    print(resp)
    resp = requests.get(config.TEST_ENDPOINT, headers={'authorization': 'Bearer ' + resp['access_token']})
    return redirect('/home') if resp.ok else resp.text


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=config.REDIRECT_URI, audience=config.API_ENDPOINT)


@app.route('/home')
def home():
    return 'welcome home'

if __name__ == '__main__':
    app.secret_key = 'client'
    port, secret = sys.argv[1:]

    auth0 = OAuth(app).register(
        'auth0',
        client_id=config.CLIENT_ID,
        client_secret=secret,
        api_base_url='https://sumana.auth0.com',
        access_token_url='https://sumana.auth0.com/oauth/token',
        authorize_url='https://sumana.auth0.com/authorize',
        grant_type='authorization_code',
        client_kwargs={
            'scope': 'offline_access read:balance read:cards',
        },
    )
    app.run(port=int(port))
