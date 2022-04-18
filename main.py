import argparse
import csv
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binck-transactions', dest='transactions_binck', help='The path to an excel file detailing BinckBank transactions.')
    parser.add_argument('--trading212-transactions', dest='transactions_trading212',help='The path to an csv file detailing Trading 212 transactions.')
    args = parser.parse_args()

    if args.transactions_trading212:
        with open(args.transactions_trading212, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                print(', '.join(row))

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

