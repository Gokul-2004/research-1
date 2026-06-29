"""
Timing spike — CPU fp16, 3B-class model (Linux, 64 GB RAM).

Measures per-scoring and per-trial wall-clock for the 3B arm so we can
compute real total hours for the 2×3B + 2×7B lineup before committing
to any full run. Identical scoring logic to spike_cpu_7b.py.

Run:
  HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/spike_cpu_3b.py
"""

import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"   # ungated, proven in original Mac spike
DEVICE = "cpu"
DTYPE = torch.float16

RESULT_DIR = Path(__file__).resolve().parent.parent / "results" / "spike"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

TOTAL_TRIALS_ESTIMATE = 12600


def log(msg):
    print(msg, flush=True)


def score_answer_logprob(model, tok, prompt: str, answer: str) -> dict:
    prompt_ids = tok(prompt, return_tensors="pt").input_ids
    answer_ids = tok(answer, return_tensors="pt", add_special_tokens=False).input_ids
    full_ids = torch.cat([prompt_ids, answer_ids], dim=1)
    with torch.no_grad():
        logits = model(full_ids).logits
    logprobs = torch.log_softmax(logits.float(), dim=-1)
    n_answer = answer_ids.shape[1]
    pred_slice = logprobs[0, -(n_answer + 1):-1, :]
    tgt = full_ids[0, -n_answer:]
    tok_lp = pred_slice[torch.arange(n_answer), tgt]
    return {
        "answer": answer,
        "n_tokens": int(n_answer),
        "sum_logprob": round(float(tok_lp.sum()), 4),
    }


def main():
    result = {"model": MODEL_ID, "device": DEVICE, "dtype": "fp16", "tests": {}}
    log(f"=== CPU 3B timing spike — {MODEL_ID} ===\n")

    log("[load] loading model on CPU (fp16)...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=DTYPE, low_cpu_mem_usage=True,
    )
    model.eval()
    load_s = time.time() - t0
    log(f"[load] done in {load_s:.1f}s\n")
    result["tests"]["load_seconds_cpu"] = round(load_s, 1)

    msgs = [{"role": "user", "content": "What is the longest river in the world? Answer in one short phrase."}]
    q = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    correct, wrong = "the Nile", "the Amazon"

    log("[throughput] timing 20 scoring calls on CPU...")
    N = 20
    t0 = time.time()
    for _ in range(N):
        score_answer_logprob(model, tok, q, correct)
        score_answer_logprob(model, tok, q, wrong)
    per_scoring = (time.time() - t0) / (N * 2)
    per_trial = per_scoring * 4
    total_hours = per_trial * TOTAL_TRIALS_ESTIMATE / 3600

    log(f"        {per_scoring*1000:.0f} ms / answer-scoring")
    log(f"        ~{per_trial:.2f} s / trial (4 scorings) -> ~{total_hours:.1f} h for {TOTAL_TRIALS_ESTIMATE} trials")

    result["tests"]["throughput"] = {
        "ms_per_scoring": round(per_scoring * 1000, 1),
        "sec_per_trial_est": round(per_trial, 2),
        "total_hours_est": round(total_hours, 1),
        "total_days_est": round(total_hours / 24, 1),
    }

    out = RESULT_DIR / "spike_cpu_3b.json"
    out.write_text(json.dumps(result, indent=2))
    log(f"\nwrote {out}")


if __name__ == "__main__":
    main()
