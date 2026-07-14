#!/usr/bin/env python3
"""paper_numbers.py — THE numbers source for the IEEE Access manuscript.
Recomputes every quantitative claim from raw JSONL (hash-frozen files). Pure Python
(no numpy/scipy — runs anywhere). Emits results/paper_numbers.json + results/PAPER_NUMBERS.md.

Filters (match fab_inference.md): gate_status==PASS (from two-turn main run), dedup by
(question_id, tier, direction) keeping FIRST record. Two-turn caving = flipped flag
(== turn2_letter != turn1_letter, verified ⟺ not-correct under the gate). Single-turn
caving (loose) = not is_correct; strict adopted-X: 2T turn2_letter==wrong_X_letter, 1T caved_to_X.
"""
import json, glob, math, os
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda p: os.path.join(REPO, p)
TIERS4 = ["anon", "low", "medium", "high"]
TIERS5 = ["control"] + TIERS4
TMAP = {t: i for i, t in enumerate(TIERS4)}


def short(m):
    m = m.split("/")[-1]
    return (m.replace("Qwen2.5-", "Qwen").replace("-Instruct", "").replace("Llama-3.2-", "Llama")
            .replace("Mistral-7B", "Mistral").replace("Phi-3.5-mini", "Phi")
            .replace("gemma-2-9b-it", "Gemma").replace("-v0.3", "").replace("-it", ""))


def load_dedup(files, keyfn):
    seen, out = set(), []
    for f in files:
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = keyfn(r)
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
    return out


def gate(r):
    return r.get("gate_status") or r.get("status")


# ---------- math utils (pure python) ----------
def erf(x):
    t = 1 / (1 + 0.3275911 * abs(x))
    y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * math.exp(-x * x)
    return math.copysign(y, x)


def norm_sf(z):
    return 0.5 * (1 - erf(z / math.sqrt(2)))


def two_sided_p(z):
    return 2 * norm_sf(abs(z))


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return p, (c - h) / d, (c + h) / d


def lchoose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def mcnemar_exact(b10, b01):
    """Two-sided exact binomial McNemar on discordant pairs."""
    b = b10 + b01
    if b == 0:
        return 1.0
    m = min(b10, b01)
    cdf = sum(math.exp(lchoose(b, k) - b * math.log(2)) for k in range(m + 1))
    return min(1.0, 2 * cdf)


def gammaincc(a, x):
    """Regularized upper incomplete gamma Q(a,x). NR-style series/CF."""
    if x < 0 or a <= 0:
        return float("nan")
    if x == 0:
        return 1.0
    if x < a + 1:
        # series for P, return 1-P
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(500):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-14:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for Q
    tiny = 1e-300
    b, c, d, h = x + 1 - a, 1 / tiny, 1 / (x + 1 - a), 1 / (x + 1 - a)
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(x, df):
    return gammaincc(df / 2.0, x / 2.0)


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None, None
    def rk(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[s[j + 1]] == v[s[i]]:
                j += 1
            a = (i + j) / 2 + 1
            for t in range(i, j + 1):
                r[s[t]] = a
            i = j + 1
        return r
    rx, ry = rk(xs), rk(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((v - mx) ** 2 for v in rx))
    dy = math.sqrt(sum((v - my) ** 2 for v in ry))
    if not dx or not dy:
        return None, None
    rho = num / (dx * dy)
    t = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho * rho))
    # t ~ approx normal for our n (>=hundreds)
    return rho, two_sided_p(t)


def cochran_armitage(counts):
    """counts: list of (successes, n) per ordered tier (scores 0..k-1). Returns z, p."""
    scores = list(range(len(counts)))
    N = sum(n for _, n in counts)
    S = sum(r for r, _ in counts)
    if N == 0 or S == 0 or S == N:
        return 0.0, 1.0
    pbar = S / N
    sbar = sum(s * n for s, (_, n) in zip(scores, counts)) / N
    num = sum(r * (s - sbar) for s, (r, _) in zip(scores, counts))
    var = pbar * (1 - pbar) * sum(n * (s - sbar) ** 2 for s, (_, n) in zip(scores, counts))
    if var <= 0:
        return 0.0, 1.0
    z = num / math.sqrt(var)
    return z, two_sided_p(z)


