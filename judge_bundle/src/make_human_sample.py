"""
Extract ~100 random trials for HUMAN validation (Step 3 of the judge phase).

Writes results/human_validation/to_label.csv with columns you fill in:
  question, options, ground_truth, ai_response, YOUR_LABEL
YOUR_LABEL: type one of  correct / incorrect / erroneous

The judge's own label is written to a SEPARATE file (judge_labels_hidden.jsonl)
so you are NOT biased while labeling. After you finish, compute_agreement.py
compares your labels to the judge's -> Cohen's kappa + Gwet's AC1.

Run:  python src/make_human_sample.py --n 100
"""
import argparse, csv, glob, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "human_validation"
OUT.mkdir(parents=True, exist_ok=True)


def main(n, seed):
    qlook = {q["id"]: q for q in json.loads((ROOT / "data" / "questions.json").read_text())}
    # Prefer sampling from judged files so we have the judge label to compare.
    judged = glob.glob(str(ROOT / "results" / "judged" / "*__judge1.jsonl"))
    if not judged:
        raise SystemExit("Run the judge first (judge1 files needed) before sampling.")
    rows = []
    for f in judged:
        for l in open(f):
            try: rows.append(json.loads(l))
            except: pass
    random.seed(seed); random.shuffle(rows)
    sample = rows[:n]

    to_label = OUT / "to_label.csv"
    hidden = OUT / "judge_labels_hidden.jsonl"
    with open(to_label, "w", newline="") as cf, open(hidden, "w") as hf:
        w = csv.writer(cf)
        w.writerow(["idx", "model", "question", "options", "ground_truth", "ai_response", "YOUR_LABEL"])
        for i, r in enumerate(sample):
            q = qlook[r["question_id"]]
            opts = " | ".join(f"{'ABCD'[j]}. {c}" for j, c in enumerate(q["choices"][:4]))
            w.writerow([i, r["model"], q["question"], opts, q["correct_text"],
                        r.get("turn2_response", ""), ""])
            hf.write(json.dumps({"idx": i, "judge_label": r["judge_turn2_class"]}) + "\n")
    print(f"wrote {to_label}  ({len(sample)} rows to label)")
    print(f"wrote {hidden}   (judge labels kept hidden until you're done)")
    print("\nNow open to_label.csv, fill YOUR_LABEL for each row (correct/incorrect/erroneous),")
    print("then run:  python src/compute_agreement.py")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    main(a.n, a.seed)
