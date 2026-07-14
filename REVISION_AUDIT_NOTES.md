# REVISION_AUDIT_NOTES — IEEE Access strengthening pass (2026-07-14)

> One lesson per note. Status of each acceptance-risk target; what survived verification,
> what's open. Companion to the proposed-diff report (audit-only; no manuscript edits
> without approval).

## Verified infrastructure
- **N1. Frozen data verified.** All 24 files in `RESULTS_MANIFEST.sha256` pass shasum -c
  (2026-07-14). The one warning is a malformed manifest line, not a hash failure.
- **N2. paper_numbers.py regenerates byte-identically.** Fresh run of `src/paper_numbers.py`
  produced `results/paper_numbers.json` identical to the committed copy. `results/PAPER_NUMBERS.md`
  is therefore valid ground truth for the numeric audit.
- **N3. Raw responses are bare single letters.** Inspected records in both
  `results/inference/*_20260630*.jsonl` (two-turn: `turn1_response: "A"`) and
  `*_singleturn.jsonl` (`answer_response: "A"`). This fact drives targets 5 and (partly) 6.

## Target 5 — incomplete pre-registered analyses (classification)
- **N4. E3 (hedging) is NOT completable from existing data.** There is no free text to count
  hedge/apology words in — outputs are single letters (N3). Only honest move: scope out
  plainly. Deviations table rows 10–11 (added 2026-07-14) already record E3/E6 as NOT RUN.
- **N5. E6 (external calibration) is scope-out, per submission owner's instruction.** A
  descriptive cross-paper comparison would be computable (control-rung rates exist in
  PAPER_NUMBERS.md) but items/models differ from Sharma's — weak calibration that invites
  objections. State "out of scope for this submission" rather than "open item".
- **N6. Single-turn judge pass = NEEDS NEW RUNS (Gemini API, ~6,880 calls) but is
  near-vacuous.** Judge substance-matching over bare-letter outputs reduces to the letter
  comparison already used (two-turn judge agreed with letters on 99.8%). Recommendation:
  reframe the Limitations sentence ("cheapest outstanding robustness addition" reads as an
  unmet promise) to state why deterministic labels suffice for single-turn; offer judge pass
  as optional hardening only.

## Target 7 — SDT hand-wave
- **N7. SDT_RESULTS.md contains a REPORTABLE robustness result, not just a failure.** Test 2:
  the pre-registered tier×direction null is robust to adding the turn-1 belief covariate and
  model fixed effects (interaction coef +0.022, p=0.78, n=5,510; belief covariate itself
  p=0.40). Replacing the dangling "signal-detection analysis failed and is deferred" clause
  with this robustness sentence strengthens the null against "your test was broken" attacks.
  Caveat: these numbers come from `src/sdt_analysis.py`, NOT `paper_numbers.py` — if cited
  with numbers, Data Availability must name sdt_analysis.py too, or keep the sentence
  number-free. SDT quintiles (85.4/62.4/...) use a different subset (incl. control tier)
  than the paper's fig11 quintiles (n=2,752, anon–high) — do NOT mix them.

## Session lessons
- **N8. E3/E6 disclosure gap already closed this session.** access.tex Limitations now says
  both were "not run"; DEVIATIONS_FROM_PREREGISTRATION.md has rows 10–11. Remaining polish:
  phrase as "out of scope for this submission". E6 row's "Scope/time" reason is a placeholder —
  owner should replace with the real reason if different.
- **N9. Overfull-box fixes (earlier session).** \code/\sq/\bk macros added for breakable
  paths; Table 1 tightened (tabcolsep 3.5pt, @{} gutters, p-values as <1e-15 text). Not yet
  compiled — verify in Overleaf.

## Numeric audit — own findings (2026-07-14, direct recomputation from frozen JSONL)
- **N10. "0.0% extraction failures in both structures" is FALSE as written.** 14/5,513 gated
  two-turn records have turn2_letter=None — ALL Phi-3.5-mini, ALL control rung, free-text
  "I apologize…" responses (flipped=None → counted as non-flips, consistent with Phi
  control=80.2% in PAPER_NUMBERS.md). Anon–high rungs: 0 failures. Single-turn: 0/6,880.
  Fix = re-scope the sentence to the analyzed rungs + one-line disclosure of the 14.
  (Also explains judge n=5,497 vs 5,513 gated — verifier to confirm the 16-record delta.)
