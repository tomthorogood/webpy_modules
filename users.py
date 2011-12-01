def login_user (username, password, db):
    query = "SELECT user_id, first_name FROM budget_calculator_users "
    query += "WHERE email='%s' AND password=PASSWORD('%s')" % (username, password)

    result = db.query(query)
    if result:
        for row in result:
            user_id = row.user_id
            first_name = row.first_name
        from web import setcookie
        setcookie('user_id', user_id)
        setcookie('first_name', first_name)
        return True
    else:
        return False

def logged_in():
    from web import cookies
    if cookies().user_id:
        return cookies().user_id
    else:
        return false	    	
