from dividend_payment import DividendPayment
import csv
import decimal
from dividend_collection import DividendCollection
from typeguard import typechecked
from datetime import datetime

FUND_DOMICILE_MAPPING = {
    "IWQU": "Ireland",
    "IUSN": "Ireland",
    "IQQW": "Ireland",
    "VAGF": "Ireland",
    "IS3S": "Ireland",
    "IQQH": "Ireland",

}

class Trading212DividendsImporter:
    @staticmethod
    @typechecked
    def import_dividends(collection: DividendCollection, file_name):
        with open(file_name, newline='') as csvfile:
            csvreader = csv.reader(csvfile)

            # If the 'Withholding tax' column is missing, we are dealing with an account that doesn't pay any dividends.
            # In this case we can just skip the file.
            actual_headers = csvfile.readline().split(',')
            if 'Withholding tax' not in actual_headers:
                return

            # Check that we have all the required headers.
            required_headers = ['Name', 'Time', 'Action', 'Total (EUR)', 'Currency (Price / share)', 'Withholding tax', 'Ticker', ]
            for required_header in required_headers:
                if required_header not in actual_headers:
                    # A required header is missing. Probably the format of the CSV file has changed. Log an error and
                    # exit.
                    print("Missing required header %s in Trading 212 file" % required_header)
                    exit()
            header_mapping = {}
            for required_header in required_headers:
                for i, j in enumerate(actual_headers):
                    if j == required_header:
                        header_mapping[required_header] = i
                        break

            # We skip the first line, because it shows column headers
            next(csvreader)
            for row in csvreader:

                # If we don't have the fund this row is a bank transaction. Skip it!
                security = row[header_mapping['Name']]
                if not security:
                    continue

                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0] != "Dividend (Ordinary)":
                    continue
                date_time = datetime.strptime(row[header_mapping['Time']], '%Y-%m-%d %H:%M:%S')
                company = security.split(' ')[header_mapping['Action']]
                dividend = decimal.Decimal(row[header_mapping['Total (EUR)']])
                currency = row[header_mapping['Currency (Price / share)']]
                purchase_price = decimal.Decimal(row[header_mapping['Withholding tax']])
                ticker = row[header_mapping['Ticker']]
                country = FUND_DOMICILE_MAPPING.get(ticker)
                tax_paid = row[header_mapping['Withholding tax']]
                if not country:
                    print("Error could not find domicile " + ticker + " add it to FUND_DOMICILE_MAPPING!")
                    exit()
                dividend_payment = DividendPayment(security, company, dividend, country, tax_paid, currency, purchase_price, date_time)
                collection.append(dividend_payment)
