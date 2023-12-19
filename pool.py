from bson import ObjectId
from flask import Blueprint, request, jsonify
import hashlib, os
from public.dbConnection import dbConnect

pool = Blueprint('pool',  __name__)

@pool.route('/list', methods = ['GET'])
def list():
    requestData = request.get_json()

    token = requestData['token']
    konpeito = requestData['konpeito']
    nuclearWaste = requestData['nuclearWaste']

    poolDb = dbConnect('pool')
    result_list = []
    result = poolDb.find({},{"_id":0})

    for r in result:
        result_list.append(r)
        print(r)
    print(result_list)
    data = jsonify(result_list)

    return data



@pool.route('/purchase', methods = ['POST'])
def purchase():
    requestData = request.get_json()
    token = requestData['token']
    poolId = requestData['poolId']
    konpeito = requestData['konpeito']
    nuclearWaste = requestData['nuclearWaste']
    poo = requestData['poo']
    purchaseCount = requestData['purchaseCount']
    spend = requestData['spend']

    purchaeDb = dbConnect('purchase')

    result = purchaeDb.find_one({'pool_id':poolId},{'record':1,'_id':0})
    print(result)
    data = {"itemsInfo":result},{"LOL":"x"}

    return jsonify(data)