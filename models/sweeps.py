"""Model 4: parameter sweeps on the room model.

  A. Diminishing returns: the same timber-frame envelope with an exposed
     dense layer of thickness t on the ground floor, intermediate floor,
     partitions and party wall (t = 0 is plasterboard and chipboard).
  B. Mass x night ventilation: overheating over a grid of t and night
     ventilation rate.
  C. Morris elementary-effects screening of eight inputs, to rank what
     matters for overheating and heating.

Writes results/sweeps.md and figures. Fine-mesh elements, synthetic weather.
"""
import os
import numpy as np

from buildups import Element, LIB, L, R, AIR_CAVITY
from room import Room, metrics
import weather as wx

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
BASE = "Timber frame, screed ground floor"
T_LIST = [0, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3]


def mass_overrides(t, wall_mw=0.14):
    ov = {"wall": Element("Wv", "Timber frame (variable MW)", "wall",
                          [L("plasterboard", .0125), L("mineral wool + studs", wall_mw), L("OSB", .009), R("cavity", AIR_CAVITY), L("brick", .102)], "ext")}
    if t <= 0:
        ov.update(ground=Element("G0", "Chipboard on PIR on slab", "floor", [L("chipboard", .022), L("PIR", .1), L("dense concrete", .1)], "ground"),
                  inter=LIB["I1"], part=LIB["P1"], party=LIB["P5"])
    else:
        ov.update(ground=Element("Gt", f"{t*1000:.0f} dense on PIR", "floor", [L("dense concrete", t), L("PIR", .1), L("dense concrete", .1)], "ground"),
                  inter=Element("It", f"{t*1000:.0f} slab", "floor", [L("dense concrete", t)], "room"),
                  part=Element("Pt", f"{2*t*1000:.0f} dense wall (half)", "partition", [L("dense concrete", t)], "adiabatic"),
                  party=Element("Qt", f"{t*1000:.0f} dense leaf", "partition", [L("dense concrete", t)], "adiabatic"))
    return ov


def sweep_a(W):
    rows = []
    for t in T_LIST:
        r = dict(t=t)
        rm = Room(BASE, overrides=mass_overrides(t))
        r["kappa1"], r["kappa_tot"] = rm.kappa_summary()
        m = metrics(rm.run(W["typical"])); r.update(heat=m["heat_kwh_m2"], peak=m["heat_peak_kw"])
        for wv in ("hot", "hot2050"):
            for nv in (False, True):
                m = metrics(Room(BASE, overrides=mass_overrides(t), night_vent=nv).run(W[wv]))
                tag = f"{wv}_{'nv' if nv else 'day'}"
                r.update({f"{tag}_dh26": m["dh26"], f"{tag}_b": m["tm59b_h"], f"{tag}_a": m["tm59a_pct"],
                          f"{tag}_max": m["T_op_max"], f"{tag}_swing": m["jul_swing"]})
        rows.append(r); print("A", {k: round(v, 2) for k, v in r.items()})
    return rows


def sweep_b(W, t_list=(0, 0.025, 0.05, 0.1, 0.15, 0.2, 0.3), ach_list=(0, 0.5, 1, 2, 3, 5)):
    dh = np.zeros((len(ach_list), len(t_list))); nb = np.zeros_like(dh)
    for j, t in enumerate(t_list):
        for i, a in enumerate(ach_list):
            m = metrics(Room(BASE, overrides=mass_overrides(t), night_vent=a > 0, ach_night=a).run(W["hot"]))
            dh[i, j], nb[i, j] = m["dh26"], m["tm59b_h"]
        print("B", t, dh[:, j].round())
    return t_list, ach_list, dh, nb


PARAMS = [  # name, low, high, how it is applied
    ("exposed mass t (m)", 0.0, 0.3), ("glazing area ×", 0.5, 1.5), ("blind factor (closed)", 0.2, 1.0),
    ("day purge ACH", 0.0, 6.0), ("night vent ACH", 0.0, 4.0), ("background ACH", 0.3, 1.0),
    ("internal gains ×", 0.6, 1.4), ("wall insulation (m MW)", 0.09, 0.24),
]


