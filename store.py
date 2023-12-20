from flask import Blueprint, request, jsonify

from public.checkToken import checkToken
from public.dbConnection import dbConnect

store = Blueprint('store', __name__)

timezone = 'Asia/Taipei'

@store.route('/list', methods = ['GET'])
def list():
    requestData = request.args

    uid = requestData['uid']

    accountDb = dbConnect('account')
    commanderDb = dbConnect('commander')

    accountOid = accountDb.find_one({'uid': uid})['_id']
    commanderRecord = commanderDb.find_one({'account_oid': accountOid})

    try:
        mu = int(requestData['mu'])
        konpeito = int(requestData['konpeito'])
        serverKonpeito = int(commanderRecord['konpeito'])
        serverMu = int(commanderRecord['mu'])

        if(serverKonpeito != konpeito or serverMu != mu):
            return jsonify({
                'statusCode': 403,
                'failedMsg': '數值驗證失敗(konpeito)'
            })
    except:
        return jsonify({
                'statusCode': 400,
                'failedMsg': '資料型態錯誤(konpeito)'
            })

    goodDb = dbConnect('good')
    itemsDb = dbConnect('items')
    transactionRecordDb = dbConnect('transaction_record')

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
        goodId = i['good_id']
        try:
            itemsRecord = itemsDb.find_one({'_id': i['item_oid']})
            itemId = itemsRecord['item_id']
            itemName = itemsRecord['language']['zh_tw']['name']
        except:
            itemName = 'language error'
        goodTypeId = i['category']
        try:
            if boughtAmounts[goodId] == None: boughtAmount = int(boughtAmounts[goodId])
        except:
            boughtAmount = 0
        leftNumber = int(i['amount']) - boughtAmount
        price = i['price']
        costItem = i['cost_item']

        product.append(
            {
                'goodId': goodId,
                'itemId': itemId,
                'itemName': itemName,
                'goodTypeId': goodTypeId,
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

@store.route('/buy', methods = ['POST'])
def buy():
    requestData = request.get_json()

    token = requestData['token']
    goodId = requestData['goodId']
    amount = int(requestData['amount'])

    tokenStatus = checkToken(token, timezone)

    # 驗證身分
    if tokenStatus['status'] is not True:
        return jsonify(tokenStatus)
    else:
        uid = tokenStatus['uid']

    # 取得資料並驗證數值
    accountDb = dbConnect('account')
    commanderDb = dbConnect('commander')

    accountOid = accountDb.find_one({'uid': uid})['_id']
    commanderRecord = commanderDb.find_one({'account_oid': accountOid})

    try:
        mu = int(requestData['mu'])
        konpeito = int(requestData['konpeito'])
        poo = int(requestData['poo'])
        serverKonpeito = int(commanderRecord['konpeito'])
        serverMu = int(commanderRecord['mu'])
        serverPoo = int(commanderRecord['poo'])

        if(serverKonpeito != konpeito or serverMu != mu or poo != serverPoo):
            print('k: {}\nm: {}\np: {}'.format(serverKonpeito, serverMu, serverPoo))
            return jsonify({
                'statusCode': 403,
                'failedMsg': '數值驗證失敗(konpeito)'
            })
    except:
        return jsonify({
                'statusCode': 400,
                'failedMsg': '資料型態錯誤(konpeito)'
            })

    # 連線所需資料表
    goodDb = dbConnect('good')
    itemsDb = dbConnect('items')
    bagDb = dbConnect('bag')
    objItemDb = dbConnect('obj_item')
    transactionRecordDb = dbConnect('transaction_record')

    # 商品資訊
    goodRecord = goodDb.find_one({'good_id': goodId})
    if(goodRecord == None):
        return jsonify({
                'statusCode': 400,
                'failedMsg': '商品不存在'
            }) 
    itemsRecord = itemsDb.find_one({'_id': goodRecord['item_oid']})

    goodPrice = goodRecord['price']
    goodCostItem = goodRecord['cost_item']
    goodAmount = int(goodRecord['amount'])
    itemId = itemsRecord['item_id']

    # 檢查item種類是否屬於obj
    isObj = False
    itemType = itemsRecord['category']
    objType = ['ic0003', 'ic0004', 'ic0005'] # suit, chip, headgear

    if(itemType in objType): isObj = True

    # 新增到備戰空間
    bagRecord = bagDb.find_one({'account_oid': accountOid})
    if(bagRecord == None):
        bagDb.insert_one({
            'items': [],
            'obj_items': [],
            'account_oid': accountOid
        })

    # 計算可購買次數
    bought = transactionRecordDb.aggregate([
        {'$group': {'_id': {'uid': '$uid', 'good_id': '$good_id'}, 'amount': {'$sum': '$amount'}}},
        {'$match': {'_id.uid': uid, '_id.good_id': goodId}}
    ])

    boughtAmount = 0
    for i in bought:
        boughtAmount = int(i['amount'])
    
    leftAmount = goodAmount - boughtAmount

    # 檢查購買數量
    if(amount > leftAmount):
        return jsonify({
                'statusCode': 200,
                'failedMsg': '超過購買上限'
            })

    if(isObj):
        newObjItem = objItemDb.insert_one({
            "item_id": itemId,
            "exp": 0,
            "attribute": None
        })
        newObjItemOid = newObjItem.inserted_id
        bagDb.update_one({'account_oid': accountOid}, {'$push': {'obj_items': newObjItemOid}})
    else:
        bagItemList = bagDb.find_one({'account_oid': accountOid, 'items': {'$elemMatch': {'item_id': {'$eq': itemId}}}})

        if(bagItemList == None):
            newItem = {
                'item_id': itemId,
                'amount': amount
            }

            bagDb.update_one({'account_oid': accountOid}, {'$push': {'items': newItem}})
        else:
            searchItem = bagDb.find_one(
                {'account_oid': accountOid, 'items': {'$elemMatch': {'item_id': {'$in': [itemId]}}}},
                {'_id': 0,'items': 1}
            )

            havingAmount = searchItem['items'][0]['amount']
            
            bagDb.update_one(
                {'account_oid': accountOid, 'items.item_id': itemId},
                {'$set': {'items.$.amount': havingAmount + amount}}
            )

    # 新增到交易紀錄  
    transactionRecordDb.insert_one({
        'uid': uid,
        'good_id': goodId,
        'discount': 1,
        'price': goodPrice,
        'cost_item': goodCostItem,
        'amount': amount
    })

    # 扣除交易花費
    if(goodCostItem == 'i0001'): # mu
        serverMu -= goodPrice
    elif(goodCostItem == 'i0002'): # konpeito
        serverKonpeito -= goodPrice
    elif(goodCostItem == 'i0009'): # poo
        serverPoo -= goodPrice
    else:
        return jsonify({
                'statusCode': 403,
                'failedMsg': '請檢察產品貨幣單位'
            })

    costItemMap = {
        'i0001': {'mu': serverMu},
        'i0002': {'konpeito': serverKonpeito},
        'i0009': {'poo': serverPoo}
    }

    commanderDb.update_one({'account_oid': accountOid}, {'$set': costItemMap[goodCostItem]})

    data = {
        'leftNumber': leftAmount - amount,
        'mu': serverMu,
        'konpeito': serverKonpeito,
        'poo': serverPoo,
        'status': '購買成功'
    }

    return jsonify(data)