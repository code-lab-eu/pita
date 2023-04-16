class Transaction:
    FUND_ALIASES = {
        'iShares S&P Global Clean Energy ETF': 'iShares Global Clean Energy UCITS ETF',
        "iShares FTSE/EPRA European Property EUR UCITS ETF": "iShares European Property Yield UCITS",
        "Amundi Index FTSE EPRA Nareit Global- ETF": "Amundi Index FTSE EPRA Nareit Global ETF",
        "iShares Core Euro Corporate Bond UCITS ETF": "iShares Core Euro Corp Bond ETF",
        "iShares MSCI World Small Cap UCITS ETF": "iShares MSCI World Small Cap",
    }

    TYPE_ALIASES = {
        'Market buy': 'Buy',
        'Bought': 'Buy',
        'TransferIn': 'Transfer in',
        'Delisting': 'Transfer out',
        'Sale': 'Sell',
        'Sold': 'Sell',
        'Purchase': 'Buy',
    }

    def __init__(self, fund_name, domicile, date_time, transaction_type, number, share_price, currency, purchase_price, profit_loss=None):
        self.fund_name = self.resolve_alias("fund_name", fund_name)
        self.domicile = domicile
        self.date_time = date_time
        self.transaction_type = self.resolve_alias("transaction_type", transaction_type)
        self.number = number
        self.share_price = share_price
        self.currency = currency
        self.purchase_price = purchase_price
        self.profit_loss = profit_loss

    def __repr__(self):
        return 'Transaction fund name: %s, domicile: %s,  date: %s, type: %s, number: %s, share price: %s, currency: %s, purchase price: %s' % (self.fund_name, self.domicile, self.date_time, self.transaction_type, self.number, self.share_price, self.currency, self.purchase_price)

    def resolve_alias(self, key, value):
        if key == 'fund_name':
            return self.FUND_ALIASES.get(value, value)
        elif key == 'transaction_type':
            return self.TYPE_ALIASES.get(value, value)
        return value
