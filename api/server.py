from functools import wraps
from flask import Flask, request, jsonify, url_for, redirect
from wallet import Wallet
from jose import jwt
from urllib.request import urlopen

import sys
import os
import json


app = Flask(__name__)
env = os.environ

app.debug = env.get('ENVIRONMENT', 'development') == 'development'

AUTH0_DOMAIN = env.get("AUTH0_DOMAIN", "sumana.auth0.com")
API_IDENTIFIER = env.get("API_IDENTIFIER", "http://localhost:8080")
ALGORITHMS = ["HS256", "RS256"]

ROLES_IDENTIFIER = 'http://sumana.com/roles'


class Error(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise Error({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise Error({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise Error({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise Error({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_IDENTIFIER,
                    issuer="https://{domain}/".format(domain=AUTH0_DOMAIN)
                )
            except jwt.ExpiredSignatureError:
                raise Error({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise Error({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception as e:
                raise Error({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication token"}, 401)

        return f(*args, **kwargs)

    return decorated


def has_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
    return False


def handle_error(f):
    @wraps(f)
    def callback(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Error as e:
            response = jsonify(e.error)
            response.status_code = e.status_code
            return response
        except Exception as ex:
            response = jsonify(ex.error)
            response.status_code = ex.status_code
            return response

    return callback


@app.route('/balance', methods=['POST', 'GET'])
@requires_auth
@handle_error
def balance():

    if request.method == 'GET' and has_scope('read:balance'):
        card_id = int(request.args.get('card_id'))
        return jsonify({'balance': Wallet.get_balance(card_id), 'card_id': card_id})

    elif request.method == 'POST':
        body = request.get_json()
        card_id = int(body['card_id'])
        balance = int(body['amount'])
        #print(card_id,balance)
        if balance > 0 and has_scope('add:balance'):
            #print("in add balance")
            Wallet.modify_balance(card_id, balance)
            return '', 204
        elif balance < 0 and has_scope('delete:balance'):
            #print("in delete balance")
            Wallet.modify_balance(card_id, balance)
            return '', 204

    raise Error({'code': 'missing:right', 'description': 'Invalid action'}, 401)


@app.route('/cards', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
@handle_error
def cards():

    if request.method == 'GET' and has_scope('read:cards'):
        return jsonify(Wallet.get_wallet())

    elif request.method == 'PUT' and has_scope('add:card'):
        body = request.get_json()
        Wallet.add_card(int(body['card_id']), int(body['amount']))
        return '', 201

    elif request.method == 'DELETE' and has_scope('delete:cards'):
        body = request.get_json()
        Wallet.remove_card(int(body['card_id']))
        return '', 204

    raise Error({'code': 'missing:right', 'description': 'Invalid action'}, 401)


if __name__ == '__main__':
    port = sys.argv[1]
    app.run(port=int(port),debug=True)
