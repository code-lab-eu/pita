from dividend_payment import DividendTransaction


class DividendCollection:
    def __init__(self):
        self.payments = []

    def append(self, dividend_payment: DividendTransaction):
        self.payments.append(dividend_payment)

    def is_empty(self):
        return not self.payments

    def get_fund_names(self):
        fund_names = []
        for payment in self.payments:
            if not payment.fund_name in fund_names:
                fund_names.append(payment.fund_name)
        return fund_names

    def get_fund_payments(self, fund_name):
        fund_payments = []
        for payment in self.payments:
            if payment.fund_name == fund_name:
                fund_payments.append(payment)
        return fund_payments

    def sort_by_date(self, reverse):
        self.payments.sort(key=lambda x: x.date_time, reverse=reverse)
