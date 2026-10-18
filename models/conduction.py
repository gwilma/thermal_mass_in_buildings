"""Model 2: fine-mesh 1D conduction as a reference for ISO 13786 and the
five-node (ISO 52016-1 / HEM) element lump.

What it does:
  1. Mesh convergence: fine-mesh daily admittance against the ISO 13786
     closed form for every build-up in the library.
  2. Five-node vs fine mesh: daily |Y| for the class the library assigns,
     and for every class, so the class that best matches is visible.
  3. Period dependence: |Y| from 1 h to 1 week, fine mesh vs five-node.
  4. Time domain: heat absorbed by the element during a hot afternoon
     (implicit Euler, 5 min steps), fine mesh vs five-node.

Run as a script to write results/conduction.md and figures.
"""
import math, os
import numpy as np

from buildups import LIB
from elements import admittance, step_response, CLASSES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
DX_REF = 0.002


def compare_all():
    rows = []
    for k, e in LIB.items():
        iso = e.iso()["Y"]
        yfd, lead_fd = admittance(e, "fd", DX_REF)
        y5, lead_5 = admittance(e, "5node")
        per_cls = {c: admittance(e, "5node", cls=c)[0] for c in CLASSES}
        best = min(per_cls, key=lambda c: abs(per_cls[c] / yfd - 1))
        rows.append(dict(key=k, name=e.name, cls=e.cls, Y_iso=iso, Y_fd=yfd, lead_fd=lead_fd,
                         Y_5n=y5, lead_5n=lead_5, per_cls=per_cls, best=best,
                         Y_fd_20mm=admittance(e, "fd", 0.02)[0]))
    return rows


def hot_day_trace(dt=300.0, days=4):
    """Room air temperature: 24 C mean, 4 K amplitude, peak 16:00."""
    t = np.arange(0, days * 86400, dt)
    return t, 24 + 4 * np.cos(2 * np.pi * (t / 3600 - 16) / 24)


def absorbed_kwh(e, mode, dt=300.0):
    """kWh/m2 absorbed by the surface between 09:00 and 18:00 on the last day."""
    t, Tr = hot_day_trace(dt)
    q = step_response(e, Tr, dt, mode, dx=DX_REF if mode == "fd" else 0.005, Tback=24.0 if e.back != "ext" else 15.0)
    h = (t / 3600) % 24
    last = t >= t[-1] - 86400 + dt
    sel = last & (h >= 9) & (h < 18)
    return q[sel].sum() * dt / 3.6e6


def figures(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

    # Five-node vs fine-mesh daily admittance
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    x = np.array([r["Y_fd"] for r in rows]); y = np.array([r["Y_5n"] for r in rows])
    ax.plot([0, 10], [0, 10], color="0.6", lw=0.8)
    ax.plot([0, 5], [0, 10], color="0.8", lw=0.8, ls="--")
    ax.text(4.6, 9.4, "2×", color="0.5")
    ax.scatter(x, y, s=14, color="#2a6fb0", zorder=3)
    for r in rows:
        ax.annotate(r["key"], (r["Y_fd"], r["Y_5n"]), xytext=(3, 2), textcoords="offset points", fontsize=7)
    ax.set_xlabel("Fine-mesh daily |Y| (= ISO 13786), W/m²K")
    ax.set_ylabel("Five-node daily |Y| (library class), W/m²K")
    ax.set_xlim(0, 8); ax.set_ylim(0, 10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fivenode_vs_fd.png"), dpi=200); plt.close(fig)

    # Period dependence
    fig, axs = plt.subplots(1, 4, figsize=(10, 2.8), sharey=False)
    periods = np.geomspace(1, 168, 40)
    for ax, k in zip(axs, ["W1", "W2", "W8", "I2"]):
        e = LIB[k]
        ax.semilogx(periods, [admittance(e, "fd", 0.004, period=p * 3600)[0] for p in periods], label="fine mesh", color="k")
        ax.semilogx(periods, [admittance(e, "5node", period=p * 3600)[0] for p in periods], label=f"five-node ({e.cls})", color="#c0504d")
        ax.axvline(24, color="0.8", lw=0.8)
        ax.set_title(f"{k}: {e.name[:34]}", fontsize=7.5)
        ax.set_xlabel("period, h")
    axs[0].set_ylabel("|Y|, W/m²K"); axs[0].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "admittance_vs_period.png"), dpi=200); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = compare_all()
    err = max(abs(r["Y_fd"] / r["Y_iso"] - 1) for r in rows)
    err20 = max(abs(r["Y_fd_20mm"] / r["Y_iso"] - 1) for r in rows)
    lines = ["# Model 2: fine-mesh conduction vs ISO 13786 vs five-node", "",
             f"Fine mesh ({DX_REF*1000:.0f} mm cells) matches the ISO 13786 closed form to within {err*100:.2f}% "
             f"for all {len(rows)} build-ups ({err20*100:.1f}% with 20 mm cells), so it is used as the reference below.", "",
             "Daily |Y| in W/m²K. 'Absorbed' is heat taken in by 1 m² of element between 09:00 and 18:00 on a "
             "hot day (room air 24 ± 4 °C, peak 16:00), kWh/m².", "",
             "| Key | Build-up | Class | |Y| ISO | |Y| fine mesh | |Y| five-node | ratio | best class (|Y|) | Absorbed fine | Absorbed five-node |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        e = LIB[r["key"]]
        a_fd, a_5 = absorbed_kwh(e, "fd"), absorbed_kwh(e, "5node")
        r.update(abs_fd=a_fd, abs_5=a_5)
        lines.append(f"| {r['key']} | {r['name']} | {r['cls']} | {r['Y_iso']:.2f} | {r['Y_fd']:.2f} | {r['Y_5n']:.2f} | "
                     f"{r['Y_5n']/r['Y_fd']:.2f} | {r['best']} ({r['per_cls'][r['best']]:.2f}) | {a_fd:.3f} | {a_5:.3f} |")
    lines += ["", "Five-node |Y| for every class (W/m²K):", "",
              "| Key | " + " | ".join(CLASSES) + " | fine mesh |", "|---|" + "---|" * (len(CLASSES) + 1)]
    for r in rows:
        lines.append(f"| {r['key']} | " + " | ".join(f"{r['per_cls'][c]:.2f}" for c in CLASSES) + f" | {r['Y_fd']:.2f} |")
    open(os.path.join(OUT, "conduction.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    figures(rows)


if __name__ == "__main__":
    main()
