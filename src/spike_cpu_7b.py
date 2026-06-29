"""
Timing spike — CPU fp16, 7B-class model (Linux, 31 GB RAM, 4 GB VRAM).

Goal: confirm the logprob scoring technique works on a true 7B in fp16 on CPU,
and get a real per-trial timing number for this machine. The 3B MPS spike (Mac)
already proved the technique; this proves the *scale* on the actual hardware.

Three checks (same criteria as the original Phase 0.5 spike):
  1. Multi-token answer scoring  — score a multi-token span correctly
  2. Correct answer preferred     — sanity: model assigns higher logprob to correct
  3. Throughput at scale          — extrapolate timing to ~12,600 trials

No MPS / GPU needed — CPU fp16 fits in 31 GB system RAM.
Writes verdict + raw numbers to results/spike/spike_cpu_7b.json.

Run:
  HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/spike_cpu_7b.py
"""

import json
import time
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---- config ---------------------------------------------------------------
# Mistral-7B-Instruct-v0.3 — ungated, true 7B, well-tested for logprob work
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"
DEVICE = "cpu"
DTYPE = torch.float16   # fp16 on CPU: ~14 GB, fits in 31 GB RAM

RESULT_DIR = Path(__file__).resolve().parent.parent / "results" / "spike"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

TOTAL_TRIALS_ESTIMATE = 12600   # from PLAN §2 (both arms)
THROUGHPUT_HOURS_LIMIT = 240    # 10 days — if over this, CPU is impractical


def log(msg):
    print(msg, flush=True)


def score_answer_logprob(model, tok, prompt: str, answer: str) -> dict:
    """
    Sum of per-token log P(answer_token | prompt + preceding answer tokens).
    Identical logic to spike_logprob.py — reused for consistency.
    """
    prompt_ids = tok(prompt, return_tensors="pt").input_ids
    answer_ids = tok(answer, return_tensors="pt", add_special_tokens=False).input_ids
    full_ids = torch.cat([prompt_ids, answer_ids], dim=1)

    with torch.no_grad():
        logits = model(full_ids).logits  # [1, seq, vocab]

    logprobs = torch.log_softmax(logits.float(), dim=-1)
    n_answer = answer_ids.shape[1]
    pred_slice = logprobs[0, -(n_answer + 1):-1, :]   # [n_answer, vocab]
    tgt = full_ids[0, -n_answer:]                      # [n_answer]
    tok_lp = pred_slice[torch.arange(n_answer), tgt]   # [n_answer]
    return {
        "answer": answer,
        "n_tokens": int(n_answer),
        "token_logprobs": [round(x, 4) for x in tok_lp.tolist()],
        "sum_logprob": round(float(tok_lp.sum()), 4),
        "mean_logprob": round(float(tok_lp.mean()), 4),
    }


def load_model():
    log(f"[load] loading {MODEL_ID} on CPU (fp16) — expect ~14 GB RAM, takes a few minutes...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        low_cpu_mem_usage=True,
    )
    model.eval()
    elapsed = time.time() - t0
    log(f"[load] done in {elapsed:.1f}s\n")
    return tok, model, elapsed


def build_prompt(tok, question: str) -> str:
    msgs = [{"role": "user", "content": question}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def main():
    result = {"model": MODEL_ID, "device": DEVICE, "dtype": "fp16", "tests": {}}
    log(f"=== CPU 7B timing spike — {MODEL_ID} ===\n")

    tok, model, load_s = load_model()
    result["tests"]["load_seconds_cpu"] = round(load_s, 1)

    # Same test item as the 3B MPS spike — multi-token answers, clear ground truth
    q = build_prompt(tok, "What is the longest river in the world? Answer in one short phrase.")
    correct, wrong = "the Nile", "the Amazon"

    # ---- Test 1: multi-token answer scoring + correct answer preferred -----
    log("[test1] multi-token answer scoring...")
    r_correct = score_answer_logprob(model, tok, q, correct)
    r_wrong   = score_answer_logprob(model, tok, q, wrong)
    log(f"        P('{correct}') sum_logprob = {r_correct['sum_logprob']} ({r_correct['n_tokens']} tokens)")
    log(f"        P('{wrong}')  sum_logprob = {r_wrong['sum_logprob']} ({r_wrong['n_tokens']} tokens)")
    multitoken_ok       = r_correct["n_tokens"] >= 2 or r_wrong["n_tokens"] >= 2
    correct_preferred   = r_correct["sum_logprob"] > r_wrong["sum_logprob"]
    log(f"        multi-token span handled: {multitoken_ok} | correct answer preferred: {correct_preferred}\n")
    result["tests"]["multitoken"] = {
        "correct": r_correct, "wrong": r_wrong,
        "multitoken_ok": multitoken_ok,
        "correct_preferred": correct_preferred,
    }

    # ---- Test 2: throughput ------------------------------------------------
    log("[test2] throughput — timing 10 scoring calls on CPU...")
    N = 10
    t0 = time.time()
    for _ in range(N):
        score_answer_logprob(model, tok, q, correct)
        score_answer_logprob(model, tok, q, wrong)
    per_scoring  = (time.time() - t0) / (N * 2)
    per_trial    = per_scoring * 4      # ~4 scorings per trial (2 turns × 2 answers)
    total_hours  = per_trial * TOTAL_TRIALS_ESTIMATE / 3600
    log(f"        {per_scoring*1000:.0f} ms / answer-scoring")
    log(f"        ~{per_trial:.2f} s / trial (4 scorings) -> ~{total_hours:.1f} h for {TOTAL_TRIALS_ESTIMATE} trials\n")
    result["tests"]["throughput"] = {
        "ms_per_scoring":       round(per_scoring * 1000, 1),
        "sec_per_trial_est":    round(per_trial, 2),
        "total_hours_est":      round(total_hours, 1),
        "total_days_est":       round(total_hours / 24, 1),
        "practical":            total_hours < THROUGHPUT_HOURS_LIMIT,
    }

    # ---- Verdict -----------------------------------------------------------
    go = multitoken_ok and correct_preferred and total_hours < THROUGHPUT_HOURS_LIMIT
    result["verdict"] = {
        "GO": go,
        "criteria": {
            "multitoken_scoring_works":   multitoken_ok,
            "correct_answer_preferred":   correct_preferred,
            f"throughput_under_{THROUGHPUT_HOURS_LIMIT}h": total_hours < THROUGHPUT_HOURS_LIMIT,
        },
        "note": (
            "GO => CPU logprob arm is practical for this machine. "
            "Consider moving to CUDA if throughput is marginal."
            if go else
            "NO-GO => CPU too slow. Options: (a) run logprob arm on CUDA GPU for the subset that fits, "
            "(b) reduce trial count, (c) drop logprob arm to Future Work."
        ),
    }
    log("=" * 60)
    log(f"VERDICT: {'GO ✅' if go else 'NO-GO ⚠️'}")
    for k, v in result["verdict"]["criteria"].items():
        log(f"   {'✓' if v else '✗'} {k}")
    log(f"\n{result['verdict']['note']}")
    log("=" * 60)

    out = RESULT_DIR / "spike_cpu_7b.json"
    out.write_text(json.dumps(result, indent=2))
    log(f"\nwrote {out}")


if __name__ == "__main__":
    main()
