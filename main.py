import argparse
import csv
import decimal
import sys

from transaction import Transaction

from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

FUND_DOMICILE_MAPPING = {
    "IWQU": "Ireland",
    "IUSN": "Ireland",
    "IQQW": "Ireland",
    "VAGF": "Ireland",
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binck-transactions', dest='transactions_binck', help='The path to an excel file detailing BinckBank transactions.')
    parser.add_argument('--trading212-transactions', dest='transactions_trading212', help='The path to an csv file detailing Trading 212 transactions.')
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

                # If we don't have the fund this row is a bank transaction. Skip it!
                fund_name = row[4]
                if not fund_name:
                    continue

                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0] == "Dividend (Ordinary)":
                    continue

                date_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                transaction_type = row[0]
                number = decimal.Decimal(row[5])
                share_price = decimal.Decimal(row[6])
                currency = row[7]
                purchase_price = decimal.Decimal(row[9])
                ticker = row[3]
                domicile = FUND_DOMICILE_MAPPING.get(ticker)
                if not domicile:
                    print("Error could not find domicile " + ticker + " add it to FUND_DOMICILE_MAPPING!")
                    exit()
                transaction = Transaction(fund_name, domicile, date_time, transaction_type, number, share_price, currency, purchase_price)
                transactions.append(transaction)

    # Export the transaction in excell file

    if not transactions.is_empty():
        wb = Workbook()

        # grab the active worksheet
        ws = wb.active

        # Create the header row.
        ws['A1'] = "Fund name"
        ws['B1'] = "Domicile"
        ws['C1'] = "Transaction date"
        ws['D1'] = "Transaction type"
        ws['E1'] = "Number"
        ws['F1'] = "Share price"
        ws['G1'] = "Total shares"
        ws['H1'] = "Purchase price"

        # Set a blue background color and white font color on row 1 (the header row).
        for cell in ws[1]:
            cell.fill = PatternFill(start_color="0066CC", fill_type="solid")
            cell.font = Font(name="Calibri", color="FFFFFF")

        # Column width
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 10
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 10
        ws.column_dimensions['H'].width = 10

        transactions.calc_total_shares()
        transactions.sort_by_date(True)
        fund_names = transactions.get_fund_names()
        for fund_name in fund_names:
            fund_transactions = transactions.get_fund_transactions(fund_name)

            # Add each transaction as a new row in the excel sheet.
            for transaction in fund_transactions:
                ws.append([transaction.fund_name, transaction.domicile, transaction.date_time, transaction.transaction_type, transaction.number, transaction.share_price, transaction.total, transaction.purchase_price])

                # Format the date as DD.MM.YYYY.
                ws.cell(ws.max_row, 3).number_format = "DD.MM.YYYY"

                # Format the currencies.
                # See https://support.microsoft.com/en-us/office/number-format-codes-5026bbd6-04bc-48cd-bf33-80f18b4eae68?ui=en-us&rs=en-us&ad=us
                number_format = '#,##0.00 [$' + transaction.currency + '];[RED]-#,##0.00 [$' + transaction.currency + ']'
                # Format the share price as a currency.
                ws.cell(ws.max_row, 6).number_format = number_format
                # Format the purchase price as a currency.
                ws.cell(ws.max_row, 9).number_format = number_format

            # Insert an empty row inbetween each fund.
            ws.append([])

        # Save the file
        wb.save("investments.xlsx")
        print("Saved file investments.xlsx!")
