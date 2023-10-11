from bson import ObjectId
from flask import Blueprint, request, jsonify
import hashlib, os
from dbConnection import dbConnect

pool = Blueprint('pool',  __name__)

@pool.route('/list', methods = ['GET'])
def list():
    token = request.get_json()['token']
    konpeito = request.get_json()['konpeito']
    nuclearWaste = request.get_json()['nuclearWaste']
    
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
    token = request.get_json()['token']
    poolId = request.get_json()['poolId']
    konpeito = request.get_json()['konpeito']
    nuclearWaste = request.get_json()['nuclearWaste']
    poo = request.get_json()['poo']
    purchaseCount = request.get_json()['purchaseCount']
    spend = request.get_json()['spend']

    purchaeDb = dbConnect('purchase')
    
    result = purchaeDb.find_one({'pool_id':poolId},{'record':1,'_id':0})
    print(result)
    data = {"itemsInfo":result},{"LOL":"x"}
    
    return jsonify(data)
    
