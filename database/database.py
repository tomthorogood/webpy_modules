#!/usr/bin/env python
import web
import formatting
import security.obfuscate
import security.cipher
import random
import string

append_with_commas = formatting.append_with_commas
hash_this = security.obfuscate.hash_this
Cipher = security.cipher.Cipher

class Database(object):
    """Uses a web.py database object to store database values for simpler querying."""
    def __init__(self, table):
        self.connection = web.database(dbn='mysql', user='clearpoint', pw='', db='clearpoint')
        self.table = table

    def query(self, query_string):
        return self.connection.query(query_string)

    def populate_from(self, key, dictionary):
        values = []
        for entry in dictionary:
            values.append(entry)
        query_string = "SELECT "
        query_string = append_with_commas(query_string, values, " FROM ", False)
        query_string += "%s WHERE %s=\"%s\"" % (self.table, key[0], key[1])
        result = self.query(query_string)
        if result:
            for row in result:
                for entry in dictionary:
                    dictionary[entry] = row[entry]
        return dictionary
    def insert (self, data ):
        query_string = "INSERT INTO %s (" % self.table
        columns = []
        values = []
        for key in data:
            columns.append(key)
            if data[key]:
                values.append(data[key])
            else:
                values.append('')
        query_string = append_with_commas(query_string, columns, ") VALUES (", False)
        query_string = append_with_commas(query_string, values, ")", True)
        self.query(query_string)
        return query_string


class Search(object):
    """A quick way of searching a database. The result will be stored as a list of dicts, each representing a row of data
    from the database, in {column : value} format."""
    def __init__(self, table, column, value, search_keys):
        if not isinstance(search_keys, (list, tuple)):
            search_keys = [search_keys]
        self.db = Database(table)
        self.query = self.build_query(search_keys, column, value)
        self.result = []

    def build_query(self, search_keys, column, value):
        values = []
        for key in search_keys:
            values.append(key)
        value = value.replace("%20", " ") #A workaround for parsing a URL encoded value
        query_string = append_with_commas("SELECT ", values, " FROM ", False)
        query_string += self.db.table + " WHERE %s=\"%s\"" % (column, value)
        return query_string

    def run(self):
        result = self.db.query(self.query)
        for row in result:
            branch = Branch(row.branch_id)
            self.result.append(branch.data)

class Session(object):
    def __init__(self, new = True, user_id = None, session_id = None):
        self.db = Database('sessions')
        if new and user_id:
            self._id = self.generate_id(user_id)
            self.store_session(user_id)
            
    def generate_id(self, user_id):
        pre_hash = ""
        for num in range(user_id):
            pre_hash += random.choice(string.lowercase)
            pre_hash += random.choice(string.digits)
        return hash_this(pre_hash)

    def store_session(self, user_id):
        query_string = "INSERT INTO %s (session_id, user_id) VALUES ('%s', '%s')" % (self.db.table, self._id, user_id)
        self.db.query(query_string)

    def set_cookie(self):
        web.setcookie('session_id', self._id)

    def get_cookie(self):
        try:
            return web.cookies().session_id
        except:
            return False

class User(object):
    def __init__(self):
        self.db = Database('users')
    
    def login (self, username, password):
        query_string = "SELECT user_id from %s WHERE username=PASSWORD('%s') AND password=PASSWORD('%s')" % (self.db.table, hash_this(username), hash_this(password))
        result = self.db.query(query_string)
        user_id = None
        for row in result:
            user_id = row.user_id
        if user_id:
            session = Session(user_id = user_id)
            self.error = None
            session.set_cookie()
        else:
            self.error = "Incorrect Login"

    def check_login (self):
        self.session = Session()
        self.key = self.session.get_cookie()
        if self.key:
            return True
        else:
            return False

    def add(self, username, password):
        username = hash_this(username)
        password = hash_this(password)
        query_string = "INSERT INTO %s (username, password) VALUES (PASSWORD('%s'), PASSWORD('%s'))" % (self.db.table, username, password)
        self.db.query(query_string)

    def get_id (self):
         if self.check_login(): 
             query_string = "SELECT user_id FROM %s where session_id = %s" % (self.session.db.table, self.key)
             result = self.db.query(query_string)
             for row in result:
                 return row.user_id

    def get_debt (self):
        """Creates self.debt, a list of dicts returned from the Search() class."""
        key_request = self.get_id()
        cipher = Cipher(key_request)
        self.debt = []
        columns = ["account_id", "account_name", "account_balance", "account_interest_rate", "account_monthly_payment", "account_extra_payment"]
        floats = ["account_balance", "account_interest_rate", "account_monthly_payment", "account_extra_payment"]
        search = Search("debt", "user_id", key_request, columns)
        search.run()
        for result in search.result:
            account = {}
            for datum in result:
                if datum not in floats:
                    account[datum] = cipher.decrypt( result[datum] )
                elif datum in floats:
                    account[datum] = float(cipher.decrypt(result[datum]) )
            self.debt.append(account)

    def get_income(self):
        """Creates self.income, a list of dicts return from the Search() class."""
        key_request = self.get_id()
        cipher = Cipher(key_request)
        self.income = []
        columns = ("source_id", "source_name", "source_amount", "source_savings")
        floats = ("source_amount", "source_savings")
        search = Search("income", "user_id", key_request, columns)
        search.run()
        for result in search.result:
            source = {}
            for datum in result:
                if datum not in floats:
                    source[datum] = cipher.decrypt( result[datum] )
                elif datum in floats:
                    source[datum] = float( cipher.decrypt( result[datum] ) )
            self.income.append(source)

