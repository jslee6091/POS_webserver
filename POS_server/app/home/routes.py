# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.base import constants
from app.home import blueprint
from app.base.routes import requires_auth
from flask import render_template, redirect, url_for, request, session
import pymysql, boto3, json

lambda_client = boto3.client('lambda',
                    region_name='REGION',
                    aws_access_key_id='AWS_ACCESS_KEY',
                    aws_secret_access_key='AWS_SECRET_ACCESS_KEY')

config = {
    'host': 'AWS_RDS_ENDPOINT',
    'port': 3306,
    'user': 'admin',
    'database': 'mydatabase',
    'password': 'silver1212',
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

    sql = '''SELECT * FROM order_info'''
    cursor.execute(sql)
    user_data = cursor.fetchall()
    enu_user_data = enumerate(user_data)
    return render_template('order-tables.html', segment='tables', userinfo=session[constants.PROFILE_KEY], user_data=enu_user_data)

@blueprint.route('/order-detail-tables', methods=['POST'])
@requires_auth
def order_detail_tables():

    received_data = int(request.form.get('num'))
    
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    sql = '''SELECT menu, quantity FROM order_detail_info WHERE order_id=%s'''
    cursor.execute(sql, [received_data])
    order_data = cursor.fetchall()
    enu_order_data = enumerate(order_data)
    return render_template('order-detail-tables.html', segment='tables', userinfo=session[constants.PROFILE_KEY], order_data=enu_order_data, user_number=received_data)

@blueprint.route('/state_change', methods=['POST'])
@requires_auth
def state_change():

    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    received_data = int(request.form.get('state'))
    state_sql = '''UPDATE order_info SET state = '처리완료' WHERE user_id = %s'''
    cursor.execute(state_sql, [received_data])
    conn.commit()


    get_phone_sql = '''SELECT phone_no FROM user_info WHERE user_id = %s'''
    cursor.execute(get_phone_sql, [received_data])
    user_phone_no = cursor.fetchone()
    send_phone_no = '+82' + str(user_phone_no[0])
    
    # AWS Lambda 함수에 Event 전달
    lambda_send = lambda_client.invoke(FunctionName='LAMBDA_FUNCTION_NAME',
                                        InvocationType='Event',
                                        Payload=json.dumps({"text": "주문하신 제품이 완료되었습니다.", "number": send_phone_no}))

    
    return redirect(url_for('home_blueprint.order_tables'))

@blueprint.route('/order_delete', methods=['POST'])
@requires_auth
def order_delete():

    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    # 삭제 대상 회원의 정보를 이용해 order_id 추출
    received_data = int(request.form.get('delete'))
    getOrderID = '''SELECT order_id FROM order_info WHERE user_id=%s'''
    cursor.execute(getOrderID, [received_data])
    orderID = cursor.fetchone()

    # 추출한 order_id로 주문 상세 내역 삭제 - Foreign Key로 인해 상세 내역부터 삭제
    state_sql = '''DELETE FROM order_detail_info WHERE order_id=%s'''
    cursor.execute(state_sql, [orderID])
    conn.commit()

    # 주문 처리 완료 회원에 대한 주문 정보 삭제
    state_sql2 = '''DELETE FROM order_info WHERE user_id=%s'''
    cursor.execute(state_sql2, [received_data])
    conn.commit()

    return redirect(url_for('home_blueprint.order_tables'))

@blueprint.route('/go_back', methods=['POST'])
@requires_auth
def go_back():
    return redirect(url_for('home_blueprint.order_tables'))

@blueprint.route('/profile')
@requires_auth
def profile():
    return render_template('profile.html', segment='profile', userinfo=session[constants.PROFILE_KEY])

