class Debt:
    """Information retrieved from the debt section of the database."""
    def __init__(self, userID):
        """Upoin instantiation, retrieves the user's list of accounts, each as a list of\
        [0]Lender Name\
        [1]Account Balance\
        [2]Minium Payment\
        [3]Additional Payments (specified by user)
        [4]APR of the Account - Can be set to zero!\
        """
        selection = db.select (
            'budgetCalculator_debt',
            what = "lender, APR, balance, minimumPayment, additionalPayment",
            where='id='+userID
            )
        self.accounts = []
        for account in selection:
            self.account.append(
                [
                    account.lender,
                    account.balance,
                    account.minimumPayment,
                    account.additionalPayment,
                    account.APR
                    ]
                )
            
