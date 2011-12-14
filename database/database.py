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

    def update(self, data, col_match, val_match):
        query_string = "UPDATE %s SET " % self.table
        cols=[]
        vals=[]
        for key in data:
            columns.append(key)
            if data[key]:
                vals.append(data[key])
            else:
                vals.append("")
        i = 0
        while i < len(cols):
            query_string + " %s=\"%s\" " % (cols[i], vals[i])
        query_string += "WHERE %s=\"%s\" " % (col_match, val_match)
        self.query(query_string)



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
             if result:
                 for row in result:
                     return row.user_id
             else:
                 return False

    def link_debt (self):
        self.debt = Debt_Account(self.get_id())

    def link_income(self):
        self.income = Income_Source(self.get_id())

class Money(object):
    def __init__(self, user_id, table):
        self.__user_id = user_id
        self.__db = Database(table)
        self.accounts = []
        self.__schematic = {}

    def __account_schematic (self, schematic):
        self.__schematic = schematic

    def __column_list(self):
        a = []
        if self.__schematic:
            for entry in self.__schematic:
                a.append(entry)
        return a

    def __float_values(self):
        a = []
        if self.__schematic:
            for entry in self.__schematic:
                if self.__schematic[entry] == "float":
                    a.append(entry)
        return a

    def __encrypt_values(self, values):
        cipher = Cipher(self.__user_id)
        for value in values:
            values[value] = cipher.encrypt(values[value])
        return values

    def get_accounts(self):
        cipher = Cipher(self.__user_id)
        search = Search(self.__db.table, "user_id", self.__user_id, self.__column_list())
        search.run()
        for result in search.result:
            account = {}
            for datum in result:
                if datum not in self.__float_values():
                    account[datum] = cipher.decrypt( result[datum] )
                elif datum in self.__float_values():
                    account[datum] = float( cipher.decrypt( result[datum] ) )
            self.accounts.append(account)

    def add_account(self, account):
        account = self.__encrypt_values(account)
        account['user_id'] = self.__account_schematic['user_id']
        self.__db.insert(account)

    def update_account(self, account_info):
        self.__db.update(self.__encrypt_values(account_info), "user_id", self.__user_id)

    def delete_acount(self, col, val):
        query_string = "DELETE FROM %s WHERE %s = \"%s\"" % (self.__db.table, col, val)
        self.__db.query(query_string)

class Debt_Account(Money):
    def __init__(self, user_id):
        Money.__init__(user_id, "debt")
        schematic = {
                "account_name"          :   "string",
                "account_balance"       :   "float",
                "account_interest_rate" :   "float",
                "account_min_payment"   :   "float",
                "account_extra_payment" :   "float",
                "account_id"            :   "int",
                "user_id"               :   user_id
                }
        self.__account_schematic(schematic)

class Income_Source(Money):
    def __init__(self, user_id):
        Money.__init__(user_id, "income")
        schematic = {
                "source_name"           :   "string",
                "source_amount"         :   "float",
                "source_savings"        :   "float",
                "user_id"               :   "user_id"
                }
        self.__account_schematic(schematic)
