class User(object):
    pass

def loginUser(username, password, db):
    query = "SELECT id,firstName FROM budgetCalculator_Users "
    query += "WHERE email='"+username+"'  and password=PASSWORD('"+password+"')"
    result = db.query(query)
    if result:
        for row in result:
            uID = row.id
            name= row.firstName
        from web import setcookie
        setcookie('username', username)
        setcookie('id', uID)
        setcookie('name', name)
        return True
    else:
        return False
