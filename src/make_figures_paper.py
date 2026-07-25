#!/usr/bin/env python3
"""make_figures_paper.py — regenerate every DATA figure in the manuscript from ONE source.

All numbers are read from results/paper_numbers.json (produced by src/paper_numbers.py),
the same file that drives the manuscript text and tables — so figures cannot drift from prose.

Figures produced (paper order in access.tex):
  fig10  commitment penalty   (headline): 1T vs 2T caving per model + amplification
  fig1   pre-registered null : pooled accuracy-retained by rung x direction, Wilson CIs
  fig8   direction asymmetry  : per-model regressive (incorrect) vs progressive (correct)
  fig2   authority ladders    : per-model 2T flip by rung (anon-high) + 1st-person control
  fig11  confidence           : 2T flip by pre-pressure belief-margin quintile, Wilson CIs
  fig3   persona A/B          : per-model generic vs domain-matched institutional ladders

NOT produced here: fig9_design_schematic.png is an author-supplied figure (do NOT overwrite it).

Design choices (2026-07-17 polish pass):
  * Drawn at final display size (single col ~3.5in, double col ~7.1in) so fonts are not
    shrunk by LaTeX downscaling — the main reason the earlier PNGs read small.
  * One consistent palette used across all figures (see COLORS below).
  * No redundant sentence-titles baked into the image (IEEE prefers caption-only titling);
    only concise DATA annotations remain on the figure.
  * Wilson 95% intervals wherever the caption promises them.

Run: .venv-figs/bin/python src/make_figures_paper.py
"""
import json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUM = json.load(open(os.path.join(REPO, "results/paper_numbers.json")))
FIGDIR = os.path.join(REPO, "paper/figures")   # the path access.tex \includegraphics reads
os.makedirs(FIGDIR, exist_ok=True)

MODELS = ["Qwen3B", "Llama3B", "Phi-instruct", "Mistral", "Qwen7B", "Gemma"]
LABEL = {"Qwen3B": "Qwen2.5-3B", "Llama3B": "Llama-3.2-3B", "Phi-instruct": "Phi-3.5-mini",
         "Mistral": "Mistral-7B", "Qwen7B": "Qwen2.5-7B", "Gemma": "Gemma-2-9B"}
RUNGS = ["anon", "low", "medium", "high"]
RLAB = ["anon", "high-\nschooler", "grad", "prof."]

# ---- one consistent palette ------------------------------------------------
C_CAVE   = "#c0392b"   # caving-inducing condition: incorrect / regressive / two-turn / commitment
C_BENIGN = "#2c6e9c"   # baseline: correct / progressive / single-turn
C_CTRL   = "#6a51a3"   # first-person control rung (separate, format-mismatched manipulation)
C_GEN    = "#2c6e9c"   # fig3 generic personas
C_DOM    = "#d98c2b"   # fig3 domain-matched personas
GRID     = "#d9d9d9"

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,   # embed TrueType (avoids Type-3 flags in IEEE PDF eXpress)
    "ps.fonttype": 42,
})


def wilson(k, n, z=1.959964):
    """Return (pct, err_low_pp, err_high_pp) — identical formula to src/paper_numbers.py."""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    lo, hi = max(0.0, c - h), min(1.0, c + h)
    return 100 * p, 100 * (p - lo), 100 * (hi - p)


def save(fig, name, pad_inches=None):
    kw = {} if pad_inches is None else dict(bbox_inches="tight", pad_inches=pad_inches)
    png = os.path.join(FIGDIR, name)
    fig.savefig(png, **kw)                    # raster preview
    fig.savefig(png[:-4] + ".pdf", **kw)      # vector, for IEEE pdflatex submission
    fig.savefig(png[:-4] + ".svg", **kw)      # vector, editable (not pdflatex-embeddable directly)
    plt.close(fig)
    print("wrote", os.path.relpath(png, REPO), "(+ .pdf, .svg)")


