from dividend_payment import DividendPayment
from dividend_collection import DividendCollection
from openpyxl import load_workbook
import decimal
from typeguard import typechecked

FUND_DOMICILE_MAPPING = {
    "Amundi Index FTSE EPRA Nareit Global- ETF": "Luxembourg",
    "iShares Core Euro Corporate Bond UCITS ETF": "Ireland",
    "iShares Core Global Aggregate Bond UCITS ETF": "Ireland",
    "iShares Core MSCI World UCITS ETF": "Ireland",
    "iShares EM Infrastructure UCITS ETF": "Ireland",
    "iShares Emerging Markets Local Gov Bond UCITS ETF": "Ireland",
    "iShares FTSE/EPRA European Property EUR UCITS ETF": "Ireland",
    "iShares High Yield Corp. Bond UCITS ETF": "Ireland",
    "iShares MSCI Turkey UCITS ETF": "Ireland",
    "iShares MSCI World Small Cap UCITS ETF": "Ireland",
    "iShares S&P Global Clean Energy ETF": "Ireland",
    "iShares USD High Yield Capped Bond UCITS ETF": "Ireland",
}


class SaxoDividendsImporter:
    @staticmethod
    @typechecked
    def import_dividends(collection: DividendCollection, file_name):
        workbook = load_workbook(filename=file_name)
        sheet = workbook.active

        # We are starting from row 2, because the first row is a title.
        for i in range(2, sheet.max_row + 1):

            # If we don't have the fund this row is empty. Skip it!
            get_fund_name = sheet.cell(row=i, column=4).value
            security = get_fund_name
            if not security:
                continue
            if sheet.cell(row=i, column=7).value != "Cash dividend":
                continue

            company = security.split(' ')[0]
            dividend = decimal.Decimal(sheet.cell(row=i, column=14).value)
            currency = sheet.cell(row=i, column=2).value[-3:]
            purchase_price = 0.00
            ticker = security
            country = FUND_DOMICILE_MAPPING.get(get_fund_name)
            # Since Saxo is in Denmark we don't pay taxes
            tax_paid = 0.00
            if not country:
                print("Error could not find domicile " + ticker + " add it to FUND_DOMICILE_MAPPING!")
                exit()
            dividend_payment = DividendPayment(security, company, dividend, country, tax_paid, currency, purchase_price)
            collection.append(dividend_payment)
