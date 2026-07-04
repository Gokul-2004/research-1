"""
DOMAIN-MATCHED PERSONA RUN (disambiguation experiment) — GPU-ready.

Re-runs the authority tiers (low/medium/high) with DOMAIN-MATCHED INSTITUTIONAL
personas instead of the generic student->professor ladder, to test whether the
null gradient was a persona-design artifact (per Joswin 746's claim that
domain-matched institutional hierarchy is required).

Reuses each model's EXISTING gate decisions + turn-1 responses from the main run
(so directly comparable). Only runs low/medium/high (anon + control are identical
to the generic run and already collected). Writes to SEPARATE *_domainmatched.jsonl.

Set DEVICE=cuda on a GPU box (falls back to cpu). Resume-safe.

Run (per model):
  MODEL_ID="Qwen/Qwen2.5-3B-Instruct" DEVICE=cuda HF_HOME="$(pwd)/hf_cache" python src/run_domainmatched.py
Or all at once:  bash src/run_domainmatched_all.sh
"""
import json, os, time
from datetime import datetime, timezone
from pathlib import Path
import torch

from run_inference import (
    build_turn2_prompt, generate_with_logprobs, extract_letter, count_tokens,
    QUESTIONS_PATH, OUT_DIR,
)

MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-3B-Instruct")
DEVICE = os.environ.get("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float16
TIERS = ["low", "medium", "high"]  # anon + control already have generic-run data
DIRECTIONS = ["incorrect_endorsement", "correct_endorsement"]
ROOT = Path(__file__).resolve().parent.parent
DM_TEMPLATES = json.loads((ROOT / "data" / "authority_templates_domainmatched.json").read_text())


def log(m): print(m, flush=True)


def load_model_gpu(model_id):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("HF_TOKEN="):
                os.environ["HF_TOKEN"] = line.split("=", 1)[1].strip()
    log(f"[load] {model_id} on {DEVICE} fp16...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=DTYPE, low_cpu_mem_usage=True)
    model.to(DEVICE); model.eval()
    log(f"[load] done in {time.time()-t0:.1f}s on {DEVICE}")
    return tok, model


def gen_gpu(model, tok, prompt, max_new_tokens=20):
    inputs = tok(prompt, return_tensors="pt").to(DEVICE)
    ilen = inputs["input_ids"].shape[1]
    cids = {L: (tok.encode(L, add_special_tokens=False) or [None])[0] for L in "ABCD"}
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                             temperature=1.0, pad_token_id=tok.eos_token_id,
                             return_dict_in_generate=True, output_scores=True)
    new = out.sequences[0][ilen:]
    resp = tok.decode(new, skip_special_tokens=True).strip()
    lp = torch.log_softmax(out.scores[0][0].float(), dim=-1)
    logprobs = {L: (float(lp[cids[L]]) if cids[L] is not None else None) for L in "ABCD"}
    return resp, logprobs


def find_main(slug):
    return [x for x in OUT_DIR.glob(f"{slug}_*.jsonl") if "__anonB" not in x.name and "_domainmatched" not in x.name][0]


def load_gate(main_path):
    g = {}
    for line in open(main_path):
        try: d = json.loads(line)
        except: continue
        if d.get("gate_status") == "PASS" and d["question_id"] not in g:
            g[d["question_id"]] = {k: d[k] for k in ("turn1_letter","turn1_response","turn1_logprobs","correct_letter","wrong_X_letter")}
    return g


def load_done(p):
    done = {}
    if p.exists():
        for line in open(p):
            try: d = json.loads(line)
            except: continue
            done[(d["question_id"], d["tier"], d["direction"])] = 1
    return done


def run(model_id):
    slug = model_id.replace("/", "_")
    qs = {q["id"]: q for q in json.loads(QUESTIONS_PATH.read_text())}
    gate = load_gate(find_main(slug))
    out_path = OUT_DIR / f"{slug}_domainmatched.jsonl"
    done = load_done(out_path)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log(f"[domainmatched] {model_id}: {len(gate)} gate-PASS Qs, {len(done)} trials already done")

    tok, model = load_model_gpu(model_id)
    with open(out_path, "a") as fout:
        for i, (qid, g) in enumerate(gate.items()):
            q = qs[qid]
            domain = q["domain"]
            personas = DM_TEMPLATES["personas"][domain]
            for direction in DIRECTIONS:
                tmpl = DM_TEMPLATES[direction]["_template"]
                for tier in TIERS:
                    if (qid, tier, direction) in done:
                        continue
                    persona = personas[tier]
                    persona_cap = persona[0].upper() + persona[1:]  # "a Nobel..." -> "A Nobel..."
                    slot = q["wrong_X"] if direction == "incorrect_endorsement" else q["correct_text"]
                    authority_text = tmpl.replace("{persona_cap}", persona_cap).replace(
                        "{wrong_X}", slot).replace("{correct_text}", slot)
                    t2p = build_turn2_prompt(tok, q["question"], q["choices"], g["turn1_response"], authority_text)
                    resp, lps = gen_gpu(model, tok, t2p)
                    t2l = extract_letter(resp)
                    flipped = (t2l != g["turn1_letter"]) if t2l else None
                    rec = {"model": model_id, "question_id": qid, "domain": domain,
                           "gate_status": "PASS", "turn1_letter": g["turn1_letter"],
                           "turn1_response": g["turn1_response"], "turn1_logprobs": g["turn1_logprobs"],
                           "correct_letter": g["correct_letter"], "wrong_X_letter": g["wrong_X_letter"],
                           "tier": tier, "direction": direction, "persona": persona,
                           "authority_text": authority_text, "turn2_letter": t2l,
                           "turn2_response": resp, "turn2_logprobs": lps, "flipped": flipped,
                           "ts": ts, "condition": "domain_matched"}
                    fout.write(json.dumps(rec) + "\n"); fout.flush()
            if (i + 1) % 20 == 0:
                log(f"  {i+1}/{len(gate)} questions")
    log(f"[done] {out_path}")


if __name__ == "__main__":
    run(MODEL_ID)
