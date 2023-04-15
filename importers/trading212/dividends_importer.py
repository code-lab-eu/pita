from dividend_payment import DividendPayment
import csv
import decimal
from dividend_collection import DividendCollection
from typeguard import typechecked

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

            # If the actually imported headers are not the same as the expected headers, the format has changed and we
            # need to check if the parsing logic still applies. Log the differences and exit.
            # Todo: It looks like Trading212 changes the format of the CSV file every now and then. Since we have to
            #  export the data year by year it would be too much work to export all the data again every year. Instead
            #  we should inspect the headers and get the data from the right columns.
            required_headers = ['Name', 'Time', 'Action', 'Total (EUR)', 'Currency (Price / share)', 'Withholding tax', 'Ticker', ]
            actual_headers = csvfile.readline().split(',')
            for required_header in required_headers:
                if required_header not in actual_headers:
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
                dividend_payment = DividendPayment(security, company, dividend, country, tax_paid, currency, purchase_price)
                collection.append(dividend_payment)
