class User(object):
    pass

def loginUser(username, password, db):
    result = db.select(
            'clearpointCalc_users',
            where = "username='"+username+"' and password='"+password+"'",
            what = "username,firstName"
            )
    if result:
        from web import setcookie
        setcookie('username', username, 3600)
        return True
    else:
        return False
