"""
Generate paper figures. Inspiration from the literature-survey papers:
- Mammen Fig 3: ΔAcc line plot across expertise tiers (correct vs misleading) -> our Fig 2 ladders
- Mammen Fig 4 / SycEval: grouped bars before/after -> our Fig 3 paired ladders
- Multilingual/ELEPHANT: Wilson-CI dot plots -> our Fig 1 interaction w/ CIs
Figures (roadmap):
  fig1_interaction_null   — pooled accuracy-retained by tier × arm, Wilson CIs (the null made visible)
  fig2_permodel_ladders   — 6-panel flip ladders incl anon (heterogeneity)
  fig3_generic_vs_domain  — paired generic vs domain-matched flip ladders (Gemma win, Mistral collapse)
  fig4_behavior_vs_belief — per-condition behavioral flip vs mean belief gap scatter
Run: .venv/bin/python src/make_figures.py   -> writes results/figures/*.png
"""
import json, glob, math
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INF="results/inference"; OUT="results/figures"
import os; os.makedirs(OUT, exist_ok=True)
MODELS={"Qwen-3B":"Qwen_Qwen2.5-3B-Instruct","Llama-3B":"meta-llama_Llama-3.2-3B-Instruct","Qwen-7B":"Qwen_Qwen2.5-7B-Instruct","Mistral-7B":"mistralai_Mistral-7B-Instruct-v0.3","Phi-3.5":"microsoft_Phi-3.5-mini-instruct","Gemma-9B":"google_gemma-2-9b-it"}
def mainf(s): return [x for x in glob.glob(f"{INF}/{s}_2*.jsonl") if "anonB" not in x and "domainmatched" not in x][0]
def files(slug): return [mainf(slug)]+([f"{INF}/{slug}__anonB.jsonl"] if glob.glob(f"{INF}/{slug}__anonB.jsonl") else [])
def wilson(k,n,z=1.96):
    if n==0: return 0,0,0
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return p,max(0,c-h),min(1,c+h)
TIERS=["anon","low","medium","high"]; TLAB=["anon","low","med","high"]

# ---- collect per-model per-tier flip + accuracy, both arms ----
def collect(slug, dm=False):
    fl=defaultdict(lambda: defaultdict(lambda:[0,0]))  # arm -> tier -> [flip,n]
    paths = [f"{INF}/{slug}_domainmatched.jsonl"] if dm else files(slug)
    for path in paths:
        for l in open(path):
            r=json.loads(l)
            if r.get("gate_status")!="PASS" or not r.get("tier"): continue
            arm=r["direction"]; t=r["tier"]
            fl[arm][t][1]+=1
            if r.get("turn2_letter")!=r.get("turn1_letter"): fl[arm][t][0]+=1
    return fl

# ===== FIG 1: the null made visible — pooled accuracy-retained by tier x arm w/ Wilson CIs =====
def fig1():
    pooled=defaultdict(lambda: defaultdict(lambda:[0,0]))  # arm -> tier -> [correct,n]
    for name,slug in MODELS.items():
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or not r.get("tier") or r["tier"]=="control": continue
                arm=r["direction"]; t=r["tier"]
                pooled[arm][t][1]+=1
                if r.get("turn2_letter")==r.get("correct_letter"): pooled[arm][t][0]+=1
    fig,ax=plt.subplots(figsize=(6,4))
    x=np.arange(len(TIERS))
    for arm,lab,col in [("incorrect_endorsement","Incorrect endorsement (regressive)","#d1495b"),
                        ("correct_endorsement","Correct endorsement (progressive)","#2e8b57")]:
        ys=[]; los=[]; his=[]
        for t in TIERS:
            k,n=pooled[arm][t]; p,lo,hi=wilson(k,n); ys.append(p*100); los.append((p-lo)*100); his.append((hi-p)*100)
        ax.errorbar(x, ys, yerr=[los,his], marker="o", capsize=3, label=lab, color=col, lw=2)
    ax.set_xticks(x); ax.set_xticklabels(TLAB)
    ax.set_xlabel("Authority tier"); ax.set_ylabel("Accuracy retained after pressure (%)")
    ax.set_title("Pooled: no clean authority gradient\n(pre-registered tier×direction interaction n.s.)")
    ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_ylim(0,100)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig1_interaction_null.png", dpi=150); plt.close()
    print("fig1 done")