def _room(x):
    v = [lo + xi * (hi - lo) for xi, (_, lo, hi) in zip(x, PARAMS)]
    win = {k: a * v[1] for k, a in {"S": 10.0, "N": 6.0, "E": 2.0}.items()}
    return lambda: Room(BASE, overrides=mass_overrides(v[0], v[7]), win=win, shade=v[2], ach_day=v[3],
                        night_vent=v[4] > 0, ach_night=v[4], ach_base=v[5], gains_scale=v[6])


def morris(W, r=10, levels=4, seed=3):
    rng = np.random.default_rng(seed)
    k = len(PARAMS); delta = levels / (2 * (levels - 1))
    grid = np.arange(levels) / (levels - 1)
    outs = ("dh26", "tm59b_h", "heat_kwh_m2", "heat_peak_kw")
    ee = {o: [[] for _ in range(k)] for o in outs}

    def evaluate(x):
        mk = _room(x)
        mh = metrics(mk().run(W["hot"])); mt = metrics(mk().run(W["typical"]))
        return dict(dh26=mh["dh26"], tm59b_h=mh["tm59b_h"], heat_kwh_m2=mt["heat_kwh_m2"], heat_peak_kw=mt["heat_peak_kw"])

    for traj in range(r):
        x = rng.choice(grid[grid <= 1 - delta + 1e-9], k)
        y = evaluate(x)
        for i in rng.permutation(k):
            x2 = x.copy(); x2[i] = x[i] + delta if x[i] + delta <= 1 + 1e-9 else x[i] - delta
            y2 = evaluate(x2)
            for o in outs:
                ee[o][i].append((y2[o] - y[o]) / (x2[i] - x[i]))
            x, y = x2, y2
        print("Morris trajectory", traj + 1, "of", r)
    res = {o: [(PARAMS[i][0], float(np.mean(np.abs(ee[o][i]))), float(np.mean(ee[o][i])), float(np.std(ee[o][i])))
               for i in range(k)] for o in outs}
    return res


def figures(A, B, M):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
    k1 = [r["t"] * 1000 for r in A]  # plotted against t: kappa_1 saturates near 100 mm and would fold the curves back
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    ax = axs[0]
    for tag, col, lab in [("hot_day", "#c0504d", "hot, day purge"), ("hot_nv", "#2a6fb0", "hot, + night vent"),
                          ("hot2050_nv", "#7f3f98", "2050s hot, + night vent")]:
        ax.plot(k1, [r[f"{tag}_dh26"] for r in A], "o-", ms=3, color=col, label=lab)
    ax.set_xlabel("exposed dense layer t, mm"); ax.set_ylabel("degree-hours > 26 °C, May–Sep"); ax.legend(frameon=False, fontsize=7)
    ax = axs[1]
    ax.plot(k1, [r["hot_day_swing"] for r in A], "o-", ms=3, color="#c0504d", label="day purge")
    ax.plot(k1, [r["hot_nv_swing"] for r in A], "o-", ms=3, color="#2a6fb0", label="+ night vent")
    ax.set_xlabel("exposed dense layer t, mm"); ax.set_ylabel("mean daily T_op swing in July, K"); ax.legend(frameon=False, fontsize=7)
    ax = axs[2]
    ax.plot(k1, [r["heat"] for r in A], "o-", ms=3, color="0.3", label="heating kWh/m²")
    ax2 = ax.twinx(); ax2.plot(k1, [r["peak"] for r in A], "s--", ms=3, color="#e08a2c", label="peak kW")
    ax.set_xlabel("exposed dense layer t, mm"); ax.set_ylabel("space heating, kWh/m² (typical year)")
    ax2.set_ylabel("peak heating, kW", color="#e08a2c"); ax2.spines["top"].set_visible(False)
    for r in A[::2]:
        axs[0].annotate(f"κ₁ {r['kappa1']:.0f}", (r["t"] * 1000, r["hot_day_dh26"]), xytext=(2, 4), textcoords="offset points", fontsize=6.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "diminishing_returns.png"), dpi=200); plt.close(fig)

    t_list, ach_list, dh, nb = B
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, Z, lab in [(axs[0], dh, "degree-hours > 26 °C"), (axs[1], nb, "night hours > 26 °C")]:
        im = ax.imshow(Z, origin="lower", aspect="auto", cmap="magma_r")
        ax.set_xticks(range(len(t_list))); ax.set_xticklabels([f"{t*1000:.0f}" for t in t_list])
        ax.set_yticks(range(len(ach_list))); ax.set_yticklabels([str(a) for a in ach_list])
        ax.set_xlabel("exposed dense layer t, mm"); ax.set_ylabel("night ventilation, ACH")
        for i in range(Z.shape[0]):
            for j in range(Z.shape[1]):
                ax.text(j, i, f"{Z[i, j]:.0f}", ha="center", va="center", fontsize=6.5,
                        color="w" if Z[i, j] > Z.mean() else "k")
        ax.set_title(lab, fontsize=8.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "mass_x_nightvent.png"), dpi=200); plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2))
    for ax, o, lab in zip(axs, ("dh26", "tm59b_h", "heat_kwh_m2"), ("degree-hours > 26 °C (hot)", "night hours > 26 °C (hot)", "heating kWh/m² (typical)")):
        rows = sorted(M[o], key=lambda r: r[1])
        ax.barh([r[0] for r in rows], [r[1] for r in rows], color="#2a6fb0")
        ax.errorbar([r[1] for r in rows], range(len(rows)), xerr=[r[3] for r in rows], fmt="none", ecolor="0.5", lw=0.8)
        ax.set_xlabel(f"Morris μ* (bar) and σ (whisker)\n{lab}", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "morris.png"), dpi=200); plt.close(fig)


