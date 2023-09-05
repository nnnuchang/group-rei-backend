import pymongo

def dbConnect(c):
    print( 'database connecting')
    client = pymongo.MongoClient('mongodb://developer:A11123008@ericchang922.synology.me:27017/?authSource=group_rei')
    db = client['group_rei']

    
    col = db[str(c)]
  

    return col

