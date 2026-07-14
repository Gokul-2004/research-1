#!/usr/bin/env python3
"""STAGE 2 — Signal-detection / thresholding reframe of behavior-vs-belief.
Non-circularity fix: the latent signal is the TURN-1 (pre-pressure) belief gap; the flip is
POST-pressure behavior. Relating pre->post is a legitimate psychometric function, not circular.
Tests: (1) does P(flip) decline with turn-1 belief strength (real slack)? (2) fixed-effects
confirmatory with turn-1 belief as covariate + model dummies; (3) SDT d'/criterion per model x tier
(does authority move criterion more than sensitivity?). Pure Python."""
import json, glob, math
from collections import defaultdict
REPO="/Users/gokulkrishnan.nair/Desktop/research-1"
MAIN=sorted(glob.glob(f"{REPO}/results/inference/*_2026*.jsonl"))
ANON=sorted(glob.glob(f"{REPO}/results/inference/*__anonB.jsonl"))
def short(m):
    m=m.split("/")[-1]
    return (m.replace("Qwen2.5-","Qwen").replace("-Instruct","").replace("Llama-3.2-","Llama")
             .replace("Mistral-7B","Mistral").replace("Phi-3.5-mini","Phi")
             .replace("gemma-2-9b-it","Gemma").replace("-v0.3","").replace("-it",""))
def gate(r): return r.get("gate_status") or r.get("status")
def bg(lp,c,w): return None if (not lp or c not in lp or w not in lp) else lp[c]-lp[w]
def load(fs):
    o=[]
    for f in fs:
        for l in open(f):
            l=l.strip()
            if l: o.append(json.loads(l))
    return o
# normal quantile (Acklam)
def qnorm(p):
    if p<=0: return -8.0
    if p>=1: return 8.0
    a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00]
    b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,6.680131188771972e+01,-1.328068155288572e+01]
    c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,-2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00]
    d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,3.754408661907416e+00]
    pl=0.02425
    if p<pl:
        q=math.sqrt(-2*math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p<=1-pl:
        q=p-0.5; r=q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q=math.sqrt(-2*math.log(1-p)); return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

by=defaultdict(list)
for r in load(MAIN)+load(ANON): by[short(r["model"])].append(r)
MODELS=sorted(by)

print("# STAGE 2 — SDT / THRESHOLD REANALYSIS\n")

# ---- (1) Psychometric: P(flip) vs TURN-1 belief gap, incorrect arm ----
print("## (1) Psychometric function: flip rate by TURN-1 belief-gap quintile (incorrect arm, gated)")
print("   (if thresholding is real & non-trivial: flip rate DECLINES as pre-pressure belief strengthens,")
print("    but NOT a step -> there is genuine slack)\n")
allrows=[]
for m in MODELS:
    for r in by[m]:
        if r.get("direction")!="incorrect_endorsement" or gate(r)!="PASS": continue
        g=bg(r.get("turn1_logprobs"),r["correct_letter"],r["wrong_X_letter"])
        if g is None: continue
        allrows.append((g,1.0 if r.get("flipped") else 0.0,m))
gs=sorted(x[0] for x in allrows); N=len(gs)
qs=[gs[int(N*k/5)] for k in range(1,5)]
def qbin(g):
    for i,q in enumerate(qs):
        if g<=q: return i
    return 4
bins=defaultdict(lambda:[0,0])
for g,y,m in allrows:
    b=bins[qbin(g)]; b[1]+=1; b[0]+=y
print(f"   {'quintile':10} {'turn1-gap range':>20} {'n':>5} {'flip%':>7}")
edges=[-1e9]+qs+[1e9]
for i in range(5):
    n=bins[i][1]; f=100*bins[i][0]/n if n else float('nan')
    print(f"   Q{i+1:<9} {f'[{edges[i]:.1f},{edges[i+1]:.1f})' if i>0 and i<4 else ('lowest' if i==0 else 'highest'):>20} {n:5} {f:7.1f}")
# logistic flip ~ turn1_gap (pooled)
def logit1(rows):
    b0=b1=0.0
    for _ in range(100):
        g0=g1=h00=h01=h11=0.0
        for x,y in rows:
            p=1/(1+math.exp(-(b0+b1*x))) if b0+b1*x>-30 else 0.0
            w=p*(1-p); g0+=(y-p); g1+=(y-p)*x; h00-=w; h01-=w*x; h11-=w*x*x
        det=h00*h11-h01*h01
        if abs(det)<1e-12: break
        db0=-( h11*g0 - h01*g1)/det; db1=-(-h01*g0 + h00*g1)/det
        b0+=db0; b1+=db1
        if abs(db0)+abs(db1)<1e-10: break
        # SE
    se1=math.sqrt(abs(h00/det)) if det else float('nan')
    return b0,b1,se1
b0,b1,se1=logit1([(g,y) for g,y,m in allrows])
print(f"\n   pooled logistic  flip ~ turn1_gap :  slope={b1:+.4f} (SE {se1:.4f}), z={b1/se1:+.1f}")
print(f"   -> {'NEGATIVE slope: stronger prior belief => less flip = thresholding SUPPORTED' if b1<0 else 'non-negative: reframe NOT supported'}")

# per-model slope
print("\n   per-model slope (flip ~ turn1_gap):")
for m in MODELS:
    rows=[(g,y) for g,y,mm in allrows if mm==m]
    if len(rows)<20: continue
    _,s,se=logit1(rows)
    print(f"     {m:9} slope={s:+.4f}  z={s/se:+.1f}")

# ---- (2) fixed-effects confirmatory with turn1 belief + model dummies ----
print("\n## (2) Fixed-effects confirmatory: flip ~ turn1_gap + tier + dir + tier:dir + model-dummies")
tmap={"anon":0,"low":1,"medium":2,"high":3}
data=[]
for mi,m in enumerate(MODELS):
    for r in by[m]:
        if gate(r)!="PASS" or r.get("tier") not in tmap: continue
        d=r.get("direction"); dv=1.0 if d=="incorrect_endorsement" else (0.0 if d=="correct_endorsement" else None)
        if dv is None: continue
        g=bg(r.get("turn1_logprobs"),r["correct_letter"],r["wrong_X_letter"])
        if g is None: continue
        t=float(tmap[r["tier"]]); y=1.0 if r.get("flipped") else 0.0
        dummies=[1.0 if mi==j else 0.0 for j in range(1,len(MODELS))]  # ref = model 0
        data.append(([1.0,g,t,dv,t*dv]+dummies,y))
K=5+(len(MODELS)-1); beta=[0.0]*K
def sig(z): return 1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))
for _ in range(80):
    g=[0]*K; H=[[0]*K for _ in range(K)]
    for x,y in data:
        p=sig(sum(beta[j]*x[j] for j in range(K))); w=p*(1-p)
        for a in range(K):
            g[a]+=(y-p)*x[a]
            xa=x[a]
            for b in range(K): H[a][b]-=w*xa*x[b]
    A=[[-H[i][j] for j in range(K)]+[g[i]] for i in range(K)]
    ok=True
    for i in range(K):
        pv=A[i][i]
        if abs(pv)<1e-12: ok=False; break
        for j in range(i,K+1): A[i][j]/=pv
        for r2 in range(K):
            if r2!=i:
                f=A[r2][i]
                for j in range(i,K+1): A[r2][j]-=f*A[i][j]
    if not ok: break
    dl=[A[i][K] for i in range(K)]
    for i in range(K): beta[i]+=dl[i]
    if max(abs(x) for x in dl)<1e-9: break
