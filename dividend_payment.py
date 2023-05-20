class DividendPayment:
    def __init__(
        self,
        fund_name,
        company,
        dividend,
        country,
        tax_paid,
        currency,
        purchase_price,
        date_time,
    ):
        self.fund_name = fund_name
        self.company = company
        self.dividend = dividend
        self.country = country
        self.tax_paid = tax_paid
        self.currency = currency
        self.purchase_price = purchase_price
        self.date_time = date_time

    def __repr__(self):
        return (
            "Dividend fund_name: %s, company: %s, dividend: %s, country: %s, tax_paid: %s, currency: %s, purchase price: %s, date_time: %s"
            % (
                self.fund_name,
                self.company,
                self.dividend,
                self.country,
                self.tax_paid,
                self.currency,
                self.purchase_price,
                self.date_time,
            )
        )
