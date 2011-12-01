#!/usr/bin/env python
def retrieve_user_debt (user_id, db):
    query = "SELECT account_id, account_name, balance_due, interest_rate, minimum_payment, extra_payment FROM budgetCalculator_Debt "
    query += "WHERE user_id=%s" % (user_id)
    result = db.query(query)

    user_accounts = {}

    if result:
        for row in result:    
            user_accounts[row.account_name] = {'account_id': row.account_id, 'balance_due' : row.balance_due, 'interest_rate' : row.interest_rate, 'minimum_payment' : row.minimum_payment, 'extra_payment' : row.extra_payment }
    return user_accounts	