- **N11. "93.6–100% correct-arm accuracy retained" is TRUE but ORPHANED.** Verified by direct
  recomputation with control excluded (Mistral 93.6, Llama 95.1, Qwen7B 98.6, Qwen3B 98.7,
  Gemma 98.8, Phi 100.0). paper_numbers.py does NOT emit it → either extend the script
  (small pure-python add) or soften prose. Including control gives 94.7–100 — coding matters.
- **N12. n=6,880 single-turn REGENERATES** (`_meta/records/singleturn` in paper_numbers.json).
- **N13. Spot-checked ~30 load-bearing prose/table stats vs PAPER_NUMBERS.md — all match**
  (Tables 1–2 every cell; abstract 1.9–9.3×/median 2.6×/89.6/97.2; direction β=3.53 SE 0.146;
  interaction β=0.0098 SE 0.0765 p=0.898; tier β=0.083 p=0.21; CA persona-only 4/6 with
  quoted z/q; Mistral anon-incl z=−2.1 p=0.036; single-turn pooled +0.0937 p=0.024 and raw
  24.0/20.8/26.6/27.3; quintiles 82.0/55.6/73.3/69.6/83.5 slope +0.01165 p=0.045; ΔH 23/24
  cells, −0.011 exception, +0.062..+0.463 range; judge 99.82%/5,497, κ=0.967; E2 q=0.0394
  (χ²₂=6.96 ⇔ p=0.0308); 13/15 pairwise with the two named exceptions; K–W q<1e-15; gate
  96–129 = 64.0–86.0%; correct-arm 0.0–20.0 per model; control>high in exactly 4/6;
  1T-errors-adopting-X 59.1–93.3%).
- **N14. PN line 32 itself documents "naive SE; cluster-robust widens; interaction ns under
  all"** — citable support for demoting pooled p-values without new fits. GEE p=0.95 / freq
  p=0.78 exist only in DEVIATIONS row 1 provenance (analyze_final.py), NOT regenerated by
  paper_numbers.py — do not put those numbers in the manuscript unless the script is extended.

## Numeric audit — subagent findings (fresh-context, exhaustive ledger)
- **N15. ~120 claims audited: all Table 1 (36 cells) and Table 2 (30 cells) EXACT; all headline
  coefficients/ranges EXACT or ROUNDED-OK.** Only 1 mismatch + 3 orphans (below).
- **N16. MISMATCH (minor, real): access.tex line ~382** "the three ceiling-saturated models …
  nothing can differ at 96–98%" — actual anon/high: Llama 96.9/97.9, Qwen7B 96.0/99.2,
  Qwen3B 85.3/80.2. Fix: "96–99%" and stop calling Qwen3B ceiling-saturated (it's a
  no-difference model at 80–85%, not a ceiling case).
- **N17. ORPHAN + internal inconsistency: "3/6 models" persona-grading-recovery count**
  (Related Work ~line 164; Discussion ~line 481). Not regenerable; §Exploratory's own text
  lists FOUR strengthened belief trends (Gemma, Llama, Phi, Qwen3B) + Qwen7B marginal. Fix:
  state the count consistently (e.g. "4/6 by belief-trend, with Qwen7B marginal") or define
  the criterion; make paper_numbers.py emit it if kept.
- **N18. Confirmed orphans (agent + my recomputation agree): 0.0%-extraction-failures and
  93.6–100% single-turn correct-arm retention.** Also listed benign derived composites
  (median 2.6×, 89.6%, 11.3×, 59–93%, 13/15, 23/24, ±17–22pp) — arithmetic on script
  outputs; fine, but "regenerates every statistic" wording should say "or is arithmetic
  derivable from" — or the script should print them.

## Open (filled as subagent reports land)
- Numeric audit of every stat in access.tex vs PAPER_NUMBERS.md — pending.
- Orphan statistics (in prose but not regenerated by paper_numbers.py) — pending; known
  suspects: kappa=0.967, judge 99.8%/5,497, GLMM betas, single-turn pooled trend, confidence
  slope, entropy cells, domain-matched Spearman rhos, three-way chi2.
- Title/abstract reframe options — pending framing subagent.
- Pooled-p demotion diff list — pending stats subagent.
- Reference classification + archival upgrades — pending reference subagent.
