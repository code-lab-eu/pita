Personal tax report
===================

Generates the data required by the Bulgarian tax office for reporting
investment returns.


Usage
-----

```
# Create a virtual environment:
$ python -m venv env
# Activate the virtual environment:
$ source env/bin/activate
# Install required dependencies:
$ pip install -r requirements.txt
```

Run the script:

```
$ python main.py
```

The following investment brokers are supported:


Saxo Bank
---------

* Open the Saxo Trader Go website (not Saxoinvestor).
* Go to Account > Historical reports.
* Open the "Trades" view. Select a custom period starting with the opening of
  the account. Export as an Excel sheet.
* Open the "Share dividends" dialog. Choose last year as the period. Export as
  an Excel sheet.
* Open the "Closed positions" dialog. Select a custom period sarting with the
  opening of the account. Export as an Excel sheet.

```
# Example: process the Excel exports from Saxo Bank.
$ python main.py --saxo-trades TradesExecuted_123456.xlsx --saxo-dividends ShareDividends_123456.xlsx --saxo-closed-positions ClosedPositions_123456.xlsx
```


Trading 212
-----------

* Open the Trading212 website.
* Go to History and click the "Export" button in the top right.
* Select a time frame from January 1 to 31 December and click "Export CSV". It is only possible to export 12 months of
  data, so you need to do this multiple times.
* A few moments later a notification will appear that the export is ready. Click the "Download" button.

```
# Example: process 2 yearly exports from Trading 212.
$ python main.py --t212 t212-2021.csv t212-2022.csv
```
