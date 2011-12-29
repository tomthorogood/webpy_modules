#!/usr/bin/env python
#Non-native libraries
import web

#Self-created libraries
import formatting, security

#Native libraries
import random, string

append_with_commas = formatting.append_with_commas  # Turns a list into "entry1, entry2, entry3" string
hash_this = security.obfuscate.hash_this            # Performs one-way hashing on a string
convert_to_tinyint = formatting.convert_to_tinyint  # Converts miscellaneous values to tinyints for mysql insertion
Cipher = security.cipher.Cipher                     # Creates an instance of a PyCrypto AES module
Querify = web.db.SQLQuery                           # Paramaterizes a query string
Paramify = web.db.SQLParam                          # Paramterizes a query string value to maintain binary integrity

# NOTE: When using the Database.query() method, you do not need to Querify a list; the method does this implicitly if
# a list is passed to it. HOWEVER, you should pass any values in the list as a Paramified version:
# ["SELECT foo FROM bar WHERE meat=", Paramify('steak')]


class Database(object):
    """Uses a web.py database object to store database values for simpler querying."""
    def __init__(self, table, db='clearpoint_resolutions'):
        self.connection = web.database(dbn='mysql', user='cpres', pw='allayallay', db=db)
        self.table = table

    def query(self, q):
        """
        Checks to see if the query passed into the method is a list. If so, Querifies the list.
        If it's a string, querifies a list where the string is the only entry.
        """
        if not isinstance(q, list):
            q = Querify([q])
        else:
            q = Querify(q)

        return self.connection.query(q)
    
    def populate_from(self, key, dictionary):
        """
        Populates a dictionary whose keys are columns in the database.
        The dictionary values are then set to the values in the database columns.
        """
        values = []
        for entry in dictionary:
            values.append(entry)
        q = [append_with_commas('SELECT ', values, ' FROM ', False), self.table, ' WHERE ', key[0], '=', Paramify(key[1])]
        result = self.query(q)
        if result:
            for row in result:
                for entry in dictionary:
                    dictionary[entry] = row[entry]
        return dictionary

    def insert (self, data ):
        q = ["INSERT INTO ", self.table, " "]
        columns = []
        values = []
        for key in data:
            columns.append(key)
            if data[key]:
                values.append(Paramify(data[key]))
            else:
                values.append('')
        q.append( append_with_commas('(', columns, ") VALUES (", False) )
        q.append( append_with_commas('', values, ")", True) )
        self.query(q)

    def update(self, data, col_match, val_match, test=False):
        query_list = []
        q0 = "UPDATE %s SET " % self.table
        query_list.append(q0)
        cols=[]
        vals=[]
        for key in data:
            cols.append(key)
            if data[key]:
                vals.append(data[key])
            else:
                vals.append("")
        i = 0
        while i < len(cols):
            query_list.append(cols[i]+'=')
            query_list.append(Paramify(vals[i]))
            if i <= len(cols)-2:
                query_list.append(', ')
            i+=1
        query_list.append(" WHERE " + col_match +"=")
        query_list.append(Paramify(val_match))
        if not test:
            self.query(query_list)
        else:
            print Querify(query_list)
    
    def delete(self, match=None, param=None, force=False):
        """
        Deletes data from a table. 
        db.delete( match=('username', 'test_user')) // Will delete entries from a table where the username is "test_user".
        db.delete( match=('username', 'test_user'), param="AND email_address IS NULL") //same as above, but where no email address exists
        db.delete( match=('username', '*test_user') ) //performs a mysql Password() hash on 'test_user' first.
        db.delete( match=(1,1), force=True ) //will delete all entries from a table 
        """
        try:
            q = ["DELETE FROM %s WHERE " %  self.table,'','']
            if match:
                if match[0] == match[1] and not force:
                    raise UserWarning #Prevents an accidental deletion of all entries in table. 
                q[1] = "%s = " % match[0]
                if match[1][0] == '*':
                    q[2] = "PASSWORD(\"%s\")" % Paramify(match[1][1:])
                else:
                    q[2] = Paramify(match[1])
            if param:
                q[len(q)] = param
            if (len(q) > 1):
                self.query(q)
        except UserWarning:
            print "You are trying to delete all entries in a table without explicitly forcing this! Try setting force=True if that's what you really want to do."


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
        query_string += self.db.table + " WHERE %s= '%s'" % (column, Paramify(value))
        return query_string

    def run(self):
        result = self.db.query(self.query)
        for row in result:
            branch = Branch(row.branch_id)
            self.result.append(branch.data)

