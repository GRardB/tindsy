import os
import time
import random
import requests
import json

from flask import Flask, url_for, session, redirect, request, render_template
from requests_oauthlib import OAuth1Session
from HTMLParser import HTMLParser

PERMISSION_SCOPES = '%20'.join([
    'favorites_rw',
    'recommend_rw',
])

ETSY_API_KEY = os.environ['ETSY_API_KEY']
ETSY_API_SECRET = os.environ['ETSY_API_SECRET']

ETSY_API_URL_BASE = 'https://openapi.etsy.com/v2/{action}/?api_key=' + ETSY_API_KEY

BASE_URL = 'https://openapi.etsy.com/v2/oauth'
REQUEST_TOKEN_URL = 'https://openapi.etsy.com/v2/oauth/request_token'
ACCESS_TOKEN_URL =  'https://openapi.etsy.com/v2/oauth/access_token'
AUTHORIZE_URL = 'https://openapi.etsy.com/v2/users/__SELF__'

app = Flask(__name__)
app.secret_key = os.environ['ETSY_API_SECRET']

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    etsy = OAuth1Session(
        ETSY_API_KEY,
        client_secret=ETSY_API_SECRET,
        callback_uri='http://localhost:5000' + url_for('oauth_authorized')
    )

    response = etsy.fetch_request_token(REQUEST_TOKEN_URL)

    login_url = response['login_url']
    oauth_token = response['oauth_token']
    oauth_token_secret = response['oauth_token_secret']
    oauth_consumer_key = response['oauth_consumer_key']

    authorization_url = etsy.authorization_url(login_url)

    session['access_token'] = oauth_token
    session['access_token_secret'] = oauth_token_secret

    return redirect(authorization_url)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('access_token')
    session.pop('access_token_secret')
    return redirect(url_for('index'))

@app.route('/oauth_authorized', methods=['GET'])
def oauth_authorized():
    etsy = OAuth1Session(
        ETSY_API_KEY,
        client_secret=ETSY_API_SECRET,
        resource_owner_key=session['access_token'],
        resource_owner_secret=session['access_token_secret'],
        verifier='oauth_verifier'
    )
    etsy.parse_authorization_response(request.url)
    token = etsy.fetch_access_token(ACCESS_TOKEN_URL)

    session['access_token'] = token['oauth_token']
    session['access_token_secret'] = token['oauth_token_secret']

    return redirect(url_for('index'))

def etsy_api_call(action, params={}):
    return requests.get(ETSY_API_URL_BASE.format(action=action), params=params).json()['results']

@app.route('/get_listing', methods=['GET'])
def get_listing():
    listing = etsy_api_call('listings/active', {
        'limit': 1,
        'offset': random.randint(0, 50000),
        'includes': 'MainImage(url_fullxfull)'
    })[0]

    html_parser = HTMLParser()

    return json.dumps({
        'listing_id': listing['listing_id'],
        'listing_title': html_parser.unescape(listing['title']),
        'listing_image': listing['MainImage']['url_fullxfull'],
        'num_favorites': listing['num_favorers']
    })


@app.route('/recommendations', methods=['GET'])
def recommendations():
    etsy = get_etsy_oauth() 

@app.route('/favorite', methods=['POST'])
def favorite():
    etsy = get_etsy_oauth() 

    listing_id = request.form['listing_id']

    return etsy.post('https://openapi.etsy.com/v2/users/__SELF__/favorites/listings/' + listing_id).content

def get_etsy_oauth():
    return OAuth1Session(
        ETSY_API_KEY,
        client_secret=ETSY_API_SECRET,
        resource_owner_key=session['access_token'],
        resource_owner_secret=session['access_token_secret']
    )

if __name__ == '__main__':
    app.run(debug=True)
