import pandas as pd
import json
from pathlib import Path
from pyglottolog import Glottolog
from clldutils.misc import slug

# Paths
in_path = Path.cwd().parent / "proto_semitic_words.tsv"
out_path = Path.cwd().parent.parent / "etc" / "languages.tsv"
glotto_path = Path.cwd() / "glottolog"
json_path = Path.cwd() / "lang_to_glottocode.json"

def main():
    # Read the proto_semitic_words.tsv file
    df = pd.read_csv(in_path, sep="\t", usecols=["DOCULECT"])

    # Load the corrected Glottocode mappings from lang_to_glottocode_corrected.json
    with open(json_path, 'r', encoding='utf-8') as f:
        lang_to_glottocode = json.load(f)

    # Load Glottolog data
    glottolog = Glottolog(glotto_path)

    # Get unique DOCULECTs from the dataframe
    languages = df.DOCULECT.unique()

    # Retrieve Glottocodes using the mapping
    ids = [lang_to_glottocode.get(lang, None) for lang in languages]

    # Retrieve language objects from Glottolog
    langs_obj = glottolog.languoids(ids)
    langs_obj_dict = {lang.glottocode: lang for lang in langs_obj}

    langs = []
    for lang_name in languages:
        if isinstance(lang_name, float):
            continue  # Skip NaN values

        lang_name_str = str(lang_name)  # Ensure lang_name is a string
        glottocode = lang_to_glottocode.get(lang_name_str, None)

        if glottocode is None:
            langs.append({
                "ID": slug(lang_name_str),
                "Name": None,
                "NameInSource": lang_name_str,
                "Glottocode": None,
                "ISO639P3code": None,
                "Latitude": None,
                "Longitude": None,
                "Family": None,
            })
        else:
            lang_obj = langs_obj_dict.get(glottocode, None)
            if lang_obj is None:
                langs.append({
                    "ID": slug(lang_name_str),
                    "Name": None,
                    "NameInSource": lang_name_str,
                    "Glottocode": glottocode,
                    "ISO639P3code": None,
                    "Latitude": None,
                    "Longitude": None,
                    "Family": None,
                })
            else:
                langs.append({
                    "ID": slug(lang_name_str),
                    "Name": lang_obj.name,
                    "NameInSource": lang_name_str,
                    "Glottocode": lang_obj.glottocode,
                    "ISO639P3code": lang_obj.iso,
                    "Latitude": lang_obj.latitude,
                    "Longitude": lang_obj.longitude,
                    "Family": lang_obj.family.name if lang_obj.family else None,
                })

    # Convert the list of language dictionaries to a DataFrame
    langs_df = pd.DataFrame(langs)

    # Save the DataFrame to a TSV file
    langs_df.to_csv(out_path, sep="\t", index=False)

    print(f"Saved {len(langs_df)} languages to {out_path}")

if __name__ == "__main__":
    main()
