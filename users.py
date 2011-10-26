class User(object):
    pass

def loginUser(username, password, db):
    query = "SELECT uID,firstName FROM budgetCalculator_Users "
    query += "WHERE email='"+username+"'  and password=PASSWORD('"+password+"')"
    result = db.query(query)
    if result:
        for row in result:
            uID = row.uID
            name= row.firstName
        from web import setcookie
        setcookie('uID', uID)
        setcookie('first_name', name)
        return True
    else:
        return False

class UserSession(object):
    def __init__(self, userID, db, app):
        import web.session
        store = web.session.DBStore(db, 'sessions')
        self.session = web.session.Session(app, store, initializer={"user", userID})
        
