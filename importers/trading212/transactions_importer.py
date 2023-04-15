from datetime import datetime
from transaction import Transaction
import csv
import decimal

FUND_DOMICILE_MAPPING = {
    "IWQU": "Ireland",
    "IUSN": "Ireland",
    "IQQW": "Ireland",
    "VAGF": "Ireland",
    "IS3S": "Ireland",
    "IQQH": "Ireland",
    "EUNL": "Ireland",
    "EUNA": "Ireland",
    "SXR8": "Ireland",
}

FUND_NAME_MAPPING = {
    "IWQU": "iShares Edge MSCI World Quality Factor",
    "IUSN": "iShares MSCI World Small Cap",
    "IQQW": "iShares MSCI World EUR",
    "VAGF": "Vanguard Global Aggregate Bond",
    "IS3S": "iShares Edge MSCI World Value Factor",
    "IQQH": "iShares Global Clean Energy",
    "EUNL": "iShares Core MSCI World EUR",
    "EUNA": "iShares Core Global Aggregate Bond EUR"
}


class Trading212TransactionsImporter:
    @staticmethod
    def import_transactions(collection, file_name):
        with open(file_name, newline='') as csvfile:
            csvreader = csv.reader(csvfile)

            # If the actually imported headers are not the same as the expected headers, the format has changed and we
            # need to check if the parsing logic still applies. Log the differences and exit.
            # Todo: It looks like Trading212 changes the format of the CSV file every now and then. Since we have to
            #  export the data year by year it would be too much work to export all the data again every year. Instead
            #  we should inspect the headers and get the data from the right columns.
            required_headers = ['Action', 'Time', 'No. of shares', 'Price / share','Total (EUR)','Ticker', 'Name', 'Currency (Price / share)']
            actual_headers = csvfile.readline().split(',')
            for required_header in required_headers:
                if required_header not in actual_headers:
                    print("Missing required header %s in Trading 212 file" % required_header)
                    exit()
            header_mapping = {}
            for required_header in  required_headers:
                for i, j in enumerate(actual_headers):
                    if j == required_header:
                        header_mapping[required_header] = i
                        break

            # We skip the first line, because it shows column headers
            next(csvreader)
            for row in csvreader:

                # If we don't have the fund this row is a bank transaction. Skip it!
                fund_name = row[header_mapping['Name']]
                if not fund_name:
                    continue

                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0] == "Dividend (Ordinary)":
                    continue

                date_time = datetime.strptime(row[header_mapping['Time']], '%Y-%m-%d %H:%M:%S')
                transaction_type = row[header_mapping['Action']]
                number = decimal.Decimal(row[header_mapping['No. of shares']])
                share_price = decimal.Decimal(row[header_mapping['Price / share']])
                currency = row[header_mapping['Currency (Price / share)']]
                purchase_price = decimal.Decimal(row[header_mapping['Total (EUR)']])
                ticker = row[header_mapping['Ticker']]
                domicile = FUND_DOMICILE_MAPPING.get(ticker)
                if not domicile:
                    print("Error could not find domicile " + ticker + " add it to FUND_DOMICILE_MAPPING!")
                    exit()
                transaction = Transaction(fund_name, domicile, date_time, transaction_type, number, share_price,
                                          currency, purchase_price)
                collection.append(transaction)
