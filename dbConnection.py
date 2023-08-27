import pymongo

def dbConnect(c):
    print( 'database connecting')
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['testDB']
    col = db[str(c)]

    return col