# ===== FIG 2: 6-panel per-model flip ladders (incorrect arm, incl anon) =====
def fig2():
    fig,axes=plt.subplots(2,3,figsize=(11,6.5),sharey=True)
    for ax,(name,slug) in zip(axes.flat, MODELS.items()):
        fl=collect(slug)["incorrect_endorsement"]
        ys=[]; los=[]; his=[]
        for t in TIERS:
            f,n=fl[t]; p,lo,hi=wilson(f,n); ys.append(p*100); los.append((p-lo)*100); his.append((hi-p)*100)
        x=np.arange(len(TIERS))
        ax.errorbar(x,ys,yerr=[los,his],marker="o",capsize=3,color="#d1495b",lw=2)
        ax.set_title(name,fontsize=10); ax.set_xticks(x); ax.set_xticklabels(TLAB,fontsize=8)
        ax.grid(alpha=.3); ax.set_ylim(0,100)
    for ax in axes[:,0]: ax.set_ylabel("Flip rate (%)")
    for ax in axes[1,:]: ax.set_xlabel("Authority tier")
    fig.suptitle("Per-model behavioral flip ladders (incorrect endorsement) — heterogeneous, not uniform",fontsize=12)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig2_permodel_ladders.png",dpi=150); plt.close()
    print("fig2 done")

# ===== FIG 3: generic vs domain-matched paired ladders (low/med/high) =====
def fig3():
    tiers=["low","medium","high"]; tl=["low","med","high"]
    fig,axes=plt.subplots(2,3,figsize=(11,6.5),sharey=True)
    for ax,(name,slug) in zip(axes.flat, MODELS.items()):
        for dm,col,lab in [(False,"#3f88c5","generic personas"),(True,"#e07a3f","domain-matched")]:
            fl=collect(slug,dm=dm)["incorrect_endorsement"]
            ys=[fl[t][0]/fl[t][1]*100 if fl[t][1] else 0 for t in tiers]
            ax.plot(range(len(tiers)),ys,marker="o",color=col,lw=2,label=lab)
        ax.set_title(name,fontsize=10); ax.set_xticks(range(len(tiers))); ax.set_xticklabels(tl,fontsize=8)
        ax.grid(alpha=.3); ax.set_ylim(0,100)
    axes[0,0].legend(fontsize=8)
    for ax in axes[:,0]: ax.set_ylabel("Flip rate (%)")
    for ax in axes[1,:]: ax.set_xlabel("Authority tier")
    fig.suptitle("Generic vs domain-matched personas (exploratory) — Gemma strengthens, Mistral collapses",fontsize=12)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig3_generic_vs_domain.png",dpi=150); plt.close()
    print("fig3 done")

# ===== FIG 4: behavior-vs-belief scatter (per model-tier point) =====
def fig4():
    fig,ax=plt.subplots(figsize=(6.5,5))
    cmap=plt.cm.tab10
    for i,(name,slug) in enumerate(MODELS.items()):
        for t in TIERS:
            f=n=0; gaps=[]
            for path in files(slug):
                for l in open(path):
                    r=json.loads(l)
                    if r.get("gate_status")!="PASS" or r.get("direction")!="incorrect_endorsement" or r.get("tier")!=t: continue
                    n+=1
                    if r.get("turn2_letter")!=r.get("turn1_letter"): f+=1
                    cl,wl=r["correct_letter"],r["wrong_X_letter"]; lp=r.get("turn2_logprobs") or {}
                    if lp.get(cl) is not None and lp.get(wl) is not None: gaps.append(lp[cl]-lp[wl])
            if n and gaps:
                ax.scatter(np.mean(gaps), f/n*100, color=cmap(i), s=60,
                           label=name if t=="high" else None, edgecolor="k", linewidth=.5)
    ax.axvline(0,color="gray",ls="--",alpha=.5)
    ax.set_xlabel("Belief gap  logP(correct) − logP(wrong)  (post-pressure)")
    ax.set_ylabel("Behavioral flip rate (%)")
    ax.set_title("Behavior vs belief (each point = model×tier, incorrect arm)")
    ax.legend(fontsize=8,title="model (high tier marked)"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig4_behavior_vs_belief.png",dpi=150); plt.close()
    print("fig4 done")

if __name__=="__main__":
    fig1(); fig2(); fig3(); fig4()
    print(f"\nAll figures -> {OUT}/")
