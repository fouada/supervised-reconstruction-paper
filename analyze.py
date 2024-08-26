"""
Analyze the data using multithreading.
"""
from lingrex.reconstruct import (
        PatternReconstructor, CorPaRClassifier,
        transform_alignment)
from sklearn.svm import SVC
from sys import argv
from pathlib import Path
import json
from functools import partial

align_psf = partial(
        transform_alignment, align=True, position=True, prosody=True, startend=True)
align_ps = partial(
        transform_alignment, align=True, position=True, prosody=True, startend=False)
align_sf = partial(
        transform_alignment, align=True, position=False, prosody=True, startend=True)
align_pf = partial(
        transform_alignment, align=True, position=True, prosody=False, startend=True)
align_p = partial(
        transform_alignment, align=True, position=True, prosody=False, startend=False)
align_s = partial(
        transform_alignment, align=True, position=False, prosody=True, startend=False)
align_f = partial(
        transform_alignment, align=True, position=False, prosody=False, startend=True)
align = partial(
        transform_alignment, align=True, position=False, prosody=False, startend=False)

if len(argv) >= 2:
    if argv[1] == "svm":
        classifier = "svm"
        clf = lambda : SVC(kernel="linear")
        onehot = True
    elif argv[1] == "corpar":
        clf = CorPaRClassifier
        onehot = False
        classifier = "corpar"
RUNS = 10

datasets = [
        ("Semitic", "ps"),
        ("Burmish", "ProtoBurmish"),
        ("Purus", "ProtoPurus"),
        ("Karen", "ProtoKaren"),
        ("Bai", "ProtoBai"),
        ("Lalo", "ProtoLalo"),
        ("Romance", "Latin"),
        ]

methods = [
        ("PosStr", align_ps),
        ("PosIni", align_pf),
        ("StrIni", align_sf),
        ("Pos", align_p),
        ("Str", align_s),
        ("Ini", align_f),
        ("none", align),
        ("PosStrIni", align_psf),
        ]

proportions = ['0.1','0.5','0.8']

def analyze_dataset_method(prop, ds, proto, i, meth_name, meth):
    print(f"[i] analyzing {ds} test {i+1} with method {meth_name}")
    wlpath = str(Path(
        "data", f"data-{prop}", "testlists", ds, "test-{0}.tsv".format(i+1)))
    with open(Path(
        "data", f"data-{prop}", "testitems", ds, "test-{0}.json".format(i+1))) as f:
        tests = json.load(f)
    res_path = Path(
        "results", f"split-{prop}", classifier, ds+"-"+meth_name+"-"+str(i+1)+".tsv")
    if not res_path.exists():
        res_path.parent.mkdir(parents=True, exist_ok=True)
        pt = PatternReconstructor(
                wlpath, ref="cogid", fuzzy=False, target=proto)
        pt.fit(clf=clf(), func=meth, onehot=onehot, aligned=False)
        results = []
        for cogid, target, alignment, languages in tests:
            results += [[
                pt.predict(
                    alignment,
                    languages),
                target]]
        with open(res_path, "w") as f:
            for a, b in results:
                f.write(" ".join(a)+"\t"+" ".join(b)+"\n")
    else:
        print("Skipping existing analysis.")

if __name__ == "__main__":
    for ds, proto in datasets:
        print("[i] analyzing {0}".format(ds))
        for prop in proportions:
            print("[i] analyzing {0} split".format(prop))
            for i in range(RUNS):
                for meth_name, meth in methods:
                    analyze_dataset_method(prop, ds, proto, i, meth_name, meth)
