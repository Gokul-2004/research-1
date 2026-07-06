# How to Use POINTS_FOR_PAPER.md

> A short guide to what POINTS_FOR_PAPER.md is, how to read it, and how to maintain it.
> Read this before drafting the paper or adding to the points file.

---

## What POINTS_FOR_PAPER.md IS
It is the **living evidence + argument bank** for the paper "Authority-Graded Sycophancy
in Open-Source LLMs." It is NOT the paper itself — it is the raw material the paper is
written from: every result, comparison, framing option, limitation, citation, and the
honest for/against notes on each claim.

Think of it as the project's memory. When we write the actual paper, we pull from here.

## What it is NOT
- Not the manuscript. Do not copy it verbatim into the paper — it is notes, not prose.
- Not a marketing doc. It records what is TRUE, including failed tests and points that
  oppose our own story. Never delete an inconvenient result from it.

---

## How it is STRUCTURED (sections, roughly)
- **0** — one-paragraph honest summary of the finding
- **1** — the genuine contribution / novelty
- **2** — methods (design, measurement, models, engine)
- **3** — all the numbers (gate survival, flip rates, belief gaps, the FAILED confirmatory
  test, model taxonomy, the anon-ladder falsification)
- **4** — comparison to the literature (per-paper, table + prose)
- **5** — framing options (and what NOT to claim)
- **6** — integrity / pre-registration points; **6b** — judge validation (κ=0.967)
- **7** — limitations (proactive)
- **8** — metrics reported
- **9** — key citations
- **10** — future work
- **11** — still-TODO before submission
- **12** — a ready-to-adapt abstract
- **13** — domain-matched persona experiment + full Mammen comparison
- **14** — mechanistic-depth gap vs Mammen (point + counterpoint)
- (new sections appended as we go — 15, 16, ...)

---

## THE MAINTENANCE RULE (important — this is the discipline)
Every time we discover something, it goes in — **both directions**:

1. **A supporting point** (helps our paper) → note it, with the evidence/numbers.
2. **An opposing point** (undercuts our claim, or a reviewer objection, or a place we
   contradict ourselves) → **note that too, right next to the point it opposes.**

This keeps the file HONEST and balanced. A points file that only records flattering
findings leads to an overclaiming paper that gets rejected. The for/against pairing is
what makes the eventual paper defensible.

Format for a for/against note:
```
### POINT (supports X): <the claim + evidence/numbers>
### COUNTERPOINT (against X / reviewer risk): <the honest objection + why it does/doesn't matter>
```
(See sections 13 and 14 for examples.)

## Other maintenance habits
- **Date new sections** (e.g. "(2026-07-06)") so we know what came when.
- **Correct, don't erase.** If an earlier read was wrong (e.g. we mislabeled a result),
  add a correction note rather than silently editing — the trail matters for integrity.
- **Keep numbers reproducible** — cite which results file / analysis produced a number.
- **Flag preliminary data** ("Mistral not yet complete — confirm") so we don't treat
  partial numbers as final.
- **One commit per meaningful update**, with a message saying what point was added.

---

## HOW TO USE IT WHEN WRITING THE PAPER
1. Read section 0 (the honest summary) and section 5 (framing) first — they set the story.
2. Pull results from section 3; comparisons from 4/13/14; citations from 9.
3. For every claim you write in the paper, check the file for its COUNTERPOINT — address
   or acknowledge it (this is what pre-empts reviewer objections).
4. Lead with what is honestly defensible; report the failed pre-registered test openly
   (section 3e); name limitations proactively (section 7).
5. Do NOT claim more than the file supports. If the file says "model-dependent, not
   universal," the paper must not say "we found a universal gradient."

## THE GOLDEN RULE
If a finding would embarrass us in review if a reviewer found it, it belongs in this file
NOW (with an honest counterpoint), so the paper addresses it before a reviewer can.
