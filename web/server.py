from flask import Flask, request, jsonify, url_for, redirect, _request_ctx_stack, session, render_template
from authlib.flask.client import OAuth

import sys
import os
import config
import requests


app = Flask(__name__, template_folder='layouts')
env = os.environ

app.debug = env.get('ENVIRONMENT', 'development') == 'development'


@app.route('/_zero/callback')
def handle_callback():

    token = auth0.authorize_access_token()
    session['token'] = token
    return redirect('/home')


@app.route('/login')
def login():
    if 'token' in session:
        return redirect('/home')
    return auth0.authorize_redirect(redirect_uri=config.REDIRECT_URI, audience=config.AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home')


@app.route('/home')
def home():
    if 'token' in session:
        userdetails = auth0.get(config.USERINFO, token=session['token'])
        userinfo = userdetails.json()
        resp = auth0.get(config.CARDS_ENDPOINT, token=session['token'])
        error = session.get('error', None)
        if error is not None:
            session['error'] = None
        return render_template('home.html', cards=resp.json(), error=error, userinfo=userinfo)

    return render_template('home.html')


@app.route('/remove_card/<int:card_id>')
def remove_card(card_id):
    resp = auth0.delete(config.CARDS_ENDPOINT, token=session['token'], json={'card_id': card_id})
    if not resp.ok:
        session['error'] = resp.json()

    return redirect('/home')


@app.route('/balance', methods=['POST'])
def modify_balance():
    card_id, amount = request.form.get('card_id'), request.form.get('balance')
    resp = auth0.post(config.BALANCE_ENDPOINT, token=session['token'], json={'card_id': card_id, 'amount': amount})
    if not resp.ok:
        session['error'] = resp.json()

    return redirect('/home')


@app.route('/')
def index():
    return '<a href="/login">Login</a>'


def update_token(token):
    session['token'] = token

if __name__ == '__main__':
    app.secret_key = 'client'
    port, secret = sys.argv[1:]

    auth0 = OAuth(app).register(
        'auth0',
        client_id=config.CLIENT_ID,
        client_secret=secret,
        api_base_url='https://sumana.auth0.com',
        access_token_url='https://sumana.auth0.com/oauth/token',
        refresh_token_url='https://sumana.auth0.com/oauth/token',
        authorize_url='https://sumana.auth0.com/authorize',
        grant_type='authorization_code',
        update_token=update_token,
        client_kwargs={
            'scope': 'openid profile offline_access read:balance read:cards add:balance delete:balance delete:cards',
        },
    )
    app.run(port=int(port),debug=True)
