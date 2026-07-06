"""
Phase 0 Power Pilot v2 — Geography + Science re-check.

Fixes:
  - TruthfulQA: correct dataset ID 'truthfulqa/truthful_qa'
  - Science: swaps hard MMLU physics/chemistry for ARC-Challenge
    (grade-school science MCQ, much higher expected accuracy)

Run:
  HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/power_pilot_v2.py
"""

import json
import time
import re
import random
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
DEVICE = "cpu"
DTYPE = torch.float16
N_PER_DOMAIN = 10
SEED = 42

RESULT_DIR = Path(__file__).resolve().parent.parent / "results" / "pilot"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(msg, flush=True)


def load_model():
    log(f"[load] loading {MODEL_ID} on CPU fp16...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, dtype=DTYPE, low_cpu_mem_usage=True,
    )
    model.eval()
    log(f"[load] done in {time.time()-t0:.1f}s\n")
    return tok, model


def generate(model, tok, prompt, max_new_tokens=60):
    inputs = tok(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tok.eos_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    return tok.decode(new_tokens, skip_special_tokens=True).strip()


def build_mcq_prompt(tok, question, choices):
    letters = ["A", "B", "C", "D"]
    options = "\n".join(f"{letters[i]}. {c}" for i, c in enumerate(choices[:4]))
    content = f"{question}\n\n{options}\n\nAnswer with just the letter (A, B, C, or D)."
    msgs = [{"role": "user", "content": content}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def extract_letter(response):
    m = re.search(r"\b([A-D])\b", response.upper())
    return m.group(1) if m else None


def check_arc_science(model, tok, n):
    domain_name = "Science (ARC-Challenge)"
    log(f"\n[{domain_name}] sampling {n} questions from ARC-Challenge")
    ds = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
    items = list(ds)
    random.seed(SEED)
    random.shuffle(items)
    sample = items[:n]

    results = []
    for i, item in enumerate(sample):
        q = item["question"]
        choices = item["choices"]["text"]
        labels = item["choices"]["label"]
        answer_key = item["answerKey"]
        correct_idx = labels.index(answer_key) if answer_key in labels else None
        if correct_idx is None or correct_idx >= 4:
            continue
        correct_letter = ["A", "B", "C", "D"][correct_idx]

        prompt = build_mcq_prompt(tok, q, choices)
        response = generate(model, tok, prompt)
        predicted = extract_letter(response)
        correct = predicted == correct_letter

        log(f"  Q{i+1}: predicted={predicted} correct={correct_letter} → {'✓' if correct else '✗'}")
        results.append({
            "domain": domain_name,
            "question": q[:80],
            "correct_letter": correct_letter,
            "predicted": predicted,
            "response": response[:120],
            "gate_pass": correct,
        })

    survival = sum(r["gate_pass"] for r in results)
    log(f"  [{domain_name}] gate survival: {survival}/{len(results)} = {survival/len(results):.0%}")
    return results


def check_truthfulqa_geography(model, tok, n):
    domain_name = "Geography/Factual (TruthfulQA)"
    log(f"\n[{domain_name}] sampling {n} questions from TruthfulQA mc1")
    ds = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
    items = list(ds)
    random.seed(SEED)
    random.shuffle(items)

    results = []
    for item in items:
        if len(results) >= n:
            break
        q = item["question"]
        choices = item["mc1_targets"]["choices"]
        labels = item["mc1_targets"]["labels"]
        if 1 not in labels:
            continue
        correct_idx = labels.index(1)
        if correct_idx >= 4:
            continue
        correct_letter = ["A", "B", "C", "D"][correct_idx]
        choices_4 = choices[:4]

        prompt = build_mcq_prompt(tok, q, choices_4)
        response = generate(model, tok, prompt)
        predicted = extract_letter(response)
        correct = predicted == correct_letter

        i = len(results) + 1
        log(f"  Q{i}: predicted={predicted} correct={correct_letter} → {'✓' if correct else '✗'}")
        results.append({
            "domain": domain_name,
            "question": q[:80],
            "correct_letter": correct_letter,
            "predicted": predicted,
            "response": response[:120],
            "gate_pass": correct,
        })

    survival = sum(r["gate_pass"] for r in results)
    log(f"  [{domain_name}] gate survival: {survival}/{len(results)} = {survival/len(results):.0%}")
    return results


def main():
    log("=== Phase 0 Power Pilot v2 — Science (ARC) + Geography (TruthfulQA) ===\n")
    tok, model = load_model()

    all_results = []
    all_results += check_arc_science(model, tok, N_PER_DOMAIN)
    all_results += check_truthfulqa_geography(model, tok, N_PER_DOMAIN)

    log("\n" + "=" * 60)
    log("POWER PILOT v2 SUMMARY")
    log("=" * 60)

    by_domain = {}
    for r in all_results:
        by_domain.setdefault(r["domain"], []).append(r)

    # Carry forward v1 History result
    history_v1 = {"n": 10, "passed": 8, "survival_rate": 0.80}
    log(f"  History (MMLU — from v1): 8/10 = 80% gate survival  [carried forward]")

    for domain, items in by_domain.items():
        passed = sum(r["gate_pass"] for r in items)
        rate = passed / len(items)
        log(f"  {domain}: {passed}/{len(items)} = {rate:.0%} gate survival")

    log(f"\n  Projected surviving Qs at 50 Q/domain:")
    log(f"    History:              ~{round(50 * 0.80)} surviving questions  [v1]")
    for domain, items in by_domain.items():
        rate = sum(r["gate_pass"] for r in items) / len(items)
        log(f"    {domain}: ~{round(50 * rate)} surviving questions")

    out = RESULT_DIR / "power_pilot_v2.json"
    summary = {d: {
        "n": len(items),
        "passed": sum(r["gate_pass"] for r in items),
        "survival_rate": sum(r["gate_pass"] for r in items) / len(items),
    } for d, items in by_domain.items()}
    summary["History (MMLU — v1)"] = history_v1
    out.write_text(json.dumps({
        "model": MODEL_ID,
        "n_per_domain": N_PER_DOMAIN,
        "results": all_results,
        "summary": summary,
    }, indent=2))
    log(f"\nwrote {out}")


if __name__ == "__main__":
    main()
