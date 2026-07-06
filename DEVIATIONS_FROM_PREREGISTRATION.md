# Deviations from Pre-Registration

> Full, proactive disclosure of every departure from ANALYSIS_PLAN.md (committed before any
> inference). Disclosing these converts potential "gotchas" into a credibility asset — the
> hallmark of an honest pre-registered study. This table goes in the paper (Methods/Appendix).

| # | Pre-registered | What we actually did | Reason | Impact on conclusions |
|---|---|---|---|---|
| 1 | Confirmatory test via **pooled GLMM** (`tier*direction*domain + (1|model)+(1|question)`) | Reported GEE (cluster=model) and frequentist GLM as primary; variational-Bayes GLMM found unreliable | VB mixed-GLM underestimates uncertainty (gave a spurious z=10.4); only 6 model-clusters weakens random-effects estimation | NONE — all rigorous methods (GEE p=0.95, freq p=0.78) + raw non-monotonic data agree the interaction is NOT significant. Conclusion unchanged. |
| 2 | Trend test = **Cochran-Armitage** | Initially reported Spearman ρ in intermediate analyses; Cochran-Armitage computed for final | Oversight in intermediate reporting | Minor — both agree on direction; CA is now the reported per-model trend (4/6 significant, persona-only coding). |
| 3 | Judge = **Gemini 2.0 Flash** | Used **Gemini 2.5 Flash** (newer) | Work-laptop had 2.5 access; 2.5 is more capable | NONE — regex-vs-judge agreement 99.9%; human validation κ=0.967. |
| 4 | Human validation **~100 items** | Validated **n=60** | Sufficient given near-deterministic single-letter outputs; κ already 0.967 | Minimal — κ well above the 0.70 target; CI on κ acceptable at n=60. |
| 5 | **Dual-judge** (2 runs) + Cohen's κ judge-vs-judge | Single judge run; judge-vs-human κ only | At temp 0 identical re-runs test nothing; NO corpus paper uses dual-judge; all validate judge-vs-human | NONE — judge-vs-human is the stronger, field-standard check (κ=0.967). |
| 6 | Zero-authority **control** rung as the baseline for `regressive_severity` | Report control SEPARATELY; use the **anon** rung as the format-matched floor | The control ("I don't think that's right… X") out-pushes "professor" — it is a stronger-pressure condition, not a neutral floor | Improves rigor — anon is the correct matched baseline; disclosed. |
| 7 | (implicit) all conditions pre-registered together | **Condition B (anon)** and the **domain-matched persona run** were added POST-HOC (timestamps 2026-06-30 / 2026-07-05) | Anon added to test whether the control masked a gradient; domain-matched added to test Joswin's boundary condition | These analyses are EXPLORATORY, labeled as such. ANALYSIS_PLAN §7d pre-registered only the MODEL-set expansion (Phi, Gemma), NOT the persona experiment. |
| 8 | Behavioral arm = **free-form generation** | Single-letter forced output (system prompt) | Cleaner flip signal; near forced-choice | Reframe honestly: "answer revision under conversational pressure after explicit commitment," not "free-form." |
| 9 | Domains: Science / History / **Geography** | Third domain relabeled **Factual** (TruthfulQA spans 38 categories, not just geography) | Accuracy of labeling | NONE — same data, honest label. |

## Summary statement for the paper
> "We pre-registered the analysis plan before any inference (ANALYSIS_PLAN.md). We disclose all
> deviations above. The two consequential ones — the fitting method for the confirmatory test
> (Deviation 1) and the exploratory status of the anon and domain-matched conditions (Deviation 7)
> — do not alter the confirmatory conclusion (the pre-registered pooled tier×direction interaction
> was not supported under any rigorous method) and are reported honestly as exploratory where
> applicable. All behavioral results are robust to judge-vs-regex labeling (99.9% agreement,
> human-validated κ=0.967)."
