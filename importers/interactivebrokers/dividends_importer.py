from dividend_payment import DividendPayment
import csv
import decimal
from dividend_collection import DividendCollection
from typeguard import typechecked

FUND_DOMICILE_MAPPING = {
    "AGGH": "Ireland",
    "IPRP": "Ireland",
    "IUSN": "Ireland",
    "IWDA": "Ireland",
    "IQQP": "Ireland",
}

FUND_NAME_MAPPING = {
    "AGGH": "ISHARES GLB AGG EUR-H ACC",
    "IPRP": "ISHARES EUROPE PRPRTY YIELD",
    "IUSN": "ISHARES MSCI WLD SMALL CAP",
    "IWDA": "ISHARES CORE MSCI WORLD",
    "IQQP": "iShares European Property Yield UCITS ETF",
}

COUNTRY_CODE = {"IE": "Ireland"}


class InteractiveBrokersDividendsImporter:
    @staticmethod
    @typechecked
    def import_dividends(collection: DividendCollection, file_name):
        with open(file_name, newline="") as csvfile:
            csvreader = csv.reader(csvfile)
            # We skip the first line, because it shows column headers
            next(csvreader)
            # We skip the second and third lines, because it shows also column headers
            next(csvreader)
            next(csvreader)
            for row in csvreader:
                if row[2] != "RevenueComponent":
                    continue
                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0] != "DividendDetail":
                    continue
                dividend = decimal.Decimal(row[12])
                currency = row[3]
                tax_paid = row[15]
                symbol = row[4]
                security = FUND_NAME_MAPPING.get(symbol)
                company = security.split(" ")[0]
                country_code = row[6]
                country = COUNTRY_CODE.get(country_code)
                purchase_price = decimal.Decimal(row[16])
                if not country:
                    print(
                        "Error could not find domicile "
                        + symbol
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
                )
                collection.append(dividend_payment)
