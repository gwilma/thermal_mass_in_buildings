"""Model 3 results: the construction packages compared in one house.

For each package in room.PACKAGES, runs the synthetic London year
("typical" for heating, "hot" and "hot2050" for overheating), with daytime
purge only and with night ventilation added, in fine-mesh and five-node
element modes. Writes results/packages.csv, results/packages.md and
results/packages.png.
"""
import csv, os
import numpy as np

from room import Room, metrics, PACKAGES
import weather as wx

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")


def run():
    W = {v: wx.synthetic(v) for v in ("typical", "hot", "hot2050")}
    rows = []
    for name in PACKAGES:
        for mode in ("fd", "5node"):
            base = Room(name, mode=mode)
            k1, kt = base.kappa_summary()
            r = dict(package=name, mode=mode, kappa1=k1, kappa_tot=kt, H_fabric=base.fabric_H())
            m = metrics(base.run(W["typical"]))
            r.update(heat_kwh_m2=m["heat_kwh_m2"], heat_peak_kw=m["heat_peak_kw"])
            for wv in ("hot", "hot2050"):
                for nv in (False, True):
                    m = metrics(Room(name, mode=mode, night_vent=nv).run(W[wv]))
                    tag = f"{wv}_{'nv' if nv else 'day'}"
                    for k in ("tm59a_pct", "tm59b_h", "dh26", "T_op_max", "jul_swing"):
                        r[f"{tag}_{k}"] = m[k]
            rows.append(r)
            print(name, mode, {k: round(v, 1) for k, v in r.items() if isinstance(v, float)})
    return rows


def write(rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "packages.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    fd = [r for r in rows if r["mode"] == "fd"]
    n5 = {r["package"]: r for r in rows if r["mode"] == "5node"}
    L = ["# Model 3: construction packages in one house", "",
         "Two-storey semi, 90 m², same windows, ventilation, gains and controls in every case; only the fabric changes. "
         "Fine-mesh elements. κ₁ is ISO 13786 daily areal heat capacity × area, per m² floor. "
         "Heating: synthetic typical year. Overheating: synthetic hot (DSY-like) year, single zone, TM59-style indicators: "
         "(a) % of occupied hours May–Sep at ΔT ≥ 1 K (limit 3%), (b) night hours above 26 °C (limit 32). "
         "DH26 is degree-hours above 26 °C, May–Sep.", "",
         "| Package | κ₁ kJ/m²K | H W/K | Heat kWh/m² | Peak kW | (a) % day vent | (b) h day vent | DH26 day vent | (a) % +night vent | (b) h +night vent | DH26 +night vent | DH26 2050 +night vent | July swing K |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(fd, key=lambda r: r["kappa1"]):
        L.append(f"| {r['package']} | {r['kappa1']:.0f} | {r['H_fabric']:.0f} | {r['heat_kwh_m2']:.1f} | {r['heat_peak_kw']:.2f} | "
                 f"{r['hot_day_tm59a_pct']:.1f} | {r['hot_day_tm59b_h']:.0f} | {r['hot_day_dh26']:.0f} | "
                 f"{r['hot_nv_tm59a_pct']:.1f} | {r['hot_nv_tm59b_h']:.0f} | {r['hot_nv_dh26']:.0f} | {r['hot2050_nv_dh26']:.0f} | {r['hot_nv_jul_swing']:.1f} |")
    L += ["", "## Five-node vs fine mesh at whole-house level", "",
          "Same runs with every element as the five-node lump (class from the library). Differences are five-node minus fine mesh.", "",
          "| Package | Heat kWh/m² Δ | Peak kW Δ | DH26 day vent Δ | DH26 +night vent Δ | (b) h +night vent Δ | July swing Δ K |",
          "|---|---|---|---|---|---|---|"]
    for r in sorted(fd, key=lambda r: r["kappa1"]):
        q = n5[r["package"]]
        L.append(f"| {r['package']} | {q['heat_kwh_m2']-r['heat_kwh_m2']:+.1f} | {q['heat_peak_kw']-r['heat_peak_kw']:+.2f} | "
                 f"{q['hot_day_dh26']-r['hot_day_dh26']:+.0f} ({100*(q['hot_day_dh26']/r['hot_day_dh26']-1):+.0f}%) | "
                 f"{q['hot_nv_dh26']-r['hot_nv_dh26']:+.0f} ({100*(q['hot_nv_dh26']/max(r['hot_nv_dh26'],1)-1):+.0f}%) | "
                 f"{q['hot_nv_tm59b_h']-r['hot_nv_tm59b_h']:+.0f} | {q['hot_nv_jul_swing']-r['hot_nv_jul_swing']:+.2f} |")
    open(os.path.join(OUT, "packages.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    figure(fd)


def figure(fd):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
    fd = sorted(fd, key=lambda r: r["kappa1"])
    names = [r["package"] for r in fd]; y = np.arange(len(fd))
    fig, axs = plt.subplots(1, 3, figsize=(11, 4.6), sharey=True)
    ax = axs[0]
    ax.barh(y - 0.2, [r["hot_day_dh26"] for r in fd], 0.4, color="#c0504d", label="day purge only")
    ax.barh(y + 0.2, [r["hot_nv_dh26"] for r in fd], 0.4, color="#2a6fb0", label="+ night ventilation")
    ax.set_xlabel("degree-hours above 26 °C, May–Sep (hot year)"); ax.legend(frameon=False, loc="lower right")
    ax = axs[1]
    ax.barh(y - 0.2, [r["hot_day_tm59b_h"] for r in fd], 0.4, color="#c0504d")
    ax.barh(y + 0.2, [r["hot_nv_tm59b_h"] for r in fd], 0.4, color="#2a6fb0")
    ax.axvline(32, color="k", lw=0.8, ls="--"); ax.text(34, len(fd) - 0.6, "TM59 (b) limit", fontsize=7)
    ax.set_xlabel("night hours above 26 °C (hot year)")
    ax = axs[2]
    ax.barh(y, [r["heat_kwh_m2"] for r in fd], 0.6, color="0.5")
    ax.set_xlabel("space heating, kWh/m² (typical year)")
    axs[0].set_yticks(y); axs[0].set_yticklabels([f"{n}  (κ₁ {r['kappa1']:.0f})" for n, r in zip(names, fd)])
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "packages.png"), dpi=200); plt.close(fig)


if __name__ == "__main__":
    write(run())
