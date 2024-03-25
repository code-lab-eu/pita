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
    "EUNA": "iShares Core Global Aggregate Bond EUR",
}


class Trading212TransactionsImporter:
    @staticmethod
    def import_transactions(collection, file_name):
        with open(file_name, newline="") as csvfile:
            csvreader = csv.reader(csvfile)

            # Trading212 changes the format of the CSV file from time to time. Since we have to export the data year by
            # year it is great if we can support historic exports, so we don't need to export ALL the data again every
            # year. For each required column we have a list of historic headers.
            header_mappings = {
                "transaction_type": ["Action"],
                "date_time": ["Time"],
                "number": ["No. of shares"],
                "share_price": ["Price / share"],
                "purchase_price": ["Total (EUR)", "Total"],
                "ticker": ["Ticker"],
                "fund_name": ["Name"],
                "currency": ["Currency (Price / share)"],
            }
            # We need to check if the format is still the same as expected. If the actual headers are not the same as
            # the expected headers, the format has changed, and we need to check if the parsing logic still applies. Log
            # the differences and exit.
            actual_headers = csvfile.readline().split(",")
            for required_header in header_mappings.values():
                if not any(header in actual_headers for header in required_header):
                    print(
                        "Missing required header in Trading 212 file: %s"
                        % ", ".join(required_header)
                    )
                    exit()

            header_rows = {}
            for required_header, headings in header_mappings.items():
                for i, j in enumerate(actual_headers):
                    if j in headings:
                        header_rows[required_header] = i
                        break

            # We skip the first line, because it contains column headers.
            next(csvreader)
            for row in csvreader:
                # If we don't have the fund this row is a bank transaction. Skip it!
                fund_name = row[header_rows["fund_name"]]
                if not fund_name:
                    continue

                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0].startswith("Dividend"):
                    continue

                # The date format has changed. Older exports have the date in the format "2021-05-17 00:00:00", while
                # newer exports have the date in the format "2021-05-17 00:00:00.000". We need to handle both cases.
                try:
                    date_time = datetime.strptime(row[header_rows["date_time"]], "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    date_time = datetime.strptime(row[header_rows["date_time"]], "%Y-%m-%d %H:%M:%S")

                transaction_type = row[header_rows["transaction_type"]]
                number = decimal.Decimal(row[header_rows["number"]])
                share_price = decimal.Decimal(row[header_rows["share_price"]])
                currency = row[header_rows["currency"]]
                purchase_price = decimal.Decimal(row[header_rows["purchase_price"]])
                ticker = row[header_rows["ticker"]]
                domicile = FUND_DOMICILE_MAPPING.get(ticker)
                if not domicile:
                    print(
                        "Error could not find domicile "
                        + ticker
                        + " add it to FUND_DOMICILE_MAPPING!"
                    )
                    exit()
                transaction = Transaction(
                    fund_name,
                    domicile,
                    date_time,
                    transaction_type,
                    number,
                    share_price,
                    currency,
                    purchase_price,
                )
                collection.append(transaction)
