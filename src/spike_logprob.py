"""
Phase 0.5 — Logprob feasibility spike (Apple Silicon / MPS).

Decides GO / NO-GO for the logprob arm of the Authority-Graded Sycophancy study.
See PLAN.md §"Phase 0.5". Tests, in risk order:

  1. MPS logprob correctness  — do per-token logits on MPS match a CPU run?
  2. Multi-token answer scoring — can we score a multi-token answer span
                                  ("the Nile", "956446") as a summed log-prob?
  3. Throughput at scale       — per-item timing -> extrapolate to ~12,600 trials.

Run:  .venv/bin/python src/spike_logprob.py
Uses an UNGATED model (no HF token needed) so we can get an answer today.
Writes a verdict + raw numbers to results/spike/spike_result.json
"""

import json
import time
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---- config ---------------------------------------------------------------
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"   # ungated, ~6GB fp16 — fits 16GB RAM
RESULT_DIR = Path(__file__).resolve().parent.parent / "results" / "spike"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Thresholds for the GO/NO-GO verdict
MAX_LOGPROB_ABS_DIFF = 0.05   # MPS vs CPU per-token logprob max abs diff allowed
TOTAL_TRIALS_ESTIMATE = 12600 # from PLAN §2 scale (both arms)


def log(msg):
    print(msg, flush=True)


# ---- answer scoring -------------------------------------------------------
def score_answer_logprob(model, tok, prompt: str, answer: str, device) -> dict:
    """
    Sum of per-token log P(answer_token | prompt + preceding answer tokens).
    Handles MULTI-TOKEN answers ("the Nile" -> several tokens). This is the
    metric-validity test: we must score the whole answer span, not one token.
    """
    prompt_ids = tok(prompt, return_tensors="pt").input_ids
    # tokenize answer WITHOUT special tokens, as a continuation
    answer_ids = tok(answer, return_tensors="pt", add_special_tokens=False).input_ids
    full_ids = torch.cat([prompt_ids, answer_ids], dim=1).to(device)

    with torch.no_grad():
        logits = model(full_ids).logits  # [1, seq, vocab]

    logprobs = torch.log_softmax(logits.float(), dim=-1)
    n_answer = answer_ids.shape[1]
    # logits at position t predict token t+1; answer tokens are the last n_answer
    # so the predictions for them sit at positions [-(n_answer+1) : -1]
    pred_slice = logprobs[0, -(n_answer + 1):-1, :]            # [n_answer, vocab]
    tgt = full_ids[0, -n_answer:]                              # [n_answer]
    tok_lp = pred_slice[torch.arange(n_answer), tgt]           # [n_answer]
    return {
        "answer": answer,
        "n_tokens": int(n_answer),
        "token_logprobs": [round(x, 4) for x in tok_lp.tolist()],
        "sum_logprob": round(float(tok_lp.sum()), 4),
        "mean_logprob": round(float(tok_lp.mean()), 4),
    }


def load_model(device):
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
    ).to(device)
    model.eval()
    return tok, model, time.time() - t0


