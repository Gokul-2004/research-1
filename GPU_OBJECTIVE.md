# OBJECTIVE — Domain-Matched Persona Run (on a rented GPU)

## THE GOAL (one sentence)
Re-run the authority tiers (low/medium/high) with DOMAIN-MATCHED INSTITUTIONAL
personas instead of the generic student→professor ladder, to test whether the null
authority-gradient we found was a persona-design artifact (Joswin 746 claims
domain-matched institutional hierarchy is REQUIRED for the graded effect).

## CONTEXT
Part of "Authority-Graded Sycophancy in Open-Source LLMs" (IEEE Access target). The
main 6-model experiment is DONE. It used a generic persona ladder (high-school student
→ grad student → professor) across all domains and found NO clean authority gradient —
matching Wang et al.'s null. But Joswin 746 argues the effect emerges ONLY with
domain-matched institutional personas. This run tests that directly with:
  Science:  undergraduate science student → PhD researcher → Nobel laureate scientist
  History:  undergraduate history student → history PhD researcher → distinguished professor
  Factual:  research assistant → subject-matter expert → world-leading authority
(Templates in data/authority_templates_domainmatched.json.)

## WHAT THIS RUN IS (and is NOT)
- It re-runs ONLY the low/medium/high tiers, INCORRECT + CORRECT arms.
- It REUSES each model's existing gate decisions + turn-1 responses from the main run
  (so it's directly comparable). anon + control are unchanged from the main run — NOT re-run.
- ~660 trials/model × 6 = ~4,000 trials. On a 24GB GPU: ~2-3h total.
- Writes to SEPARATE results/inference/<model>_domainmatched.jsonl — does NOT touch
  the main experiment files.

## SETUP (on the rented GPU box, e.g. Vast.ai RTX 3090)
1. `git clone https://github.com/Gokul-2004/research-1 && cd research-1`
2. `python -m venv .venv && .venv/bin/pip install torch transformers accelerate`
   (or use the box's preinstalled PyTorch — then just `pip install transformers accelerate`)
3. Create `.env` with the HuggingFace token (needed for gated Llama + Gemma):
   `HF_TOKEN=hf_...`   (get it from the main machine's .env; do NOT commit .env)
4. Confirm GPU is visible: `.venv/bin/python -c "import torch; print(torch.cuda.is_available())"`  → must print True

## RUN
```
DEVICE=cuda bash src/run_domainmatched_all.sh
```
- Resume-safe: if it stops, re-run the same command — it continues.
- Model weights (~40GB total) download on first use; the 9B (Gemma) is the slow load.
- Watch for: gated-model access (Llama-3.2, Gemma-2) — needs a valid HF_TOKEN that has
  accepted those licenses (the main account already did).

## WHAT SUCCESS LOOKS LIKE
- results/inference/<model>_domainmatched.jsonl for all 6 models
- Each file ≈ 660 records (110 gate-pass Qs × 3 tiers × 2 arms, minus any gate-fails)

## HAND BACK
```
git add results/inference/*_domainmatched.jsonl
git commit -m "Domain-matched persona run (6 models)"
git push
```
Then on the main machine we compare the domain-matched gradient to the generic-persona
result — the decisive test of the 746-vs-Wang debate.

## NOTES FOR THE ASSISTANT
- Do NOT modify the main *_2026*.jsonl or *__anonB.jsonl files — they are the source data.
- Do NOT commit .env.
- Keep temperature 0, max_new_tokens 20 (pre-specified; matches the main run).
- The script auto-uses cuda if available; force with DEVICE=cuda.
- If a gated model 401/403s, the HF_TOKEN is missing/invalid — fix .env, don't skip the model.
- results/**/*.json is gitignored but *.jsonl is NOT — the domainmatched files WILL commit. Good.
