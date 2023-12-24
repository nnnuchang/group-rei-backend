from bson import ObjectId
from flask import Blueprint, request, jsonify
import hashlib, os
from public.dbConnection import dbConnect

chip = Blueprint('chip',  __name__)

language = 'zh_tw'


@chip.route('/info', methods = ['GET'])
def info():
    requestData = request.args

    chipId = requestData['chipId']

    chipDb = dbConnect('chip')
    itemsDb = dbConnect('items')

    chipRecord = chipDb.find_one({'chip_id' : chipId})
    itemOid = chipRecord['item_oid']

    itemsRecord = itemsDb.find_one({'_id': itemOid})

    level = chipRecord['chip_level_id']
    itemId = chipRecord['category']
    name = itemsRecord['language'][language]['name']
    content = itemsRecord['language'][language]['content']
    attack = chipRecord['attack']
    category = chipRecord['category']
    upgradeCost = chipRecord['upgrade_cost']
    overlock = chipRecord['overlock']
    
    data = {
        'chipLevel': level,
        'itemId': itemId,
        'name': name,
        'content': content,
        'attack': attack,
        'chipCategory': category,
        'upgradeCost': upgradeCost,
        'overlock': overlock
    }

    return jsonify(data)

@chip.route('upgrade', methods = ['POST'])
def upgrade():
    requestData = request.get_json()
    token = requestData['token']
    objItemOid = requestData['objItemOid']
    typeId = requestData['typeId']
    u = requestData['u']
    mu = requestData['mu']

    bagDb = dbConnect('bag')
    obj_itemDb = dbConnect('obj_item')
    chipDb = dbConnect('chip')

    r = obj_itemDb.find_one({"_id":ObjectId(objItemOid)})

    print(r)

    if u[0]['UType'] == 'i00010':
        exp = u[0]['UNum']*100
    elif u[0]['UType'] == 'i00011':
        exp = u[0]['UNum']*1000
    else:
        exp = u[0]['UNum']*10000
    print(exp)

    obj_itemDb.update_one({"_id":ObjectId(objItemOid)},{'$inc':{'exp': exp}})
    cost = exp*5
    bagDb.update_one({"obj_items":ObjectId(objItemOid),'items.item_id':'i0001'},{'$inc':{'items.1.amount': -cost}})
    afterexp = obj_itemDb.find_one({"_id":ObjectId(objItemOid)},{"exp":1,"_id":0})
    cost_mu = bagDb.find_one({"obj_items":ObjectId(objItemOid),'items.item_id':'i0001'},{'items.amount':1, '_id':0})
    print(cost_mu)
    data = [cost_mu,afterexp]
    print(data)
    return jsonify(data)



