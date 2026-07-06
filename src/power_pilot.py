"""
Phase 0 — Power pilot.

Loads 10 questions per domain (Science, History, Geography) from real
datasets, runs Qwen2.5-3B-Instruct at temp=0, checks whether the model
answers correctly unprompted (baseline gate), and reports survival rate.

This gives us the real gate survival rate to plug into the power check
instead of the analytical estimate of ~50%.

Sources (matching PLAN.md §9b):
  Science   → MMLU: high_school_physics + high_school_chemistry (MCQ)
  History   → MMLU: high_school_world_history
  Geography → TruthfulQA (mc1 format, 2-answer version)

Run:
  HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/power_pilot.py
"""

import json
import time
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
DEVICE = "cpu"
DTYPE = torch.float16
N_PER_DOMAIN = 10

RESULT_DIR = Path(__file__).resolve().parent.parent / "results" / "pilot"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(msg, flush=True)


def load_model():
    log(f"[load] loading {MODEL_ID} on CPU fp16...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=DTYPE, low_cpu_mem_usage=True,
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
    options = "\n".join(f"{letters[i]}. {c}" for i, c in enumerate(choices))
    content = f"{question}\n\n{options}\n\nAnswer with just the letter (A, B, C, or D)."
    msgs = [{"role": "user", "content": content}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def extract_letter(response):
    m = re.search(r"\b([A-D])\b", response.upper())
    return m.group(1) if m else None


def check_mmlu_domain(model, tok, subjects, domain_name, n):
    log(f"\n[{domain_name}] sampling {n} questions from MMLU: {subjects}")
    results = []
    collected = []
    for subj in subjects:
        try:
            ds = load_dataset("cais/mmlu", subj, split="test", trust_remote_code=True)
            for item in ds:
                collected.append(item)
                if len(collected) >= n * 3:
                    break
        except Exception as e:
            log(f"  warning: could not load {subj}: {e}")
    if not collected:
        log(f"  ERROR: no items collected for {domain_name}")
        return results

    import random
    random.seed(42)
    random.shuffle(collected)
    sample = collected[:n]

    for i, item in enumerate(sample):
        q = item["question"]
        choices = item["choices"]
        correct_idx = item["answer"]
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


def check_truthfulqa(model, tok, n):
    domain_name = "Geography/Factual"
    log(f"\n[{domain_name}] sampling {n} questions from TruthfulQA (mc1)")
    results = []
    try:
        ds = load_dataset("truthful_qa", "multiple_choice", split="validation", trust_remote_code=True)
    except Exception as e:
        log(f"  ERROR loading TruthfulQA: {e}")
        return results

    import random
    random.seed(42)
    items = list(ds)
    random.shuffle(items)
    sample = items[:n]

    for i, item in enumerate(sample):
        q = item["question"]
        choices = item["mc1_targets"]["choices"]
        labels = item["mc1_targets"]["labels"]
        correct_idx = labels.index(1)
        correct_letter = ["A", "B", "C", "D", "E"][correct_idx] if correct_idx < 5 else "A"

        # Only use first 4 choices to keep MCQ clean
        choices_4 = choices[:4]
        correct_letter_4 = ["A", "B", "C", "D"][correct_idx] if correct_idx < 4 else None

        if correct_letter_4 is None:
            continue

        prompt = build_mcq_prompt(tok, q, choices_4)
        response = generate(model, tok, prompt)
        predicted = extract_letter(response)
        correct = predicted == correct_letter_4

        log(f"  Q{i+1}: predicted={predicted} correct={correct_letter_4} → {'✓' if correct else '✗'}")
        results.append({
            "domain": domain_name,
            "question": q[:80],
            "correct_letter": correct_letter_4,
            "predicted": predicted,
            "response": response[:120],
            "gate_pass": correct,
        })
        if len(results) >= n:
            break

    survival = sum(r["gate_pass"] for r in results)
    log(f"  [{domain_name}] gate survival: {survival}/{len(results)} = {survival/len(results):.0%}")
    return results


def main():
    log("=== Phase 0 Power Pilot — Qwen2.5-3B baseline gate check ===\n")
    tok, model = load_model()

    all_results = []

    # Science: MMLU high_school_physics + high_school_chemistry
    all_results += check_mmlu_domain(
        model, tok,
        subjects=["high_school_physics", "high_school_chemistry"],
        domain_name="Science",
        n=N_PER_DOMAIN,
    )

    # History: MMLU high_school_world_history
    all_results += check_mmlu_domain(
        model, tok,
        subjects=["high_school_world_history", "prehistory"],
        domain_name="History",
        n=N_PER_DOMAIN,
    )

    # Geography/Factual: TruthfulQA
    all_results += check_truthfulqa(model, tok, n=N_PER_DOMAIN)

    # Summary
    log("\n" + "=" * 60)
    log("POWER PILOT SUMMARY")
    log("=" * 60)
    by_domain = {}
    for r in all_results:
        d = r["domain"]
        by_domain.setdefault(d, []).append(r)

    total_pass = 0
    total = 0
    for domain, items in by_domain.items():
        passed = sum(r["gate_pass"] for r in items)
        total_pass += passed
        total += len(items)
        log(f"  {domain}: {passed}/{len(items)} = {passed/len(items):.0%} gate survival")

    overall = total_pass / total if total > 0 else 0
    log(f"\n  Overall: {total_pass}/{total} = {overall:.0%} gate survival")
    log(f"\n  Projected surviving Qs at 50 Q/domain:")
    for domain, items in by_domain.items():
        rate = sum(r["gate_pass"] for r in items) / len(items)
        log(f"    {domain}: ~{round(50 * rate)} surviving questions")

    out = RESULT_DIR / "power_pilot.json"
    out.write_text(json.dumps({
        "model": MODEL_ID,
        "n_per_domain": N_PER_DOMAIN,
        "results": all_results,
        "summary": {d: {
            "n": len(items),
            "passed": sum(r["gate_pass"] for r in items),
            "survival_rate": sum(r["gate_pass"] for r in items) / len(items),
        } for d, items in by_domain.items()},
        "overall_survival_rate": overall,
    }, indent=2))
    log(f"\nwrote {out}")


if __name__ == "__main__":
    main()
