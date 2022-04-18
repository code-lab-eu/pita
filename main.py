import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binck-transactions', dest='transactions_binck', help='The path to an excel file detailing BinckBank transactions.')
    args = parser.parse_args()
    print(args.transactions)
    parser.print_help()