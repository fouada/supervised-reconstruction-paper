import csv

# Convert CSV to TSV
with open('./raw/proto_semitic_words.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    with open('./raw/proto_semitic_words.tsv', 'w', encoding='utf-8', newline='') as tsvfile:
        tsvwriter = csv.writer(tsvfile, delimiter='\t')
        for row in csvreader:
            tsvwriter.writerow(row)