"""Library of common UK construction build-ups (model 1).

Each build-up is a list of layers from the ROOM side outwards, in the
format used by physics/iso13786.py: (name, d m, lambda W/mK, rho kg/m3,
c J/kgK), or (name, R) for a massless resistance (cavity, dab void).

`back` says what the far side of the element sees:
  "ext"       outdoor air (via Rse)
  "ground"    soil, modelled in the room model as 1 m of clay at the
              annual mean outdoor temperature
  "adiabatic" symmetry plane (half of a partition or party wall)
  "room"      the same zone (intermediate floor: top and soffit both in the zone)

Run as a script to print the characterisation table and write
results/buildups.csv and results/buildups.md.
"""
import csv, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics"))
from iso13786 import characterise, T  # noqa: E402

# lambda W/mK, rho kg/m3, c J/kgK. Typical design values (CIBSE Guide A,
# ISO 10456, manufacturers' literature); swap for product data as needed.
MAT = {
    "dense concrete": (2.0, 2400, 1000),
    "precast plank": (1.6, 2200, 1000),
    "screed": (1.15, 2000, 1000),
    "brick": (0.77, 1700, 800),
    "dense block": (1.13, 2000, 1000),
    "medium block": (0.51, 1400, 1000),
    "aerated block": (0.15, 600, 1000),
    "gypsum plaster": (0.5, 1300, 1000),
    "lime plaster": (0.7, 1600, 1000),
    "render": (0.8, 1800, 1000),
    "plasterboard": (0.21, 700, 1000),
    "CLT": (0.13, 470, 1600),
    "OSB": (0.13, 650, 1700),
    "chipboard": (0.14, 650, 1700),
    "timber": (0.13, 500, 1600),
    "mineral wool": (0.035, 30, 1030),
    "mineral wool + studs": (0.040, 60, 1200),  # bridged by 15% softwood
    "PIR": (0.022, 30, 1400),
    "EPS": (0.032, 20, 1450),
    "wood fibre": (0.038, 160, 2100),
    "hempcrete": (0.07, 330, 1500),
    "rammed earth": (1.0, 1900, 900),
    "carpet + underlay": (0.06, 200, 1300),
    "clay soil": (1.5, 1500, 2000),
}

AIR_CAVITY = 0.18     # m2K/W, unventilated 25-100 mm cavity (ISO 6946)
DAB_VOID = 0.10       # m2K/W, plasterboard on dabs void (typical assumption)
SERVICE_VOID = 0.17   # m2K/W, 25 mm service void behind lining


def L(name, d):
    return (name, d, *MAT[name])


def R(name, r):
    return (name, r)


class Element:
    def __init__(self, key, name, kind, layers, back, rsi=None, rse=0.04, cls=None):
        self.key, self.name, self.kind = key, name, kind
        self.layers, self.back = layers, back
        # ISO 6946 surface resistances: horizontal 0.13, upward 0.10, downward 0.17
        self.rsi = rsi if rsi is not None else {"floor": 0.17, "ceiling": 0.10}.get(kind, 0.13)
        self.rse = rse if back == "ext" else 0.0
        self.cls = cls or mass_class(layers)

    @property
    def kappa_tot(self):
        return sum(l[3] * l[4] * l[1] for l in self.layers if len(l) == 5) / 1000

    def iso(self, period=T):
        """ISO 13786 characteristics. Elements whose back is not outdoors are
        given a far-side boundary consistent with their use: adiabatic (very
        large back resistance) for partitions, the room-side Rsi for
        intermediate floors, and soil for ground floors."""
        layers, rse = list(self.layers), self.rse
        if self.back == "adiabatic":
            layers.append(R("adiabatic", 1e6)); rse = 0.0
        elif self.back == "room":
            rse = self.rsi
        elif self.back == "ground":
            layers.append(L("clay soil", 1.0)); rse = 0.0
        return characterise(layers, rsi=self.rsi, rse=rse, period=period)


