#!/usr/bin/env python
#Non-native libraries
import web

#Self-created libraries
import formatting, security

#Native libraries
import random, string,copy,time,json

def debug(data):
    """
    Messy function for emailing the site admin in case of an emergency.
    """
    f = open('admin_log', 'a')
    w = "\n"+time.asctime()+"\t"
    try:
        f.write(w+repr(data)+'\n')
    except:
        f.write(w+type(data)+'\n')
append_with_commas = formatting.append_with_commas  # Turns a list into "entry1, entry2, entry3" string
hash_this = security.obfuscate.hash_this            # Performs one-way hashing on a string
convert_to_tinyint = formatting.convert_to_tinyint  # Converts miscellaneous values to tinyints for mysql insertion
Cipher = security.cipher.Cipher                     # Creates an instance of a PyCrypto AES module
Querify = web.db.SQLQuery                           # Paramaterizes a query string
Paramify = web.db.SQLParam                          # Paramterizes a query string value to maintain binary integrity

# NOTE: When using the Database.query() method, you do not need to Querify a list; the method does this implicitly if
# a list is passed to it. HOWEVER, you should pass any values in the list as a Paramified version:
# ["SELECT foo FROM bar WHERE meat=", Paramify('steak')]


class Time_Difference(object):
    def __init__(self, sec_val,operator, count, period):
        """
        Takes as arguments a time in seconds, a textual operator, the number the time in secnods is being compared to, and the period type. 
        Returns a boolean automatically.
        Example:
            over_a_month = Time_Difference(2419201, "greater than", 1, "month")
            if over_a_month:
                print "It's been over a month!"
        """        
        functions = {
                "second"    :   self.second,
                "minute"    :   self.minute,
                "hour"      :   self.hour,
                "day"       :   self.day,
                "week"      :   self.week,
                "month"     :   self.month,
                "year"      :   self.year
                }
        self.result = functions[period](sec_val,operator, count)

    def operations(self, num1, operator, num2):
        if operator == "greater than":
            return num1 > num2
        elif operator == "less than":
            return num1 < num2
        elif operator == "equal to":
            return num1 == num2
        elif operator == "not equal to":
            return num1 != num2
    def second (self, seconds, operator, count):
        return self.operations(seconds, operator, count)
    
    def minute (self, seconds, operator, count):
        return self.operations((seconds/60),operator,count)
    
    def hour (self, seconds, operator, count):
        return self.minute((seconds/60),operator,count)
    
    def day (self, seconds, operator, count):
        return self.hour((seconds/24),operator,count)

    def week (self, seconds, operator, count):
        return self.day((seconds/7), operator, count)

    def month (self, seconds, operator, count):
        return self.week((seconds/4),operator,count)
    
    def year (self, seconds, operator, count):
        return self.month((seconds/12), operator,count)

class Database(object):
    """Uses a web.py database object to store database values for simpler querying."""
    def __init__(self, table, db='budget_calculator'):
        self.connection = web.database(dbn='mysql', user='cpcalc', pw='tikkitonga', db=db)
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
        print repr(q)

        return self.connection.query(q)

    def unzip(self, data):
        return data.keys(), data.values()

    
    def populate_from(self, key, dictionary):
        """
        Populates a dictionary whose keys are columns in the database.
        The dictionary values are then set to the values in the database columns.
        """
        values, trash = self.unzip(dictionary)
        del trash
        q = [append_with_commas('SELECT ', values, ' FROM ', False), self.table, ' WHERE ', key[0], '=', Paramify(key[1])]
        result = self.query(q)
        if result:
            for row in result:
                for entry in dictionary:
                    dictionary[entry] = row[entry]
        return dictionary

    def insert (self, data ):
        """
        Adds dictionary data into a table, where the data is in {column: value} format.
        """
        q = ["INSERT INTO ", self.table, " "]
        columns, values = self.unzip(data)
        q.append( append_with_commas('(', columns, ") VALUES (", False) )
        q.append( append_with_commas('', values, ")", True) )
        self.query(q)

    def time_passed(self, column, match, count, period):
        """
        Returns a boolean whether or not a certain amount of time has passed since a timestamp was set in the database.
        example:
            db.time_passed("last_login", ("user_id", 1), 1, "month")
        """
        q = ["SELECT NOW()-", column, " FROM ", self.table, " WHERE ", match[0], "=", Paramify(match[1])]
        debug(q)
        timestamp_diff = self.query(q)[0]
        debug(copy.copy(timestamp_diff))
        difference = Time_Difference(int(timestamp_diff['NOW()-last_login']), "greater than", count, period)
        return difference.result

    def update(self, data, col_match, val_match, test=False):
        """
        Updates a row.
        Data should be in {column:value} format. col_match and val_match represent 'where col_match = val_match".
        The test param simply prints out the query without actually querying the database. Useful for, well, testing.
        """
        query_list = ["UPDATE %s SET " % self.table]
        cols,vals = self.unzip(data)
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
                try:
                    if match[1][0] == "*":
                        q[2] = "PASSWORD(\"%s\")" % Paramify(match[1][1:])
                    else:
                        q[2] = Paramify(match[1])
                except TypeError:
                        q[2] = Paramify(match[1])
            if param:
                q[len(q)-1] = param
            if (len(q) > 1):
                self.query(q)
        except UserWarning:
            print "You are trying to delete all entries in a table without explicitly forcing this! Try setting force=True if that's what you really want to do."

