"""Additional figures matching literature-survey conventions.
fig5_delta_acc      — Mammen-style ΔAccuracy line-ladder (direct visual comparison to Mammen Fig 3)
fig6_delta_entropy  — ∆Entropy per tier (our positive vs Mammen's negative confident-error signal)
fig7_robustness_split — Robustness Rate bars w/ resist/saturate split (SycoEval-EM bimodal style)
fig8_direction_asymmetry — regressive vs progressive bars (the recency rebuttal)
"""
import json, glob, math
from collections import defaultdict
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
INF="results/inference"; OUT="results/figures"
MODELS={"Qwen-3B":"Qwen_Qwen2.5-3B-Instruct","Llama-3B":"meta-llama_Llama-3.2-3B-Instruct","Qwen-7B":"Qwen_Qwen2.5-7B-Instruct","Mistral-7B":"mistralai_Mistral-7B-Instruct-v0.3","Phi-3.5":"microsoft_Phi-3.5-mini-instruct","Gemma-9B":"google_gemma-2-9b-it"}
def mainf(s): return [x for x in glob.glob(f"{INF}/{s}_2*.jsonl") if "anonB" not in x and "domainmatched" not in x][0]
def files(slug): return [mainf(slug)]+([f"{INF}/{slug}__anonB.jsonl"] if glob.glob(f"{INF}/{slug}__anonB.jsonl") else [])
def entropy(lp):
    v=[lp.get(L) for L in "ABCD" if lp.get(L) is not None]
    if not v: return None
    m=max(v); ex=[math.exp(x-m) for x in v]; s=sum(ex); p=[e/s for e in ex]
    return -sum(pi*math.log(pi) for pi in p if pi>0)
TIERS=["anon","low","medium","high"]; TL=["anon","low","med","high"]
COL={"Qwen-3B":"#1f77b4","Llama-3B":"#ff7f0e","Qwen-7B":"#2ca02c","Mistral-7B":"#d62728","Phi-3.5":"#9467bd","Gemma-9B":"#8c564b"}

# FIG5: Mammen-style ΔAccuracy (accuracy_after - baseline). baseline = 100% (all gate-pass correct at turn1)
def fig5():
    fig,ax=plt.subplots(figsize=(7,4.5))
    for name,slug in MODELS.items():
        acc=defaultdict(lambda:[0,0])
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or r.get("direction")!="incorrect_endorsement" or r.get("tier") not in TIERS: continue
                acc[r["tier"]][1]+=1
                if r.get("turn2_letter")==r.get("correct_letter"): acc[r["tier"]][0]+=1
        dacc=[(acc[t][0]/acc[t][1]-1.0)*100 for t in TIERS]  # ΔAcc vs 100% baseline
        ax.plot(range(len(TIERS)),dacc,marker="o",color=COL[name],lw=2,label=name)
    ax.axhline(0,color="gray",ls="--",alpha=.4)
    ax.set_xticks(range(len(TIERS))); ax.set_xticklabels(TL)
    ax.set_xlabel("Authority tier"); ax.set_ylabel("ΔAccuracy vs unpressured baseline (pp)")
    ax.set_title("ΔAccuracy under incorrect endorsement (Mammen-style)\nmonotonic degradation would go steadily down-left→down-right")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.savefig(f"{OUT}/fig5_delta_acc.png",dpi=150,bbox_inches="tight"); plt.close(); print("fig5 done")

