# REVIEW_ME_FABLE — co-author handback (Fable pass, 2026-07-14)
> Read top-to-bottom; ~2 pages. Everything below is done and in the repo unless marked ⛔/⚠️.

## What exists now
| Deliverable | Where |
|---|---|
| Framing decision (scored vs Wang/Mammen/Kim–Khashabi) | `PAPER_SELECTION.md` |
| Manuscript, submission-structured | `paper/access.tex` (official IEEE Access template; figures in `paper/figures/`) |
| Canonical numbers (one script → every stat, incl. the never-run BH) | `src/paper_numbers.py` → `results/paper_numbers.json` + `results/PAPER_NUMBERS.md` |
| New figures (committed scripts, from JSON, visually checked) | `src/make_figures_paper.py` → fig9 schematic, fig10 commitment, fig11 confidence |
| Submission checklist (admin + mechanics) | `SUBMISSION_CHECKLIST.md` |
| Session log / restart point | `FABLE_WORKLOG.md` |

## The paper (one line)
**"Presence, Not Prestige: Commitment Structure Dominates Source Authority in the Sycophancy of
Small Open LLMs"** — pre-registered gradient FAILS (reported as failure); commitment penalty
1.9–9.3× (McNemar p<10⁻¹⁵ ×6) leads; direction second; presence third; authority = small
sign-inconsistent modulation (±17–22pp, both signs); confidence doesn't protect.

## Verification (your hard constraint): DONE
Six fresh sub-agents recomputed every claim cluster from raw JSONL (~50 claims). Outcome:
- **All commitment-penalty numbers: exact MATCH** (incl. 434:0 discordant pairs, strict adopted-X,
  11.3× strict amplification, n-pairs 384–516, 89.6% single-turn correctness).
- All flip tables, pooled logistic (interaction +0.010 p=0.90; dir +3.53), gate rates, anon-vs-high
  McNemars, CA trends (both codings), single-turn pooled FE trend (+0.094, p=0.024), confidence
  quintiles (82.0/55.6/73.3/69.6/83.5, slope +0.012 p=0.045), ΔH (23/24 cells positive, Llama-high
  −0.011), domain-matched rhos, judge agreement 99.8%: **MATCH**.
- **3 mismatches found and FIXED in access.tex** (worklog D-log):
  1. "control out-pushes professor in 5/6" → **4/6** (Phi 80.2<94.0, Qwen-7B 98.4<99.2). Fixed.
  2. Gemma domain-matched Spearman p 2.7e-7 → verifier's exact-t 4.3e-7; manuscript now says
     **p<10⁻⁶** (rho −0.254 exact). My script used a normal approx for the t — cosmetic, but
     the manuscript no longer quotes the sloppy digit.
  3. Table 2 (anon-vs-high) q-column: I hand-typed 3 q's ~2× too large; script was right all
     along. Fixed to 5.1e-8 / 1.2e-3 / 5.1e-5.
- Post-fix grep confirms no stale values remain. **No CANNOT-VERIFY items.**

## Judgment calls I made (chronological; challenge any)
1. **Commitment leads** (your prior + fab_inference verdict + it's the largest, unanimous effect).
2. Kept fab_inference's title verbatim; abstract leads with the failed pre-registration.
3. **Mammen = unresolved difference**, not "bounded": our single-turn arm shows no per-model
   gradient on our items, so protocol alone doesn't explain his clean gradient; stated as a
   4-axis confound in Discussion + Limitations (your hard constraint, honored).
4. **anon≈professor never stated universally**: Table 2 shows both signs with paired tests; the
   ±17–22pp inconsistent-sign modulation is framed as the sharpest refinement over Wang's ≤4.4%.
5. E1 BH family = persona-only coding (pre-reg ladder minus control; anon post-hoc → sensitivity
   family). Commitment + anon-high McNemars = separate post-hoc BH family. Defensible; a reviewer
   could quibble family membership — the deviations table says exactly what was done.
6. fab_inference Finding 6's own gloss ("1T caving largely generic error in resisters") is
   **wrong on its own numbers** (59–93% of 1T errors adopt X); manuscript reports both metrics
   and never uses that gloss.
7. Cut fig4/fig5/fig6/fig7 from the manuscript (fig4 circular per SDT_RESULTS; fig6 ΔH numbers
   in text; fig5/7 redundant with Table 1 + fig2).
8. SDT/behavior-vs-belief thesis stays OUT (failed; SCOPE_DECISION honored) — belief used
   descriptively only (confidence quintiles, ΔH).
9. E6 not run, E3 descriptive-only → disclosed in Limitations rather than silently dropped.
10. Wrote fresh prose throughout (plagiarism-safe vs internal notes; no text reused from them).

## Numbers I could NOT verify to source (none in the manuscript)
- κ=0.967 rests on n=60 human labels in `judge_bundle/results/human_validation/` — I reproduced
  59/60 + the API-error row earlier (VERIFICATION.md), but the human labels themselves are your
  hand-work; nobody can re-derive those.
- Wang/Mammen/Kim–Khashabi paper numbers (≤4.4%, 46.6–95.1%, their setups) are transcribed from
  KEY_PAPERS_DEEP_DIVE.md, which was read from the sources — spot-check before camera-ready
  (flagged [VERIFY] items there: Wang venue/affiliations).

## RANKED: what you must do before submission
1. ⛔ **Compile** (no LaTeX on this machine): upload `paper/` to Overleaf; fix cosmetic float/hbox
   issues only. Structural checks (envs/refs/cites/figures) already pass.
2. ⛔ **Authors/ORCID/bios/photos/funding** — `TODO-AUTHORS` markers in access.tex; APC (~$2k) plan.
3. ⚠️ **Single-turn judge evening** (~6,880 trials; adapt `judge_bundle/src/run_judge.py`): not a
   blocker (κ correctly scoped in-text) but kills the likeliest reviewer ask. Then re-run
   `src/paper_numbers.py`, add one sentence to §Method-C.
4. ⚠️ **Zenodo DOI** for a frozen snapshot + (optional) clean `paper-repo` so reviewers see a
   curated package; cite DOI in Data Availability.
5. ⚠️ Read the manuscript once as yourself — especially Abstract, §Presence (the sign-inconsistent
   modulation is the most attackable framing), and Limitations (bundling of commitment/contradiction).
6. ⚠️ Optional polish: regenerate fig1/2/3/8 without embedded titles (IEEE prefers caption-only);
   vector export.

## Honest residual risks (in review)
- The headline finding is post-hoc (disclosed, timestamped, BH'd) — a strict reviewer may still
  ask for a confirmatory replication; the per-model unanimity at p<10⁻¹⁵ is the counterweight.
- Family-membership choices for BH (see call #5).
- Six-model pooled inference (mixed model unstable) — we lean on paired per-model tests; stated.
- Acceptance estimate: **~70–75%** as it stands; +judge pass ≈ small bump; the framing no longer
  contains the two overclaim traps fab_inference flagged ("flat in single-turn", "anon≈professor").