def mass_class(layers):
    """Pick the ISO 52016-1 / HEM mass distribution class from where the heat
    capacity sits relative to the insulation (layers with lambda < 0.08 W/mK
    and thicker than 40 mm). A user of HEM picks this by judgement; this rule
    is our own reading of the class definitions."""
    caps = [(l[3] * l[4] * l[1] if len(l) == 5 else 0.0) for l in layers]
    ins = [i for i, l in enumerate(layers) if len(l) == 5 and l[2] < 0.08 and l[1] > 0.04]
    tot = sum(caps) or 1.0
    if not ins:
        return "D"
    inner = sum(caps[:ins[0]]) / tot
    outer = sum(caps[ins[-1] + 1:]) / tot
    middle = sum(c for i, c in enumerate(caps[ins[0]:ins[-1] + 1], ins[0]) if i not in ins) / tot
    if middle >= 0.5:
        return "M"
    if inner >= 0.5 and outer < 0.2:
        return "I"
    if outer >= 0.5 and inner < 0.2:
        return "E"
    if inner >= 0.2 and outer >= 0.2:
        return "IE"
    return "D"


E = Element
LIB = {e.key: e for e in [
    # --- external walls -------------------------------------------------
    E("W1", "Cavity: wet plaster, 100 dense block, 150 MW, brick", "wall",
      [L("gypsum plaster", .013), L("dense block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W2", "Cavity: board on dabs, 100 dense block, 150 MW, brick", "wall",
      [L("plasterboard", .0125), R("dab void", DAB_VOID), L("dense block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W3", "Cavity: wet plaster, 100 aircrete, 150 MW, brick", "wall",
      [L("gypsum plaster", .013), L("aerated block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W4", "Cavity: board on dabs, 100 aircrete, 150 MW, brick", "wall",
      [L("plasterboard", .0125), R("dab void", DAB_VOID), L("aerated block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W5", "Timber frame: board, 140 MW studs, OSB, cavity, brick", "wall",
      [L("plasterboard", .0125), L("mineral wool + studs", .14), L("OSB", .009), R("cavity", AIR_CAVITY), L("brick", .102)], "ext"),
    E("W6", "Timber frame: board, 140 MW studs, 60 wood fibre, render", "wall",
      [L("plasterboard", .0125), L("mineral wool + studs", .14), L("wood fibre", .06), L("render", .01)], "ext"),
    E("W7", "SIPs: board, OSB, 142 PUR, OSB, ventilated cladding", "wall",
      [L("plasterboard", .0125), R("service void", SERVICE_VOID), L("OSB", .015), L("PIR", .142), L("OSB", .015)], "ext"),
    E("W8", "Exposed 100 CLT, 160 wood fibre, render", "wall",
      [L("CLT", .1), L("wood fibre", .16), L("render", .01)], "ext"),
    E("W9", "Lined CLT: board, 100 CLT, 160 MW, cladding", "wall",
      [L("plasterboard", .0125), R("service void", SERVICE_VOID), L("CLT", .1), L("mineral wool", .16)], "ext"),
    E("W10", "ICF: board on dabs, 70 EPS, 150 concrete, 70 EPS, render", "wall",
      [L("plasterboard", .0125), R("dab void", DAB_VOID), L("EPS", .07), L("dense concrete", .15), L("EPS", .07), L("render", .01)], "ext"),
    E("W11", "Solid 215 brick, wet plaster, uninsulated", "wall",
      [L("gypsum plaster", .013), L("brick", .215)], "ext"),
    E("W12", "Solid brick + IWI: board, 80 PIR, 215 brick", "wall",
      [L("plasterboard", .0125), L("PIR", .08), L("brick", .215)], "ext"),
    E("W13", "Solid brick + EWI: plaster, 215 brick, 100 EPS, render", "wall",
      [L("gypsum plaster", .013), L("brick", .215), L("EPS", .1), L("render", .01)], "ext"),
    E("W14", "Hempcrete: lime plaster, 300 hempcrete, lime render", "wall",
      [L("lime plaster", .015), L("hempcrete", .3), L("render", .015)], "ext"),
    E("W15", "Exposed 300 rammed earth, 120 wood fibre, render", "wall",
      [L("rammed earth", .3), L("wood fibre", .12), L("render", .01)], "ext"),
    # --- ground floors ----------------------------------------------------
    E("F1", "65 screed on 100 PIR on slab", "floor",
      [L("screed", .065), L("PIR", .1), L("dense concrete", .1)], "ground"),
    E("F2", "Suspended timber: 22 chipboard, 150 MW, vented void", "floor",
      [L("chipboard", .022), L("mineral wool + studs", .15)], "ext"),
    E("F3", "Exposed 150 slab (polished) on 120 PIR", "floor",
      [L("dense concrete", .15), L("PIR", .12)], "ground"),
    E("F4", "Carpet on 65 screed on 100 PIR on slab", "floor",
      [L("carpet + underlay", .012), L("screed", .065), L("PIR", .1), L("dense concrete", .1)], "ground"),
    # --- intermediate floors (both faces in the zone) ----------------------
    E("I1", "Timber joist: 22 chipboard, void, 12.5 board ceiling", "floor",
      [L("chipboard", .022), R("joist void", AIR_CAVITY), L("plasterboard", .0125)], "room"),
    E("I2", "Concrete: 50 screed, 150 plank, exposed soffit", "floor",
      [L("screed", .05), L("precast plank", .15)], "room"),
    E("I3", "Exposed 160 CLT floor, 50 screed on top", "floor",
      [L("screed", .05), L("CLT", .16)], "room"),
    # --- partitions and party walls (half-thickness, adiabatic midplane) ---
    E("P1", "Stud partition: 12.5 board each side (half)", "partition",
      [L("plasterboard", .0125), R("half void", AIR_CAVITY / 2)], "adiabatic"),
    E("P2", "100 dense block, wet plaster both sides (half)", "partition",
      [L("gypsum plaster", .013), L("dense block", .05)], "adiabatic"),
    E("P3", "100 aircrete, wet plaster both sides (half)", "partition",
      [L("gypsum plaster", .013), L("aerated block", .05)], "adiabatic"),
    E("P4", "Party wall: plaster, 100 dense block leaf (cavity behind)", "partition",
      [L("gypsum plaster", .013), L("dense block", .1)], "adiabatic"),
    E("P5", "Party wall: board, 90 MW studs (timber frame twin stud)", "partition",
      [L("plasterboard", .025), L("mineral wool + studs", .09)], "adiabatic"),
    # --- ceilings / roofs -------------------------------------------------
    E("R1", "12.5 board ceiling under 300 MW (cold loft)", "ceiling",
      [L("plasterboard", .0125), L("mineral wool", .3)], "ext"),
    E("R2", "Exposed 200 concrete roof slab, 150 PIR", "ceiling",
      [L("dense concrete", .2), L("PIR", .15)], "ext"),
]}


def row(e):
    r = e.iso()
    return dict(key=e.key, name=e.name, kind=e.kind, back=e.back, cls=e.cls,
                U=r["U"] if e.back == "ext" or e.back == "ground" else float("nan"),
                Y=r["Y"], Y_lead_h=r["Y_lead_h"],
                f=r["f"] if e.back == "ext" else float("nan"),
                lag_h=r["lag_h"] if e.back == "ext" else float("nan"),
                kappa1=r["kappa1"], kappa_tot=e.kappa_tot)


def table():
    return [row(e) for e in LIB.values()]


if __name__ == "__main__":
    from conduction import compare_all
    out = os.path.join(HERE, "results"); os.makedirs(out, exist_ok=True)
    rows = table()
    cmp = {c["key"]: c for c in compare_all()}
    for r in rows:
        c = cmp[r["key"]]
        r.update(Y_fd=c["Y_fd"], Y_5n=c["Y_5n"], ratio_5n=c["Y_5n"] / c["Y_fd"])
    keys = list(rows[0])
    with open(os.path.join(out, "buildups.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, keys); w.writeheader(); w.writerows(rows)
    fmt = lambda v: "–" if isinstance(v, float) and math.isnan(v) else (f"{v:.2f}" if isinstance(v, float) else str(v))
    lines = ["| Key | Build-up (room side first) | Class | U | Y | Y lead h | f | lag h | κ₁ | κ_tot | Y 5-node / FD |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join([r["key"], r["name"], r["cls"], fmt(r["U"]), fmt(r["Y"]), f"{r['Y_lead_h']:.1f}",
                                        fmt(r["f"]), "–" if math.isnan(r["lag_h"]) else f"{r['lag_h']:.1f}",
                                        f"{r['kappa1']:.0f}", f"{r['kappa_tot']:.0f}", f"{r['ratio_5n']:.2f}"]) + " |")
    open(os.path.join(out, "buildups.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