def write(A, B, M):
    L = ["# Model 4: sweeps", "",
         f"Base: '{BASE}' envelope with an exposed dense layer of thickness t on the ground floor, intermediate floor (slab "
         "of thickness t), partitions (2t thick) and party wall. t = 0 swaps in board and chipboard. Synthetic weather.", "",
         "## A. Diminishing returns", "",
         "| t mm | κ₁ kJ/m²K per m² floor | κ_tot | heat kWh/m² | peak kW | DH26 hot day | DH26 hot +nv | DH26 2050 +nv | (b) h hot +nv | T_op max hot +nv | July swing +nv K |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in A:
        L.append(f"| {r['t']*1000:.0f} | {r['kappa1']:.0f} | {r['kappa_tot']:.0f} | {r['heat']:.1f} | {r['peak']:.2f} | {r['hot_day_dh26']:.0f} | "
                 f"{r['hot_nv_dh26']:.0f} | {r['hot2050_nv_dh26']:.0f} | {r['hot_nv_b']:.0f} | {r['hot_nv_max']:.1f} | {r['hot_nv_swing']:.1f} |")
    t_list, ach_list, dh, nb = B
    L += ["", "## B. Degree-hours above 26 °C (hot year): rows night ventilation ACH, columns t mm", "",
          "| ACH \\ t | " + " | ".join(f"{t*1000:.0f}" for t in t_list) + " |", "|---|" + "---|" * len(t_list)]
    for i, a in enumerate(ach_list):
        L.append(f"| {a} | " + " | ".join(f"{v:.0f}" for v in dh[i]) + " |")
    L += ["", "Night hours above 26 °C:", "", "| ACH \\ t | " + " | ".join(f"{t*1000:.0f}" for t in t_list) + " |", "|---|" + "---|" * len(t_list)]
    for i, a in enumerate(ach_list):
        L.append(f"| {a} | " + " | ".join(f"{v:.0f}" for v in nb[i]) + " |")
    L += ["", "## C. Morris screening (10 trajectories, 4 levels; μ* = mean |elementary effect| over the full range of each input)", "",
          "Ranges: " + "; ".join(f"{n} {lo}–{hi}" for n, lo, hi in PARAMS) + ".", ""]
    for o, lab in (("dh26", "Degree-hours > 26 °C, hot year"), ("tm59b_h", "Night hours > 26 °C, hot year"),
                   ("heat_kwh_m2", "Space heating kWh/m², typical year"), ("heat_peak_kw", "Peak heating kW, typical year")):
        L += [f"**{lab}**", "", "| Input | μ* | μ (signed) | σ |", "|---|---|---|---|"]
        for n, mus, mu, sd in sorted(M[o], key=lambda r: -r[1]):
            L.append(f"| {n} | {mus:.1f} | {mu:+.1f} | {sd:.1f} |")
        L.append("")
    open(os.path.join(OUT, "sweeps.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    W = {v: wx.synthetic(v) for v in ("typical", "hot", "hot2050")}
    A = sweep_a(W); B = sweep_b(W); M = morris(W)
    write(A, B, M)
    figures(A, B, M)
