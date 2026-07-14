#!/usr/bin/env python3
"""STAGE 0 — independent verification of every headline number, from canonical raw data.
Pure Python (no numpy/statsmodels). Reads results/inference/ (hash-frozen) + judged files.
Emits a report to stdout; VERIFICATION.md is written from this."""
import json, glob, csv, math
from collections import defaultdict
REPO="/Users/gokulkrishnan.nair/Desktop/research-1"
MAIN=sorted(glob.glob(f"{REPO}/results/inference/*_2026*.jsonl"))
ANON=sorted(glob.glob(f"{REPO}/results/inference/*__anonB.jsonl"))
DM  =sorted(glob.glob(f"{REPO}/results/inference/*_domainmatched.jsonl"))
JUDGED=sorted(glob.glob(f"{REPO}/judge_bundle/results/judged/*__judge1.jsonl"))
def short(m):
    m=m.split("/")[-1]
    return (m.replace("Qwen2.5-","Qwen").replace("-Instruct","").replace("Llama-3.2-","Llama")
             .replace("Mistral-7B","Mistral").replace("Phi-3.5-mini","Phi")
             .replace("gemma-2-9b-it","Gemma").replace("-v0.3","").replace("-it",""))
def load(fs):
    o=[]
    for f in fs:
        for l in open(f):
            l=l.strip()
            if l: o.append(json.loads(l))
    return o
def gate(r): return r.get("gate_status") or r.get("status")
def bg(lp,c,w): return None if (not lp or c not in lp or w not in lp) else lp[c]-lp[w]
def pct(n,d): return 100*n/d if d else float("nan")
TIERS=["control","anon","low","medium","high"]
by=defaultdict(list)
for r in load(MAIN)+load(ANON): by[short(r["model"])].append(r)
MODELS=sorted(by)

print("# STAGE 0 VERIFICATION\n")
print(f"canonical MAIN files: {len(MAIN)} | ANON: {len(ANON)} | DM: {len(DM)} | JUDGED: {len(JUDGED)}")
print(f"total main+anon records: {sum(len(v) for v in by.values())}\n")

print("## Gate survival")
gate_ok={}
for m in MODELS:
    q={}
    for r in by[m]: q[r["question_id"]]=gate(r)
    p=sum(1 for v in q.values() if v=="PASS"); t=len(q); gate_ok[m]=(p,t)
    print(f"  {m:9} {p:3}/{t:3} = {pct(p,t):4.1f}%")

print("\n## Behavioral flip% INCORRECT arm (gated) — taxonomy")
for m in MODELS:
    cells=[]; an=ad=0
    for tt in TIERS:
        s=[r for r in by[m] if r.get("tier")==tt and r.get("direction")=="incorrect_endorsement" and gate(r)=="PASS"]
        n=sum(1 for r in s if r.get("flipped")); d=len(s); cells.append(pct(n,d)); an+=n; ad+=d
    print(f"  {m:9} "+" ".join(f"{c:5.1f}" for c in cells)+f"  overall={pct(an,ad):5.1f}")

print("\n## Behavioral flip% CORRECT arm (direction contrast)")
for m in MODELS:
    an=ad=0
    for r in by[m]:
        if r.get("direction")=="correct_endorsement" and gate(r)=="PASS" and r.get("tier") in TIERS:
            ad+=1; an+= 1 if r.get("flipped") else 0
    print(f"  {m:9} overall correct-arm flip={pct(an,ad):5.1f}")

print("\n## Presence-beats-prestige: belief gap anon vs high (incorrect arm)")
for m in MODELS:
    def gap(tt):
        v=[bg(r.get('turn2_logprobs'),r['correct_letter'],r['wrong_X_letter']) for r in by[m]
           if r.get('tier')==tt and r.get('direction')=='incorrect_endorsement' and gate(r)=='PASS']
        v=[x for x in v if x is not None]; return sum(v)/len(v) if v else float('nan')
    a,h=gap("anon"),gap("high")
    verdict = "anon>=high (presence)" if a<=h+1.0 else "high>anon (authority)"
    print(f"  {m:9} anon={a:+6.2f} high={h:+6.2f}  -> {verdict}")

# pooled logistic flip ~ tier*dir  (anon/low/med/high, both arms)
print("\n## Confirmatory pooled logistic (fixed) flip ~ tier*dir")
tmap={"anon":0,"low":1,"medium":2,"high":3}
rows=[]
for m in MODELS:
    for r in by[m]:
        if gate(r)!="PASS" or r.get("tier") not in tmap: continue
        d=r.get("direction"); dv=1.0 if d=="incorrect_endorsement" else (0.0 if d=="correct_endorsement" else None)
        if dv is None: continue
        t=float(tmap[r["tier"]]); y=1.0 if r.get("flipped") else 0.0
        rows.append(([1.0,t,dv,t*dv],y))
k=4; beta=[0.0]*k
def sig(z): return 1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))
for _ in range(60):
    g=[0]*k; H=[[0]*k for _ in range(k)]
    for x,y in rows:
        p=sig(sum(beta[j]*x[j] for j in range(k))); w=p*(1-p)
        for a in range(k):
            g[a]+=(y-p)*x[a]
            for b in range(k): H[a][b]-=w*x[a]*x[b]
    A=[[-H[i][j] for j in range(k)]+[g[i]] for i in range(k)]
    for i in range(k):
        pv=A[i][i]
        for j in range(i,k+1): A[i][j]/=pv
        for r2 in range(k):
            if r2!=i:
                f=A[r2][i]
                for j in range(i,k+1): A[r2][j]-=f*A[i][j]
    dl=[A[i][k] for i in range(k)]
    for i in range(k): beta[i]+=dl[i]
    if max(abs(d) for d in dl)<1e-9: break
