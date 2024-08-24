import json
from fuzzywuzzy import process

# Load the JSON file
input_json = 'lang_to_glottocode.json'
output_json = 'lang_to_glottocode_corrected.json'

# Manually create a dictionary for known correct mappings
manual_corrections = {
    "Aymällä": "correct_glottocode",  # Replace with actual Glottocode
    "Mäseqan": "mesq1240",
    "Änor": "correct_glottocode",  # Replace with actual Glottocode
    "Čäha": "correct_glottocode",  # Replace with actual Glottocode
    "Gyäto": "correct_glottocode",  # Replace with actual Glottocode
    # Add other manual corrections as needed
}

# Load the existing JSON
with open(input_json, 'r', encoding='utf-8') as f:
    lang_to_glottocode = json.load(f)

# Step 1: Apply manual corrections directly
corrected_lang_to_glottocode = {}
for doculect, glottocode in lang_to_glottocode.items():
    # Directly apply manual corrections
    corrected_doculect = manual_corrections.get(doculect, doculect)
    corrected_glottocode = manual_corrections.get(corrected_doculect, glottocode)
    
    # Check for "null" or "incorrect_glottocode" entries and handle them
    if corrected_glottocode in (None, "null", "incorrect_glottocode"):
        # Fuzzy match or manually assign if not found
        best_match, score = process.extractOne(doculect, lang_to_glottocode.keys())
        if score >= 70:  # Adjust the threshold as needed
            corrected_glottocode = lang_to_glottocode[best_match]
        else:
            corrected_glottocode = "unknown"  # Flag for further review

    corrected_lang_to_glottocode[corrected_doculect] = corrected_glottocode

# Step 2: Write the corrected JSON file
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(corrected_lang_to_glottocode, f, ensure_ascii=False, indent=2)

print(f"Saved corrected language to Glottocode mapping to {output_json}")
