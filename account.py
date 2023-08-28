from flask import Blueprint, request, jsonify
import hashlib, os

from datetime import datetime

from dbConnection import dbConnect

account = Blueprint('account',  __name__)

@account.route('/login', methods = ['POST'])
def login():

    accountDb = dbConnect('account')
    loginDb = dbConnect('loginRecord')

    if request.method == 'POST':
        print('post')
    
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

    return 0