import hashlib
from datetime import datetime

import pytz

from dbConnection import dbConnect

expiresDays = 30


def checkToken(token: str, timezone: str):
    loginDb = dbConnect('login_record')

    tokenHash = hashlib.md5(token.encode('utf-8')).hexdigest()

    query = {'token_hash': tokenHash}

    record = loginDb.find_one(query)
    uid = record['uid']

    if record is None:
        data = {'status': 'none login', 'statusMessage': '無此登入記錄'}
        return data

    if record['is_login'] is False:
        data = {'status': 'token invalid', 'statusMessage': '此登入狀態無效'}
        return data
    loginDate = record['_id'].generation_time

    loginDays = (
        datetime.now().astimezone(pytz.utc).replace(microsecond=0) - loginDate
    ).days

    if loginDays > expiresDays:
        data = {
            'status': 'token expires',
            'statusMessage': '此登入已過期',
            'date': loginDate,
        }
        return data

    if record['timezone'] != timezone:
        data = {'status': 'wrong timezone', 'statusMessage': '跨時區請重新登入'}
        return data

    data = {
        'uid': uid,
        'status': True
    }

    return data
