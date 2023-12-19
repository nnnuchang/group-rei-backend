from flask import Blueprint, request, jsonify

from public.checkToken import checkToken
from public.dbConnection import dbConnect

store = Blueprint('store', __name__)

timezone = 'Asia/Taipei'

@store.route('/list', methods = ['GET'])
def list():
    requestData = request.args

    uid = requestData['uid']
    mu = requestData['mu']
    konpeito = requestData['konpeito']

    accountDb = dbConnect('account')
    commanderDb = dbConnect('commander')
    goodDb = dbConnect('good')
    itemsDb = dbConnect('items')
    transactionRecordDb = dbConnect('transaction_record')

    accountOid = accountDb.find_one({'uid': uid})['_id']
    commanderRecord = commanderDb.find_one({'account_oid': accountOid})

    serverKonpeito = commanderRecord['konpeito']
    serverMu = commanderRecord['mu']

    try:
        if(int(serverKonpeito) != int(konpeito) or int(serverMu) != int(mu)):
            return jsonify({
                'statusCode': 403,
                'failedMsg': '數值驗證失敗(konpeito)'
            })
    except:
        return jsonify({
                'statusCode': 400,
                'failedMsg': '資料型態錯誤(konpeito)'
            })



    goodRecord = goodDb.find()
    bought = transactionRecordDb.aggregate([
        {'$group': {'_id': {'id': '$id', 'good_id': '$good_id'}, 'amount': {'$sum': '$amount'}}},
        {'$match': {'_id.id': uid}}
    ])

    boughtAmounts = {}
    for i in bought:
        boughtAmounts.update(
            {
                i['_id']['good_id']: i['amount']
            }
        )

    product = []
    for i in goodRecord:
        itemId = i['good_id']
        try:
            itemName = itemsDb.find_one({'_id': i['item_oid']})['language']['zh_tw']['name']
        except:
            itemName = 'language error'
        itemTypeId = i['category']
        try:
            if boughtAmounts[itemId] == None: boughtAmount = int(boughtAmounts[itemId])
        except:
            boughtAmount = 0
        leftNumber = int(i['amount']) - boughtAmount
        price = i['price']
        costItem = i['cost_item']

        product.append(
            {
                'itemId': itemId,
                'itemName': itemName,
                'itemTypeId': itemTypeId,
                'leftNumber': leftNumber,
                'price': price,
                'costItem': costItem
            }
        )

    data = {
        "product": product,
        "konpeito": serverKonpeito,
        "mu": serverMu
    }

    return jsonify(data)