def retrieve_user_income (user_id, db):
    user_income = {}
    
    query = "SELECT source_id, source_name, source_amount, source_savings FROM budget_calculator_income WHERE user_id=%s" % (user_id)
    result = db.query(query)

    if result:
        for row in result:
            user_income[row.source_name] = {}
            user_income[row.source_name]['source_id'] = row.source_id
            user_income[row.source_name]['source_amount'] = row.source_amount
            user_income[row.source_name]['source_savings'] = row.source_savings
    return user_income
