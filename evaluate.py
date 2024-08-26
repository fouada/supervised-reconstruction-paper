"""
Script plots the results of the study.
"""
from matplotlib import pyplot as plt
from pathlib import Path
import json
import numpy as np
from collections import defaultdict
from tabulate import tabulate
from statistics import mean, stdev
from glob import glob
from collections import defaultdict
from lingpy import *
from lingrex.reconstruct import eval_by_dist, eval_by_bcubes
from tqdm import tqdm as progressbar


classifiers = ["svm", "corpar"]
methods = ["PosStrIni", "PosStr", "PosIni", "StrIni", "Pos", "Str", "Ini", "none"]
datasets = ["Semitic", "Bai", "Burmish", "Karen", "Lalo", "Purus", "Romance"]


proportions = ['0.1','0.5','0.8']

# collect metrics per prop, lang, clf in a dataframe, the columns are clf test_prop	lng	ED	NED	B3_F1
results_detailed = defaultdict(list)

for prop in proportions:
    all_data = defaultdict(list)
    by_ds = defaultdict(list)
    for clf in classifiers:
        for pth in progressbar(list(Path("results", f"split-{prop}", clf).glob("*.tsv"))[:]):
            with open(pth, "r", encoding="utf-8") as f:
                res = []
                for row in f:
                    res += [[[a.strip() for a in x.split()] for x in row.split("\t")]]

            ds, meth, run = pth.name[:-4].split("-")
            ed, dst, bc = (
                    eval_by_dist(res),
                    eval_by_dist(res, normalized=True),
                    eval_by_bcubes(res))
            if ds in datasets:
                by_ds[ds, clf, meth] += [bc]
                all_data[clf, meth, "dst"] += [dst]
                all_data[clf, meth, "ed"] += [ed]
                all_data[clf, meth, "bc"] += [bc]
                results_detailed[clf, prop, ds, meth, run] = [ed, dst, bc]

    table = []
    for clf in classifiers:
        for meth in methods:
            table += [[
                clf,
                meth,
                mean(all_data[clf, meth, "ed"] or [0]),
                mean(all_data[clf, meth, "dst"] or [0]),
                mean(all_data[clf, meth, "bc"] or [0])
                ]]

    print(tabulate(table, headers=["Classifier", "Analysis", "ED", "NED", "BC"],
        floatfmt=".4f", tablefmt="latex"))
    with open(Path("results", f"split-{prop}", "alldata.tsv"), "w") as f:
        for row in table:
            f.write("\t".join([row[0], row[1]]+["{0:.4f}".format(x) for x in
                row[2:]])+"\n")


    transform = {
            "PosStrIni": ("PosStrIni", "cornflowerblue"),
            "StrIni": ("StrIni", "olivedrab"),
            "Ini": ("Ini", "darksalmon"),
            "Str": ("Str", "blueviolet"),
            "none": ("-", "plum"),
            }

    for clf in ["svm", "corpar"]:
        print("[i] {0}".format(clf))
        res, colors, poss = [], [], []
        idx = 0
        dsf = open(Path("results", f"split-{prop}", "datasets-{0}.tsv".format(clf)), "w")
        selected_methods = ["PosStrIni", "StrIni", "Str", "Ini", "none"]
        dsf.write("DATASET\t"+"\t".join(selected_methods)+"\n")
        dslabels = [ "Semitic", "Bai", "Burmish", "Karen", "Lalo", "Purus", "Romance"]
        table = []
        for ds in datasets:
            dsf.write(ds)
            table += [[ds]]

            for m in selected_methods:
                res += [
                        mean(by_ds[ds, clf, m] or [0])
                        ]
                poss += [idx]
                idx += 1
                colors += [transform[m][1]]
                dsf.write("\t{0:.4f}".format(res[-1]))
                table[-1] += [res[-1]]
            dsf.write("\n")
            idx += 1
        plt.figure(figsize=(10,3))
        plt.bar(poss, res, color=colors)
        for m in selected_methods:
            plt.plot(-2, -2, "o", color=transform[m][1], label=transform[m][0])
        plt.ylim(0.65, 0.92)
        plt.xlim(-1, len(res)+5)
        plt.xticks(
                range(2, len(res)+6, 6),
                labels=dslabels)
        plt.legend(loc=1)
        plt.savefig(Path("results", f"split-{prop}") / "results-{0}.pdf".format(clf))

        print(tabulate(table, tablefmt="latex", headers=["DATASET"]+selected_methods, floatfmt=".4f"))

    ress, poss = [], []
    selected_methods = ["PosStrIni", "StrIni", "Ini", "none"]

    transform = {
            "PosStrIni-svm": ("PosStrIni/SVM", "#b2182b"),
            "StrIni-svm": ("StrIni/SVM", "#f4a582"),
            "Ini-svm": ("Ini/SVM", "#d1e5f0"),
            "none-svm": ("-/SVM", "#4393c3"),
            "PosStrIni-corpar": ("PosStrIni/CorPaR", "#d6604d"),
            "StrIni-corpar": ("StrIni/CorPaR", "#fddbc7"),
            "Ini-corpar": ("Ini/CorPaR", "#92c5de"),
            "none-corpar": ("-/CorPaR", "#2166ac"),
            }

    yerrs = []
    idx = 0
    colors = []
    for ds in datasets:
        for m in selected_methods:
            for clf in ["svm", "corpar"]:
                ress += [mean(by_ds[ds, clf, m] or [0])]
                yerrs += [np.array(by_ds[ds, clf, m]).std()]
                poss += [idx]
                idx += 1
                colors += [transform[m+'-'+clf][1]]
        idx += 1
    plt.figure(figsize=(10, 3))
    ax = plt.subplot(111)
    plt.bar(poss, ress, color=colors, yerr=yerrs)
    for m in selected_methods:
        for clf in ["svm", "corpar"]:
            plt.plot(
                    -2, -2, "o", color=transform[m+'-'+clf][1],
                    label=transform[m+'-'+clf][0]
                    )
    plt.ylim(0.65, 1)
    plt.xlim(-1, len(ress)+5)
    plt.xticks(
            range(2, len(ress)+1, 9),
            labels=dslabels)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.05), ncol=4,
            fancybox=True, shadow=True)
    plt.savefig(Path("results", f"split-{prop}") / "results-compared.pdf".format(clf))

# average results per prop, lang, clf and save to separate tsv files for svm and corpar with the columns test_prop	lng	ED	NED	B3_F1
for clf in classifiers:
    table = []
    for prop in proportions:
        for ds in datasets:
            for meth in methods:
                for run in range(1, 11):
                    table += [[
                        prop,
                        str(run),
                        ds,
                        meth,
                        *results_detailed[clf, prop, ds, meth, str(run)]
                        ]]
    with open(Path("results", f"all-{clf}.tsv"), "w") as f:
        f.write("test_prop\tvalid\tlng\tmethod\tED\tNED\tBC\n")
        for row in table:
            f.write("\t".join([row[0], row[1], row[2], row[3]]+["{0:.4f}".format(x) for x in row[4:]])+"\n")


