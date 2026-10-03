"""Periodic (ISO 13786) dynamic thermal characteristics of a wall/floor build-up.

Layers are listed from the INTERNAL surface outwards. Each layer is
(name, thickness m, conductivity W/mK, density kg/m3, specific heat J/kgK).
A layer with thickness 0 and a resistance is given as (name, R) instead.
"""
import cmath, math

T = 86400.0  # period, s
RSI, RSE = 0.13, 0.04  # ISO 6946 horizontal heat flow


def layer_matrix(d, lam, rho, c, period=T):
    delta = math.sqrt(lam * period / (math.pi * rho * c))  # periodic penetration depth
    x = d / delta
    ch, sh, co, si = math.cosh(x), math.sinh(x), math.cos(x), math.sin(x)
    z11 = complex(ch * co, sh * si)
    z12 = -delta / (2 * lam) * complex(sh * co + ch * si, ch * si - sh * co)
    z21 = -lam / delta * complex(sh * co - ch * si, sh * co + ch * si)
    return [[z11, z12], [z21, z11]]


def res_matrix(R):
    return [[1, -R], [0, 1]]


def mul(a, b):
    return [[a[0][0]*b[0][0]+a[0][1]*b[1][0], a[0][0]*b[0][1]+a[0][1]*b[1][1]],
            [a[1][0]*b[0][0]+a[1][1]*b[1][0], a[1][0]*b[0][1]+a[1][1]*b[1][1]]]


def characterise(layers, rsi=RSI, rse=RSE, period=T):
    # ISO 13786: Z = Z_se * Z_N ... Z_1 * Z_si, layer 1 at the internal side
    Z = res_matrix(rsi)
    R = rsi + rse
    kappa_sum = 0.0
    for L in layers:
        if len(L) == 2:
            Z = mul(res_matrix(L[1]), Z); R += L[1]
        else:
            _, d, lam, rho, c = L
            Z = mul(layer_matrix(d, lam, rho, c, period), Z)
            R += d / lam
            kappa_sum += rho * c * d
    Z = mul(res_matrix(rse), Z)
    U = 1 / R
    Y11 = -Z[0][0] / Z[0][1]           # internal admittance
    Y12 = -1 / Z[0][1]                  # periodic thermal transmittance
    k1 = period / (2 * math.pi) * abs((Z[0][0] - 1) / Z[0][1])  # internal areal heat capacity
    lead = lambda y: period / (2 * math.pi) * cmath.phase(y) / 3600
    return dict(U=U, Y=abs(Y11), Y_lead_h=lead(Y11), f=abs(Y12) / U,
                lag_h=(-lead(Y12)) % 24, kappa1=k1 / 1000, total_C=kappa_sum / 1000)


MAT = {  # d is set per build-up; lambda, rho, c from typical CIBSE/ISO 10456 values
    "dense concrete": (2.0, 2400, 1000),
    "brick": (0.77, 1700, 800),
    "dense block": (1.13, 2000, 1000),
    "aerated block": (0.15, 600, 1000),
    "gypsum plaster": (0.5, 1300, 1000),
    "plasterboard": (0.21, 700, 1000),
    "CLT (softwood)": (0.13, 470, 1600),
    "mineral wool": (0.035, 30, 1030),
    "PIR": (0.022, 30, 1400),
    "rammed earth": (1.0, 1900, 900),
    "screed": (1.15, 2000, 1000),
}

def L(name, d):
    return (name, d, *MAT[name])

BUILDUPS = {
    "Exposed 200 mm concrete soffit + 100 mm PIR": [L("dense concrete", .2), L("PIR", .1)],
    "13 mm plaster on 100 mm dense block, 150 mm MW, 102 mm brick": [L("gypsum plaster", .013), L("dense block", .1), L("mineral wool", .15), L("brick", .102)],
    "13 mm plaster on 100 mm aerated block, 150 mm MW, 102 mm brick": [L("gypsum plaster", .013), L("aerated block", .1), L("mineral wool", .15), L("brick", .102)],
    "Plasterboard on dabs (R=0.1) on 100 mm dense block, 150 mm MW, brick": [L("plasterboard", .0125), ("dab cavity", 0.1), L("dense block", .1), L("mineral wool", .15), L("brick", .102)],
    "12.5 mm plasterboard, 150 mm MW timber frame (lightweight)": [L("plasterboard", .0125), L("mineral wool", .15)],
    "Exposed 100 mm CLT + 150 mm MW": [L("CLT (softwood)", .1), L("mineral wool", .15)],
    "300 mm rammed earth (uninsulated)": [L("rammed earth", .3)],
    "65 mm screed on 100 mm PIR (floor, Rsi 0.17)": [L("screed", .065), L("PIR", .1)],
}

if __name__ == "__main__":
    print("| Material | λ W/mK | ρ kg/m³ | c J/kgK | α mm²/s | b J/m²Ks½ | δ (24 h) mm |")
    print("|---|---|---|---|---|---|---|")
    for k, (lam, rho, c) in MAT.items():
        a = lam / (rho * c); b = math.sqrt(lam * rho * c); d = math.sqrt(lam * T / (math.pi * rho * c))
        print(f"| {k} | {lam} | {rho} | {c} | {a*1e6:.2f} | {b:.0f} | {d*1000:.0f} |")
    print()
    print("| Build-up (inside → outside) | U W/m²K | Y W/m²K | Y lead h | f | lag h | κ₁ kJ/m²K | Σρcd kJ/m²K |")
    print("|---|---|---|---|---|---|---|---|")
    for k, layers in BUILDUPS.items():
        rsi = 0.17 if "floor" in k else RSI
        r = characterise(layers, rsi=rsi)
        print(f"| {k} | {r['U']:.2f} | {r['Y']:.2f} | {r['Y_lead_h']:.1f} | {r['f']:.2f} | {r['lag_h']:.1f} | {r['kappa1']:.0f} | {r['total_C']:.0f} |")
    print()
    print("Internal admittance Y (W/m²K) and κ₁ (kJ/m²K) vs exposed thickness, layer backed by 100 mm PIR")
    th = (0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3)
    print("| Material | " + " | ".join(f"{d*1000:.0f} mm" for d in th) + " |")
    print("|---|" + "---|" * len(th))
    for m in ("dense concrete", "dense block", "brick", "rammed earth", "aerated block", "CLT (softwood)"):
        cells = []
        for d in th:
            r = characterise([L(m, d), L("PIR", .1)])
            cells.append(f"{r['Y']:.1f} / {r['kappa1']:.0f}")
        print(f"| {m} | " + " | ".join(cells) + " |")
    print()
    print("Penetration depth δ (mm) by period")
    for m in ("dense concrete", "brick", "CLT (softwood)"):
        lam, rho, c = MAT[m]
        print(m, [round(1000*math.sqrt(lam*P*3600/(math.pi*rho*c))) for P in (1, 24, 168)])
    print("Semi-infinite concrete, Rsi=0: |Y| = b*sqrt(ω) =", round(math.sqrt(2.0*2400*1000)*math.sqrt(2*math.pi/T), 2))
    print("Semi-infinite concrete with Rsi=0.13:", round(characterise([L("dense concrete", 2.0)])['Y'], 2))
    print("200 mm concrete + PIR, Y by period (h):", {P: round(characterise([L("dense concrete", .2), L("PIR", .1)], period=P*3600)['Y'], 2) for P in (1, 6, 24, 168)})