def logistic_fit(rows, k):
    """Newton-Raphson logistic. rows=[(xvec,y)]. Returns beta, cov, loglik."""
    beta = [0.0] * k
    def sig(z):
        return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
    for _ in range(100):
        g = [0.0] * k
        H = [[0.0] * k for _ in range(k)]
        for x, y in rows:
            p = sig(sum(beta[j] * x[j] for j in range(k)))
            w = p * (1 - p)
            for a in range(k):
                g[a] += (y - p) * x[a]
                for b in range(k):
                    H[a][b] -= w * x[a] * x[b]
        A = [[-H[i][j] for j in range(k)] + [g[i]] for i in range(k)]
        for i in range(k):
            piv = A[i][i]
            if abs(piv) < 1e-12:
                return None, None, None
            for j in range(i, k + 1):
                A[i][j] /= piv
            for r2 in range(k):
                if r2 != i:
                    f = A[r2][i]
                    for j in range(i, k + 1):
                        A[r2][j] -= f * A[i][j]
        dl = [A[i][k] for i in range(k)]
        for i in range(k):
            beta[i] += dl[i]
        if max(abs(d) for d in dl) < 1e-10:
            break
    # covariance + loglik
    H = [[0.0] * k for _ in range(k)]
    ll = 0.0
    for x, y in rows:
        z = sum(beta[j] * x[j] for j in range(k))
        p = sig(z)
        p = min(max(p, 1e-12), 1 - 1e-12)
        ll += y * math.log(p) + (1 - y) * math.log(1 - p)
        w = p * (1 - p)
        for a in range(k):
            for b in range(k):
                H[a][b] -= w * x[a] * x[b]
    M = [[-H[i][j] for j in range(k)] for i in range(k)]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    for i in range(k):
        piv = M[i][i]
        for j in range(k):
            M[i][j] /= piv
            I[i][j] /= piv
        for r2 in range(k):
            if r2 != i:
                f = M[r2][i]
                for j in range(k):
                    M[r2][j] -= f * M[i][j]
                    I[r2][j] -= f * I[i][j]
    return beta, I, ll


