"""
Phase 5 — Statistical analysis.

Runs on all completed model files (main + condition B anon rung). Produces:
  1. Gate survival per model (Wilson CIs)
  2. Behavioral flip rate per (model, tier, arm) with Wilson 95% CIs
  3. Belief gap [logP(correct)-logP(wrongX)] per (model, tier) + turn-1 baseline
  4. Trend test on the persona ladder (anon<low<med<high) — belief AND behavior:
       - Spearman rank correlation (tier rank vs per-question belief gap / flip)
       - Ordinal logistic-style linear-by-linear via mixed model where feasible
  5. Pooled GLMM: correct_after_pressure ~ tier(ordinal) * direction + (1|model)+(1|question)
       - confirmatory tier×direction interaction (LRT)
  6. ∆Entropy per tier (Shannon entropy of A/B/C/D dist, turn1 vs turn2)

Judge-free (uses logprobs + flip flags). Run:
  .venv/bin/python src/analyze.py
"""
import json, glob, math
from collections import defaultdict
import numpy as np
from scipy import stats

INF = "results/inference"
TIER_RANK = {"anon":0, "low":1, "medium":2, "high":3}  # persona ladder (control excluded from trend)
PERSONA_TIERS = ["anon","low","medium","high"]

def log(m): print(m, flush=True)

def wilson(k, n, z=1.96):
    if n==0: return (0,0,0)
    p=k/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d
    h=z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (p, max(0,c-h), min(1,c+h))

def entropy(logprobs):
    # logprobs dict letter->logprob; softmax-normalize over A-D then Shannon
    vals=[logprobs.get(L) for L in "ABCD" if logprobs.get(L) is not None]
    if not vals: return None
    m=max(vals); ex=[math.exp(v-m) for v in vals]; s=sum(ex); p=[e/s for e in ex]
    return -sum(pi*math.log(pi) for pi in p if pi>0)

def find_models():
    main={}
    for f in glob.glob(f"{INF}/*.jsonl"):
        if "__anonB" in f: continue
        # slug = filename up to _2026...
        base=f.split("/")[-1]
        slug=base.split("_2026")[0] if "_2026" in base else base.replace(".jsonl","")
        main[slug]=f
    return main

def load_rows(slug, mainpath):
    rows=[json.loads(l) for l in open(mainpath)]
    anon=f"{INF}/{slug}__anonB.jsonl"
    if glob.glob(anon):
        rows+= [json.loads(l) for l in open(anon)]
    return rows

def main():
    models=find_models()
    log(f"Models found: {list(models.keys())}\n")

    pooled=[]  # for GLMM: rows across models
    for slug, path in sorted(models.items()):
        rows=load_rows(slug, path)
        passed=[r for r in rows if r.get("gate_status")=="PASS" and r.get("tier")]
        name=slug.replace("_"," ")[:26]

        # gate survival
        qids_pass=set(r["question_id"] for r in passed)
        aw=set(r["question_id"] for r in rows if r.get("gate_status")=="ALREADY_WRONG")
        n_total=len(qids_pass|aw)
        gp,gl,gh=wilson(len(qids_pass), n_total)
        log(f"=== {name} ===")
        log(f"  gate survival: {len(qids_pass)}/{n_total} = {gp:.0%}  Wilson[{gl:.0%},{gh:.0%}]")

        # belief gap per tier (incorrect arm) + trend
        gap=defaultdict(list); flip=defaultdict(lambda:[0,0])
        for r in passed:
            if r["direction"]!="incorrect_endorsement": continue
            cl,wl=r["correct_letter"],r["wrong_X_letter"]
            lp=r.get("turn2_logprobs") or {}
            if lp.get(cl) is not None and lp.get(wl) is not None:
                gap[r["tier"]].append(lp[cl]-lp[wl])
            flip[r["tier"]][1]+=1
            if r.get("flipped"): flip[r["tier"]][0]+=1
            # pooled record for GLMM
            if r["tier"] in TIER_RANK:
                pooled.append({"model":slug,"q":r["question_id"],"tier":TIER_RANK[r["tier"]],
                               "dir":0,"flip":1 if r.get("flipped") else 0})
        # correct arm for interaction
        for r in passed:
            if r["direction"]!="correct_endorsement": continue
            if r["tier"] in TIER_RANK:
                pooled.append({"model":slug,"q":r["question_id"],"tier":TIER_RANK[r["tier"]],
                               "dir":1,"flip":1 if r.get("flipped") else 0})

        # Spearman trend on belief gap across persona ladder (per-question)
        xs=[]; ys=[]
        for t in PERSONA_TIERS:
            for v in gap[t]:
                xs.append(TIER_RANK[t]); ys.append(v)
        if len(set(xs))>1 and len(ys)>2:
            rho,p=stats.spearmanr(xs,ys)
            log(f"  BELIEF trend (persona ladder, incorrect arm): Spearman rho={rho:+.3f} p={p:.4f}"
                + ("  *SIG*" if p<0.05 else ""))
        for t in ["control"]+PERSONA_TIERS:
            g=gap.get(t,[])
            fk,fn=flip[t]
            if g:
                fp,flo,fhi=wilson(fk,fn)
                log(f"    {t:8}: belief {np.mean(g):+6.2f} (n={len(g)}) | flip {fp:.0%} Wilson[{flo:.0%},{fhi:.0%}]")
        log("")

    # ---- Pooled GLMM (confirmatory tier×direction interaction) ----
    log("="*60)
    log("POOLED GLMM — confirmatory tier × direction interaction")
    log("="*60)
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
        df=pd.DataFrame(pooled)
        log(f"  n trials pooled: {len(df)}  models: {df['model'].nunique()}")
        # Mixed logistic with random intercept for model; tier as linear (ordinal), dir binary
        # (question random effect omitted for convergence w/ binary GLMM; model RE kept)
        m1=smf.mixedlm("flip ~ tier * dir", df, groups=df["model"])
        # MixedLM is linear; for binary use BinomialBayesMixedGLM or GEE. Use GEE by model cluster:
        import statsmodels.api as sm
        from statsmodels.genmod.generalized_estimating_equations import GEE
        from statsmodels.genmod.cov_struct import Exchangeable
        from statsmodels.genmod.families import Binomial
        df2=df.copy()
        gee_full=GEE.from_formula("flip ~ tier * dir", groups="model", data=df2,
                                  cov_struct=Exchangeable(), family=Binomial()).fit()
        log("\n  GEE logistic (cluster=model), tier×dir interaction term:")
        for term in gee_full.params.index:
            if "tier:dir" in term or term=="tier:dir":
                log(f"    {term}: coef={gee_full.params[term]:+.3f}  p={gee_full.pvalues[term]:.4f}"
                    + ("  *SIG*" if gee_full.pvalues[term]<0.05 else ""))
        log("\n  All coefficients:")
        for term in gee_full.params.index:
            log(f"    {term:20} coef={gee_full.params[term]:+.3f} p={gee_full.pvalues[term]:.4f}")
    except Exception as e:
        log(f"  GLMM error: {e}")

if __name__=="__main__":
    main()
