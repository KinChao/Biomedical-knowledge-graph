from typedb.client import TransactionType
import csv
import re


with open('g.txt', 'rt', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')
    raw_file = []
    n = 0


    for row in csvreader:
        n = n + 1
        if n != 1:
            raw_file.append(row)
    print(raw_file)
