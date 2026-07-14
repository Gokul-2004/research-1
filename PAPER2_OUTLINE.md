# PAPER 2 — Boundary & Outline (deferred; NOT writable from current data)

> Working title: **"Compliance without conviction? Locating authority sycophancy between behavior and
> belief in open LLMs."** Status: future work. Named in Paper 1's Future Work; do not start until Paper 1
> is submitted and a GPU box is available.

## The question Paper 1 could NOT answer (and why it's a separate paper)
Paper 1 shows authority level barely matters *behaviorally* and that prior confidence doesn't protect. It
CANNOT say whether the model still internally "knows" the answer while complying (compliance vs
internalization, Kelman 1958), because its behavioral channel (single letter) is the arg-max of the same
logits it reads for "belief" — so any behavior-vs-belief claim is tautological (SDT_RESULTS.md). Paper 2 exists
to break that circularity.

## What Paper 2 must add (new data / methods — cannot reuse Paper 1's JSONL as-is)
1. **An independent behavioral channel.** Free-form answers *with reasoning* (not forced single letter), or
   temperature-sampled response distributions, so behavior is not a deterministic function of the A–D logits.
2. **Full belief trajectories.** Per-token / full-vocab distributions across the response, and across >2 turns,
   not just A–D logprobs at turn-1/turn-2.
3. **Mechanistic localization.** Steering vectors / activation patching / logit-lens to test *where* authority
   acts and whether the correct answer is represented-but-overridden vs erased (cf. Joswin workshop). Needs GPU.
4. **Single-turn vs two-turn ablation.** Run Mammen-style Question-then-Hint on the same items to separate the
   commit-then-challenge protocol effect from persona effects (partially pilots the modality×persona factorial).

## Candidate structure
- **Study A** — modality × persona-type factorial (single-turn-logit vs two-turn-behavioral × anon/generic/
  domain-matched) → adjudicates the field's clean-gradient vs general-susceptibility tension.
- **Study B** — mechanistic probe of the saturation ceiling (does authority erase or merely override the
  correct representation? does the ceiling live downstream of graded belief?).
- **Study C (optional)** — multi-turn persistence: does authority grade *resistance duration* (Turn-of-Flip /
  Number-of-Flip) even when it doesn't grade first-flip probability?

## Venue fit (tentative)
The mechanistic version aims **higher** than Paper 1 — a NeurIPS/ICLR MechInterp workshop or a main-track
submission — because white-box results carry more weight than behavioral ones. Decide after Paper 1 lands.

## Do-not
- Do not claim Paper 2 results in Paper 1 (name the direction only).
- Do not attempt Paper 2 on Paper 1's data — it is under-identified for the dissociation claim (that is the
  whole reason it is a separate paper).
