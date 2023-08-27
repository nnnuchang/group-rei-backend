from flask import Blueprint, request, jsonify
import hashlib, os

import time

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
    record = accountDb.find(query)

    dbData = {}
    for d in record:
        dbData.update(d)

    if dbData['password'] == password:
        print('uid login')
        token = hashlib.sha1(os.urandom(24)).hexdigest()
        loginDb.insert_one({'tokenHash': hashlib.md5(token.encode('utf-8')).hexdigest(), 'uid': uid, 'time': time.time()})

        data = {
            'token': token,
            'name': dbData['name'], 
            'birthday': dbData['birthday'],
            'phone': dbData['phone'],
            'memberLevel': dbData['memberLevel'],
            'mail': dbData['mail']
        }

        print(data) 
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