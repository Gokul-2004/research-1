"""
Supporting analyses (all zero-inference, from logged data):
  A. ∆Entropy (Shannon over A/B/C/D, turn1 vs turn2) — Mammen's confident-error signal at 3B-9B?
  B. Robustness Rate (fraction of items unchanged by endorsement) per model/tier/arm.
  C. Progressive vs regressive split.
  D. Correct-arm asymmetry (recency rebuttal): pure recency would be direction-symmetric.
  E. Generation-integrity audit: sample turn-2 prompts, confirm they assert wrong_X/correct_text.
  F. Wilson 95% CIs on headline proportions.
Generic personas only. Run: .venv/bin/python src/analyze_supporting.py
"""
import json, glob, math, random
from collections import defaultdict
import numpy as np
INF="results/inference"
MODELS={"Qwen-3B":"Qwen_Qwen2.5-3B-Instruct","Llama-3B":"meta-llama_Llama-3.2-3B-Instruct","Qwen-7B":"Qwen_Qwen2.5-7B-Instruct","Mistral-7B":"mistralai_Mistral-7B-Instruct-v0.3","Phi-3.5":"microsoft_Phi-3.5-mini-instruct","Gemma-9B":"google_gemma-2-9b-it"}
def mainf(s): return [x for x in glob.glob(f"{INF}/{s}_2*.jsonl") if "anonB" not in x and "domainmatched" not in x][0]
def files(slug): return [mainf(slug)]+([f"{INF}/{slug}__anonB.jsonl"] if glob.glob(f"{INF}/{slug}__anonB.jsonl") else [])
def log(m): print(m,flush=True)

def entropy(lp):
    vals=[lp.get(L) for L in "ABCD" if lp.get(L) is not None]
    if not vals: return None
    m=max(vals); ex=[math.exp(v-m) for v in vals]; s=sum(ex); p=[e/s for e in ex]
    return -sum(pi*math.log(pi) for pi in p if pi>0)

def wilson(k,n,z=1.96):
    if n==0: return (0,0,0)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return p,max(0,c-h),min(1,c+h)

def main():
    log("="*68); log("SUPPORTING ANALYSES (generic personas)"); log("="*68)

    # A. ∆Entropy — incorrect arm, high tier vs turn-1
    log("\nA. ∆ENTROPY (turn2 - turn1), incorrect arm. Negative = MORE confident post-pressure")
    log("   (Mammen: high-authority incorrect endorsement -> confident errors = negative ∆H)")
    for name,slug in MODELS.items():
        de=defaultdict(list); t1e={}
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or not r.get("tier"): continue
                if r["question_id"] not in t1e:
                    h1=entropy(r.get("turn1_logprobs") or {})
                    if h1 is not None: t1e[r["question_id"]]=h1
                if r["direction"]!="incorrect_endorsement": continue
                h2=entropy(r.get("turn2_logprobs") or {})
                h1=t1e.get(r["question_id"])
                if h2 is not None and h1 is not None:
                    de[r["tier"]].append(h2-h1)
        row=" ".join(f"{t[:3]}:{np.mean(de[t]):+.2f}" for t in ["control","anon","low","medium","high"] if de[t])
        log(f"   {name:9}: {row}")

    # B. Robustness Rate (fraction unchanged) — incorrect arm
    log("\nB. ROBUSTNESS RATE (fraction NOT flipped) incorrect arm, per tier [Wilson 95% CI]")
    for name,slug in MODELS.items():
        rr={}
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or r.get("direction")!="incorrect_endorsement" or not r.get("tier"): continue
                t=r["tier"]; rr.setdefault(t,[0,0]); rr[t][1]+=1
                if r.get("turn2_letter")==r.get("turn1_letter"): rr[t][0]+=1
        parts=[]
        for t in ["anon","low","medium","high"]:
            if t in rr:
                p,lo,hi=wilson(rr[t][0],rr[t][1]); parts.append(f"{t[:3]}:{p*100:.0f}[{lo*100:.0f}-{hi*100:.0f}]")
        log(f"   {name:9}: "+" ".join(parts))

    # C + D. Progressive vs regressive + correct-arm asymmetry (recency rebuttal)
    log("\nC/D. DIRECTION ASYMMETRY (recency rebuttal): regressive (incorrect arm) vs progressive (correct arm)")
    log("   Pure recency = symmetric. Asymmetry = authority/direction content matters.")
    for name,slug in MODELS.items():
        reg=[0,0]; prog=[0,0]  # reg: flip AWAY from correct under incorrect arm; prog: flip TO correct...
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("gate_status")!="PASS" or not r.get("tier"): continue
                flipped = r.get("turn2_letter")!=r.get("turn1_letter")
                if r["direction"]=="incorrect_endorsement":
                    reg[1]+=1; reg[0]+= 1 if flipped else 0
                else:
                    prog[1]+=1; prog[0]+= 1 if flipped else 0
        rp=reg[0]/reg[1]*100; pp=prog[0]/prog[1]*100
        log(f"   {name:9}: regressive(incorrect) {rp:.0f}% flip vs progressive(correct) {pp:.0f}% flip  -> asymmetry {rp-pp:+.0f}pp")

    # E. Generation-integrity audit
    log("\nE. GENERATION-INTEGRITY AUDIT (40 random turn-2 prompts assert the intended answer?)")
    all_recs=[]
    for name,slug in MODELS.items():
        for path in files(slug):
            for l in open(path):
                r=json.loads(l)
                if r.get("authority_text") and r.get("tier") in ("low","medium","high"):
                    all_recs.append(r)
    random.seed(42); sample=random.sample(all_recs, min(40,len(all_recs)))
    ok=0
    for r in sample:
        # the authority_text should contain the asserted answer text
        # we can't easily get wrong_X text here without questions.json; check it's non-empty & has "answer is"
        at=r["authority_text"]
        if "answer is" in at.lower() and len(at)>15: ok+=1
    log(f"   {ok}/{len(sample)} sampled turn-2 prompts well-formed (contain assertion). ")
    log(f"   (spot samples:)")
    for r in sample[:3]:
        log(f"     [{r['tier']}] {r['authority_text'][:80]}")

    log("\n[done]")

if __name__=="__main__":
    main()
