import pandas as pd
import json
from pathlib import Path
from pyglottolog import Glottolog

# Paths
in_path = Path.cwd().parent / "proto_semitic_words.tsv"
glotto_path = Path("./glottolog")  # Update this to your Glottolog repository path
output_json = Path.cwd() / "lang_to_glottocode.json"

# Step 1: Extract unique DOCULECTs
df = pd.read_csv(in_path, sep="\t", usecols=["DOCULECT"])

# Filter out non-string DOCULECTs to avoid errors
df = df[df["DOCULECT"].apply(lambda x: isinstance(x, str))]

unique_doculects = df["DOCULECT"].unique()

# Step 2: Initialize Glottolog
glottolog = Glottolog(glotto_path)

# Step 3: Create a mapping from DOCULECT to Glottocode
lang_to_glottocode = {}
for doculect in unique_doculects:
    try:
        # Attempt to match the DOCULECT to a Glottocode using Glottolog
        lang = glottolog.languoid(doculect)
        if lang:
            lang_to_glottocode[doculect] = lang.glottocode
        else:
            print(f"No match found for {doculect}")
    except Exception as e:
        print(f"Error processing {doculect}: {e}")

# Step 4: Save the mapping to JSON
with open(output_json, 'w') as f:
    json.dump(lang_to_glottocode, f, indent=2)

print(f"Saved language to Glottocode mapping to {output_json}")
