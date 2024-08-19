"""
Prepare test and training data for the experiments.
"""
from pkg.util import Trainer
from pathlib import Path
import json
from tabulate import tabulate
from tqdm import tqdm as progressbar

datasets = {
    "kogansemitic": ("ps", "Semitic"),
    "wangbai": ("ProtoBai", "Bai"),
    "hillburmish": ("ProtoBurmish", "Burmish"),
    "ltkkaren": ("ProtoKaren", "Karen"),
    "yanglalo": ("ProtoLalo", "Lalo"),
    "carvalhopurus": ("ProtoPurus", "Purus"),
    "meloniromance": ("Latin", "Romance"),
        }

proportions = ['0.1','0.5','0.8']
cross_val_size = 10

table = []
for ds, (proto, name) in progressbar(datasets.items()):
    for prop in proportions:
        props = (100 - int(float(prop) * 100), int(float(prop) * 100), 0)
        trn = Trainer(
                str(Path("data", ds+".tsv")),
                ref="cogids",
                fuzzy=True,
                target=proto
                )
        cognates, words = 0, 0
        etd = trn.get_etymdict(ref="cogids")
        for cogid, idxs in etd.items():
            lngs = [trn[idx[0], "doculect"] for idx in idxs if idx]
            if proto in lngs and len(lngs) > 2:
                cognates += 1
                words += len(lngs)

        for i in range(cross_val_size):
            wl, test_set, _ = trn.split(proportions=props)
            wl.output(
                    "tsv",
                    filename=str(Path(
                        "data", f"data-{prop}", "testlists", name, "test-{0}".format(i+1))),
                    ignore="all",
                    prettify=False
                    )
            output_path = Path("data", f"data-{prop}", "testitems", name)
            output_path.mkdir(parents=True, exist_ok=True)
            with open(output_path / "test-{0}.json".format(i + 1), "w") as f:
                json.dump(test_set, f)

    table += [[name, trn.width, cognates, words]]
print(tabulate(table, tablefmt="latex"))
