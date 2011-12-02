def connect_to_database():
    import web
    return web.database(dbn='mysql', user='clearpointCalc', pw='', db='clearpoint')
