import csv

# Function to load CSV into a dictionary by ID
def load_csv_to_dict(filename, id_column):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return {row[id_column]: row for row in reader}

# Load data from CSV files
languages = load_csv_to_dict('languages.csv', 'ID')
parameters = load_csv_to_dict('parameters.csv', 'ID')
forms = load_csv_to_dict('forms.csv', 'ID')
cognates = load_csv_to_dict('cognates.csv', 'Form_ID')

# Validate Language_IDs in forms.csv
missing_languages = [row['Language_ID'] for row in forms.values() if row['Language_ID'] not in languages]
if missing_languages:
    print("Missing Language_IDs in languages.csv:", missing_languages)
else:
    print("All Language_IDs in forms.csv are valid.")

# Validate Parameter_IDs in forms.csv
missing_parameters = [row['Parameter_ID'] for row in forms.values() if row['Parameter_ID'] not in parameters]
if missing_parameters:
    print("Missing Parameter_IDs in parameters.csv:", missing_parameters)
else:
    print("All Parameter_IDs in forms.csv are valid.")

# Validate Form_IDs in cognates.csv
missing_forms = [row['Form_ID'] for row in cognates.values() if row['Form_ID'] not in forms]
if missing_forms:
    print("Missing Form_IDs in forms.csv:", missing_forms)
else:
    print("All Form_IDs in cognates.csv are valid.")