class Session(object):
    """
    This defines a user session. 
    usage:
        s = Session(new=False)
            Calling this way will simply attempt to find the user's session ID stored in their cookie.
        s = Session(user_id='foobar')
            Instantiating in this manner will generate a new session_id, store in the database table, and set a local cookie.
        s = Session(new=False, length=600).cleanup()
            This will cleanup the database table, deleting sessions that have been inactive for more then 10 minutes.
            This can also be accomplished by setting length=10, as the class assumes values less than 60 are intended to be minutes.
        s = Session(new=False, user_id='foobar', length=600).cleanup()
            Same as above, but this will only run if there is a local cookie stored and it is attributed to the user 'foobar'.
    """
    def __init__(self, new = True, user_id = None, session_id = None, length=1200):
        self.db = Database('sessions')
        self._id = session_id
        if length < 60:
            self.length = length * 60   # length is set in seconds; if someone passes a length of less than 60 seconds, assume they attempted to pass minutes
        else:                           # and multiply the passed number by 60. Default is 20 minutes (1200 seconds) 
            self.length = length
        if new and user_id:
            self._id = self.generate_id(user_id)
            self.store_session(user_id)
        elif not new and user_id:
            self._id = self.get_cookie()
            if not self._id:
                raise UserWarning
        elif not new and not user_id:
            self._id = False
            
    def generate_id(self, user_id):
        pre_hash = ""
        for num in range(user_id):
            pre_hash += random.choice(string.lowercase)
            pre_hash += random.choice(string.digits)
        return hash_this(pre_hash)

    def store_session(self, user_id):
        q = ['','','']
        q[0] = "INSERT INTO %s (session_id, user_id) VALUES (" % self.db.table
        q[1] = "\"%s\", '%s'" % ( Paramify(self._id), Paramify(user_id) )
        q[2] = ")"
        self.db.query(q)

    def set_cookie(self):
        web.setcookie('session_id', self._id)

    def get_cookie(self):
        try:
            return web.cookies().session_id
        except:
            return False

    def ping(self):
        """
        Pings a user session to keep it active. Every 100 pings will clean up the session table.
        usage: 
            sesh = Session(new=False, user_id='foo')
            sesh.ping()
            
            The above code retrieves the cookie on the local machine, ensures the user_id is valid for the session_id, and updates the session
            to keep it active.
        """
        p = 1
        q = "SELECT ping FROM %s ORDER BY ping DESC LIMIT 1" % self.db.table
        r = self.db.query(q)
        if r:
            p = int(r[0].ping) + 1
        if p > 100:
            p = 1
            self.db.update({"ping" : p}, "session_id", self._id)
            self.cleanup()
        else:
            self.db.update({"ping" : p}, "session_id", self._id)

    def cleanup(self):
        """
        Cleans up the session database table. Called automatically every 100 pings, but can be called explicitly if necessary.
        """
        param = "NOW() - last_activity) > %s" % self.length
        self.db.delete(param=param)

