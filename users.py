#!/usr/bin/env python

import database.database

class User(database.database.User):
    def load_debt(self):
        if self.check_login():

