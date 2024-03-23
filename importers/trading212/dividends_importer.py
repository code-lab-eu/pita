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
        with open(file_name, newline="") as csvfile:
            csvreader = csv.reader(csvfile)

            # If the 'Withholding tax' column is missing, we are dealing with an account that doesn't pay any dividends.
            # In this case we can just skip the file.
            actual_headers = csvfile.readline().split(",")
            if "Withholding tax" not in actual_headers:
                return

            # Check that we have all the required headers.
            header_mappings = {
                "security": ["Name"],
                "date_time": ["Time"],
                "action": ["Action"],
                "dividend": ["Total (EUR)", "Total"],
                "currency": ["Currency (Price / share)"],
                "tax_paid": ["Withholding tax"],
                "ticker": ["Ticker"],
            }
            required_headers = header_mappings.keys()

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

            # We skip the first line, because it shows column headers
            next(csvreader)
            for row in csvreader:
                # If we don't have the fund this row is a bank transaction. Skip it!
                security = row[header_rows["security"]]
                if not security:
                    continue

                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0] != "Dividend (Ordinary)":
                    continue
                date_time = datetime.strptime(
                    row[header_rows["date_time"]], "%Y-%m-%d %H:%M:%S"
                )
                company = security.split(" ")[header_rows["action"]]
                dividend = decimal.Decimal(row[header_rows["dividend"]])
                currency = row[header_rows["currency"]]
                purchase_price = decimal.Decimal(row[header_rows["tax_paid"]])
                ticker = row[header_rows["ticker"]]
                country = FUND_DOMICILE_MAPPING.get(ticker)
                tax_paid = row[header_rows["tax_paid"]]
                if not country:
                    print(
                        "Error could not find domicile "
                        + ticker
                        + " add it to FUND_DOMICILE_MAPPING!"
                    )
                    exit()
                dividend_payment = DividendPayment(
                    security,
                    company,
                    dividend,
                    country,
                    tax_paid,
                    currency,
                    purchase_price,
                    date_time,
                )
                collection.append(dividend_payment)