class User(object):
    def __init__(self, preferences = {}):
        self.db = Database('users')
        self.__define__ (preferences)
    
    def __define__(self, prefs):
        self.preferences = {}
        if self.check_login() and prefs:
            for i in prefs:
                if prefs[i].lower() == "checkdb":
                    q = ['','']
                    q[0] = "SELECT %s FROM %s" % (i, self.db.table)
                    q[1] = " WHERE %s='%s'" % ('user_id', Paramify(self.get_id() ))
                    self.preferences[i] = self.db.query(q)[0][i]
                else:
                    l = prefs[i].split('set ')
                    self.preferences[i] = ' '.join(l)[1:]
                    if self.preferences[i] == 'True':
                        self.preferences[i] = True
                    elif self.preferences[i] == 'False':
                        self.preferences[i] = False

    def login (self, username, password):
        q = ["SELECT user_id FROM ", self.db.table, " WHERE username=PASSWORD(", Paramify(hash_this(username)), ") AND password=PASSWORD(", Paramify(hash_this(password)), ")"]
        result = self.db.query(q)
        user_id = None
        if result:
            user_id = result[0].user_id
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
            self.session.ping()
            return True
        else:
            return False

    def add(self, username, password):
        email = username
        username = hash_this(username)
        password = hash_this(password)
        q = ["INSERT INTO ", self.db.table, "(username, password) VALUES (PASSWORD(", Paramify(username), "),PASSWORD(", Paramify(password), "))"]
        self.db.query(q) 
        q = ["SELECT username, user_id FROM ", self.db.table, " WHERE username = PASSWORD(", Paramify(username), ")"]
        result = self.db.query(q)
        user_id = ""
        key_request = ""
        if result:
            r = result[0]
            user_id = r['user_id']
            key_request = r['username']
            cipher = Cipher(key_request)
            encrypted_email = cipher.encrypt(email)
            self.db.update({'email_address' : encrypted_email}, 'user_id', user_id)
        else:
            self.error = "We're sorry, but you could not be added to the database. Please try again later."

    def get_id (self, plain=False, username=None):
         if self.check_login():
             query_string = "SELECT user_id FROM %s where session_id = '%s'" % (self.session.db.table, Paramify(self.key))
             try:
                 user_id = self.db.query(query_string)[0].user_id
             except IndexError:
                 return None
             if user_id and not plain and not username:
                 return user_id
             elif not user_id and not username:
                 return False
             elif not plain and username:
                 q = ["SELECT user_id FROM %s WHERE username = PASSWORD('%s')" % (self.db.table, Paramify(hash_this(username)))]
                 try:
                     return self.db.query(q)[0].user_id
                 except IndexError:
                     return None
             elif user_id and plain:
                 q = ["SELECT username,email_address FROM %s WHERE user_id = '%s'" % (self.db.table, Paramify(user_id))]
                 try:
                    row = self.db.query(q)[0]
                    key = row.username
                    cipher = Cipher(key)
                    return cipher.decrypt(row.email_address)
                 except IndexError:
                    return None
         elif username:
             q = ["SELECT user_id FROM %s WHERE username = PASSWORD('%s')" % (self.db.table, Paramify(hash_this(username)))]
             return self.db.query(q)[0].user_id
         else:
             return False

    def link_debt (self):
        self.debt = Debt_Account(self.get_id())

    def link_income(self):
        self.income = Income_Source(self.get_id())

    def exists(self, val):
        """
        Checks to see whether a username already exists in the database.
        """
        q = ["SELECT username FROM %s " % self.db.table, "WHERE username = PASSWORD('%s')" % Paramify(hash_this(val))]
        if not self.db.query(q):
            return False
        else:
            return True

    def match_password(self, val):
        """
        Checks to see whether the passed password matches that which is attached to the currently logged in user.
        """
        k = "PASSWORD('%s')" % Paramify(hash_this(val))
        z = ["SELECT %s" % k]
        val = self.db.query(z)[0][k]
        q = ['SELECT %s FROM %s' % ('password', self.db.table),'']
        q[1] = " WHERE %s = %s" % ('user_id', Paramify( self.get_id() ) )
        try:
            return self.db.query(q)[0].password == val
        except:
            return False

    def update_password(self, new):
        try:
            q = ['UPDATE %s SET %s=PASSWORD(\"%s\")' % (self.db.table, 'password', Paramify(hash_this(new))),'']
            q[1] = "WHERE %s = %s" % ('user_id', Paramify( self.get_id() ) )
            self.db.query(q)
            self.error = None
        except:
            self.error = "There was an error processing your request."

    def update_preferences(self, new):
        try:
            for preference in self.preferences:
                self.preferences[preference] = convert_to_tinyint(new[preference])
            self.db.update(self.preferences, "user_id", self.get_id())
            self.error = None
        except:
            self.error = "There was an error processing your request."


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

    def delete_account(self, col, val):
        query_string = "DELETE FROM %s WHERE %s = '%s'" % (self.__db.table, col, Paramify(val))
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
