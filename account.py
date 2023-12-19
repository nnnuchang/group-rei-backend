from flask import Blueprint, request, jsonify
import hashlib, os

from datetime import datetime

from public.dbConnection import dbConnect
from public.checkToken import checkToken
from public.logoutAll import logoutAll

account = Blueprint('account', __name__)

timezone = 'Asia/Taipei'


@account.route('/login', methods=['POST'])
def login():
    accountDb = dbConnect('account')
    loginDb = dbConnect('login_record')

    requestData = request.get_json()

    uid = requestData['uid'].lower()
    password = hashlib.md5(requestData['password'].encode('utf-8')).hexdigest()

    try:
        tzString = requestData['timezone']
    except:
        tzString = 'UTC'

    if tzString is None:
        tzString = 'UTC'

    query = {'uid': uid}
    record = accountDb.find_one(query, {'_id': 0})

    if record['password'] == password:
        token = hashlib.sha1(os.urandom(24)).hexdigest()
        token_hash = hashlib.md5(token.encode('utf-8')).hexdigest()

        loginDb.find()
        logoutAll(uid)
        loginDb.insert_one(
            {
                'token_hash': token_hash,
                'uid': uid,
                'is_login': True,
                'timezone': tzString
            }
        )

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
        return jsonify({'statusCode': 400, 'failedMsg': '登入失敗'})


@account.route('/logout', methods=['POST'])
def logout():
    requestData = request.get_json()

    token = requestData['token']
    tokenStatus = checkToken(token, timezone)

    if tokenStatus['status'] is not True:
        data = tokenStatus
    else:
        uid = tokenStatus['uid']
        logoutAll(uid)

        data = {'state': 'success', 'stateMessage': '登出成功'}

    return jsonify(data)


@account.route('/signup', methods=['POST'])
def signup():
    requestData = request.get_json()

    uid = requestData['uid'].lower()
    name = requestData['name']
    email = requestData['email']
    phone = requestData['phone']
    birthday = datetime.strptime(requestData['birthday'], '%Y-%m-%d')
    password = hashlib.md5(requestData['password'].encode('utf-8')).hexdigest()

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

        accountDb.insert_one(insertData)
        data = {'state': 'success', 'stateMessage': '註冊成功'}
    except:
        data = {'state': 'failed', 'stateMessage': '註冊失敗'}

    return jsonify(data)


@account.route('/check-uid', methods=['GET'])
def checkUid():
    requestData = request.args

    uid = requestData['uid'].lower()

    accountDb = dbConnect('account')

    record = accountDb.find_one({'uid': uid})

    if record is not None:
        data = {'isUsed': True}
    else:
        data = {'isUsed': False}

    return jsonify(data)

@account.route('/forget-password', methods = ['POST'])
def forgetPassword():
    requestData = request.get_json()
    uid = requestData['uid']

    return jsonify({'message': "請至登記信箱收信(開發版本無此功能)"})