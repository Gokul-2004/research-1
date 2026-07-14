# REVIEW_ME — co-author handback (read this first)
> One autonomous pass, skeptical-reviewer hat. All deliverables are files in the repo root + src/.
> Nothing here rescues the failed pre-registered hypothesis; every number is tagged to its source.

## The one decision that shapes everything: the spine
The SDT / behavior-vs-belief reframe **failed my own robustness test** (SDT_RESULTS.md): pre-pressure belief
does NOT predict flipping (pooled slope ≈ 0), and authority does not cleanly load on the decision criterion
(2/6). So I did **not** build the paper on "measurement modality is decisive." Per your Stage-2.5 rule this
triggered **option (B)**: Paper 1 = the robust empirical findings; the method → Paper 2 (SCOPE_DECISION.md,
PAPER2_OUTLINE.md). **If you disagree with anything, disagree with this** — it drove the draft, the figure
cuts, and the venue call.

## Deliverables written
VERIFICATION.md · SPINE_DECISION.md · SDT_RESULTS.md (+ src/sdt_analysis.py) · SCOPE_DECISION.md ·
PAPER2_OUTLINE.md · PAPER_DRAFT.md · FIGURE_AUDIT.md · RED_TEAM.md · src/verify_stage0.py · this file.

## Judgment calls I made (so you can overrule)
1. **Spine = presence-beats-prestige + "confidence doesn't protect"**, not behavior-vs-belief. (SDT failed.)
2. **Reframed the whole paper's title/thesis** around "presence, not prestige." Big call — swap the spine in
   PAPER_DRAFT.md §1 if you prefer direction-dominance as the lead (weaker: it's a replication).
3. **Promoted "prior confidence doesn't protect" to co-headline** — it's the only finding not scooped by Wang.
4. **Cut Figure 4** (behavior-vs-belief scatter): it uses post-pressure belief, so it's circular; moved to Paper 2.
5. **Called presence "4/6, not 5/6"** — the belief metric gives 4/6; the "5/6" in prior notes is overstated
   (VERIFICATION.md #1). Corrected everywhere.
6. **Venue: recommended TMLR primary over your locked IEEE Access** (see below). This overrides a "locked"
   decision — flagged so you can veto.
7. **Framed the null as "does not translate to two-turn behavioral," never "fails to replicate Mammen"**
   (VERIFY_MAMMEN.md: you never ran their protocol).

## Open questions I'd have asked you (answered with my best call, logged)
- Is IEEE Access locked for a hard reason (institutional/APC funding)? I assumed not and recommended TMLR;
  reverse if the APC or an IEEE requirement is fixed.
- Do you have GPU access for Paper 2 / the single-turn ablation? PAPER2_OUTLINE assumes eventually yes.
- Is a ~5–10h overnight CPU run acceptable now for the single-turn ablation? RED_TEAM says it's the single
  highest-leverage addition; I scoped but did not run it (no inference without your go-ahead).

## Numbers I could NOT reproduce / flagged
- **Human κ:** 0.967 reproduces ONLY if the 1 judge API ERROR counts as a disagreement (conservative). Excluding
  it: κ=1.0 on n=59. Both correct; state the handling. (VERIFICATION.md #3)
- **"presence ≈ prestige for 5/6"** → actually **4/6** on belief; Phi & Gemma show authority adding. (Overstated.)
- **"institutional personas help 3/6" vs "gradient exists 5/6"** → two different metrics; don't conflate.
- **GEE cluster-robust p=0.95 exact:** I reproduced the coefficient ≈0 and naive p=0.89 (no statsmodels in the
  clone); cluster-robust only widens → conclusion invariant. Recompute with statsmodels for the paper.
- **Generic-ladder per-model Spearman ρ table** (POINTS §3d) not re-run here — recompute before it enters text.
- Gemma overall flip 54.9% (mine) vs 59% (POINTS): tier-averaging convention differs; pick one, state it.

## Venue (Stage 6)
**TMLR primary** — claims-audited review is the ideal home for a pre-registered null + full deviation table +
κ validation; free; open-access satisfied. **IEEE Access fallback** — sound+open but ~$2,160 APC and
out-of-field reviewers who may miss the subtlety. **Alignment Forum** at preprint time, lead with the safety
upshot ("credentials don't gate capitulation; prior confidence doesn't protect — any pushback flips 49–98%").
Limitations paragraph is drafted in PAPER_DRAFT.md §6 to pre-empt weaponization (post-hoc disclosure,
fixed-effects justification, no free-form/dissociation claims, scope stated).

## What to check first (ranked)
1. **Do you accept the spine pivot (SDT out, presence+confidence in)?** Everything hangs on this.
2. **RED_TEAM.md "must do" list** — esp. the single-turn ablation and the Wang-convergence reframe; these move
   it from borderline-reject to accept. Say go/no-go on the overnight ablation.
3. **VERIFICATION.md discrepancies** — the 4/6-not-5/6 and κ-handling corrections must propagate to POINTS_FOR_PAPER.md.
4. **Venue** — confirm TMLR vs IEEE Access (affects formatting + APC).
5. **FIGURE_AUDIT.md** — approve cutting fig4, building the confidence-doesn't-protect figure, reframing fig6.
6. **PAPER_DRAFT.md §2** — the positioning against Wang/Mammen/Joswin is the make-or-break section; sanity-check it.

## Not done (needs you / compute)
- No new inference run (single-turn ablation) — awaiting your go-ahead.
- statsmodels GLMM recompute (not installed in clone).
- The new "confidence-doesn't-protect" figure (spec in FIGURE_AUDIT.md) — can build on request.
- Propagating VERIFICATION corrections into POINTS_FOR_PAPER.md — held pending your review (didn't want to
  edit the evidence bank without sign-off).