class Session(object):
    """
    This defines a user session. 
    usage:
        s = Session(new=False)
            Calling this way will simply attempt to find the user's session ID stored in their cookie.
        s = Session(user_id=6)
            Instantiating in this manner will generate a new session_id, store in the database table, and set a local cookie.
        s = Session(new=False, length=600).cleanup()
            This will cleanup the database table, deleting sessions that have been inactive for more then 10 minutes.
            This can also be accomplished by setting length=10, as the class assumes values less than 60 are intended to be minutes.
        s = Session(new=False, user_id=6, length=600).cleanup()
            Same as above, but this will only run if there is a local cookie stored and it is attributed to the user #6.
        s = Session(new=False, user_id=6, test=True)
            Will initiate a test session; useful for debugging. Test sessions will not be stored in the database, but will
            act like real sessions. 
    """
    def __init__(self, new = True, user_id = None, session_id = None, length=1200, test=False):
        """
        You can explicitly set most of this params for test cases. 
        Setting new=False will not generate a new session in the database.
        length determines the amount of time after which a session will be deactivated.
        """
        self.debug = test
        self.db = Database('sessions')
        self._id = session_id
        if length < 60:
            self.length = length * 60   # length is set in seconds; if someone passes a length of less than 60 seconds, assume they attempted to pass minutes
        else:                           # and multiply the passed number by 60. Default is 20 minutes (1200 seconds) 
            self.length = length
        if new and user_id and not test:
            #Typical behaviour. Generates a session ID and stores it in the database.
            self._id = self.generate_id(user_id)
            self.store_session(user_id)
        elif test and not new:
            #This simply generates a session id.
            self._id = self.generate_id(user_id)
        elif new and not user_id and not test:
            #If a user_id was not passed in, but a new session is expected, check to see if the user is already in the session table.
            self._id = self.get_cookie()
        elif not new and user_id and not test:
            #Same as above, but raises an exception if a user is supposed to be logged in but has no cookie.
            self._id = self.get_cookie()
            if not self._id:
                raise UserWarning
        elif not new and not user_id and not test:
            #In any other case, set the id of the session to false and leave it at that.
            self._id = False
            
    def generate_id(self, user_id):
        """
        Generates a session ID based on the user ID.
        Since user id's are all digits, it simply strings together random numbers and letters from the
        user id, then hashes it.
        """
        pre_hash = ""
        for num in range(user_id):
            pre_hash += random.choice(string.lowercase)
            pre_hash += random.choice(string.digits)
        return hash_this(pre_hash)

    def store_session(self, user_id):
        """
        Stores a session in the database table.
        """
        q = ['','','']
        q[0] = "INSERT INTO %s (session_id, user_id) VALUES (" % self.db.table
        q[1] = "\"%s\", '%s'" % ( Paramify(self._id), Paramify(user_id) )
        q[2] = ")"
        self.db.query(q)

    def set_cookie(self):
        """
        Sets a cookie in the user's browser. The cookie will only last until the user closes their browser.
        """
        web.setcookie('session_id', self._id)

    def get_cookie(self):
        """
        Attempts to retrieve a cookie from the user's browser.
        """
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
        param = "(NOW() - last_activity) > %s" % self.length
        self.db.delete(param=param)

