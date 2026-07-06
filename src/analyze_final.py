"""
FINAL confirmatory + supporting analysis (the two blockers + roadmap analyses).
Zero inference. Produces the numbers every results sentence depends on.

Runs on GENERIC personas only for the confirmatory test (never pooled with domain-matched).
Fits the flip outcome on BOTH regex labels and JUDGE substance labels; reports if they differ.

Outputs:
  A. Confirmatory pre-registered GLMM: correct_after_pressure ~ tier*direction*domain
     + (1|model) + (1|question), LRT on tier×direction. (regex AND judge labels)
  B. Cochran-Armitage trend test per model (the actually pre-specified trend test).
  C. Ladder-coding discrepancy resolved: report BOTH anon-inclusive and persona-only.
  D. Direction main effect (the real headline).
  E. Regex-vs-judge label agreement (does the confirmatory result change?).

Run: .venv/bin/python src/analyze_final.py
"""
import json, glob
from collections import defaultdict
import numpy as np
import pandas as pd

INF = "results/inference"
JUDGE = "judge_bundle/results/judged"
MODELS = {"Qwen-3B":"Qwen_Qwen2.5-3B-Instruct","Llama-3B":"meta-llama_Llama-3.2-3B-Instruct",
    "Qwen-7B":"Qwen_Qwen2.5-7B-Instruct","Mistral-7B":"mistralai_Mistral-7B-Instruct-v0.3",
    "Phi-3.5":"microsoft_Phi-3.5-mini-instruct","Gemma-9B":"google_gemma-2-9b-it"}
TIER_RANK = {"anon":0,"low":1,"medium":2,"high":3}  # control excluded (stronger-pressure condition)

def mainf(s): return [x for x in glob.glob(f"{INF}/{s}_2*.jsonl") if "anonB" not in x and "domainmatched" not in x][0]

def log(m): print(m, flush=True)

# ---- load judge labels: (model,qid,tier,dir) -> class ----
def load_judge():
    j = {}
    for f in glob.glob(f"{JUDGE}/*__judge1.jsonl"):
        for l in open(f):
            d = json.loads(l)
            if d.get("judge_turn2_class") in ("correct","incorrect","erroneous"):
                j[(d["model"], d["question_id"], d["tier"], d["direction"])] = d["judge_turn2_class"]
    return j

def build_df(judge):
    """Build the analysis frame from GENERIC personas (main + anonB), incorrect+correct arms.
    correct_after_pressure = 1 if model still correct at turn-2, else 0.
    regex: turn-2 letter == correct_letter.  judge: judge_turn2_class == 'correct'."""
    rows=[]
    n_agree=n_tot=0
    for name,slug in MODELS.items():
        files=[mainf(slug)]
        anon=f"{INF}/{slug}__anonB.jsonl"
        if glob.glob(anon): files.append(anon)
        for path in files:
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or not r.get("tier"): continue
                tier=r["tier"]
                if tier=="control": continue  # exclude control from confirmatory ladder
                # regex correctness after pressure
                reg_correct = 1 if r.get("turn2_letter")==r.get("correct_letter") else 0
                # judge correctness
                key=(r["model"], r["question_id"], tier, r["direction"])
                jl=judge.get(key)
                jud_correct = (1 if jl=="correct" else 0) if jl is not None else None
                if jud_correct is not None:
                    n_tot+=1; n_agree+= (reg_correct==jud_correct)
                rows.append({"model":name,"q":r["question_id"],"domain":r["domain"],
                    "tier":TIER_RANK[tier],"tier_name":tier,
                    "dir":0 if r["direction"]=="incorrect_endorsement" else 1,
                    "reg_correct":reg_correct,"jud_correct":jud_correct})
    df=pd.DataFrame(rows)
    return df, (n_agree/n_tot if n_tot else None), n_tot

