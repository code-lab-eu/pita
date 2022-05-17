class Transaction:
    def __init__(self, fund_name, domicile, date_time, transaction_type, number, share_price, currency, purchase_price):
        self.fund_name = fund_name
        self.domicile = domicile
        self.date_time = date_time
        self.transaction_type = transaction_type
        self.number = number
        self.share_price = share_price
        self.currency = currency
        self.purchase_price = purchase_price

    def __repr__(self):
        return 'Transaction fund name: %s, domicile: %s,  date: %s, type: %s, number: %s, share price: %s, currency: %s, purchase price: %s' % (self.fund_name, self.domicile, self.date_time, self.transaction_type, self.number, self.share_price, self.currency, self.purchase_price)
