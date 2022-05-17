class DividendTransaction:
    def __init__(self, fund_name, company, dividend, country, tax_paid, currency, purchase_price):
        self.fund_name = fund_name
        self.company = company
        self.dividend = dividend
        self.country = country
        self.tax_paid = tax_paid
        self.currency = currency
        self.purchase_price = purchase_price

    def __repr__(self):
        return 'Transaction fund_name: %s, company: %s, dividend: %s, country: %s, tax_paid: %s, currency: %s, purchase price: %s' % (self.fund_name, self.company, self.dividend, self.country, self.tax_paid, self.currency, self.purchase_price)