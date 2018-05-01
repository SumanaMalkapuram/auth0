from functools import wraps
from flask import Flask, request, jsonify, url_for, redirect
from jose import jwt

import sys
import os


app = Flask(__name__)
env = os.environ

app.debug = env.get('ENVIRONMENT', 'development') == 'development'

AUTH0_DOMAIN = env.get("AUTH0_DOMAIN", "sumana.auth0.com")
API_IDENTIFIER = env.get("API_IDENTIFIER", "http://localhost:8080")
AUTH0_SECRET = "MISSING"
ALGORITHMS = ["HS256"]

ROLES_IDENTIFIER = 'http://sumana.com/roles'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
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
        try:
            jwt.decode(
                token,
                AUTH0_SECRET,
                algorithms=ALGORITHMS,
                audience=API_IDENTIFIER,
                issuer="https://{domain}/".format(domain=AUTH0_DOMAIN)
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                            "description":
                                "incorrect claims,"
                                " please check the audience and issuer"}, 401)
        except Exception as e:
            raise AuthError({"code": "invalid_header",
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
    print(unverified_claims )
    if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
    return False


@app.route('/balance', methods=['DELETE', 'POST', 'GET'])
@requires_auth
def balance():
    if has_scope('delete:balance'):
        pass

    raise AuthError('Missing required scope', 403)


@app.route('/cards', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
def cards():
    if has_scope('read:cards'):
        pass

    raise AuthError('Missing required scope', 403)


if __name__ == '__main__':
    port, secret = sys.argv[1:]
    AUTH0_SECRET = secret
    app.run(port=int(port),debug=True)