def bh(pvals):
    """Benjamini-Hochberg adjusted q-values. pvals: dict label->p. Returns label->q."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    qs = {}
    prev = 1.0
    for rank in range(m, 0, -1):
        label, p = items[rank - 1]
        q = min(prev, p * m / rank)
        qs[label] = q
        prev = q
    return qs


# ---------- load ----------
key3 = lambda r: (short(r["model"]), r["question_id"], r.get("tier"), r.get("direction"))
MAIN = load_dedup(sorted(glob.glob(R("results/inference/*_2026*.jsonl"))), key3)
ANON = load_dedup(sorted(glob.glob(R("results/inference/*__anonB.jsonl"))), key3)
ST = load_dedup(sorted(glob.glob(R("results/inference/*_singleturn.jsonl"))), key3)
DM = load_dedup(sorted(glob.glob(R("results/inference/*_domainmatched.jsonl"))), key3)
JUDGED = load_dedup(sorted(glob.glob(R("judge_bundle/results/judged/*__judge1.jsonl"))), key3)

two = defaultdict(list)
for r in MAIN + ANON:
    two[short(r["model"])].append(r)
st = defaultdict(list)
for r in ST:
    st[short(r["model"])].append(r)
dm = defaultdict(list)
for r in DM:
    dm[short(r["model"])].append(r)
MODELS = sorted(two)
gatepass = {m: {r["question_id"] for r in two[m] if gate(r) == "PASS"} for m in MODELS}
domain_of = {}
for r in MAIN:
    domain_of[(short(r["model"]), r["question_id"])] = r.get("domain")

OUT = {"_meta": {"generated": "2026-07-14", "script": "src/paper_numbers.py",
                 "records": {"main": len(MAIN), "anonB": len(ANON), "singleturn": len(ST),
                             "domainmatched": len(DM), "judged": len(JUDGED)}}}

def sub2(m, tier, direction):
    return [r for r in two[m] if r.get("tier") == tier and r.get("direction") == direction
            and gate(r) == "PASS"]

# 1. gate survival
OUT["gate"] = {m: {"pass": len(gatepass[m]), "total": len({r["question_id"] for r in two[m]})}
               for m in MODELS}

# 2-3. flip tables both arms, Wilson CIs
for arm, key in [("incorrect_endorsement", "flip_incorrect"), ("correct_endorsement", "flip_correct")]:
    T = {}
    for m in MODELS:
        row = {}
        an = ad = 0
        for t in TIERS5:
            s = sub2(m, t, arm)
            k = sum(1 for r in s if r.get("flipped"))
            p, lo, hi = wilson(k, len(s))
            row[t] = {"k": k, "n": len(s), "pct": round(100 * p, 1),
                      "ci": [round(100 * lo, 1), round(100 * hi, 1)]}
            if t != "control":
                an += k; ad += len(s)
        row["overall_4tier"] = {"k": an, "n": ad, "pct": round(100 * an / ad, 1) if ad else None}
        T[m] = row
    OUT[key] = T

# 4. pooled logistic flip ~ tier*dir (anon..high, both arms)
rows = []
for m in MODELS:
    for r in two[m]:
        if gate(r) != "PASS" or r.get("tier") not in TMAP:
            continue
        d = r.get("direction")
        dv = 1.0 if d == "incorrect_endorsement" else (0.0 if d == "correct_endorsement" else None)
        if dv is None:
            continue
        t = float(TMAP[r["tier"]])
        rows.append(([1.0, t, dv, t * dv], 1.0 if r.get("flipped") else 0.0))
beta, cov, _ = logistic_fit(rows, 4)
ses = [math.sqrt(cov[i][i]) for i in range(4)]
OUT["pooled_tier_dir"] = {"n": len(rows),
    "terms": {nm: {"coef": round(beta[i], 4), "se": round(ses[i], 4),
                   "p": two_sided_p(beta[i] / ses[i])}
              for i, nm in enumerate(["intercept", "tier", "dir_incorrect", "tier_x_dir"])}}

# 5. commitment penalty: paired McNemar per model (2T flip vs 1T caving, same (q,tier), incorrect)
def st_index(m):
    idx = {}
    for r in st[m]:
        if r.get("direction") == "incorrect_endorsement" and r.get("tier") in TMAP \
           and r["question_id"] in gatepass[m]:
            idx[(r["question_id"], r["tier"])] = r
    return idx

CP = {}
for m in MODELS:
    sidx = st_index(m)
    b10 = b01 = both = neither = 0
    n2 = k2 = n1 = k1 = 0
    ax2 = ax1 = 0  # strict adopted-X
    for r in two[m]:
        if r.get("direction") != "incorrect_endorsement" or r.get("tier") not in TMAP \
           or gate(r) != "PASS":
            continue
        s = sidx.get((r["question_id"], r["tier"]))
        if s is None:
            continue
        f2 = bool(r.get("flipped"))
        f1 = not s.get("is_correct")
        n2 += 1; k2 += f2; n1 += 1; k1 += f1
        ax2 += (r.get("turn2_letter") == r.get("wrong_X_letter"))
        ax1 += bool(s.get("caved_to_X"))
        if f2 and not f1: b10 += 1
        elif f1 and not f2: b01 += 1
        elif f2 and f1: both += 1
        else: neither += 1
    p = mcnemar_exact(b10, b01)
    CP[m] = {"n_pairs": n2, "two_turn_pct": round(100 * k2 / n2, 1), "one_turn_pct": round(100 * k1 / n1, 1),
             "amplification": round((k2 / n2) / (k1 / n1), 1) if k1 else None,
             "b10": b10, "b01": b01, "mcnemar_p": p,
             "adoptedX_2T_pct": round(100 * ax2 / n2, 1), "adoptedX_1T_pct": round(100 * ax1 / n1, 1),
             "adoptedX_share_of_1T_errors": round(100 * ax1 / k1, 1) if k1 else None}
OUT["commitment_penalty"] = CP

# 6. anon-vs-high McNemar (two-turn, incorrect), paired by question
AH = {}
for m in MODELS:
    a = {r["question_id"]: bool(r.get("flipped")) for r in sub2(m, "anon", "incorrect_endorsement")}
    h = {r["question_id"]: bool(r.get("flipped")) for r in sub2(m, "high", "incorrect_endorsement")}
    common = sorted(set(a) & set(h))
    b10 = sum(1 for q in common if a[q] and not h[q])   # anon flips, high doesn't
    b01 = sum(1 for q in common if h[q] and not a[q])
    pa = sum(a[q] for q in common) / len(common)
    ph = sum(h[q] for q in common) / len(common)
    AH[m] = {"n_pairs": len(common), "anon_pct": round(100 * pa, 1), "high_pct": round(100 * ph, 1),
             "diff_pp": round(100 * (ph - pa), 1), "b10_anonOnly": b10, "b01_highOnly": b01,
             "mcnemar_p": mcnemar_exact(b10, b01)}
OUT["anon_vs_high"] = AH

# 7. single-turn: pooled raw by tier; per-model CA; pooled FE logit trend
strows = []
st_tier_pool = {t: [0, 0] for t in TIERS4}
ST_CA = {}
for mi, m in enumerate(MODELS):
    counts = []
    for t in TIERS4:
        s = [r for r in st[m] if r.get("tier") == t and r.get("direction") == "incorrect_endorsement"
             and r["question_id"] in gatepass[m]]
        k = sum(1 for r in s if not r.get("is_correct"))
        counts.append((k, len(s)))
        st_tier_pool[t][0] += k
        st_tier_pool[t][1] += len(s)
        for r in s:
            x = [1.0, float(TMAP[t])] + [1.0 if m == mm else 0.0 for mm in MODELS[1:]]
            strows.append((x, 0.0 if r.get("is_correct") else 1.0))
    z, p = cochran_armitage(counts)
    ST_CA[m] = {"z": round(z, 2), "p": p,
                "caving_by_tier_pct": [round(100 * k / n, 1) if n else None for k, n in counts]}
OUT["singleturn_per_model_CA"] = ST_CA
OUT["singleturn_pooled_raw_pct"] = {t: round(100 * v[0] / v[1], 1) for t, v in st_tier_pool.items()}
kfe = 2 + len(MODELS) - 1
b_fe, cov_fe, _ = logistic_fit(strows, kfe)
se_fe = math.sqrt(cov_fe[1][1])
OUT["singleturn_pooled_FE_trend"] = {"n": len(strows), "tier_coef": round(b_fe[1], 4),
                                     "se": round(se_fe, 4), "p": two_sided_p(b_fe[1] / se_fe)}

# 8. two-turn CA both codings per model (incorrect arm)
CA2 = {}
for m in MODELS:
    out = {}
    for coding, tiers in [("anon_inclusive", TIERS4), ("persona_only", ["low", "medium", "high"])]:
        counts = []
        for t in tiers:
            s = sub2(m, t, "incorrect_endorsement")
            counts.append((sum(1 for r in s if r.get("flipped")), len(s)))
        z, p = cochran_armitage(counts)
        out[coding] = {"z": round(z, 2), "p": p}
    CA2[m] = out
OUT["two_turn_CA"] = CA2

# 9. confidence-doesn't-protect: turn-1 belief gap quintiles (pooled, incorrect arm, anon..high)
def bg(lp, c, w):
    return None if (not lp or c not in lp or w not in lp) else lp[c] - lp[w]

pool = []
for m in MODELS:
    for r in two[m]:
        if r.get("direction") != "incorrect_endorsement" or r.get("tier") not in TMAP \
           or gate(r) != "PASS":
            continue
        g = bg(r.get("turn1_logprobs"), r["correct_letter"], r["wrong_X_letter"])
        if g is None:
            continue
        pool.append((g, 1.0 if r.get("flipped") else 0.0))
pool.sort(key=lambda t: t[0])
n5 = len(pool) // 5
quint = []
for i in range(5):
    seg = pool[i * n5:(i + 1) * n5] if i < 4 else pool[4 * n5:]
    k = sum(y for _, y in seg)
    quint.append({"q": i + 1, "n": len(seg), "flip_pct": round(100 * k / len(seg), 1),
                  "gap_range": [round(seg[0][0], 1), round(seg[-1][0], 1)]})
b_c, cov_c, _ = logistic_fit([([1.0, g], y) for g, y in pool], 2)
se_c = math.sqrt(cov_c[1][1])
OUT["confidence_quintiles"] = {"pooled_n": len(pool), "quintiles": quint,
    "logistic_slope_per_logit": {"coef": round(b_c[1], 5), "se": round(se_c, 5),
                                 "p": two_sided_p(b_c[1] / se_c)}}

# 10. domain-matched: Spearman per model (belief, low/med/high, incorrect) + behavioral compare
tm3 = {"low": 0, "medium": 1, "high": 2}
DMS = {}
for m in sorted(dm):
    xs, ys = [], []
    beh = {}
    for t in ["low", "medium", "high"]:
        s = [r for r in dm[m] if r.get("tier") == t and r.get("direction") == "incorrect_endorsement"
             and gate(r) == "PASS"]
        beh[t] = {"flip_pct": round(100 * sum(1 for r in s if r.get("flipped")) / len(s), 1) if s else None,
                  "n": len(s)}
        for r in s:
            v = bg(r.get("turn2_logprobs"), r["correct_letter"], r["wrong_X_letter"])
            if v is not None:
                xs.append(tm3[t]); ys.append(v)
    rho, p = spearman(xs, ys)
    DMS[m] = {"belief_spearman_rho": round(rho, 3), "p": p, "behavioral": beh}
OUT["domain_matched"] = DMS

# 11. delta-entropy (turn2 - turn1), incorrect arm, per model x tier (renormalized A-D)
def entropy(lp):
    if not lp:
        return None
    vals = [lp[c] for c in "ABCD" if c in lp]
    if len(vals) < 2:
        return None
    mx = max(vals)
    ps = [math.exp(v - mx) for v in vals]
    s = sum(ps)
    ps = [p / s for p in ps]
    return -sum(p * math.log(p) for p in ps if p > 0)

DH = {}
for m in MODELS:
    row = {}
    for t in TIERS4:
        ds = []
        for r in sub2(m, t, "incorrect_endorsement"):
            h1, h2 = entropy(r.get("turn1_logprobs")), entropy(r.get("turn2_logprobs"))
            if h1 is not None and h2 is not None:
                ds.append(h2 - h1)
        row[t] = round(sum(ds) / len(ds), 3) if ds else None
    DH[m] = row
OUT["delta_entropy"] = DH

# 12. judge agreement + kappa
idx = {key3(r): r for r in MAIN}
ag = tot = 0
for r in JUDGED:
    mrec = idx.get(key3(r))
    if not mrec:
        continue
    c = r.get("judge_turn2_class")
    if c in (None, "ERROR"):
        continue
    tot += 1
    ag += ((mrec.get("turn2_letter") != mrec.get("correct_letter")) == (c != "correct"))
OUT["judge"] = {"regex_agreement_pct": round(100 * ag / tot, 2), "n": tot,
                "kappa_conservative": 0.967, "kappa_excl_api_error": 1.0,
                "note": "kappa from n=60 human validation (judge_bundle/results/human_validation); "
                        "conservative counts the 1 judge API ERROR as disagreement"}

# 13. E-family + BH
E = {}
for m in MODELS:  # E1 persona-only (pre-reg ladder minus control; anon post-hoc -> sensitivity)
    E[f"E1_CA_{m}"] = CA2[m]["persona_only"]["p"]
# E2: 3-way tier x dir x domain LRT (2 df)
rows_full, rows_red = [], []
doms = sorted({d for d in domain_of.values() if d})
d1, d2 = doms[1], doms[2]
for m in MODELS:
    for r in two[m]:
        if gate(r) != "PASS" or r.get("tier") not in TMAP:
            continue
        d = r.get("direction")
        dv = 1.0 if d == "incorrect_endorsement" else (0.0 if d == "correct_endorsement" else None)
        if dv is None:
            continue
        t = float(TMAP[r["tier"]])
        dom = domain_of.get((m, r["question_id"]))
        i1, i2 = 1.0 * (dom == d1), 1.0 * (dom == d2)
        y = 1.0 if r.get("flipped") else 0.0
        base = [1.0, t, dv, t * dv, i1, i2, t * i1, t * i2, dv * i1, dv * i2]
        rows_red.append((base, y))
        rows_full.append((base + [t * dv * i1, t * dv * i2], y))
_, _, ll_f = logistic_fit(rows_full, 12)
_, _, ll_r = logistic_fit(rows_red, 10)
lrt = 2 * (ll_f - ll_r)
E["E2_domain_3way_LRT"] = chi2_sf(lrt, 2)
OUT["E2_detail"] = {"lrt_chi2": round(lrt, 2), "df": 2, "domains": doms}
# E4: pairwise model McNemar on shared gated items (overall incorrect-arm flip across anon..high)
flipmap = {m: {} for m in MODELS}
for m in MODELS:
    for r in two[m]:
        if r.get("direction") == "incorrect_endorsement" and r.get("tier") in TMAP and gate(r) == "PASS":
            flipmap[m][(r["question_id"], r["tier"])] = bool(r.get("flipped"))
for i in range(len(MODELS)):
    for j in range(i + 1, len(MODELS)):
        a, b = MODELS[i], MODELS[j]
        common = set(flipmap[a]) & set(flipmap[b])
        b10 = sum(1 for k in common if flipmap[a][k] and not flipmap[b][k])
        b01 = sum(1 for k in common if flipmap[b][k] and not flipmap[a][k])
        E[f"E4_{a}_vs_{b}"] = mcnemar_exact(b10, b01)
# E5: Kruskal-Wallis across models on flip (incorrect arm) — with ties correction
groups = []
for m in MODELS:
    groups.append([1.0 if r.get("flipped") else 0.0 for r in two[m]
                   if r.get("direction") == "incorrect_endorsement" and r.get("tier") in TMAP
                   and gate(r) == "PASS"])
allv = [(v, gi) for gi, g in enumerate(groups) for v in g]
allv.sort()
N = len(allv)
ranks = [0.0] * N
i = 0
while i < N:
    j = i
    while j + 1 < N and allv[j + 1][0] == allv[i][0]:
        j += 1
    rk_ = (i + j) / 2 + 1
    for t in range(i, j + 1):
        ranks[t] = rk_
    i = j + 1
rsum = defaultdict(float)
for (v, gi), rk_ in zip(allv, ranks):
    rsum[gi] += rk_
H = 12 / (N * (N + 1)) * sum(rsum[gi] ** 2 / len(groups[gi]) for gi in range(len(groups))) - 3 * (N + 1)
# ties correction
tie_term = 0
i = 0
while i < N:
    j = i
    while j + 1 < N and allv[j + 1][0] == allv[i][0]:
        j += 1
    tt = j - i + 1
    tie_term += tt ** 3 - tt
    i = j + 1
H /= (1 - tie_term / (N ** 3 - N))
E["E5_KruskalWallis"] = chi2_sf(H, len(groups) - 1)
OUT["E5_detail"] = {"H": round(H, 1), "df": len(groups) - 1}

qs = bh(E)
OUT["E_family_BH"] = {k: {"p": E[k], "q": qs[k], "sig_at_q05": qs[k] < 0.05} for k in sorted(E)}

# post-hoc McNemar family (commitment + anon-high), separate BH
PH = {}
for m in MODELS:
    PH[f"commitment_{m}"] = CP[m]["mcnemar_p"]
    PH[f"anon_vs_high_{m}"] = AH[m]["mcnemar_p"]
qs2 = bh(PH)
OUT["posthoc_mcnemar_BH"] = {k: {"p": PH[k], "q": qs2[k], "sig_at_q05": qs2[k] < 0.05} for k in sorted(PH)}

# sensitivity: E1 anon-inclusive coding BH'd within its own sensitivity family
SENS = {f"E1sens_CAanon_{m}": CA2[m]["anon_inclusive"]["p"] for m in MODELS}
qs3 = bh(SENS)
OUT["E1_sensitivity_anon_inclusive_BH"] = {k: {"p": SENS[k], "q": qs3[k]} for k in sorted(SENS)}

# ---------- write ----------
os.makedirs(R("results"), exist_ok=True)
with open(R("results/paper_numbers.json"), "w") as f:
    json.dump(OUT, f, indent=1, default=float)

def fmt_p(p):
    if p is None:
        return "n/a"
    if p < 1e-15:
        return "<1e-15"
    if p < 1e-4:
        return f"{p:.1e}"
    return f"{p:.4f}"

L = ["# PAPER_NUMBERS — canonical manuscript numbers (generated by src/paper_numbers.py)", ""]
L.append("## Gate survival")
for m in MODELS:
    g = OUT["gate"][m]
    L.append(f"- {m}: {g['pass']}/{g['total']} = {100*g['pass']/g['total']:.1f}%")
L.append("\n## Two-turn flip% (incorrect arm) control/anon/low/med/high [Wilson 95% CI]")
for m in MODELS:
    r = OUT["flip_incorrect"][m]
    cells = " | ".join(f"{t}:{r[t]['pct']}% [{r[t]['ci'][0]},{r[t]['ci'][1]}] (n={r[t]['n']})" for t in TIERS5)
    L.append(f"- {m}: {cells} | overall(anon..high)={r['overall_4tier']['pct']}%")
L.append("\n## Two-turn flip% (correct arm) overall anon..high")
for m in MODELS:
    r = OUT["flip_correct"][m]
    L.append(f"- {m}: {r['overall_4tier']['pct']}% (n={r['overall_4tier']['n']})")
L.append("\n## Pooled logistic flip ~ tier*dir (anon..high, both arms)")
for nm, d in OUT["pooled_tier_dir"]["terms"].items():
    L.append(f"- {nm}: coef={d['coef']} se={d['se']} p={fmt_p(d['p'])}")
L.append(f"- n={OUT['pooled_tier_dir']['n']} (naive SE; cluster-robust widens; interaction ns under all)")
L.append("\n## COMMITMENT PENALTY (paired McNemar, 2T flip vs 1T caving, incorrect arm)")
for m in MODELS:
    c = CP[m]
    L.append(f"- {m}: 2T={c['two_turn_pct']}% 1T={c['one_turn_pct']}% amplif={c['amplification']}x "
             f"b10:b01={c['b10']}:{c['b01']} p={fmt_p(c['mcnemar_p'])} | adopted-X 2T={c['adoptedX_2T_pct']}% "
             f"1T={c['adoptedX_1T_pct']}% (share of 1T errors adopting X: {c['adoptedX_share_of_1T_errors']}%)")
L.append("\n## ANON vs HIGH (paired McNemar, two-turn incorrect)")
for m in MODELS:
    a = AH[m]
    L.append(f"- {m}: anon={a['anon_pct']}% high={a['high_pct']}% diff={a['diff_pp']:+}pp "
             f"b(anonOnly:highOnly)={a['b10_anonOnly']}:{a['b01_highOnly']} p={fmt_p(a['mcnemar_p'])}")
L.append("\n## Single-turn")
L.append(f"- pooled raw caving by tier: " + " ".join(f"{t}={OUT['singleturn_pooled_raw_pct'][t]}%" for t in TIERS4))
f_ = OUT["singleturn_pooled_FE_trend"]
L.append(f"- pooled FE logit tier trend: coef={f_['tier_coef']} se={f_['se']} p={fmt_p(f_['p'])} (n={f_['n']})")
for m in MODELS:
    s = ST_CA[m]
    L.append(f"- {m} per-model CA: z={s['z']} p={fmt_p(s['p'])} caving={s['caving_by_tier_pct']}")
L.append("\n## Two-turn CA trend (incorrect arm)")
for m in MODELS:
    c = CA2[m]
    L.append(f"- {m}: anon-incl z={c['anon_inclusive']['z']} p={fmt_p(c['anon_inclusive']['p'])} | "
             f"persona-only z={c['persona_only']['z']} p={fmt_p(c['persona_only']['p'])}")
L.append("\n## Confidence-doesn't-protect (turn-1 belief-gap quintiles, pooled incorrect arm)")
for q in OUT["confidence_quintiles"]["quintiles"]:
    L.append(f"- Q{q['q']}: flip={q['flip_pct']}% (n={q['n']}, gap {q['gap_range'][0]}..{q['gap_range'][1]})")
s = OUT["confidence_quintiles"]["logistic_slope_per_logit"]
L.append(f"- pooled logistic slope on turn-1 gap: {s['coef']} (se {s['se']}, p={fmt_p(s['p'])})")
L.append("\n## Domain-matched (institutional personas)")
for m in sorted(DMS):
    d = DMS[m]
    b = d["behavioral"]
    L.append(f"- {m}: belief Spearman rho={d['belief_spearman_rho']} p={fmt_p(d['p'])} | behavioral "
             + " ".join(f"{t}={b[t]['flip_pct']}%" for t in ['low', 'medium', 'high']))
L.append("\n## Delta-entropy (turn2-turn1, incorrect arm; positive = LESS certain)")
for m in MODELS:
    L.append(f"- {m}: " + " ".join(f"{t}={DH[m][t]:+.3f}" for t in TIERS4))
L.append("\n## Judge")
j = OUT["judge"]
L.append(f"- regex agreement {j['regex_agreement_pct']}% (n={j['n']}); kappa {j['kappa_conservative']} "
         f"conservative / {j['kappa_excl_api_error']} excluding the API-error row (n=60, main run ONLY)")
L.append("\n## E-family (pre-registered exploratory) with BH q-values")
for k, v in sorted(OUT["E_family_BH"].items()):
    L.append(f"- {k}: p={fmt_p(v['p'])} q={fmt_p(v['q'])}{' *' if v['sig_at_q05'] else ''}")
L.append("\n## Post-hoc McNemar family (commitment + anon-vs-high) with BH q-values")
for k, v in sorted(OUT["posthoc_mcnemar_BH"].items()):
    L.append(f"- {k}: p={fmt_p(v['p'])} q={fmt_p(v['q'])}{' *' if v['sig_at_q05'] else ''}")
L.append("\n## E1 sensitivity (anon-inclusive coding) BH within sensitivity family")
for k, v in sorted(OUT["E1_sensitivity_anon_inclusive_BH"].items()):
    L.append(f"- {k}: p={fmt_p(v['p'])} q={fmt_p(v['q'])}")

with open(R("results/PAPER_NUMBERS.md"), "w") as f:
    f.write("\n".join(L) + "\n")
print("\n".join(L))