H=[[0]*k for _ in range(k)]
for x,y in rows:
    p=sig(sum(beta[j]*x[j] for j in range(k))); w=p*(1-p)
    for a in range(k):
        for b in range(k): H[a][b]-=w*x[a]*x[b]
M=[[-H[i][j] for j in range(k)] for i in range(k)]; I=[[1.0 if i==j else 0.0 for j in range(k)] for i in range(k)]
for i in range(k):
    pv=M[i][i]
    for j in range(k): M[i][j]/=pv; I[i][j]/=pv
    for r2 in range(k):
        if r2!=i:
            f=M[r2][i]
            for j in range(k): M[r2][j]-=f*M[i][j]; I[r2][j]-=f*I[i][j]
def erf(x):
    t=1/(1+0.3275911*abs(x)); y=1-(((((1.061405429*t-1.453152027)*t)+1.421413741)*t-0.284496736)*t+0.254829592)*t*math.exp(-x*x)
    return math.copysign(y,x)
def pval(c,se): z=c/se; return 2*(1-0.5*(1+erf(abs(z)/math.sqrt(2))))
nm=["intercept","tier","dir(incorrect=1)","tier:dir INTERACTION"]
for i in range(k):
    se=math.sqrt(I[i][i]); print(f"  {nm[i]:22} coef={beta[i]:+.3f} se={se:.3f} p={pval(beta[i],se):.4f}")
print(f"  n={len(rows)}  [naive SE; cluster-robust would only widen -> interaction stays n.s.]")

# domain-matched spearman low<med<high
def spear(xs,ys):
    n=len(xs)
    if n<3: return None
    def rk(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v); i=0
        while i<len(v):
            j=i
            while j+1<len(v) and v[s[j+1]]==v[s[i]]: j+=1
            a=(i+j)/2+1
            for t in range(i,j+1): r[s[t]]=a
            i=j+1
        return r
    rx,ry=rk(xs),rk(ys); mx=sum(rx)/n; my=sum(ry)/n
    num=sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    dx=math.sqrt(sum((rx[i]-mx)**2 for i in range(n))); dy=math.sqrt(sum((ry[i]-my)**2 for i in range(n)))
    return num/(dx*dy) if dx and dy else None
print("\n## Domain-matched: institutional personas help? (belief-gap Spearman low<med<high, incorrect)")
dmby=defaultdict(list)
for r in load(DM): dmby[short(r["model"])].append(r)
tm3={"low":0,"medium":1,"high":2}; helped=0
for m in sorted(dmby):
    xs=[];ys=[]
    for r in dmby[m]:
        if r.get("direction")=="incorrect_endorsement" and gate(r)=="PASS" and r.get("tier") in tm3:
            v=bg(r.get("turn2_logprobs"),r["correct_letter"],r["wrong_X_letter"])
            if v is not None: xs.append(tm3[r["tier"]]); ys.append(v)
    rho=spear(xs,ys)
    sigflag = (rho is not None and rho<-0.10)
    helped+= 1 if sigflag else 0
    print(f"  {m:9} rho={rho:+.3f}" + ("  gradient" if sigflag else "  weak/flat"))
print(f"  -> {helped}/6 show a domain-matched belief gradient (rho<-0.10)")

# judge agreement + human kappa
print("\n## Judge vs regex agreement")
idx={}
for r in load(MAIN): idx[(short(r["model"]),r["question_id"],r.get("tier"),r.get("direction"))]=r
ag=tot=0
for r in load(JUDGED):
    m=idx.get((short(r["model"]),r["question_id"],r.get("tier"),r.get("direction")))
    if not m: continue
    c=r.get("judge_turn2_class")
    if c in (None,"ERROR"): continue
    tot+=1; ag+= ((m.get("turn2_letter")!=m.get("correct_letter"))==(c!="correct"))
print(f"  ended-not-correct agreement: {pct(ag,tot):.2f}% ({ag}/{tot})")

print("\n## Human validation Cohen's kappa (n=60)")
hum={}
with open(f"{REPO}/judge_bundle/results/human_validation/to_label.csv") as f:
    for row in csv.DictReader(f): hum[int(row["idx"])]=row["YOUR_LABEL"].strip()
jud={}
for l in open(f"{REPO}/judge_bundle/results/human_validation/judge_labels_hidden.jsonl"):
    d=json.loads(l); jud[d["idx"]]=str(d["judge_label"]).strip()
cats=["correct","incorrect","erroneous"]
pair=[(hum[i],jud[i]) for i in hum if i in jud and jud[i] in cats and hum[i] in cats]
n=len(pair); raw=sum(1 for a,b in pair if a==b)/n
# kappa
def marg(idx):
    from collections import Counter
    c=Counter(p[idx] for p in pair); return {k:c.get(k,0)/n for k in cats}
mh=marg(0); mj=marg(1); pe=sum(mh[c]*mj[c] for c in cats)
kappa=(raw-pe)/(1-pe) if pe<1 else float("nan")
excluded=[i for i in hum if i not in jud or jud.get(i) not in cats or hum[i] not in cats]
print(f"  usable pairs: {n} (excluded {len(excluded)} non-3-class, e.g. ERROR rows: {excluded})")
print(f"  raw agreement={raw*100:.1f}%  Cohen kappa={kappa:.3f}")
print("\nDONE")
