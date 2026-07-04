"""
Compute inter-rater reliability for the judge phase:
  A) judge-vs-judge (dual-judge, run1 vs run2)  -> Cohen's kappa
  B) judge-vs-human (your labels vs judge)       -> Cohen's kappa + Gwet's AC1

Run AFTER:
  - both judge runs done (for A)
  - you've filled to_label.csv (for B)

Usage:  python src/compute_agreement.py
"""
import csv, glob, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cohens_kappa(a, b):
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[c]/n) * (cb[c]/n) for c in cats)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0, po


def gwet_ac1(a, b):
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    q = len(cats)
    pk = {}
    for c in cats:
        pk[c] = (Counter(a)[c] + Counter(b)[c]) / (2 * n)
    pe = (1/(q-1)) * sum(pk[c] * (1 - pk[c]) for c in cats) if q > 1 else 0
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def part_A():
    print("=== A) JUDGE-vs-JUDGE (dual-judge reliability) ===")
    r1 = {}; r2 = {}
    for f in glob.glob(str(ROOT/"results"/"judged"/"*__judge1.jsonl")):
        for l in open(f):
            d = json.loads(l); r1[(d["question_id"], d["tier"], d["direction"])] = d["judge_turn2_class"]
    for f in glob.glob(str(ROOT/"results"/"judged"/"*__judge2.jsonl")):
        for l in open(f):
            d = json.loads(l); r2[(d["question_id"], d["tier"], d["direction"])] = d["judge_turn2_class"]
    keys = [k for k in r1 if k in r2]
    if not keys:
        print("  (need both judge1 and judge2 files)"); return
    a = [r1[k] for k in keys]; b = [r2[k] for k in keys]
    k, po = cohens_kappa(a, b)
    print(f"  n={len(keys)}  raw agreement={po:.3f}  Cohen's kappa={k:.3f}"
          + ("  >=0.70 OK" if k >= 0.70 else "  BELOW 0.70 — investigate"))


def part_B():
    print("\n=== B) JUDGE-vs-HUMAN (validation) ===")
    tl = ROOT/"results"/"human_validation"/"to_label.csv"
    hid = ROOT/"results"/"human_validation"/"judge_labels_hidden.jsonl"
    if not tl.exists():
        print("  (run make_human_sample.py and fill to_label.csv first)"); return
    human = {}
    for row in csv.DictReader(open(tl)):
        lab = row["YOUR_LABEL"].strip().lower()
        if lab in ("correct", "incorrect", "erroneous"):
            human[int(row["idx"])] = lab
    judge = {}
    for l in open(hid):
        d = json.loads(l); judge[d["idx"]] = d["judge_label"]
    keys = [i for i in human if i in judge]
    if not keys:
        print("  (no filled YOUR_LABEL rows found)"); return
    a = [human[i] for i in keys]; b = [judge[i] for i in keys]
    k, po = cohens_kappa(a, b); ac1 = gwet_ac1(a, b)
    print(f"  n={len(keys)}  raw agreement={po:.3f}")
    print(f"  Cohen's kappa={k:.3f}" + ("  >=0.70 OK" if k >= 0.70 else "  BELOW 0.70"))
    print(f"  Gwet's AC1  ={ac1:.3f}  (prevalence-robust complement)")


if __name__ == "__main__":
    part_A()
    part_B()
