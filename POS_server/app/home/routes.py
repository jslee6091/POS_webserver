# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.base import constants
from app.home import blueprint
from app.base.routes import requires_auth
from flask import render_template, redirect, url_for, request, session
import pymysql

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password' : 'mysql',
    'database': 'mydb',
    'charset': 'utf8'
}

@blueprint.route('/index')
@requires_auth
def index():

    return render_template('index.html', segment='index', userinfo=session[constants.PROFILE_KEY])


@blueprint.route('/order-tables')
@requires_auth
def order_tables():
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    sql = '''SELECT DISTINCT userinfo_no FROM order_info'''
    cursor.execute(sql)
    user_data = cursor.fetchall()
    enu_user_data = enumerate(user_data)
    return render_template('order-tables.html', segment='tables', userinfo=session[constants.PROFILE_KEY], user_data=enu_user_data)

@blueprint.route('/order-detail-tables', methods=['POST'])
@requires_auth
def order_detail_tables():

    received_data = int(request.form.get('num'))
    print('received_data : ', received_data, type(received_data))

    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    sql = '''SELECT name, quantity FROM order_info WHERE userinfo_no=%s'''
    cursor.execute(sql, [received_data])
    order_data = cursor.fetchall()
    print('order_data : ', order_data)
    enu_order_data = enumerate(order_data)
    return render_template('order-detail-tables.html', segment='tables', userinfo=session[constants.PROFILE_KEY], order_data=enu_order_data, user_number=received_data)


@blueprint.route('/profile')
@requires_auth
def profile():
    return render_template('profile.html', segment='profile', userinfo=session[constants.PROFILE_KEY])

