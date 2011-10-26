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

def logged_in():
    from web import cookies
    if cookies().uID:
        return cookies.uID
    else:
        return false	    	