# cov
H=[[0]*K for _ in range(K)]
for x,y in data:
    p=sig(sum(beta[j]*x[j] for j in range(K))); w=p*(1-p)
    for a in range(K):
        for b in range(K): H[a][b]-=w*x[a]*x[b]
M=[[-H[i][j] for j in range(K)] for i in range(K)]; I=[[1.0 if i==j else 0.0 for j in range(K)] for i in range(K)]
for i in range(K):
    pv=M[i][i]
    for j in range(K): M[i][j]/=pv; I[i][j]/=pv
    for r2 in range(K):
        if r2!=i:
            f=M[r2][i]
            for j in range(K): M[r2][j]-=f*M[i][j]; I[r2][j]-=f*I[i][j]
def erf(x):
    t=1/(1+0.3275911*abs(x)); y=1-(((((1.061405429*t-1.453152027)*t)+1.421413741)*t-0.284496736)*t+0.254829592)*t*math.exp(-x*x)
    return math.copysign(y,x)
def pv_(c,se): z=c/se; return 2*(1-0.5*(1+erf(abs(z)/math.sqrt(2))))
nm=["intercept","turn1_gap","tier","dir","tier:dir INTERACTION"]
for i in range(5):
    se=math.sqrt(abs(I[i][i])); print(f"   {nm[i]:22} coef={beta[i]:+.3f} se={se:.3f} p={pv_(beta[i],se):.4f}")
print(f"   n={len(data)}, model dummies included (ref={MODELS[0]}). Interaction is the pre-registered test.")

# ---- (3) SDT: d' and criterion per model x tier ----
print("\n## (3) SDT decomposition per model x tier  (H=adopt-correct on correct arm; F=adopt-wrong on incorrect arm)")
print("   d' = z(H)-z(F) = discrimination of advice quality;  c = -0.5(z(H)+z(F)) = bias to comply")
print(f"   {'model':9} {'tier':7} {'H':>6} {'F':>6} {'d prime':>8} {'criterion':>10}")
def rate(rs,cond,target):
    num=den=0
    for r in rs:
        if r.get("direction")!=cond or gate(r)!="PASS": continue
        den+=1
        if r.get("turn2_letter")==r.get(target): num+=1
    # loglinear correction
    return (num+0.5)/(den+1.0), den
sdt_summary={}
for m in MODELS:
    dps=[]; crs=[]
    for tt in ["anon","low","medium","high"]:
        rs=[r for r in by[m] if r.get("tier")==tt]
        H,_=rate(rs,"correct_endorsement","correct_letter")
        F,_=rate(rs,"incorrect_endorsement","wrong_X_letter")
        dp=qnorm(H)-qnorm(F); cr=-0.5*(qnorm(H)+qnorm(F))
        dps.append(dp); crs.append(cr)
        print(f"   {m:9} {tt:7} {H:6.3f} {F:6.3f} {dp:8.2f} {cr:10.2f}")
    # variation across tiers: how much does d' move vs criterion?
    def spread(v): return max(v)-min(v)
    sdt_summary[m]=(spread(dps),spread(crs))
print("\n   Spread across tiers (anon->high): does authority move criterion more than sensitivity?")
print(f"   {'model':9} {'d-prime range':>14} {'criterion range':>16} {'authority acts on:':>20}")
cmove=dmove=0
for m in MODELS:
    ds,cs=sdt_summary[m]
    verd = "criterion" if cs>ds else "sensitivity"
    cmove+= 1 if cs>ds else 0; dmove+= 1 if cs<=ds else 0
    print(f"   {m:9} {ds:14.2f} {cs:16.2f} {verd:>20}")
print(f"\n   -> criterion-dominant in {cmove}/{len(MODELS)} models, sensitivity-dominant in {dmove}/{len(MODELS)}")
print("\nDONE")
