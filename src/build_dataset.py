"""
Phase 2 — Dataset builder.

Pulls 50 questions per domain from the sources identified in the literature
survey (Appendix B/D of Analysis of Literature Survey.md) and writes the
150-question bank to data/questions.json.

Sources:
  Science   → ARC-Challenge (allenai/ai2_arc) [Zhang 2508.13743]
  History   → MMLU high_school_world_history + prehistory [Sharma 2310.13548]
  Geography → TruthfulQA mc1 (truthfulqa/truthful_qa) [Ben Natan 2601.15436]
              fallback: TriviaQA (mandarjoshi/trivia_qa) [Sharma 2310.13548]

Output schema (one item):
  {
    "id": "sci_001",
    "domain": "Science",
    "source": "ARC-Challenge",
    "question": "...",
    "choices": ["A text", "B text", "C text", "D text"],
    "correct_letter": "C",
    "correct_text": "...",
    "wrong_X": "...",          # best distractor (wrong answer for incorrect-endorsement arm)
    "wrong_X_letter": "A"
  }

Run:
  HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/build_dataset.py
"""

import json
import random
from pathlib import Path

from datasets import load_dataset

N_PER_DOMAIN = 50
SEED = 42
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Science — ARC-Challenge
# ---------------------------------------------------------------------------

def build_science(n):
    log(f"\n[Science] loading ARC-Challenge...")
    ds = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
    items = list(ds)
    random.seed(SEED)
    random.shuffle(items)

    out = []
    for item in items:
        if len(out) >= n:
            break
        choices_text = item["choices"]["text"]
        choices_labels = item["choices"]["label"]
        answer_key = item["answerKey"]

        # Only 4-choice items; answerKey must be A-D
        if answer_key not in ["A", "B", "C", "D"]:
            continue
        if len(choices_text) < 4:
            continue

        correct_idx = ["A", "B", "C", "D"].index(answer_key)
        correct_text = choices_text[correct_idx]

        # wrong_X = LAST distractor = most plausible wrong answer.
        # First distractor is often trivially wrong; last is the hardest.
        # More realistic authority pressure. (SycEval 2502.08177 uses best-wrong.)
        wrong_candidates = [
            (choices_text[i], ["A", "B", "C", "D"][i])
            for i in range(4) if i != correct_idx
        ]
        wrong_text, wrong_letter = wrong_candidates[-1]

        out.append({
            "id": f"sci_{len(out)+1:03d}",
            "domain": "Science",
            "source": "ARC-Challenge",
            "question": item["question"],
            "choices": [choices_text[i] for i in range(4)],
            "correct_letter": answer_key,
            "correct_text": correct_text,
            "wrong_X": wrong_text,
            "wrong_X_letter": wrong_letter,
        })

    log(f"  collected {len(out)} Science items")
    return out


# ---------------------------------------------------------------------------
# History — MMLU
# ---------------------------------------------------------------------------

def build_history(n):
    log(f"\n[History] loading MMLU world_history + prehistory...")
    collected = []
    for subj in ["high_school_world_history", "prehistory"]:
        try:
            ds = load_dataset("cais/mmlu", subj, split="test")
            collected.extend(list(ds))
        except Exception as e:
            log(f"  warning: {subj}: {e}")

    random.seed(SEED)
    random.shuffle(collected)

    letters = ["A", "B", "C", "D"]
    out = []
    for item in collected:
        if len(out) >= n:
            break
        choices = item["choices"]
        if len(choices) < 4:
            continue
        correct_idx = item["answer"]
        if correct_idx >= 4:
            continue
        correct_letter = letters[correct_idx]
        correct_text = choices[correct_idx]

        wrong_candidates = [
            (choices[i], letters[i]) for i in range(4) if i != correct_idx
        ]
        wrong_text, wrong_letter = wrong_candidates[-1]

        out.append({
            "id": f"his_{len(out)+1:03d}",
            "domain": "History",
            "source": "MMLU",
            "question": item["question"],
            "choices": choices,
            "correct_letter": correct_letter,
            "correct_text": correct_text,
            "wrong_X": wrong_text,
            "wrong_X_letter": wrong_letter,
        })

    log(f"  collected {len(out)} History items")
    return out


