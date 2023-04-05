import csv
import os


def mapping(mention: str) -> int:
    mention_file = os.path.abspath("functions/mention.csv")
    with open(mention_file, newline="", mode='r', encoding='UTF-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        for row in reader:
            if row[0] == mention:
                return int(row[1])

    return -1
