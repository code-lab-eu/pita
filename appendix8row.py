import datetime
from decimal import Decimal
from transaction import Transaction


class Appendix8Row:

    date: datetime = None
    domicile: str = None
    number: Decimal = None
    price_eur: Decimal = None

    def __init__(self, date: datetime, domicile: str):
        self.date = date
        self.domicile = domicile
        self.number = Decimal(0)
        self.price_eur = Decimal(0)

    def __repr__(self):
        return 'Appendix 8 row - date: %s, domicile: %s,  number: %s, price EUR: %s, price BGN: %s' % (self.date, self.domicile, self.number, self.price_eur, self.price_eur * Decimal(1.95583))

    def add_transaction(self, transaction: Transaction):
        transaction_date = transaction.date_time.date()
        if self.date != transaction_date:
            raise ValueError("Invalid transaction date. This is the Appendix 8 row for %s, got a transaction for %s" % (self.date, transaction_date))

        if self.domicile != transaction.domicile:
            raise ValueError("Invalid domicile. This is the Appendix 8 row for %s, got a transaction from %s" % (self.domicile, transaction.domicile))

        # For now we can only calculate the price in EUR since the euro and leva are locked. To add different currencies
        # we need to have the exact exchange rate of the day the stock was purchased.
        if transaction.currency != 'EUR':
            raise ValueError("Only EUR transactions are supported for Appendix 8. Got a transaction in %s" % transaction.currency)

        self.number += transaction.number
        self.price_eur += transaction.purchase_price
