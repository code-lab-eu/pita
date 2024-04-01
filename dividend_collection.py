from dividend_payment import DividendPayment


class DividendCollection:
    def __init__(self):
        self.payments = []

    def __iter__(self):
        return iter(self.payments)

    def append(self, dividend_payment: DividendPayment):
        self.payments.append(dividend_payment)

    def is_empty(self):
        return not self.payments

    def get_fund_names(self):
        fund_names = []
        for payment in self.payments:
            if not payment.fund_name in fund_names:
                fund_names.append(payment.fund_name)
        return fund_names

    # Returns all dividend payments for the given fund.
    def get_fund_payments(self, fund_name) -> list[DividendPayment]:
        fund_payments = []
        for payment in self.payments:
            if payment.fund_name == fund_name:
                fund_payments.append(payment)
        return fund_payments

    def sort_by_date(self, reverse):
        self.payments.sort(key=lambda x: x.date_time, reverse=reverse)
