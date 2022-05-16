from transaction import Transaction
from openpyxl import load_workbook
import decimal

FUND_DOMICILE_MAPPING = {
    "iShares USD High Yield Capped Bond UCITS ETF (ISIN: IE00B4PY7Y77)": "Ireland",
    "iShares FTSE/EPRA European Property EUR UCITS ETF (ISIN: IE00B0M63284)": "Ireland",
    "iShares High Yield Corp. Bond UCITS ETF (ISIN: IE00B66F4759)": "Ireland",
    "Amundi Index FTSE EPRA Nareit Global- ETF (ISIN: LU1437018838)": "Luxembourg",
    "iShares Core MSCI World UCITS ETF (ISIN: IE00B4L5Y983)": "Ireland",
    "iShares MSCI World Small Cap UCITS ETF (ISIN: IE00BF4RFH31)": "Ireland",
    "iShares EM Infrastructure UCITS ETF (ISIN: IE00B2NPL135)" : "Ireland",
    "iShares Core Global Aggregate Bond UCITS ETF (ISIN: IE00BDBRDM35)": "Ireland",
    "iShares Core Euro Corporate Bond UCITS ETF (ISIN: IE00B3F81R35)": "Ireland",
    "iShares Emerging Markets Local Gov Bond UCITS ETF (ISIN: IE00B5M4WH52)": "Ireland",
    "iShares MSCI Turkey UCITS ETF (ISIN: IE00B1FZS574)": "Ireland",
    "iShares S&P Global Clean Energy ETF (ISIN: IE00B1XNHC34)": "Ireland",
}


class SaxoImporter:
    @staticmethod
    def import_transactions(collection, file_name):
        workbook = load_workbook(filename=file_name)
        sheet = workbook.active

        # We are starting from row 2, because the first row is a title.
        for i in range(2, sheet.max_row + 1):

            # If we don't have the fund this row is empty. Skip it!
            get_fund_name = sheet.cell(row=i, column=3).value
            fund_name = get_fund_name[:get_fund_name.index("(")]
            if not fund_name:
                continue

            date_time = sheet.cell(row=i, column=4).value
            domicile = FUND_DOMICILE_MAPPING.get(get_fund_name)
            transaction_type = sheet.cell(row=i, column=5).value
            number = decimal.Decimal(sheet.cell(row=i, column=7).value)
            share_price = decimal.Decimal(sheet.cell(row=i, column=8).value)
            currency = sheet.cell(row=i, column=2).value[-3:]
            purchase_price = share_price * number
            transaction = Transaction(fund_name, domicile, date_time, transaction_type, number, share_price,
                                      currency, purchase_price)
            collection.append(transaction)
