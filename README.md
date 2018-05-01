# The Wallet App

The API service allows the `parent` profile to `add`, `delete` and `read` all cards associated with his profile.
The API service allows the `parent` profile to `add`, `delete` balance against his card
The API service allows the `child` profile to `read` all cards and `delete` balance against a card


## Requirements
- Python3
- Auth0 free account


## Installation
- `pip install -r requirements.txt`


## Setup
- This application requires that you configure both the webapp and api with auth0
- API server port = 9090
- Webapp server port = 8080

### Setting up on Auth0
- Create an API with title: `MyWallet API` and make sure to enable `Allow Offline Access` and disable `Allow skipping user consent` (as we would like to see the consent screen)
- Choose the API identifier to map to `http://localhost:9090`
- Choose Signing algorithm as `HS256`.
- Create an application with title: `MyWallet Web` and set the redirect url as `http://localhost:9090/_zero/callback`, allowed web origins as `http://localhost:9090/` and also make sure to enable `Refresh Token` in the Grants
- Create a rule `Custom authorization scopes` with the content of the file `auth0/rule.js`. This logic takes care of mapping the role to scopes of the api
- Modify the hosted page with contents of the file from `auth0/hosted-login.html`, we customized it so as to see our custom select box with roles during signup


## Running the application
- Both the `api/server.py` and `web/server.py` take two arguments.
    * Port
    * Secret key (for api) / Client secret (for web app)
- Start both the applications such that we have the api server listening on port `9090` and the webapp server listening on port `8080`


## Testing
- Try to hit the url `http://localhost:8080` that should make the user go through the signup process to begin with
