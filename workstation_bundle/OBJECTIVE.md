# OBJECTIVE — Domain-Matched Persona Run, MODELS 4-6 (other workstation)

## THE GOAL (one sentence)
Run the domain-matched institutional-persona experiment for 3 models (Mistral-7B,
Phi-3.5, Gemma-2-9B) on this workstation, IN PARALLEL with the main laptop which is
doing models 1-3 — to halve the total wall-clock time.

## CONTEXT
Part of "Authority-Graded Sycophancy in Open-Source LLMs" (IEEE Access target). The
main 6-model experiment used a GENERIC persona ladder (high-schooler → grad → professor)
and found NO clean authority gradient. Joswin 746 claims the graded effect emerges ONLY
with DOMAIN-MATCHED INSTITUTIONAL personas. This run tests that with:
  Science:  undergraduate science student → PhD researcher → Nobel laureate scientist
  History:  undergraduate history student → history PhD researcher → distinguished professor
  Factual:  research assistant → subject-matter expert → world-leading authority
It re-runs ONLY the low/medium/high tiers (2 arms), REUSING each model's existing gate
decisions + turn-1 responses from the main run (already in results/inference/). Writes to
SEPARATE *_domainmatched.jsonl files.

## THIS WORKSTATION DOES MODELS 4-6 (group B):
  4. mistralai/Mistral-7B-Instruct-v0.3   (UNGATED)
  5. microsoft/Phi-3.5-mini-instruct       (UNGATED)
  6. google/gemma-2-9b-it                   (GATED — needs HF token, see below)

Machine specs assumed: CPU-only (P2000 too small — ignore GPU), 64GB RAM. Same as the
main laptop. Each 7B/9B model takes ~10-13h on CPU; ~1.5 days total for the 3.

## SETUP
1. `git clone https://github.com/Gokul-2004/research-1 && cd research-1`
   (Or use this workstation_bundle folder directly — it is self-contained.)
2. `python3 -m venv .venv && .venv/bin/pip install torch transformers accelerate`
3. Create `.env` with the HuggingFace token (REQUIRED for Gemma, which is gated):
   `HF_TOKEN=hf_...`
   The token must belong to an account that has accepted the Gemma-2 license at
   https://huggingface.co/google/gemma-2-9b-it (the main account already did).
   Mistral + Phi are ungated and need no token, but include it anyway for Gemma.
4. DO NOT commit .env.

## RUN
```
DEVICE=cpu bash src/run_domainmatched_split.sh B
```
- Group B = Mistral, Phi, Gemma (models 4-6).
- Resume-safe: if it stops (power/thermal), re-run the same command — it continues.
- Model weights download on first use (~35GB for these 3). Ensure ~60GB free disk.
- Keep it plugged into AC power; keep it cool (fan on intake vents).

## WHAT SUCCESS LOOKS LIKE
- results/inference/mistralai_..._domainmatched.jsonl
- results/inference/microsoft_..._domainmatched.jsonl
- results/inference/google_gemma-2-9b-it_domainmatched.jsonl
- Each ≈ 600-660 records (gate-pass Qs × 3 tiers × 2 arms).

## HAND BACK
```
git add results/inference/*_domainmatched.jsonl
git commit -m "Domain-matched persona run models 4-6 (group B)"
git push
```
The main laptop is pushing models 1-3. Once both are in, we compare the domain-matched
gradient to the generic-persona result — the decisive 746-vs-Wang test.

## IMPORTANT NOTES FOR THE ASSISTANT
- ONLY run group B (models 4-6). The laptop is doing group A (1-3). Do NOT run group A
  here or you'll duplicate work.
- Do NOT modify the main *_2026*.jsonl or *__anonB.jsonl files — they are source data
  (needed for gate + turn-1 reuse).
- Do NOT commit .env.
- If Gemma 401/403s: the HF_TOKEN is missing/invalid or hasn't accepted the license.
- Keep temperature 0, max_new_tokens 20 (pre-specified; matches the main run).
- CPU-only: the script auto-detects (DEVICE=cpu). P2000 GPU is too small — do not use it.
