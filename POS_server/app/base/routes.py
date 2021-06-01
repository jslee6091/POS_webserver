# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for, session

from app import db, login_manager
from app.base import blueprint
from app.base.models import User

from functools import wraps
import json, pymysql
from app.base import constants
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

blueprint.config = {}
blueprint.config['SECRET_KEY'] = constants.SECRET_KEY
blueprint.config['DEBUG'] = True

@blueprint.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

oauth = OAuth(blueprint)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

config = {
    'host': 'AWS_RDS_ENDPOINT',
    'port': 3306,
    'user': 'admin',
    'database': 'mydatabase',
    'password': 'silver1212',
    'charset': 'utf8'
}


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return render_template('accounts/requires.html')
        return f(*args, **kwargs)
    
    return decorated


# Login & Registration
@blueprint.route('/')
def route_default():
    return render_template('accounts/index_init.html')

@blueprint.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


@blueprint.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@blueprint.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('base_blueprint.route_default', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@blueprint.route('/dashboard')
def dashboard():
    return render_template('accounts/dashboard.html',
                           userinfo=session[constants.PROFILE_KEY])


# Data Transfer Between Android & Web Server
@blueprint.route('/android', methods=['POST'])
def android():
    received_data = request.form
    received_json = json.dumps(received_data)
    data_json = json.loads(received_json)
    
    data_dict = dict(data_json)
    data_dict['userID'] = int(data_dict['userID'])
    data_dict['quantity'] = int(data_dict['quantity'])
    data_dict['phonenum'] = int(data_dict['phonenum'])
    
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    
    # 회원 정보 먼저 저장 - 이미 있으면 저장 안함
    userinfo_sql = '''INSERT IGNORE INTO user_info(user_id, phone_no) VALUES(%s, %s)'''
    cursor.execute(userinfo_sql, [data_dict['userID'], data_dict['phonenum']])
    conn.commit()
    
    # 회원의 주문 정보 저장 - 현재 주문 내용이 있는 회원만 저장
    # user_id와 state 저장
    orderinfo_sql = '''INSERT IGNORE INTO order_info(user_id, state) VALUES(%s, %s)'''
    cursor.execute(orderinfo_sql, [data_dict['userID'], data_dict['state']])
    conn.commit()
    
    # 회원의 주문 상세 내역 저장을 위한 정보 추출
    # user_id를 이용한 order_id 추출
    getorderinfo_sql = '''SELECT order_id FROM order_info WHERE user_id=%s'''
    cursor.execute(getorderinfo_sql, [data_dict['userID']])
    orderID = cursor.fetchone()
    
    # 회원의 주문 상세 내역 저장
    orderdetail_info_sql = '''INSERT INTO order_detail_info(order_id, menu, quantity) VALUES(%s, %s, %s)'''
    cursor.execute(orderdetail_info_sql, [orderID, data_dict['menu'], data_dict['quantity']])
    conn.commit()

    return jsonify(data_dict)

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
