from transaction import Transaction
from openpyxl import load_workbook
import decimal

FUND_DOMICILE_MAPPING = {
    "Amundi Index FTSE EPRA Nareit Global- ETF": "Luxembourg",
    "iShares Core Euro Corporate Bond UCITS ETF": "Ireland",
    "iShares Core Global Aggregate Bond UCITS ETF": "Ireland",
    "iShares Core MSCI World UCITS ETF": "Ireland",
    "iShares EM Infrastructure UCITS ETF" : "Ireland",
    "iShares Emerging Markets Local Gov Bond UCITS ETF": "Ireland",
    "iShares FTSE/EPRA European Property EUR UCITS ETF": "Ireland",
    "iShares High Yield Corp. Bond UCITS ETF": "Ireland",
    "iShares MSCI Turkey UCITS ETF": "Ireland",
    "iShares MSCI World Small Cap UCITS ETF": "Ireland",
    "iShares S&P Global Clean Energy ETF": "Ireland",
    "iShares USD High Yield Capped Bond UCITS ETF": "Ireland",
}


class SaxoImporter:
    @staticmethod
    def import_transactions(collection, file_name):
        workbook = load_workbook(filename=file_name)
        sheet = workbook.active

        # We are starting from row 2, because the first row is a title.
        for i in range(2, sheet.max_row + 1):

            # If we don't have the fund this row is empty. Skip it!
            get_fund_name = sheet.cell(row=i, column=4).value
            fund_name = get_fund_name
            if not fund_name:
                continue
            if sheet.cell(row=i, column=7).value != "Buy":
                continue

            date_time = sheet.cell(row=i, column=1).value
            domicile = FUND_DOMICILE_MAPPING.get(get_fund_name)
            transaction_type = sheet.cell(row=i, column=7).value
            number = decimal.Decimal(sheet.cell(row=i, column=10).value)
            share_price = decimal.Decimal(sheet.cell(row=i, column=11).value)
            currency = sheet.cell(row=i, column=2).value[-3:]
            purchase_price = share_price * number
            transaction = Transaction(fund_name, domicile, date_time, transaction_type, number, share_price,
                                      currency, purchase_price)
            collection.append(transaction)
