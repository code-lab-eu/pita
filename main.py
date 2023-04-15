import argparse
import datetime
import sys

from importers.trading212.transactions_importer import Trading212TransactionsImporter
from importers.binck.transactions_importer import BinckTransactionsImporter
from importers.trading212.dividends_importer import Trading212DividendsImporter
from importers.saxo.dividends_importer import SaxoDividendsImporter
from importers.saxo.transactions_importer import SaxoImporter
from transaction_collection import TransactionCollection
from dividend_collection import DividendCollection

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binck-transactions', '--binck', dest='transactions_binck', help='The path to an excel file detailing BinckBank transactions.')
    parser.add_argument('--trading212-transactions', '--t212', dest='transactions_trading212', help='The path to an csv file detailing Trading 212 transactions + dividends.', action='append', nargs='*')
    parser.add_argument('--saxo-transactions', '--saxo', dest='transactions_saxo', help='The path to an excel file detailing Saxo transactions.')
    args = parser.parse_args()

    # If the user doesn't supply input print the help and exit.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    transactions = TransactionCollection()
    payments = DividendCollection()

    if args.transactions_trading212:
        # Loop over the CSV files.
        for csv_files in args.transactions_trading212:
            # Argparse allows to add multiple values for an option in a row.
            for csv_file in csv_files:
                Trading212TransactionsImporter.import_transactions(transactions, csv_file)
                Trading212DividendsImporter.import_dividends(payments, csv_file)

    if args.transactions_binck:
        BinckTransactionsImporter.import_transactions(transactions, args.transactions_binck)

    if args.transactions_saxo:
        SaxoImporter.import_transactions(transactions, args.transactions_saxo)
        SaxoDividendsImporter.import_dividends(payments, args.transactions_saxo)

    # Export the transactions to an Excel file.
    if not transactions.is_empty():
        wb = Workbook()

        # Grab the active worksheet.
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

        # Column widths.
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 10
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 15
        ws.column_dimensions['H'].width = 15

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

                # Format negative number in number column.
                number_format = '#,0.000;[RED]-#,0.000'
                # Format and styling the negative number in number column.
                ws.cell(ws.max_row, 5).number_format = number_format
                # Format and styling total share column.
                ws.cell(ws.max_row, 7).number_format = number_format

                # Format the currencies.
                # See https://support.microsoft.com/en-us/office/number-format-codes-5026bbd6-04bc-48cd-bf33-80f18b4eae68?ui=en-us&rs=en-us&ad=us
                number_format = '#,##0.00 [$' + transaction.currency + '];[RED]-#,##0.00 [$' + transaction.currency + ']'
                # Format the share price as a currency.
                ws.cell(ws.max_row, 6).number_format = number_format
                # Format the purchase price as a currency.
                ws.cell(ws.max_row, 8).number_format = number_format

            # Insert an empty row inbetween each fund.
            ws.append([])

        # Save the file
        wb.save("investments.xlsx")
        print("Saved file investments.xlsx!")


        # Dividend payments
        if not payments.is_empty():
            wb = Workbook()

            # grab the active worksheet
            ws = wb.active

            # Create the header row.
            ws["A1"] = "Dividend date"
            ws["B1"] = "Security"
            ws["C1"] = "Company"
            ws["D1"] = "Country"
            ws["E1"] = "Dividend"
            ws["F1"] = "Tax paid/withheld abroad"

            # Set a blue background color and white font color on row 1 (the header row).
            for cell in ws[1]:
                cell.fill = PatternFill(start_color="0066CC", fill_type="solid")
                cell.font = Font(name="Calibri", color="FFFFFF")

            # Column width
            ws.column_dimensions["A"].width = 20
            ws.column_dimensions["B"].width = 50
            ws.column_dimensions["C"].width = 10
            ws.column_dimensions["D"].width = 20
            ws.column_dimensions["E"].width = 20
            ws.column_dimensions["F"].width = 30

            fund_names = payments.get_fund_names()
            for fund_name in fund_names:
                fund_payments = payments.get_fund_payments(fund_name)

                # Add each transaction as a new row in the excel sheet.
                for payment in fund_payments:
                    # We only need to report the dividends for last year.
                    last_year = datetime.date.today().year - 1
                    if payment.date_time.year != last_year:
                        continue
                    ws.append(
                        [
                            payment.date_time,
                            payment.fund_name,
                            payment.company,
                            payment.country,
                            payment.dividend,
                            payment.purchase_price,
                        ]
                    )

                    # Format the date as DD.MM.YYYY.
                    ws.cell(ws.max_row, 1).number_format = "DD.MM.YYYY"
                    # Format the currencies.
                    # See https://support.microsoft.com/en-us/office/number-format-codes-5026bbd6-04bc-48cd-bf33-80f18b4eae68?ui=en-us&rs=en-us&ad=us
                    number_format = (
                        "#,##0.00 [$"
                        + payment.currency
                        + "];[RED]-#,##0.00 [$"
                        + payment.currency
                        + "]"
                    )
                    # Format the share price as a currency.
                    ws.cell(ws.max_row, 5).number_format = number_format
                    # Format the purchase price as a currency.
                    ws.cell(ws.max_row, 6).number_format = number_format

                # Insert an empty row inbetween each fund.
                ws.append([])

            # Save the file
            wb.save("dividends.xlsx")
            print("Saved file dividends.xlsx!")