# ================= fig10: commitment penalty (headline, single column) =======
def fig10():
    CP = NUM["commitment_penalty"]
    fig, ax = plt.subplots(figsize=(3.5, 3.35))
    xs = list(range(len(MODELS)))
    w = 0.40
    one = [CP[m]["one_turn_pct"] for m in MODELS]
    two = [CP[m]["two_turn_pct"] for m in MODELS]
    ax.bar([x - w / 2 for x in xs], one, w, label="single-turn (no commitment)",
           color=C_BENIGN, ec="black", lw=0.4)
    ax.bar([x + w / 2 for x in xs], two, w, label="two-turn (after self-commitment)",
           color=C_CAVE, ec="black", lw=0.4)
    for x, m in zip(xs, MODELS):
        ax.annotate(f"×{CP[m]['amplification']:.1f}", (x + w / 2, two[x] + 1.5),
                    ha="center", va="bottom", fontsize=8.5, weight="bold", color=C_CAVE)
        ax.annotate(f"{one[x]:.1f}", (x - w / 2, one[x] + 1.5),  # single-turn value labels
                    ha="center", va="bottom", fontsize=5.6, color=C_BENIGN)
    # direct headline call-out on the most structure-sensitive model, to the RIGHT of its bar
    # (uses the headroom above 100 opened up by the extended y-axis)
    qi = MODELS.index("Qwen7B")
    ax.set_xlim(-0.55, 6.2)  # right margin to hold the call-out beside the tall bar
    ax.annotate("434:0\ndiscordant pairs\n(0 reverse)", (qi + w / 2 + 0.03, 93),
                xytext=(5.55, 74), fontsize=6.5, ha="center", va="center", color="black",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="black"))
    ax.set_xticks(xs)
    ax.set_xticklabels([LABEL[m] for m in MODELS], rotation=35, ha="right", fontsize=7.2)
    ax.set_ylabel("caving rate, incorrect arm (%)")
    ax.set_ylim(0, 120)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=1, frameon=False,
              handlelength=1.3, fontsize=7.6)
    save(fig, "fig10_commitment_penalty.png")


# ================= fig1: the pre-registered null (single column) =============
def fig1():
    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    xs = list(range(len(RUNGS)))
    series = [("flip_incorrect", "incorrect endorsement", C_CAVE, "o"),
              ("flip_correct",   "correct endorsement",   C_BENIGN, "s")]
    retained = {}
    for key, lab, col, mk in series:
        D = NUM[key]
        ys, elo, ehi = [], [], []
        for rung in RUNGS:
            kept = sum(D[m][rung]["n"] - D[m][rung]["k"] for m in MODELS)  # retained = not flipped
            tot = sum(D[m][rung]["n"] for m in MODELS)
            p, lo, hi = wilson(kept, tot)
            ys.append(p); elo.append(lo); ehi.append(hi)
        retained[key] = ys
        ax.errorbar(xs, ys, yerr=[elo, ehi], marker=mk, capsize=2.5, lw=1.6, ms=4.5,
                    color=col, label=lab)
    # direct annotation: the direction gap dwarfs the (flat) tier structure
    gtop, gbot = retained["flip_correct"][0], retained["flip_incorrect"][0]
    ax.annotate("", (0, gtop), (0, gbot),
                arrowprops=dict(arrowstyle="<->", lw=1.1, color="#555555"))
    ax.text(0.12, (gtop + gbot) / 2, "direction\ngap", fontsize=7.2, va="center", color="#555555")
    ax.set_xticks(xs); ax.set_xticklabels(RLAB, fontsize=7.5)
    ax.set_xlabel("authority rung")
    ax.set_ylabel("accuracy retained after pushback (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower right", frameon=False, fontsize=7.6)
    ax.text(1.6, 64, "tier$\\times$direction interaction\n$\\beta=+0.010$, $p=0.90$\n95% CI $[-0.14,+0.16]$",
            fontsize=6.0, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbbbbb", lw=0.6))
    save(fig, "fig1_interaction_null.png")


# ================= fig8: direction asymmetry (single column) =================
def fig8():
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    xs = list(range(len(MODELS)))
    w = 0.40
    reg = [NUM["flip_incorrect"][m]["overall_4tier"]["pct"] for m in MODELS]
    prog = [NUM["flip_correct"][m]["overall_4tier"]["pct"] for m in MODELS]
    ax.bar([x - w / 2 for x in xs], reg, w, label="incorrect (regressive)",
           color=C_CAVE, ec="black", lw=0.4)
    ax.bar([x + w / 2 for x in xs], prog, w, label="correct (progressive)",
           color=C_BENIGN, ec="black", lw=0.4)
    for x, v in zip(xs, prog):  # label correct-arm bars so 0.0/0.4 aren't read as missing
        ax.annotate(f"{v:.1f}", (x + w / 2, v + 1.5), ha="center", va="bottom",
                    fontsize=5.8, color=C_BENIGN)
    ax.set_xticks(xs)
    ax.set_xticklabels([LABEL[m] for m in MODELS], rotation=35, ha="right", fontsize=7.2)
    ax.set_ylabel("flip rate, rungs anon–high (%)")
    ax.set_ylim(0, 120)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", frameon=False, fontsize=7.6)
    save(fig, "fig8_direction_asymmetry.png")


# ================= fig2: per-model authority ladders (double column) =========
def fig2():
    D = NUM["flip_incorrect"]
    fig, axes = plt.subplots(2, 3, figsize=(7.1, 4.3), sharey=True)
    xs = list(range(len(RUNGS)))
    for ax, m in zip(axes.flat, MODELS):
        ys, elo, ehi = [], [], []
        for rung in RUNGS:
            p, lo, hi = wilson(D[m][rung]["k"], D[m][rung]["n"])
            ys.append(p); elo.append(lo); ehi.append(hi)
        ax.errorbar(xs, ys, yerr=[elo, ehi], marker="o", capsize=2.5, lw=1.6, ms=4,
                    color=C_CAVE, label="graded rung")
        # first-person control rung, plotted separately (stronger, format-mismatched)
        cp, clo, chi = wilson(D[m]["control"]["k"], D[m]["control"]["n"])
        ax.errorbar([4.3], [cp], yerr=[[clo], [chi]], marker="*", ms=10, capsize=2.5,
                    color=C_CTRL, label="1st-person (excl.)")
        ax.axvline(3.65, color=GRID, lw=0.8)
        ax.set_title(LABEL[m], fontsize=9)
        ax.set_xticks(xs + [4.3])
        ax.set_xticklabels(RLAB + ["1P"], fontsize=7)
        ax.set_ylim(0, 120)
        ax.grid(axis="x", visible=False)
    for ax in axes[:, 0]:
        ax.set_ylabel("two-turn flip rate (%)")
    axes[0, 0].legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=6.8,
                      handlelength=1.2)
    fig.tight_layout(h_pad=2.0)
    save(fig, "fig2_permodel_ladders.png", pad_inches=0.28)


