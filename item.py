from flask import Blueprint, Response, request, jsonify
import hashlib, json

from datetime import datetime

from dbConnection import dbConnect



item = Blueprint('item',  __name__)
@item.route('/item-list', methods = ['GET'])
def itemList():
    
    uid =  request.get_json()['uid'].lower()
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()
    fillter = request.get_json()['fillter']
    
    record_list = []
    
    itemDb = dbConnect('items')
    
    record = itemDb.find({'category': fillter[0]['type'] }, {'_id': 0})

    for r in record:
        type(r)
        record_list.append(r)
        print(r)
        

    data = {'itemList': record_list}
    print(data)

    return jsonify(data)

@item.route('/delete-items', methods = ['POST'])
def deleteItems():
    uid =  request.get_json()['uid'].lower()
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()
    itemInfo = request.get_json()['itemInfo']
    category = request.get_json()['category']

        
    