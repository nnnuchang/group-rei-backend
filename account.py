from flask import Blueprint, request, jsonify
import hashlib, os

from datetime import datetime

from dbConnection import dbConnect

account = Blueprint('account',  __name__)

@account.route('/login', methods = ['POST'])
def login():

    accountDb = dbConnect('account')
    loginDb = dbConnect('loginRecord')

    uid = request.get_json()['uid']
    password = hashlib.md5(request.get_json()['password'].encode('utf-8')).hexdigest()

    query = {"uid": uid}
    record = accountDb.find_one(query, {'_id': 0})

    if record['password'] == password:
        print('uid login')
        token = hashlib.sha1(os.urandom(24)).hexdigest()

        logoutAll(uid)
        loginDb.insert_one({
            'tokenHash': hashlib.md5(token.encode('utf-8')).hexdigest(),
            'uid': uid,
            'loginDate': datetime.today().replace(microsecond = 0),
            'isLogin': True
        })

        data = {
            'token': token,
            'name': record['name'],
            'birthday': record['birthday'],
            'phone': record['phone'],
            'memberLevel': record['memberLevel'],
            'mail': record['mail']
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
    expiresDays = 30

    loginDb = dbConnect('loginRecord')

    uid = request.get_json()['uid']
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()

    query = {
        'uid': uid,
        'tokenHash': tokenHash,
    }

    record = loginDb.find_one(query, {"_id": 0})

    if record is not None:
        loginDays = (datetime.today()-record['loginDate']).days

        if loginDays > expiresDays:
            data = {
                'state': 'token expires',
                'stateMessage': '此登入過期',
                'date': record['loginDate']
            }
            return data

        if record['isLogin'] == True:
            logoutAll(uid)

            data = {
                'state': 'success',
                'stateMessage': '登出成功'
            }

            return data
        else:
            data = {
                'state': 'token invalid',
                'stateMessage': '此登入狀態無效'
            }
            return data
    else:
        data = {
                'state': 'none login',
                'stateMessage': '無此登入記錄'
            }
        return data

@account.route("/signup", methods = ['POST'])
def signup():
    uid =  request.get_json()['uid']
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

# 登出所有裝置
def logoutAll(uid):
    loginDb = dbConnect('loginRecord')

    allLoginData = loginDb.update_many({'uid': uid}, {'$set': {'isLogin': False}})
    print(uid, allLoginData.modified_count, "documents of loginRecord updated")