# FIG6: ∆Entropy (turn2 - turn1), incorrect arm. Mammen: negative (confident errors). Us: mostly positive.
def fig6():
    fig,ax=plt.subplots(figsize=(7,4.5))
    for name,slug in MODELS.items():
        t1={}; de=defaultdict(list)
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or not r.get("tier"): continue
                if r["question_id"] not in t1:
                    h1=entropy(r.get("turn1_logprobs") or {}); 
                    if h1 is not None: t1[r["question_id"]]=h1
                if r["direction"]!="incorrect_endorsement" or r["tier"] not in TIERS: continue
                h2=entropy(r.get("turn2_logprobs") or {}); h1=t1.get(r["question_id"])
                if h2 is not None and h1 is not None: de[r["tier"]].append(h2-h1)
        ys=[np.mean(de[t]) for t in TIERS]
        ax.plot(range(len(TIERS)),ys,marker="o",color=COL[name],lw=2,label=name)
    ax.axhline(0,color="gray",ls="--",alpha=.5)
    ax.text(0.02,0.95,"Mammen: NEGATIVE (confident errors)\nOurs: mostly POSITIVE (less certain)",transform=ax.transAxes,fontsize=8,va="top",bbox=dict(boxstyle="round",fc="#fff3cd"))
    ax.set_xticks(range(len(TIERS))); ax.set_xticklabels(TL)
    ax.set_xlabel("Authority tier"); ax.set_ylabel("∆Entropy (turn2 − turn1)")
    ax.set_title("∆Entropy under incorrect endorsement — Mammen's confident-error signal\nDOES NOT replicate at 3B–9B under two-turn measurement")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.savefig(f"{OUT}/fig6_delta_entropy.png",dpi=150,bbox_inches="tight"); plt.close(); print("fig6 done")

# FIG7: Robustness Rate (fraction NOT flipped) at HIGH tier, bar chart, resist/saturate split
def fig7():
    fig,ax=plt.subplots(figsize=(7,4.5))
    names=[]; rr=[]; cols=[]
    for name,slug in MODELS.items():
        f=n=0
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or r.get("direction")!="incorrect_endorsement" or r.get("tier")!="high": continue
                n+=1
                if r.get("turn2_letter")==r.get("turn1_letter"): f+=1
        rate=f/n*100; names.append(name); rr.append(rate)
        cols.append("#2e8b57" if rate>=30 else "#d1495b")
    order=np.argsort(rr)[::-1]
    ax.bar([names[i] for i in order],[rr[i] for i in order],color=[cols[i] for i in order])
    ax.axhline(30,color="gray",ls="--",alpha=.5); ax.text(5.1,31,"resist/saturate split",fontsize=8,ha="right")
    ax.set_ylabel("Robustness Rate at high authority (%)")
    ax.set_title("Robustness under strong authority — bimodal (resisters vs saturators)")
    ax.grid(alpha=.3,axis="y"); ax.set_ylim(0,80)
    fig.savefig(f"{OUT}/fig7_robustness_split.png",dpi=150,bbox_inches="tight"); plt.close(); print("fig7 done")

# FIG8: direction asymmetry (regressive vs progressive) — recency rebuttal
def fig8():
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    names=list(MODELS); reg=[]; prog=[]
    for name,slug in MODELS.items():
        R=[0,0]; P=[0,0]
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or not r.get("tier"): continue
                fl=r.get("turn2_letter")!=r.get("turn1_letter")
                if r["direction"]=="incorrect_endorsement": R[1]+=1; R[0]+=fl
                else: P[1]+=1; P[0]+=fl
        reg.append(R[0]/R[1]*100); prog.append(P[0]/P[1]*100)
    x=np.arange(len(names)); w=0.38
    ax.bar(x-w/2,reg,w,label="Regressive (incorrect arm)",color="#d1495b")
    ax.bar(x+w/2,prog,w,label="Progressive (correct arm)",color="#2e8b57")
    ax.set_xticks(x); ax.set_xticklabels(names,fontsize=8,rotation=15)
    ax.set_ylabel("Flip rate (%)")
    ax.set_title("Direction asymmetry: flips are content-sensitive, NOT recency\n(pure recency would make these bars equal)")
    ax.legend(fontsize=8); ax.grid(alpha=.3,axis="y")
    fig.savefig(f"{OUT}/fig8_direction_asymmetry.png",dpi=150,bbox_inches="tight"); plt.close(); print("fig8 done")

if __name__=="__main__":
    fig5(); fig6(); fig7(); fig8(); print("extra figures done")
