from flask import Blueprint, request, jsonify

from bson import ObjectId

from public.dbConnection import dbConnect
from public.checkToken import checkToken

chip = Blueprint('chip',  __name__)

timezone = 'Asia/Taipei'
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
    objItemOid = ObjectId(requestData['objItemOid'])
    U = requestData['U']
    mu = requestData['mu']

    tokenStatus = checkToken(token, timezone)

    if tokenStatus['status'] is not True:
        data = tokenStatus
        return jsonify(data)
    else:
        uid = tokenStatus['uid']

    objItemDb = dbConnect('obj_item')
    bagDb = dbConnect('bag')

    accountDb = dbConnect('account')
    commanderDb = dbConnect('commander')

    itemDb = dbConnect('items')
    chipDb = dbConnect('chip')
    chipLevelDb = dbConnect('chip_level')

    accountOid = accountDb.find_one({'uid': uid})['_id']
    objItemRecord = objItemDb.find_one({'_id': objItemOid})

    commanderRecord = commanderDb.find_one({'account_oid': accountOid})

    itemId = objItemRecord['item_id']
    oldExp = objItemRecord['exp']

    try:
        serverMu = int(commanderRecord['mu'])
        havingMu = int(mu)

        if serverMu!= havingMu:
            print('m: {}\n'.format(serverMu))
            return jsonify({
                'statusCode': 403,
                'failedMsg': '數值驗證失敗(konpeito)'
            })
    except:
        return jsonify({
                'statusCode': 400,
                'failedMsg': '資料型態錯誤(konpeito)'
            })

    # 確認是否擁有道具
    objItemsList = bagDb.find_one({'account_oid': accountOid})['obj_items']
    print(objItemsList)

    if objItemOid not in objItemsList:
        return jsonify({
            'statusCode': 404,
            'failedMsg': '晶片不存在或不屬於使用者'
        })

    # 計算經驗、扣除素材
    UType = {
        'i0010': 100, # u238
        'i0011': 1000, # u235
        'i0012': 10000 # u234
    }

    upExp = 0
    cost = 0
    for i in U:
        # 計算經驗
        category = i['UType']
        num = i['UNum']
        exp = UType[category] * int(num)

        upExp += exp

        # 計算花費
        cost += exp * 10
        if (serverMu - cost) < 0:
            print('mu not enough')
            break

        # 扣除素材
        bagDb.update_one(
            {'account_oid': accountOid, 'items.item_id': category},
            {'$inc': {'items.$.amount': -num}}
        )

    # 確認經驗上限
    itemOid = itemDb.find_one({'item_id': itemId})['_id']
    chipLevel = chipDb.find_one({'item_oid': itemOid})['chip_level_id']
    maxExp = chipLevelDb.find_one({'chip_level_id': chipLevel})['max_experience']

    if oldExp + upExp > maxExp:
        upExp = maxExp - oldExp

    # 更新經驗
    objItemDb.update_one({'_id': objItemOid}, {'$inc': {'exp': upExp}})

    # 扣除立日
    commanderDb.update_one({'account_oid': accountOid}, {'$inc': {'mu': -cost}})

    newMu = dbConnect('commander').find_one({'account_oid': accountOid})['mu']
    newExp = dbConnect('obj_item').find_one({'_id': objItemOid})['exp']

    data = {
        'mu': newMu,
        'expAfter': newExp
    }

    return jsonify(data)



