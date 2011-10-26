#!/usr/bin/env python

def retrieve_user_debt (uID, db):
   query = "SELECT accounts FROM budgetCalculator_Debt "
   query += "WHERE uID=%s" % (uID)
   result = db.query(query)

   user_accounts = {}
   
   if result:
	for row in result:    
	    user_accounts[row.account_name] = {'balance_due' : row.balance_due, 'interest_rate' : row.interest_rate, 'minimum_payment' : row.minimum_payment, 'extra_payment' : row.extra_payment }
   return user_accounts	
	    

