from flask import Blueprint, request, jsonify
import hashlib, os

from datetime import datetime

from dbConnection import dbConnect
from checkToken import checkToken
from logoutAll import logoutAll

account = Blueprint('account',  __name__)

timezone = 'Asia/Taipei'

@account.route('/login', methods = ['POST'])
def login():

    accountDb = dbConnect('account')
    loginDb = dbConnect('login_record')

    uid = request.get_json()['uid'].lower()
    password = hashlib.md5(request.get_json()['password'].encode('utf-8')).hexdigest()

    try:
        tzString = request.get_json()['timezone']
    except:
        tzString = 'UTC'

    if tzString is None:
        tzString = 'UTC'

    query = {"uid": uid}
    record = accountDb.find_one(query, {'_id': 0})

    if record['password'] == password:
        token = hashlib.sha1(os.urandom(24)).hexdigest()

        logoutAll(uid)
        loginDb.insert_one({
            'token_hash': hashlib.md5(token.encode('utf-8')).hexdigest(),
            'uid': uid,
            'is_login': True,
            'timezone': tzString
        })

        data = {
            'token': token,
            'name': record['name'],
            'birthday': record['birthday'],
            'phone': record['phone'],
            'memberLevel': record['member_level'],
            'email': record['email']
        }

        return jsonify(data)

    else:
        return jsonify(
            {
                "statusCode": 400,
                "failedMsg": "登入失敗"
            }
        )


@account.route('/logout', methods = ['POST'])
def logout():
    uid = request.get_json()['uid'].lower()

    tokenStatus = checkToken(uid, request.get_json()['token'], timezone)

    if tokenStatus is not True:
        data = tokenStatus
    else:
        logoutAll(uid)

        data = {
            'state': 'success',
            'stateMessage': '登出成功'
        }

    return jsonify(data)

@account.route('/signup', methods = ['POST'])
def signup():
    uid =  request.get_json()['uid'].lower()
    name = request.get_json()['name']
    email = request.get_json()['email']
    phone = request.get_json()['phone']
    birthday = datetime.strptime(
        request.get_json()['birthday'], '%Y-%m-%d'
    )
    password = hashlib.md5(request.get_json()['password'].encode('utf-8')).hexdigest()

    insertData = {
        'uid': uid,
        'name': name,
        'password': password,
        'email': email,
        'birthday': birthday,
        'phone': phone,
        'member_level': 0
    }

    try:
        accountDb = dbConnect('account')

        print(insertData)
        accountDb.insert_one(insertData)
        data = {
            'state': 'success',
            'stateMessage': '註冊成功'
        }
    except:
        data = {
            'state': 'failed',
            'stateMessage': '註冊失敗'
        }

    return jsonify(data)

@account.route('/check-uid', methods = ['GET'])
def checkUid():
    uid = request.args['uid'].lower()

    accountDb = dbConnect('account')

    record = accountDb.find_one({'uid': uid})

    if record is not None:
        data = {
            'isUsed': True
        }
    else:
        data = {
            'isUsed': False
        }
    
    return jsonify(data)

