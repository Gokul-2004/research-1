# FABLE_WORKLOG — autonomous co-author pass (started 2026-07-14)

> Read this first on any restart. Plan → decisions → findings → open questions, updated as I go.

## Goal
Submission-ready IEEE Access manuscript in `paper/access.tex` from completed experimental work.
Deliverables: PAPER_SELECTION.md, manuscript, figures (audit + 2 new + 1 new from FIGURE_AUDIT),
BH correction (pre-registered, never run), SUBMISSION_CHECKLIST.md, REVIEW_ME_FABLE.md.

## Plan (sequence)
1. ✅ Scope: read fab_inference.md (freshest ground truth, 2026-07-14), KEY_PAPERS_DEEP_DIVE.md,
   SCOPE_DECISION.md, FIGURE_AUDIT.md, SDT_RESULTS.md verdict, ANALYSIS_PLAN E-family, PAPER_DRAFT structure.
2. → PAPER_SELECTION.md (framing decision).
3. → src/paper_numbers.py: recompute EVERY manuscript number from raw JSONL in one committed script
   (incl. McNemar commitment penalty, anon-vs-high McNemar, adopted-X, CA both codings, BH family,
   Wilson CIs, single-turn pooled FE trend, confidence quintiles, ΔH). Output → results/paper_numbers.json + .md.
4. → figures: venv + matplotlib; scripts for (a) design schematic fig9, (b) commitment figure fig10,
   (c) confidence-doesn't-protect fig11; apply FIGURE_AUDIT fixes to captions in-text (not regenerating fig1-8).
5. → paper/: extract IEEE template, write access.tex (structure per PAPER_DRAFT.md headers, numbers ONLY
   from results/paper_numbers.json, framing per PAPER_SELECTION.md + fab_inference reframes).
6. → verification: fresh sub-agent workflow re-verifies every quantitative sentence in access.tex against raw data.
7. → SUBMISSION_CHECKLIST.md + REVIEW_ME_FABLE.md.

## Key decisions (made, logged)
- D1. **Framing**: commitment-structure leads (user prior + fab_inference verdict agree; McNemar 1.9–9.3×,
  all 6 models, p<10⁻¹⁵ — un-scooped as a *per-model factorial on self-committed small open weights*).
  Title from fab_inference: "Presence, Not Prestige: Commitment Structure Dominates Source Authority in
  the Sycophancy of Small Open LLMs." Presence-vs-prestige stated with Finding-2 refinement (prestige adds
  model-dependent, inconsistent-sign ±17–22pp modulation — the sharpest anti-Wang differentiation).
- D2. **Never write**: "flat in single-turn" (pooled FE trend +0.094 p=0.024 exists — report it);
  "anon ≈ professor" as universal (3/6 contradict by McNemar); "bound/refute Mammen via protocol"
  (single-turn also fails to reproduce his gradient per-model → difference NOT explained by protocol).
- D3. **Mistral–Mammen bridge**: report as *unresolved difference* — Mistral grades in Mammen (3/4 datasets,
  Q-then-Hint logit, med/legal/math) but shows no significant single-turn gradient on our items
  → domains/personas/measurement remain confounded; honest limitation, not a claim.
- D4. E-family BH: E1 (CA per model, both codings), E2 (domain term), E4 (McNemar pairs incl. commitment +
  anon-high), E5 (KW) — E3 (hedge words) descriptive-only, E6 not run (disclose in deviations table).
- D5. Figures: per FIGURE_AUDIT net plan + new schematic + commitment + confidence figs. fig4 CUT (circular).
- D6. Belief content retained descriptively per SCOPE_DECISION (anon≈high in belief 4/6; confidence-doesn't-
  protect). No SDT formalization (failed — SDT_RESULTS).
- D7. κ=0.967 scoped to main run explicitly; single-turn = regex-only with the three verified mitigations
  (0.0% extraction failures; 93.6–100% correct-arm accuracy; 99.9% main-run regex-judge agreement).
- D8. Single-turn control tier excluded-with-reason (incoherent referent — Finding 4).

## Findings / gotchas
- No numpy/scipy/matplotlib on this machine → paper_numbers.py is pure Python; figures need a venv
  (matplotlib only) — install as project-local .venv-figs (do NOT touch repo requirements.txt).
- PAPER_DRAFT.md predates single-turn → structure reusable, framing/numbers NOT.
- results/ANALYSIS_4model_summary.md exists but is 4-model era — do not source from it.

## Open questions (proceeding on best answer; user may override)
- Q1. Author list/affiliation/ORCID unknown → placeholders in access.tex, flagged in checklist.
- Q2. Single-turn judge pass (~6.9k trials) requires GEMINI_API_KEY + an evening — recommended in
  checklist as pre-submission add; manuscript written with κ scoped to main run so it ships either way.
- Q3. E6 (SycophancyEval calibration) never run — disclosed as deviation, not silently dropped.

## Status
- [x] Scope
- [x] PAPER_SELECTION.md
- [x] paper_numbers.py → results/paper_numbers.json + results/PAPER_NUMBERS.md (all stats incl. BH)
- [x] figures: fig9 schematic + fig10 commitment + fig11 confidence (committed script, visually checked;
      fig10 legend/n fixed from JSON; fig9 text-overlap fixed)
- [x] paper/access.tex — full manuscript (~4,700 words, 7 figures, 2 tables, 20 refs; structural
      check clean: envs balanced, refs/cites resolve, figure files present). NOT compiled (no local LaTeX).
- [x] SUBMISSION_CHECKLIST.md
- [x] verification pass — wf_01827398-c80 (relaunched after usage reset): 6/6 agents done,
      ~50 claims, ALL MATCH except 3 → fixed in access.tex:
      (V1) "control out-pushes professor 5/6" → 4/6 (Phi, Qwen-7B reversed);
      (V2) Gemma DM Spearman p 2.7e-7 → stated as p<1e-6 (exact-t 4.3e-7; rho −0.254 exact);
      (V3) Table 2 q-column hand-typo → 5.1e-8 / 1.2e-3 / 5.1e-5 (script was already correct).
      Post-fix grep: no stale values. Structural re-check clean.
- [x] REVIEW_ME_FABLE.md — final handback written.

## DONE (2026-07-14). Remaining human-only items: see REVIEW_ME_FABLE.md ranked list
(compile on Overleaf; authors/ORCID/APC; optional single-turn judge evening; Zenodo DOI).
