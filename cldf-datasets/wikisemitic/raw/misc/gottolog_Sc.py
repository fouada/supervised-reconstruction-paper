import json
from pathlib import Path
import pandas as pd
from pyglottolog import Glottolog
from fuzzywuzzy import process

# Paths
in_path = Path.cwd().parent / "proto_semitic_words.tsv"
glotto_path = Path.cwd() / "glottolog"
output_json = Path.cwd() / "lang_to_glottocode.json"

# Step 1: Extract unique DOCULECTs
df = pd.read_csv(in_path, sep="\t", usecols=["DOCULECT"])

# Handle NaN values by dropping them
df = df.dropna(subset=["DOCULECT"])

# Convert DOCULECTs to string in case of other unexpected types
df["DOCULECT"] = df["DOCULECT"].astype(str)

# Step 2: Split combined DOCULECTs into individual languages
df["DOCULECT"] = df["DOCULECT"].str.split(', ')

# Flatten the list of DOCULECTs to get unique values
unique_doculects = set([doculect for sublist in df["DOCULECT"] for doculect in sublist])

# Step 3: Initialize Glottolog
glottolog = Glottolog(glotto_path)

# Get a list of all language names in Glottolog
glottolog_languages = {lang.name: lang.glottocode for lang in glottolog.languoids()}

# Step 4: Create a mapping from DOCULECT to Glottocode with fuzzy matching
lang_to_glottocode = {}
for i, doculect in enumerate(unique_doculects):
    print(f"Processing DOCULECT {i+1}/{len(unique_doculects)}: '{doculect}'")
    
    # Attempt to match the DOCULECT to a Glottocode using exact match first
    lang = glottolog.languoid(doculect)
    if lang:
        lang_to_glottocode[doculect] = lang.glottocode
    else:
        # If no exact match is found, use fuzzy matching
        best_match, score = process.extractOne(doculect, glottolog_languages.keys())
        if score >= 70:  # Adjust this threshold based on how close the matches should be
            lang_to_glottocode[doculect] = glottolog_languages[best_match]
            print(f"Fuzzy match for '{doculect}' is '{best_match}' with score {score}")
        else:
            print(f"No good match found for {doculect} (best was {best_match} with score {score})")
            lang_to_glottocode[doculect] = None  # Handle this case as needed

# Step 5: Save the mapping to JSON
with open(output_json, 'w') as f:
    json.dump(lang_to_glottocode, f, indent=2)

print(f"Saved language to Glottocode mapping to {output_json}")
