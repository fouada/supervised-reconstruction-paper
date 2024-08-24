from pathlib import Path
import pandas as pd
from pysem.glosses import to_concepticon

in_path = Path.cwd().parent / "proto_semitic_words.tsv"
out_path = Path.cwd().parent.parent / "etc" / "concepts.tsv"

def gg(d):
    """
    dict vals to tuples (gloss, cogid, doculect) or ("", "", "")
    """
    return {k: (d[k][0][0], d[k][0][1], d[k][0][2]) if d[k] else ("", "", "") for k in d}

def main():
    """
    read proto_semitic_words.tsv, link it to concepticon, and write out concepts.tsv
    """
    # read file and clean column "sense"
    dfgot = pd.read_csv(in_path, sep="\t", usecols=["CONCEPT"])

    # define list of dictionaries and plug into the concepticon()
    glo = [{"gloss": g} for g in dfgot["CONCEPT"].unique() if type(g) == str]
    G = gg(to_concepticon(glo))
    
    # Handle unlinked concepts: Add fallback values if needed
    data_list = [{'NUMBER': i, 'ENGLISH': k, 'CONCEPTICON_ID': v[0] if v[0] else "Unmapped",
                  'CONCEPTICON_GLOSS': v[1] if v[1] else "Unknown",
                  'CONCEPTICON_POS': v[2] if v[2] else "Unknown"}
                 for i, (k, v) in enumerate(G.items(), 1)]

    result = pd.DataFrame(data_list)
    result.to_csv(out_path, sep="\t", index=False, encoding="utf-8")

if __name__ == "__main__":
    main()
