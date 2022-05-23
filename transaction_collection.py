from transaction import Transaction


class TransactionCollection:
    def __init__(self):
        self.transactions = []

    def append(self, transaction: Transaction):
        self.transactions.append(transaction)

    def is_empty(self):
        return not self.transactions

    def get_fund_names(self):
        fund_names = []
        for transaction in self.transactions:
            if not transaction.fund_name in fund_names:
                fund_names.append(transaction.fund_name)
        return fund_names

    def get_fund_transactions(self, fund_name):
        fund_transactions = []
        for transaction in self.transactions:
            if transaction.fund_name == fund_name:
                fund_transactions.append(transaction)
        return fund_transactions

    def sort_by_date(self, reverse):
        self.transactions.sort(key=lambda x: x.date_time, reverse=reverse)

    def calc_total_shares(self):
        for fund_name in self.get_fund_names():
            transactions = self.get_fund_transactions(fund_name)
            transactions.sort(key=lambda x: x.date_time, reverse=False)
            total_shares = 0
            for transaction in transactions:
                total_shares += transaction.number
                transaction.total = total_shares
