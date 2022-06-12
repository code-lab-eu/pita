Personal tax report
===================

Generates the data required by the Bulgarian tax office for reporting
investment returns.


Usage
-----

Install required dependencies:

```
$ pip install -r requirements.txt
```

Run the script:

```
$ python main.py
```

The following investment brokers are supported:


Saxo Bank
---------

* Open the saxoinvester website.
* Historical reports > Transaction report.
* Period: last year.
* Ensure to select all products and transaction types.
* Export as Excel sheet.
