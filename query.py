class Query(object):
    def __init__(self, command="select"):
        self.structure = None
        self.query = [command]
        self._components = {
                "command"   :   command not None,
                "link"      :   False,
                "act_on"    :   False,
                "where"     :   False
                "table"     :   False
               }

    def is_complete(self):
        return all([self._components[piece] is True for piece in self._components])

    def _structure(self, component, command=None):
            allowances = {
                "select"    :   {
                    "link"      :   ("from",),
                    "act_on"    :   (str,list,tuple),
                    "where"     :   "optional"
                    },
                "delete"    :   {
                    "link"      :   ("from",),
                    "where"     :   "required",
                    },
                "update"    :   {
                    "link"      :   ("set",),
                    "act_on"    :   (dict),
                    "where"     :   "required",
                    },
                "insert"    :   {
                    "link"      :   ("into","values"),
                    "act_on"    :   (dict),
                    "where"     :   "optional"
                    }
                }
            structures = {
                "select"    :   ("select", allowances["select"]["act_on"], allowances["select"]["link"][0], "table", allowances["select"]["where"]),
                "delete"    :   ("delete", allowances["delete"]["link"][0], "table", allowances["delete"]["where"]),
                "update"    :   ("update", "table", allowances["update"]["link"][0], allowances["update"]["act_on"], allowances["update"]["where"]),
                "insert"    :   ("insert", allowances["insert"]["link"][0], "table", allowances["update"]["act_on"], 
                    allowances["insert"]["link"][1], allowances["insert"]["act_on"], allowances["update"]["where"])
                }

        if not self.structure:
            if not command:
                raise AttributeError
           self.structure = structures[command]
        else:
            return 

    def set_table(self, table):
        component = "table"
        else:
            raise IndexError
        self._components[component] = True

    def _sql_assignment(self,dictionary):
        for entry in diectionary:
            yield entry+"=\"%s\"" % Parmify(dictionary[entry])

    def _sql_params(self, params):
        return [entry for entry in self.sql_assignment(params)]

    def act_on(self, columns):
        
        # If columns is in string form, we can assume we're selecting a 
        # single column. If a list, we're selecting multiple columns.
        # If a dictionary, we are updating or inserting.

        if isinstance(columns, str):
            self.query.append(columns)
        elif isinstance(columns, (list,tuple)):
            self.query.extend(columns)
        elif isinstance(columns, dict):
            self.query.extend(self._sql_params(columns))
        else:
            raise TypeError
        self._components['act_on'] = True

    def link(self, word):
        if word in ("set", "from"):
            self.query.append(word)
        else:
            raise ValueError
        self._components['link'] = True

    def where(self, params=False):
        if params:
            self.query.extend(self.sql_params(columns))
        self._components["where"] = True
