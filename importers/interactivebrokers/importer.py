import sys
from _csv import reader
from datetime import datetime

from dividend_collection import DividendCollection
from dividend_payment import DividendPayment
from transaction import Transaction
from typeguard import typechecked

import csv
import decimal

from transaction_collection import TransactionCollection

FUND_DOMICILE_MAPPING = {
    "AGGH": "Ireland",
    "EPRA": "Luxembourg",
    "IEAC": "Ireland",
    "IHYG": "Ireland",
    "INRG": "Ireland",
    "IPRP": "Ireland",
    "IS0R": "Ireland",
    "IUSN": "Ireland",
    "IWDA": "Ireland",
    "SEML": "Ireland",
}

FUND_NAME_MAPPING = {
    "AGGH": "iShares Core Global Aggregate Bond UCITS ETF",
    "EPRA": "Amundi Index FTSE EPRA Nareit Global ETF",
    "IEAC": "iShares Core Euro Corp Bond ETF",
    "IHYG": "iShares High Yield Corp. Bond UCITS ETF",
    "INRG": "iShares Global Clean Energy UCITS ETF",
    "IPRP": "iShares European Property Yield UCITS",
    "IS0R": "iShares USD High Yield Capped Bond UCITS ETF",
    "IUSN": "iShares MSCI World Small Cap",
    "IWDA": "iShares Core MSCI World UCITS ETF",
    "SEML": "iShares Emerging Markets Local Gov Bond UCITS ETF",
}


class InteractiveBrokersImporter:
    @staticmethod
    @typechecked
    def process_transactions(csvreader: reader, transactions: TransactionCollection):
        # Skip all rows until we find the first transaction. We can recognize it by "Trades" in the first column.
        for row in csvreader:
            if row[0] == "Trades":
                break

        # The first Trades row is a header. Identify the columns we are interested in.
        symbol_column = row.index("Symbol")
        date_time_column = row.index("Date/Time")
        transaction_type_column = row.index("Code")
        quantity_column = row.index("Quantity")
        share_price_column = row.index("T. Price")
        currency_column = row.index("Currency")
        proceeds_column = row.index("Proceeds")
        profit_loss_column = row.index("Realized P/L")

        data_discriminator_column = row.index("DataDiscriminator")
        asset_category_column = row.index("Asset Category")

        # Now loop over the rest of the rows and process them.
        while row := next(csvreader, None):
            # If the first column no longer contains "Trades", we are done.
            if row[0] != "Trades":
                break

            # Only process rows that are orders on the stock market.
            if row[data_discriminator_column] != "Order" or row[asset_category_column] != "Stocks":
                continue

            symbol = row[symbol_column]
            if symbol not in FUND_NAME_MAPPING:
                print("Error: could not find fund name for " + symbol + ".", file=sys.stderr)
                exit(1)
            if symbol not in FUND_DOMICILE_MAPPING:
                # Throw an error, we need to add this symbol to the mapping.
                print("Error: could not find domicile for " + symbol + ".", file=sys.stderr)
                exit(1)

            date_time = datetime.strptime(row[date_time_column], "%Y-%m-%d, %H:%M:%S")
            transaction_type = row[transaction_type_column]

            # If the transaction type starts with "C" (Close), it is a sale. If it starts with "O" (Open), it is a buy.
            if transaction_type.startswith("C"):
                transaction_type = "Sell"
            elif transaction_type.startswith("O"):
                transaction_type = "Buy"
            else:
                print(
                    "Error: could not determine transaction type for " + symbol + ".", file=sys.stderr
                )
                exit(1)

            number = decimal.Decimal(row[quantity_column].replace(",", ""))
            share_price = decimal.Decimal(row[share_price_column])
            currency = row[currency_column]
            purchase_price = -decimal.Decimal(row[proceeds_column])
            profit_loss = decimal.Decimal(row[profit_loss_column]) if transaction_type == "Sell" else None

            fund_name = FUND_NAME_MAPPING[symbol]
            domicile = FUND_DOMICILE_MAPPING[symbol]

            transaction = Transaction(
                fund_name,
                domicile,
                date_time,
                transaction_type,
                number,
                share_price,
                currency,
                purchase_price,
                profit_loss,
            )
            transactions.append(transaction)

    @staticmethod
    @typechecked
    def process_dividends(csvreader: reader, dividends: DividendCollection):
        # We need to process USD dividends separately. We will store them in a temporary collection.
        usd_dividends = DividendCollection()
        total_usd_dividends_in_eur = decimal.Decimal(0)

        # Skip all rows until we find the first dividend. We can recognize it by "Dividends" in the first column.
        for row in csvreader:
            if row[0] == "Dividends":
                break

        # The first Dividends row is a header. Identify the columns we are interested in.
        symbol_column = row.index("Description")
        date_time_column = row.index("Date")
        amount_column = row.index("Amount")
        currency_column = row.index("Currency")

        # Now loop over the rest of the rows and process them.
        while row := next(csvreader, None):
            # If the first column no longer contains "Dividends", we are done.
            if row[0] != "Dividends":
                break

            # The currency column is used for other purposes as well.
            currency = row[currency_column]
            if currency == "Total in EUR":
                total_usd_dividends_in_eur = decimal.Decimal(row[amount_column].replace(",", ""))
                continue

            if currency not in ["EUR", "USD"]:
                continue

            # The fund name has a bunch of extra information in it. Keep only the first 4 characters.
            symbol = row[symbol_column][:4]
            if symbol not in FUND_NAME_MAPPING:
                print("Error: could not find fund name for " + symbol + ".", file=sys.stderr)
                exit(1)
            if symbol not in FUND_DOMICILE_MAPPING:
                # Throw an error, we need to add this symbol to the mapping.
                print("Error: could not find domicile for " + symbol + ".", file=sys.stderr)
                exit(1)

            date_time = datetime.strptime(row[date_time_column], "%Y-%m-%d")
            amount = decimal.Decimal(row[amount_column].replace(",", ""))

            fund_name = FUND_NAME_MAPPING[symbol]
            domicile = FUND_DOMICILE_MAPPING[symbol]
            # The company name is the first word of the fund name.
            company = fund_name.split(" ")[0]

            dividend = DividendPayment(
                fund_name=fund_name,
                company=company,
                dividend=amount,
                country=domicile,
                tax_paid=0,
                currency=currency,
                date_time=date_time,
            )

            if currency == "USD":
                usd_dividends.append(dividend)
            else:
                dividends.append(dividend)

        # Convert the USD dividends to EUR and add them to the main collection.
        total_in_usd = sum(dividend.dividend for dividend in usd_dividends)
        conversion = total_usd_dividends_in_eur / total_in_usd
        for dividend in usd_dividends:
            dividend.dividend *= conversion
            dividend.currency = "EUR"
            dividends.append(dividend)

    @staticmethod
    @typechecked
    def import_activity(transactions: TransactionCollection, dividends: DividendCollection, file_name: str):
        with open(file_name, newline="") as csvfile:
            csvreader = csv.reader(csvfile)
            InteractiveBrokersImporter.process_transactions(csvreader, transactions)
            InteractiveBrokersImporter.process_dividends(csvreader, dividends)
