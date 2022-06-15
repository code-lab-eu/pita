from datetime import datetime
from transaction import Transaction
import csv
import decimal

FUND_DOMICILE_MAPPING = {
    "AGGH": "Ireland",
    "IPRP": "Ireland",
    "IUSN": "Ireland",
    "IWDA": "Ireland",
}

FUND_NAME_MAPPING = {
    "AGGH": "ISHARES GLB AGG EUR-H ACC",
    "IPRP": "ISHARES EUROPE PRPRTY YIELD",
    "IUSN": "ISHARES MSCI WLD SMALL CAP",
    "IWDA": "ISHARES CORE MSCI WORLD",
    "IQQP": "iShares European Property Yield UCITS ETF",
}


class InteractiveBrokersImporter:
    @staticmethod
    def import_transactions(collection, file_name):
        with open(file_name, newline="") as csvfile:
            csvreader = csv.reader(csvfile)
            # We skip the first line, because it shows column headers
            headers = next(csvreader)
            symbol_column = headers.index("Symbol")
            description_column = headers.index("Description")
            currency_primary_column = headers.index("CurrencyPrimary")
            date_time_column = headers.index("TradeDate")
            quantity_column = headers.index("Quantity")
            price_column = headers.index("Price")
            amount_column = headers.index("Amount")
            transaction_type_column = headers.index("Buy/Sell")
            level_of_detail_column = headers.index("LevelOfDetail")
            for row in csvreader:
                # If we don't have the fund this row is a bank transaction. Skip it!
                fund_name = row[description_column]
                if not fund_name:
                    continue
                # The transaction list should only contain buys and sells. Skip dividends.
                if row[level_of_detail_column] != "ORDER":
                    continue
                date_time = datetime.strptime(row[date_time_column], "%Y%m%d")
                transaction_type = row[transaction_type_column]
                number = decimal.Decimal(row[quantity_column])
                share_price = decimal.Decimal(row[price_column])
                currency = row[currency_primary_column]
                purchase_price = decimal.Decimal(row[amount_column])
                ticker = row[symbol_column]
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
