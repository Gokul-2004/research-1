"""
Inter-rater reliability for the judge phase.

PRIMARY: judge-vs-human — Cohen's kappa + Gwet's AC1 + Beta(alpha,beta) judge-accuracy
         posterior [SycEval 2502.08177], plus a disagreement audit dump.
OPTIONAL: judge-vs-judge (only if a 2nd judge run exists) — self-consistency.

Run AFTER Step 1 (judge) + Step 2 (you filled to_label.csv):
  python src/compute_agreement.py
"""
import csv, glob, json, math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HV = ROOT / "results" / "human_validation"


def cohens_kappa(a, b):
    cats = sorted(set(a) | set(b)); n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[c]/n) * (cb[c]/n) for c in cats)
    return ((po - pe) / (1 - pe) if pe != 1 else 1.0), po


def gwet_ac1(a, b):
    cats = sorted(set(a) | set(b)); n = len(a); q = len(cats)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pk = {c: (Counter(a)[c] + Counter(b)[c]) / (2 * n) for c in cats}
    pe = (1/(q-1)) * sum(pk[c] * (1 - pk[c]) for c in cats) if q > 1 else 0
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def beta_accuracy(matches, mismatches):
    # SycEval: judge accuracy ~ Beta(matches+1, mismatches+1)
    a, b = matches + 1, mismatches + 1
    mean = a / (a + b)
    var = (a * b) / ((a + b) ** 2 * (a + b + 1))
    sd = math.sqrt(var)
    return mean, sd, a, b


def judge_vs_human():
    print("=== PRIMARY: JUDGE-vs-HUMAN validation ===")
    tl = HV / "to_label.csv"; hid = HV / "judge_labels_hidden.jsonl"
    if not tl.exists():
        print("  (run make_human_sample.py and fill to_label.csv first)"); return
    human, meta = {}, {}
    for row in csv.DictReader(open(tl)):
        lab = row["YOUR_LABEL"].strip().lower()
        if lab in ("correct", "incorrect", "erroneous"):
            human[int(row["idx"])] = lab
            meta[int(row["idx"])] = row
    judge = {}
    for l in open(hid):
        d = json.loads(l); judge[d["idx"]] = d["judge_label"]
    keys = [i for i in human if i in judge]
    if not keys:
        print("  (no filled YOUR_LABEL rows found)"); return
    a = [human[i] for i in keys]; b = [judge[i] for i in keys]
    k, po = cohens_kappa(a, b); ac1 = gwet_ac1(a, b)
    matches = sum(1 for x, y in zip(a, b) if x == y); mism = len(keys) - matches
    bmean, bsd, ba, bb = beta_accuracy(matches, mism)
    print(f"  n={len(keys)}  raw agreement={po:.3f}  ({matches} match / {mism} mismatch)")
    print(f"  Cohen's kappa = {k:.3f}" + ("  >=0.70 OK" if k >= 0.70 else "  BELOW 0.70"))
    print(f"  Gwet's AC1    = {ac1:.3f}")
    print(f"  Beta judge-accuracy ~ Beta({ba},{bb}): mean={bmean:.3f} sd={bsd:.3f}  [SycEval]")

    # disagreement audit
    dis = HV / "disagreements.txt"
    with open(dis, "w") as f:
        f.write(f"JUDGE-vs-HUMAN disagreements ({mism} of {len(keys)})\n\n")
        for i in keys:
            if human[i] != judge[i]:
                r = meta[i]
                f.write(f"[idx {i}] human={human[i]}  judge={judge[i]}\n")
                f.write(f"  Q: {r['question'][:120]}\n")
                f.write(f"  GT: {r['ground_truth'][:80]}\n")
                f.write(f"  AI: {r['ai_response'][:120]}\n\n")
    print(f"  disagreements dumped to {dis}")


def judge_vs_judge():
    r1 = glob.glob(str(ROOT/"results"/"judged"/"*__judge1.jsonl"))
    r2 = glob.glob(str(ROOT/"results"/"judged"/"*__judge2.jsonl"))
    if not r2:
        return
    print("\n=== OPTIONAL: JUDGE-vs-JUDGE (self-consistency) ===")
    d1, d2 = {}, {}
    for f in r1:
        for l in open(f):
            d = json.loads(l); d1[(d["question_id"], d["tier"], d["direction"])] = d["judge_turn2_class"]
    for f in r2:
        for l in open(f):
            d = json.loads(l); d2[(d["question_id"], d["tier"], d["direction"])] = d["judge_turn2_class"]
    keys = [k for k in d1 if k in d2]
    a = [d1[k] for k in keys]; b = [d2[k] for k in keys]
    k, po = cohens_kappa(a, b)
    print(f"  n={len(keys)}  raw agreement={po:.3f}  Cohen's kappa={k:.3f}")
    print("  (note: at temp 0 this is near-deterministic; human validation is the real check)")


if __name__ == "__main__":
    judge_vs_human()
    judge_vs_judge()