# ---------------------------------------------------------------------------
# Geography — TruthfulQA (mc1), fallback TriviaQA
# ---------------------------------------------------------------------------

def build_geography(n):
    log(f"\n[Factual] loading TruthfulQA mc1...")
    ds = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
    items = list(ds)
    random.seed(SEED)
    random.shuffle(items)

    out = []
    for item in items:
        if len(out) >= n:
            break
        choices = item["mc1_targets"]["choices"]
        labels = item["mc1_targets"]["labels"]
        if 1 not in labels:
            continue
        correct_idx = labels.index(1)
        if correct_idx >= 4 or len(choices) < 2:
            continue

        choices_4 = choices[:4]
        correct_letter = ["A", "B", "C", "D"][correct_idx]
        correct_text = choices[correct_idx]

        # wrong_X = mc1 last distractor = most plausible wrong answer.
        # TruthfulQA mc1 orders distractors by plausibility; last = hardest wrong.
        wrong_candidates = [
            (choices_4[i], ["A", "B", "C", "D"][i])
            for i in range(len(choices_4)) if i != correct_idx
        ]
        if not wrong_candidates:
            continue
        wrong_text, wrong_letter = wrong_candidates[-1]

        out.append({
            "id": f"geo_{len(out)+1:03d}",
            "domain": "Factual",
            "source": "TruthfulQA",
            "question": item["question"],
            "choices": choices_4,
            "correct_letter": correct_letter,
            "correct_text": correct_text,
            "wrong_X": wrong_text,
            "wrong_X_letter": wrong_letter,
        })

    if len(out) < n:
        log(f"  TruthfulQA only gave {len(out)} items — falling back to TriviaQA for remaining {n - len(out)}")
        out += build_geography_trivia_fallback(n - len(out), existing=len(out))

    log(f"  collected {len(out)} Factual items")
    return out


def build_geography_trivia_fallback(n, existing=0):
    log(f"\n[Geography fallback] loading TriviaQA...")
    try:
        ds = load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")
    except Exception as e:
        log(f"  ERROR: {e}")
        return []

    items = list(ds)
    random.seed(SEED + 1)
    random.shuffle(items)

    out = []
    for item in items:
        if len(out) >= n:
            break
        q = item["question"]
        answers = item["answer"]["aliases"] if item["answer"]["aliases"] else [item["answer"]["value"]]
        correct_text = item["answer"]["value"]
        if not correct_text:
            continue

        # TriviaQA is open-ended — we store it as free-form (no MCQ choices)
        # wrong_X must be hand-verified; flag for manual review
        out.append({
            "id": f"geo_{existing + len(out)+1:03d}",
            "domain": "Geography",
            "source": "TriviaQA",
            "question": q,
            "choices": None,
            "correct_letter": None,
            "correct_text": correct_text,
            "wrong_X": "NEEDS_MANUAL_WRONG_X",
            "wrong_X_letter": None,
            "note": "TriviaQA fallback — verify correct_text and fill wrong_X before use",
        })

    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log("=== Phase 2 Dataset Builder ===")
    log(f"Target: {N_PER_DOMAIN} Q/domain × 3 domains = {N_PER_DOMAIN * 3} total\n")

    science = build_science(N_PER_DOMAIN)
    history = build_history(N_PER_DOMAIN)
    geography = build_geography(N_PER_DOMAIN)

    all_items = science + history + geography

    log(f"\n{'='*60}")
    log(f"DATASET SUMMARY")
    log(f"{'='*60}")
    log(f"  Science:   {len(science)} items")
    log(f"  History:   {len(history)} items")
    log(f"  Factual:   {len(geography)} items")
    log(f"  Total:     {len(all_items)} items")

    needs_review = [q for q in all_items if q.get("wrong_X") == "NEEDS_MANUAL_WRONG_X"]
    if needs_review:
        log(f"\n  ⚠ {len(needs_review)} items need manual wrong_X before inference (TriviaQA fallback)")

    OUT_PATH.write_text(json.dumps(all_items, indent=2))
    log(f"\nwrote {OUT_PATH}")


if __name__ == "__main__":
    main()
