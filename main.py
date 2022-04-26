import argparse
import csv
import sys

from openpyxl import Workbook




FUND_DOMICILE_MAPPING = {
    "IWQU": "Ireland",
    "IUSN": "Ireland",
    "IQQW": "Ireland",
    "VAGF": "ireland",
    "IS3S": "Ireland",
    "IQQH": "Ireland",

}

FUND_NAME_MAPPING = {
    "IWQU": "iShares Edge MSCI World Quality Factor",
    "IUSN": "iShares MSCI World Small Cap",
    "IQQW": "iShares MSCI World EUR",
    "VAGF": "Vanguard Global Aggregate Bond",
    "IS3S": "iShares Edge MSCI World Value Factor",
    "IQQH": "iShares Global Clean Energy",
}



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
        return 'Transaction fund name: %s, domicile: %s,  date: %s, type: %s, number: %s, share price: %s,currency: %s,  purchase price: %s' % (self.fund_name, self.domicile, self.date_time, self.transaction_type, self.number, self.share_price, self.currency, self.purchase_price)


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



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binck-transactions', dest='transactions_binck', help='The path to an excel file detailing BinckBank transactions.')
    parser.add_argument('--trading212-transactions', dest='transactions_trading212',help='The path to an csv file detailing Trading 212 transactions.')
    args = parser.parse_args()

    # If the user doesn't supply the input print the help and exit

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    transactions = TransactionCollection()

    if args.transactions_trading212:
        with open(args.transactions_trading212, newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            # We skip the first line, because it shows column headers
            next(csvreader)
            for row in csvreader:
                fund_name = row[4]
                if not fund_name:
                    # If we don't have the fund this row is a bank transaction. Skip it!
                    continue
                date_time = row[1]
                transaction_type = row[0]
                number = row[5]
                share_price = row[6]
                currency = row[7]
                purchase_price = row[9]
                ticker = row[3]
                domicile = FUND_DOMICILE_MAPPING.get(ticker)
                if not domicile:
                    print("Error could not find domicile " + ticker + " add it to FUND_DOMICILE_MAPPING!")
                    exit()

                print(', '.join(row))
                transaction = Transaction(fund_name, domicile, date_time, transaction_type, number, share_price, currency, purchase_price)
                transactions.append(transaction)
                print(transaction)
            print(transactions.is_empty())


    # Export the transaction in excell file

    if not transactions.is_empty():
        wb = Workbook()

        # grab the active worksheet
        ws = wb.active

        # Data can be assigned directly to cells
        ws['A1'] = "Fund name"
        ws['B1'] = "Domicile"
        ws['C1'] = "Transaction date"
        ws['D1'] = "Transaction type"
        ws['E1'] = "Number"
        ws['F1'] = "Share price"
        ws['G1'] = "Total shares"
        ws['H1'] = "Currency (Price / share)"
        ws["I1"] = "Purchase prise"

        transactions.sort_by_date(True)
        fund_names = transactions.get_fund_names()
        for fund_name in fund_names:
            fund_transactions = transactions.get_fund_transactions(fund_name)


        # Rows can also be appended
            for transaction in fund_transactions:
                ws.append([transaction.fund_name, transaction.domicile, transaction.date_time, transaction.transaction_type, transaction.number, transaction.share_price, " ", transaction.currency, transaction.purchase_price])

            ws.append([])

        # Save the file
        wb.save("investments.xlsx")
        print("Save file investments.xlsx!")