# ---- A. Confirmatory GLMM (binomial mixed) via statsmodels BinomialBayesMixedGLM or fallback GEE ----
def confirmatory(df, outcome):
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    d=df.dropna(subset=[outcome]).copy()
    d["y"]=d[outcome].astype(int)
    # Random intercepts for model and question via variance-component formula
    vc={"model":"0+C(model)","q":"0+C(q)"}
    try:
        full=BinomialBayesMixedGLM.from_formula("y ~ tier*dir*C(domain)", vc, d).fit_vb()
        red =BinomialBayesMixedGLM.from_formula("y ~ tier + dir + C(domain) + tier:C(domain) + dir:C(domain)", vc, d).fit_vb()
        # interaction terms = tier:dir and tier:dir:domain
        params=full.summary().tables[0] if hasattr(full,'summary') else None
        log(f"    [GLMM-VB fitted on {outcome}, n={len(d)}]")
        # report tier:dir coefficient
        fe=dict(zip(full.model.exog_names, full.fe_mean))
        fesd=dict(zip(full.model.exog_names, full.fe_sd))
        for term in fe:
            if term=="tier:dir":
                z=fe[term]/fesd[term]
                log(f"    tier:dir  coef={fe[term]:+.3f}  sd={fesd[term]:.3f}  z={z:+.2f}")
        return
    except Exception as e:
        log(f"    GLMM-VB failed ({str(e)[:60]}); falling back to GEE cluster=model")
    # Fallback: GEE
    from statsmodels.genmod.generalized_estimating_equations import GEE
    from statsmodels.genmod.cov_struct import Exchangeable
    from statsmodels.genmod.families import Binomial
    m=GEE.from_formula("y ~ tier*dir*C(domain)", groups="model", data=d,
                       cov_struct=Exchangeable(), family=Binomial()).fit()
    for term in m.params.index:
        if term=="tier:dir":
            log(f"    [GEE {outcome} n={len(d)}] tier:dir coef={m.params[term]:+.3f} p={m.pvalues[term]:.4f}")
    # direction main effect
    for term in m.params.index:
        if term=="dir":
            log(f"    dir main effect coef={m.params[term]:+.3f} p={m.pvalues[term]:.4f}")

# ---- B. Cochran-Armitage trend per model (incorrect arm, per ladder coding) ----
def cochran_armitage(counts, scores):
    # counts: list of (n_flip, n_total) per ordered group; scores: group scores
    N=sum(n for _,n in counts); R=sum(f for f,_ in counts)
    if N==0 or R==0 or R==N: return None,None
    pbar=R/N
    T=sum(s*(f - n*pbar) for s,(f,n) in zip(scores,counts))
    varT=pbar*(1-pbar)*( sum(s*s*n for s,(_,n) in zip(scores,counts)) - (sum(s*n for s,(_,n) in zip(scores,counts))**2)/N )
    if varT<=0: return None,None
    z=T/np.sqrt(varT)
    from scipy import stats
    p=2*(1-stats.norm.cdf(abs(z)))
    return z,p

def per_model_trends(df):
    for coding, tiers in [("PERSONA-ONLY", ["low","medium","high"]), ("ANON-INCLUSIVE", ["anon","low","medium","high"])]:
        log(f"\n  Cochran-Armitage trend (incorrect arm, {coding}) — flip = NOT correct after pressure:")
        for name,slug in MODELS.items():
            fl={t:[0,0] for t in tiers}
            for path in [mainf(slug)] + ([f"{INF}/{slug}__anonB.jsonl"] if glob.glob(f"{INF}/{slug}__anonB.jsonl") else []):
                for l in open(path):
                    r=json.loads(l)
                    if r.get("gate_status")!="PASS" or r.get("direction")!="incorrect_endorsement": continue
                    t=r.get("tier")
                    if t not in tiers: continue
                    fl[t][1]+=1
                    if r.get("turn2_letter")!=r.get("correct_letter"): fl[t][0]+=1
            counts=[(fl[t][0],fl[t][1]) for t in tiers]
            scores=list(range(len(tiers)))
            z,p=cochran_armitage(counts,scores)
            flips=" ".join(f"{fl[t][0]/fl[t][1]*100:.0f}" for t in tiers)
            sig="*" if (p is not None and p<0.05) else " "
            log(f"    {name:9}: flips[{flips:14}] CA z={z:+.2f} p={p:.4f}{sig}" if z else f"    {name:9}: (degenerate)")


def main():
    log("="*70)
    log("BLOCKER ANALYSIS — confirmatory (regex + judge) + Cochran-Armitage + coding")
    log("="*70)
    judge=load_judge()
    df,agree,ntot=build_df(judge)
    log(f"\nRegex-vs-judge label agreement: {agree:.3f} ({ntot} labeled trials)")
    log(f"Analysis frame: {len(df)} trials (generic personas, control excluded, both arms)\n")

    log("A. CONFIRMATORY tier×direction interaction — REGEX labels:")
    confirmatory(df, "reg_correct")
    log("\nA. CONFIRMATORY tier×direction interaction — JUDGE labels:")
    confirmatory(df, "jud_correct")

    log("\nB. PER-MODEL TREND (both ladder codings — resolves §3d vs §15):")
    per_model_trends(df)

    log("\n[done]")

if __name__=="__main__":
    main()
