from dbConnection import dbConnect

# 登出所有裝置
def logoutAll(uid):
    loginDb = dbConnect('login_record')

    allLoginData = loginDb.update_many({'uid': uid}, {'$set': {'is_login': False}})
    print(uid, allLoginData.modified_count, "documents of login_record updated")