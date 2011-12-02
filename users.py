def login_user (username, password, db):
    import modules.security.hash_this as hash_this
    username = hash_this(username)
    password = hash_this(password)

    query = "SELECT user_id, first_name FROM budget_calculator_users "
    query += "WHERE email=PASSWORD('%s') AND password=PASSWORD('%s')" % (username, password)

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

def register_user():
    import web
    import modules.security
    import modules.database
    i = web.input()
    username = modules.security.hash_this(i.username)
    password = moduules.security.hash_this(i.password)

    query_string = "INSERT INTO budget_calculator_users (email, first_name, last_name, password)"
    query_string += " VALUES ("
    query_string += " PASSWORD('%s'), '%s', '%s', PASSWORD('%s') )" % (username, i.first_name, i.last_name, password)
    
    try:
        db = modules.database.connect_to_database()
        db.query(query_string)
        return True
    except:
        return False