# ================= fig11: prior confidence does not protect (single col) =====
def fig11():
    Q = NUM["confidence_quintiles_within_model"]["quintiles"]
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    xs = [q["q"] for q in Q]
    ys, elo, ehi = [], [], []
    for q in Q:
        k = round(q["flip_pct"] * q["n"] / 100)
        p, lo, hi = wilson(k, q["n"])
        ys.append(p); elo.append(lo); ehi.append(hi)
    ax.errorbar(xs, ys, yerr=[elo, ehi], fmt="o-", color=C_CAVE, capsize=3, lw=1.6, ms=5)
    ax.annotate(f"highest-confidence\nquintile still flips {ys[-1]:.1f}%",
                (5, ys[-1]), xytext=(2.4, 30), fontsize=7.4, ha="center",
                arrowprops=dict(arrowstyle="->", color="black", lw=0.8))
    ax.set_xticks(xs)
    ax.set_xticklabels([f"Q{q['q']}\n{q['z_range'][0]:g}–{q['z_range'][1]:g}" for q in Q],
                       fontsize=7)
    ax.set_xlabel("pre-pressure belief-margin quintile\n(within-model SD)")
    ax.set_ylabel("two-turn flip rate,\nincorrect arm (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="x", visible=False)
    save(fig, "fig11_confidence.png")


# ================= fig3: generic vs domain-matched personas (double col) =====
def fig3():
    GEN = NUM["flip_incorrect"]
    DOM = NUM["domain_matched"]
    tiers = ["low", "medium", "high"]
    tl = ["low", "med", "high"]   # neutral ordinal labels (two persona wordings share these rungs)
    fig, axes = plt.subplots(2, 3, figsize=(7.1, 4.3), sharey=True)
    xs = list(range(len(tiers)))
    for ax, m in zip(axes.flat, MODELS):
        gy = [GEN[m][t]["pct"] for t in tiers]
        dy = [DOM[m]["behavioral"][t]["flip_pct"] for t in tiers]
        ax.plot(xs, gy, marker="o", lw=1.6, ms=4, color=C_GEN, label="generic ladder")
        ax.plot(xs, dy, marker="s", lw=1.6, ms=4, color=C_DOM, label="domain-matched")
        ax.set_title(LABEL[m], fontsize=9)
        ax.set_xticks(xs); ax.set_xticklabels(tl, fontsize=7.5)
        ax.set_ylim(0, 120)
        ax.grid(axis="x", visible=False)
    for ax in axes[:, 0]:
        ax.set_ylabel("two-turn flip rate (%)")
    axes[0, 0].legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=6.8,
                      handlelength=1.4)
    fig.tight_layout(h_pad=2.0)
    save(fig, "fig3_generic_vs_domain.png", pad_inches=0.28)


if __name__ == "__main__":
    fig10(); fig1(); fig8(); fig2(); fig11(); fig3()
    print("done — fig9_design_schematic.png left untouched (author-supplied).")
