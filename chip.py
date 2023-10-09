from flask import Blueprint, request, jsonify
import hashlib, os
from dbConnection import dbConnect

chip = Blueprint('chip',  __name__)
@chip.route('/upgrade', methods = ['POST'])
def upgrade():
    tokenHash = hashlib.md5(request.get_json()['token'].encode('utf-8')).hexdigest()
    serialNum = request.get_json()['serialNum']
    typeId = request.get_json()['typeId']
    U = request.get_json()['U']
    mu = request.get_json()['mu']

@chip.route('/info', methods = ['GET'])
def info():
    chipId = request.get_json()['chipId']
    
    chipDb = dbConnect('chip')
    
    record = chipDb.find_one({'chip_id' : chipId},{'_id': 0 ,'item_oid':0})
    
    print(record)
    
    return jsonify(record)
    
    

