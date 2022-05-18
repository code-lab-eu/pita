from dividend_payment import DividendPayment
import csv
import decimal

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


class Trading212DividendsImporter:
    @staticmethod
    def import_dividends(collection, file_name):
        with open(file_name, newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            # We skip the first line, because it shows column headers
            next(csvreader)
            for row in csvreader:

                # If we don't have the fund this row is a bank transaction. Skip it!
                security = row[4]
                if not security:
                    continue

                # The transaction list should only contain buys and sells. Skip dividends.
                if row[0] != "Dividend (Ordinary)":
                    continue
                company = security.split(' ')[0]
                dividend = decimal.Decimal(row[10])
                currency = row[7]
                purchase_price = decimal.Decimal(row[11])
                ticker = row[3]
                country = FUND_DOMICILE_MAPPING.get(ticker)
                tax_paid = row[11]
                if not country:
                    print("Error could not find domicile " + ticker + " add it to FUND_DOMICILE_MAPPING!")
                    exit()
                dividend_payment = DividendPayment(security, company, dividend, country, tax_paid, currency, purchase_price)
                collection.append(dividend_payment)

