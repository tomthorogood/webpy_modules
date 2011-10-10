#!/usr/bin/python
import math, shelve

class Amortization:
    """Allows a user to obtain balance information at any point in the repayment process."""
    def __init__(self, currentBalance, APR, monthsElapsed, monthlyPayment):
        self.startingBalance = currentBalance
        self.periodicInterest = float(APR/12)
        self.startAtMonth = monthsElapsed
        self.monthlyPayment = monthlyPayment

    def elapsedBalance(self, balance, monthsElapsed):
        """Allows a user to predict a balance some months in advance based on pre-existing conditions."""
        interestFactor = math.pow( (1+self.periodicInterest), monthsElapsed)
        paymentFactor = self.monthlyPayment / self.periodicInterest
        leftSide = balance * interestFactor
        rightSide = paymentFactor * (interestFactor - 1)
        newBalance = leftSide - rightSide
        return newBalance

    def monthsToPayoff(self, balance):
        """Amortizes the loan so the user can see, based on a current payment, how long it will take to pay it off (in months)."""
        months = 0
        while balance > 0:
            months += 1
            balance = self.elapsedBalance(balance, 1)
            if balance <= 0:
                return months

class Method:
    """Defines either the "Snowball" or "Ladder" method, and sorts the user's list of cards accordingly."""
    def __init__(self, methodName, loanList):
        if methodName.lower() == "snowball":
            self.sortedBy = "APR"
        elif methodName.lower() == "ladder":
            self.sortedBy = "balance"
        print "Sorting cards by " + self.sortedBy
        self.list = self.sortList(loanList)
        self.monthsElapsed = 0
        self.result = ""

    def sortList(self, toBeSorted):
        sortedList = []
        identifiers = []
        for loan in toBeSorted:
            identifiers.append(toBeSorted[loan][self.sortedBy])
        if self.sortedBy == 'APR':              #Since the snowball method pays cards with the HIGHEST APR first, the list has to be sorted in reverse
            identifiers.sort(reverse=True)
        else:
            identifiers.sort()
        for identifier in identifiers:
            for loan in toBeSorted:
                if toBeSorted[loan][self.sortedBy] == identifier:
                    sortedList.append(toBeSorted[loan])
        return sortedList
    
    def amortize(self):
        """Shows the user how long it will take to pay off their current debt using the Snowball  method."""
#@TODO: Allow users to set their own additional payment!
        additionalPayment = 0                       #At the beginning, all payments are the minimum payments
        for account in self.list:
            print account['name']
            if self.monthsElapsed < 300:
                debt = Amortization(account['balance'], account['APR'], self.monthsElapsed, account['monthly payment'])
                if self.monthsElapsed == 0:
                    self.monthsElapsed += debt.monthsToPayoff(debt.startingBalance)
                else:
                    #For each card thereafter, start by first determining what the balance would be X months into paying only the minimum payments on the card.
                    balanceAtPaymentIncrease = debt.elapsedBalance(debt.startingBalance, self.monthsElapsed)
                    if balanceAtPaymentIncrease:
                    #If the card hasn't already been paid off...
                        debt.monthlyPayment += additionalPayment            #Adds any aditional payment (ie: minimum payments for cards already paid off)
                        nextPayoff = debt.monthsToPayoff(balanceAtPaymentIncrease)
                        if nextPayoff:
                            self.monthsElapsed += nextPayoff
                additionalPayment += debt.monthlyPayment
                self.result += str(self.monthsElapsed) + " months until " + account['name'] + " is paid off.\n\n"
            else:
                self.result += "Something has gone wrong. We're showing that it will take more than 25 years for you to pay off your debts. Double check your entries to make sure your balances and interest rates match your statements. Otherwise, please call us at 1-877-877-1995 so we can determine whether this is a fault within our application, or otherwise assist you in getting out of debt faster!"
        self.result +=  str(self.monthsElapsed) + " months until debt free using this  method, and starting with the "
        if self.sortedBy == 'APR':
            adjective = "highest"
        else: 
            adjective = "lowest"
        
        self.result +=  "account that has the " + adjective + " " + self.sortedBy + "."


class Snowball(Method):
    """Sorts a user's debt by APR and determines how long it will be before the debt is paid off."""
    def __init__(self, loanList):
        Method.__init__(self, 'snowball', loanList)
        self.amortize()
    
class Ladder(Method):
    """Sorts a user's debt by balance and determines how long it will be before the debt is paid off."""
    def __init__(self, loanList):
        Method.__init__(self, 'ladder', loanList)
        self.amortize()

