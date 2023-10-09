from flask import Blueprint, Response, request, jsonify
import hashlib, json

from datetime import datetime

from dbConnection import dbConnect

from bson.objectid import ObjectId



item = Blueprint('item',  __name__)
@item.route('/list', methods = ['GET'])
def itemList():
    
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()
    fillter = request.get_json()['fillter']
    
    record_list = []
    record_list2 = []
    

    bagDb = dbConnect('bag')

    pipeline = [ { "$lookup": { "from": 'items', "localField": 'items.item_id', "foreignField": 'item_id', "as": 'itemData' } },
                 { "$unwind" : "$itemData" }
                ,{'$match':{'itemData.category' : fillter[0]['category']}},
                 {"$project": { "itemData.language.zh_tw.name":1,'itemData.category':1,'items.amount':1, '_id':0, }}]
    
    for doc in (bagDb.aggregate(pipeline)):
        record_list.append(doc)
        
    print(record_list)

    data = {'itemList': record_list}

    return jsonify(data)

@item.route('/delete', methods = ['POST'])
def deleteItems():
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()
    itemsInfo = request.get_json()['itemsInfo']
    category = request.get_json()['category']
    
    bagDb = dbConnect('bag')
    items_deletedDb = dbConnect('items_deleted')
    record = bagDb.find_one( { 'items.item_id' : itemsInfo[0]['itemId']},{'_id': 0 ,'account_oid':0, 'obj_items':0})
    #if itemsInfo[0]['amount']>='items.0.amount':
    if category==0:
        print("selling items")
        bagDb.update_one({'account_oid':ObjectId('64a52170a2ea213e1810c2aa')},{'$inc':{'items.0.amount': -itemsInfo[0]['amount']}})
        items_deletedDb.update_one({"uid":"botoudon"},{"$push":{"items":{"item_id":itemsInfo[0]['itemId'],"amount":-itemsInfo[0]['amount']}},})

    else:
        print("break down items")
        bagDb.update_one({'account_oid':ObjectId('64a52170a2ea213e1810c2aa')},{'$inc':{'items.0.amount': -itemsInfo[0]['amount']}})

    print(record)
    return jsonify(record)

        
    