class User(object):
    """
    The User class connects to the user table in the database.
    In this case, usernames are email addresses, and are not stored in plaintext.
    Usernames are hashed by the obfuscate method, and hashed again with MySQL's native password function.
    So are passwords. 
    The email_address column of the database must be set to binary. This is encrypted with the pycrypto library,
    using the MySQL hash of the username as a key.
    Instantiating a User object requires no arguments, but preferences can be set in dict form, and if desired,
    the test flag can be switched on to allow for debugging.
    """
    def __init__(self, preferences = {}, test=False):
        """
        Preferences should probably be deprecated.
        Set test to true if you are running command line tests and don't want it to deal with cookies.
        """
        self.db = Database('users')
        self.debug = test
        self.__define__ (preferences)
        self.__profile__ = [] 
    
    def __define__(self, prefs):
        """
        Obtains a user's preferences from the database, if set up.
        """
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

    def login (self, username=None, password=None, sensitive=False):
        """
        Chekcs the passed username and password against the database.
        Information should be sent into this method the same way it was passed into the add method.
        It returns no values, but if a user login is correct a session will be instantiated with the 
        user's information, and a cookie will be set.
        If there is a login error, the error property will no longer be None.
        When calling this method, you should have something like this:
        
        user = webpy_modules.User()
        user.login('myLogin', 'myPassword')
        if not user.error:
            print "You're logged in because you're awesome!"
        else:
            print user.error
        """
        q = ["SELECT user_id FROM ", self.db.table, " WHERE username=PASSWORD(", Paramify(hash_this(username.lower())), ") AND password=PASSWORD(", Paramify(hash_this(password)), ")"]
        result = self.db.query(q)
        user_id = None
        if result:
            user_id = result[0].user_id
        if user_id:
            if not self.debug:
                session = Session(user_id = user_id)
                session.set_cookie()
            else:
                self.test_id = user_id
            self.error = None
            self.month_elapsed = self.db.time_passed("last_login", ("user_id", user_id), 1, "month") 
            debug(self.month_elapsed)
        else:
            self.error = "Incorrect Login"

    def key_request(self):
        """
        Retrieves the user's unique cryptographic key.
        """
        q = ["SELECT username FROM ", self.db.table, " WHERE user_id = ", Paramify(self.get_id())]
        return self.db.query(q)[0].username

    def check_login (self):
        """
        Checks the database for a user session and checks the user's environment for a cookie.
        Additionally, pings the database table to allow for cleanup if necessary.
        """
        if self.debug:
            return True
        self.session = Session()
        self.key = self.session.get_cookie()
        if self.key:
            self.session.ping()
            return True
        else:
            return False

    def last_login(self):
        """
        Returns then number of days since the user last logged in.
        """

    def add(self, username, password):
        """
        Takes two strings, a username and a password,
        sends them both through the obfuscate method, then hashes them again in MySQL before storing them in the database.
        **THIS ASSUMES THAT A DUAL PASSWORD CHECK HAS ALREADY BEEN HANDLED!**
        This is the last step to adding a user. Make sure to do anything else you want to do before calling this.
        Sets the user.error flag if there's a problem, but returns no values.
        """
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
        """
        Looks up a user in the database if they are logged in.
        If plain is set to true, it will return their plaintext email address.
        Otherwise, it will return their user ID number (which, incidentally, is what is actually important).
        Plaintext availability should be at the discretion of the user. It is wise to allow them the option to 
        turn it off.
        """
        if self.debug:
            return self.test_id
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

    def decrypt_profile (self):
        self.profile = {}
        cipher = Cipher(self.key_request())
        columns = append_with_commas("SELECT ", self.__profile__, " FROM ", False)
        q = [columns, self.db.table, " WHERE user_id=", Paramify(self.get_id())]
        result = self.db.query(q)[0]
        for value in result:
            self.profile[value] = cipher.decrypt(result[value])

    def encrypt_profile (self, data):
        self.decrypt_profile()
        cipher = Cipher(self.key_request())
        for key in self.profile:
            value = data[key]
            if value != self.profile[key]:
                self.profile[key] = value
            self.profile[key] = cipher.encrypt(self.profile[key])
        self.db.update(self.profile, "user_id", self.get_id())

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
        """
        Changes a user's password.
        """
        try:
            q = ['UPDATE %s SET %s=PASSWORD(\"%s\")' % (self.db.table, 'password', Paramify(hash_this(new))),'']
            q[1] = "WHERE %s = %s" % ('user_id', Paramify( self.get_id() ) )
            self.db.query(q)
            self.error = None
        except:
            self.error = "There was an error processing your request."
    
    def update_preferences(self, new):
        """
        Updates a user's preferences.The parameter is a dict.
        """
        try:
            for preference in self.preferences:
                try:
                    self.preferences[preference] = convert_to_tinyint(new[preference])
                except KeyError: #If there's an error, default to the most private setting
                    self.preferences[preference] = 0
            self.db.update(self.preferences, "user_id", self.get_id())
            self.error = None
        except KeyError:
            self.error = None
        except:
            self.error = "There was an error processing your request. Please try again later."