def build_prompt(tok, question: str) -> str:
    msgs = [{"role": "user", "content": question}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def main():
    result = {"model": MODEL_ID, "tests": {}}
    log(f"=== Phase 0.5 logprob spike — {MODEL_ID} ===\n")

    if not torch.backends.mps.is_available():
        log("FATAL: MPS not available. Aborting (this Mac can't run the MPS arm).")
        sys.exit(1)

    # A multi-token-answer test item: the answer 'the Nile' / wrong 'the Amazon'
    # are deliberately multi-token, plus a numeric one.
    q = build_prompt(
        AutoTokenizer.from_pretrained(MODEL_ID),
        "What is the longest river in the world? Answer in one short phrase.",
    )
    correct, wrong = "the Nile", "the Amazon"

    # ---- Test 0: load on MPS --------------------------------------------
    log("[load] loading model on MPS (fp16)...")
    tok, model_mps, load_s = load_model("mps")
    log(f"[load] done in {load_s:.1f}s\n")
    result["tests"]["load_seconds_mps"] = round(load_s, 1)

    # ---- Test 2 (run first; needed by Test 1): multi-token scoring on MPS
    log("[test2] multi-token answer scoring on MPS...")
    mps_correct = score_answer_logprob(model_mps, tok, q, correct, "mps")
    mps_wrong = score_answer_logprob(model_mps, tok, q, wrong, "mps")
    log(f"        P('{correct}') sum_logprob = {mps_correct['sum_logprob']} "
        f"({mps_correct['n_tokens']} tokens)")
    log(f"        P('{wrong}')  sum_logprob = {mps_wrong['sum_logprob']} "
        f"({mps_wrong['n_tokens']} tokens)")
    multitoken_ok = mps_correct["n_tokens"] >= 2 or mps_wrong["n_tokens"] >= 2
    correct_preferred = mps_correct["sum_logprob"] > mps_wrong["sum_logprob"]
    log(f"        multi-token span handled: {multitoken_ok} | "
        f"correct answer preferred: {correct_preferred}\n")
    result["tests"]["multitoken"] = {
        "correct": mps_correct, "wrong": mps_wrong,
        "multitoken_ok": multitoken_ok,
        "correct_preferred": correct_preferred,
    }

    # ---- Test 1: MPS vs CPU correctness ---------------------------------
    log("[test1] MPS-vs-CPU logprob correctness (reload on CPU)...")
    del model_mps
    tok_cpu, model_cpu, _ = load_model("cpu")
    cpu_correct = score_answer_logprob(model_cpu, tok_cpu, q, correct, "cpu")
    # align per-token logprobs and take max abs diff
    diffs = [abs(a - b) for a, b in
             zip(mps_correct["token_logprobs"], cpu_correct["token_logprobs"])]
    max_diff = max(diffs) if diffs else float("nan")
    mps_cpu_ok = max_diff <= MAX_LOGPROB_ABS_DIFF
    log(f"        CPU sum_logprob = {cpu_correct['sum_logprob']} | "
        f"MPS sum_logprob = {mps_correct['sum_logprob']}")
    log(f"        max per-token |MPS-CPU| = {max_diff:.4f} "
        f"(threshold {MAX_LOGPROB_ABS_DIFF}) -> {'OK' if mps_cpu_ok else 'FAIL'}\n")
    result["tests"]["mps_vs_cpu"] = {
        "cpu_sum_logprob": cpu_correct["sum_logprob"],
        "mps_sum_logprob": mps_correct["sum_logprob"],
        "max_token_abs_diff": round(max_diff, 4),
        "ok": mps_cpu_ok,
    }
    del model_cpu

    # ---- Test 3: throughput on MPS --------------------------------------
    log("[test3] throughput on MPS (timing a scoring batch)...")
    tok3, model3, _ = load_model("mps")
    N = 20
    t0 = time.time()
    for _ in range(N):
        score_answer_logprob(model3, tok3, q, correct, "mps")
        score_answer_logprob(model3, tok3, q, wrong, "mps")
    per_scoring = (time.time() - t0) / (N * 2)
    # each trial ~= 2 turns x (score correct + score X) ~= 4 scorings, rough
    per_trial = per_scoring * 4
    total_hours = per_trial * TOTAL_TRIALS_ESTIMATE / 3600
    log(f"        {per_scoring*1000:.0f} ms / answer-scoring")
    log(f"        ~{per_trial:.2f} s / trial (4 scorings) -> "
        f"~{total_hours:.1f} h for {TOTAL_TRIALS_ESTIMATE} trials\n")
    result["tests"]["throughput"] = {
        "ms_per_scoring": round(per_scoring * 1000, 1),
        "sec_per_trial_est": round(per_trial, 2),
        "total_hours_est": round(total_hours, 1),
    }

    # ---- Verdict --------------------------------------------------------
    go = mps_cpu_ok and multitoken_ok and correct_preferred and total_hours < 96
    result["verdict"] = {
        "GO": go,
        "criteria": {
            "mps_matches_cpu": mps_cpu_ok,
            "multitoken_scoring_works": multitoken_ok,
            "correct_answer_preferred (sanity)": correct_preferred,
            "throughput_under_4_days": total_hours < 96,
        },
    }
    log("=" * 60)
    log(f"VERDICT: {'GO ✅  (logprob arm feasible — behaviour-vs-belief headline)' if go else 'NO-GO ⚠️  (see failing criteria)'}")
    for k, v in result["verdict"]["criteria"].items():
        log(f"   {'✓' if v else '✗'} {k}")
    log("=" * 60)

    out = RESULT_DIR / "spike_result.json"
    out.write_text(json.dumps(result, indent=2))
    log(f"\nwrote {out}")


if __name__ == "__main__":
    main()
