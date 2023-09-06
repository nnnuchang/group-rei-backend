import hashlib
from datetime import datetime

import pytz

from dbConnection import dbConnect

expiresDays = 30


def checkToken(uid: str, token: str, timezone: str):
    loginDb = dbConnect('login_record')

    uid = uid.lower()
    tokenHash = hashlib.md5(token.encode('utf-8')).hexdigest()

    query = {'uid': uid, 'token_hash': tokenHash}
    print(query)

    record = loginDb.find_one(query)

    if record is None:
        data = {'state': 'none login', 'stateMessage': '無此登入記錄'}
        return data

    if record['is_login'] is False:
        data = {'state': 'token invalid', 'stateMessage': '此登入狀態無效'}
        return data
    loginDate = record['_id'].generation_time

    loginDays = (
        datetime.now().astimezone(pytz.utc).replace(microsecond=0) - loginDate
    ).days

    if loginDays > expiresDays:
        data = {
            'state': 'token expires',
            'stateMessage': '此登入已過期',
            'date': loginDate,
        }
        return data

    if record['timezone'] != timezone:
        data = {'state': 'wrong timezone', 'stateMessage': '跨時區請重新登入'}
        return data

    return True
