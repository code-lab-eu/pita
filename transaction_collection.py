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

    def aggregate_daily_buys_by_fund(self):
        aggregated_buys = {}
        passthrough_transactions = []

        for transaction in self.transactions:
            if transaction.transaction_type != "Buy":
                passthrough_transactions.append(transaction)
                continue

            key = (
                transaction.date_time.date(),
                transaction.fund_name,
                transaction.domicile,
                transaction.currency,
            )
            if key not in aggregated_buys:
                aggregated_buys[key] = {
                    "date_time": transaction.date_time,
                    "fund_name": transaction.fund_name,
                    "domicile": transaction.domicile,
                    "number": transaction.number,
                    "purchase_price": transaction.purchase_price,
                    "currency": transaction.currency,
                }
            else:
                aggregated = aggregated_buys[key]
                if transaction.date_time < aggregated["date_time"]:
                    aggregated["date_time"] = transaction.date_time
                aggregated["number"] += transaction.number
                aggregated["purchase_price"] += transaction.purchase_price

        aggregated_transactions = []
        for aggregated in aggregated_buys.values():
            number = aggregated["number"]
            share_price = (
                aggregated["purchase_price"] / number if number != 0 else 0
            )
            aggregated_transactions.append(
                Transaction(
                    fund_name=aggregated["fund_name"],
                    domicile=aggregated["domicile"],
                    date_time=aggregated["date_time"],
                    transaction_type="Buy",
                    number=number,
                    share_price=share_price,
                    currency=aggregated["currency"],
                    purchase_price=aggregated["purchase_price"],
                )
            )

        self.transactions = passthrough_transactions + aggregated_transactions
        self.sort_by_date(False)

    def calc_total_shares(self):
        for fund_name in self.get_fund_names():
            transactions = self.get_fund_transactions(fund_name)
            transactions.sort(key=lambda x: x.date_time, reverse=False)
            total_shares = 0
            for transaction in transactions:
                total_shares += transaction.number
                transaction.total = total_shares
