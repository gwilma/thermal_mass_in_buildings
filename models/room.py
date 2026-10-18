"""Model 3: hourly single-zone dwelling model.

A two-storey semi-detached house treated as one zone, in the spirit of
ISO 52016-1 / HEM but deliberately small enough to read:

  * every opaque element is a node chain from elements.py, either fine-mesh
    finite differences ("fd") or the five-node lump ("5node")
  * one air node (air plus furniture, 10 kJ/K per m2 floor as in HEM) and one
    massless radiant star node; surfaces couple to air by convection and to
    the star node by long-wave radiation (h_r = 5.13 W/m2K)
  * external walls see sol-air temperature; roof (cold loft) and suspended
    floor void see outdoor air; ground floors sit on 1 m of soil held at the
    annual mean temperature
  * windows: U-value to outdoor air, solar gain g x (1 - frame) x incident,
    optional blinds that close above 150 W/m2 on the glass
  * ventilation: background rate, plus windows opened for purge when the
    operative temperature is above 22 C and outdoors is cooler (day 07-23,
    and at night only if night ventilation is on)
  * heating: ideal convective, 21 C 07-09 and 16-23, 16 C setback otherwise,
    limited to `q_max`; no cooling
  * implicit Euler, 15 min steps, hourly weather

Outputs: annual heating, peak heating, CIBSE TM59-style overheating
indicators applied to the single zone, degree-hours above 26 C.
"""
import math
import numpy as np

from buildups import LIB
from elements import chain, conductance_matrix
import weather as wx

HR = 5.13
H_E = 25.0
ALPHA_SOLAR = 0.6

PACKAGES = {
    # name: walls, ground floor, intermediate floor, partitions, party wall, ceiling
    "Timber frame, suspended timber floor": dict(wall="W5", ground="F2", inter="I1", part="P1", party="P5", ceil="R1"),
    "Timber frame, screed ground floor": dict(wall="W5", ground="F1", inter="I1", part="P1", party="P5", ceil="R1"),
    "SIPs, screed ground floor": dict(wall="W7", ground="F1", inter="I1", part="P1", party="P5", ceil="R1"),
    "Lined CLT, CLT floor": dict(wall="W9", ground="F1", inter="I3", part="P1", party="P5", ceil="R1"),
    "Exposed CLT, CLT floor": dict(wall="W8", ground="F1", inter="I3", part="P1", party="P5", ceil="R1"),
    "Masonry (aircrete, dabs), stud partitions": dict(wall="W4", ground="F1", inter="I1", part="P1", party="P4", ceil="R1"),
    "Masonry (dense block, dabs), stud partitions": dict(wall="W2", ground="F1", inter="I1", part="P1", party="P4", ceil="R1"),
    "Masonry (dense block, wet plaster), block partitions": dict(wall="W1", ground="F1", inter="I1", part="P2", party="P4", ceil="R1"),
    "Heavyweight: dense masonry, exposed slab floors": dict(wall="W1", ground="F3", inter="I2", part="P2", party="P4", ceil="R1"),
    "ICF, screed ground floor": dict(wall="W10", ground="F1", inter="I1", part="P1", party="P4", ceil="R1"),
    "Hempcrete, screed ground floor": dict(wall="W14", ground="F1", inter="I1", part="P1", party="P4", ceil="R1"),
    "Solid brick, uninsulated": dict(wall="W11", ground="F2", inter="I1", part="P2", party="P4", ceil="R1"),
    "Solid brick + internal insulation": dict(wall="W12", ground="F2", inter="I1", part="P2", party="P4", ceil="R1"),
    "Solid brick + external insulation": dict(wall="W13", ground="F2", inter="I1", part="P2", party="P4", ceil="R1"),
}

DEFAULTS = dict(
    floor_area=90.0, storey_h=2.4, wall_h=5.2, width=6.0, depth=7.5,
    win={"S": 10.0, "N": 6.0, "E": 2.0}, front="S",
    U_win=1.4, g_win=0.6, frame=0.25, shade=1.0,
    ach_base=0.5, ach_day=3.0, ach_night=2.0, night_vent=False, t_open=22.0,
    partition_area=60.0, gains_scale=1.0,
    t_set=21.0, t_setback=16.0, q_max=6000.0,
    mode="fd", dx=0.01, dt=900.0,
    overrides=None,  # {"wall": Element, ...} to swap in a custom element
)

ORIENT_AZ = {"S": 0, "W": 90, "N": 180, "E": -90}
GAINS_PROFILE = np.array([250] * 7 + [400] * 2 + [150] * 9 + [600] * 5 + [250])  # W, by hour


def internal_gains(hours):
    return GAINS_PROFILE[(hours % 24).astype(int)]


class Room:
    def __init__(self, package, **kw):
        p = dict(DEFAULTS); p.update(kw)
        self.p = p
        pk = PACKAGES[package] if isinstance(package, str) else package
        ov = p["overrides"] or {}
        el = lambda role: ov.get(role) or LIB[pk[role]]
        A_floor = p["floor_area"] / 2
        rot = {"S": ["S", "N", "E"], "N": ["N", "S", "W"], "E": ["E", "W", "S"], "W": ["W", "E", "N"]}[p["front"]]
        gross = {rot[0]: p["width"] * p["wall_h"], rot[1]: p["width"] * p["wall_h"], rot[2]: p["depth"] * p["wall_h"]}
        # windows are given for the default S/N/E layout and rotate with the house
        win = {rot[i]: p["win"][o] for i, o in enumerate(["S", "N", "E"])}
        self.windows = win
        # (role, element, area, face, orientation)
        groups = [("wall", el("wall"), gross[o] - win[o], "single", o) for o in gross]
        groups += [("ground", el("ground"), A_floor, "single", None),
                   ("inter", el("inter"), A_floor, "both", None),
                   ("part", el("part"), 2 * p["partition_area"], "single", None),
                   ("party", el("party"), p["depth"] * p["wall_h"], "single", None),
                   ("ceil", el("ceil"), A_floor, "single", None)]
        self.groups = groups
        self.elements = {g[0]: g[1] for g in groups}

        # Node layout: 0 air, 1 star, then each group's chain
        n = 2; self.off = []
        chains = []
        for role, e, A, face, o in groups:
            ch = chain(e, p["mode"], p["dx"])
            chains.append(ch); self.off.append(n); n += ch.n
        self.n, self.chains = n, chains
        C = np.zeros(n); G = np.zeros((n, n))
        C[0] = 10e3 * p["floor_area"]
        self.surf = []      # (node index, area, is_floor_top)
        self.back_src = []  # (node index, conductance W/K, group index) for external/ground sides
        for gi, ((role, e, A, face, o), ch, k0) in enumerate(zip(groups, chains, self.off)):
            sl = slice(k0, k0 + ch.n)
            C[sl] += A * ch.C
            G[sl, sl] += A * conductance_matrix(ch)
            G[k0 + ch.n - 1, k0 + ch.n - 1] -= A * ch.back_g  # added back below as a source coupling
            faces = [(k0, e.rsi, role in ("ground", "inter"))]
            if face == "both":  # soffit of intermediate floor is a ceiling surface
                faces.append((k0 + ch.n - 1, 0.10, False))
            for k, rsi, floor_top in faces:
                hc = max(1 / rsi - HR, 0.5)
                self._couple(G, k, 0, hc * A)
                self._couple(G, k, 1, HR * A)
                self.surf.append((k, A, floor_top))
            if ch.back_g > 0:
                kb = k0 + ch.n - 1
                G[kb, kb] += A * ch.back_g
                self.back_src.append((kb, A * ch.back_g, gi))
        self.H_win = p["U_win"] * sum(win.values())
        G[0, 0] += self.H_win
        self.V = p["floor_area"] * p["storey_h"]
        self.C, self.G = C, G
        self._inv = {}

    @staticmethod
    def _couple(G, i, j, h):
        G[i, i] += h; G[j, j] += h; G[i, j] -= h; G[j, i] -= h

    def _system(self, ach):
        if ach not in self._inv:
            A = np.diag(self.C / self.p["dt"]) + self.G
            A[0, 0] += 0.33 * ach * self.V
            Ainv = np.linalg.inv(A)
            self._inv[ach] = (Ainv, Ainv[:, 0].copy())
        return self._inv[ach]

    # --- simulation --------------------------------------------------------
    def run(self, w, days=None):
        p = self.p
        hours = np.arange(8760)
        T_out = w["T"]
        T_ground = T_out.mean()
        irr = {o: wx.plane_irradiance(w, 90, ORIENT_AZ[o]) for o in "SNEW"}
        # solar through windows (with optional blinds)
        q_sol = np.zeros(8760)
        for o, Aw in self.windows.items():
            I = irr[o]
            f_sh = np.where(I > 150, p["shade"], 1.0)
            q_sol += Aw * (1 - p["frame"]) * p["g_win"] * f_sh * I
        q_int = internal_gains(hours) * p["gains_scale"]
        # far-side temperature per back-coupled node
        back_T = []
        for kb, H, gi in self.back_src:
            role, e, A, face, o = self.groups[gi]
            if e.back == "ground":
                back_T.append(np.full(8760, T_ground))
            elif role == "wall":
                back_T.append(T_out + ALPHA_SOLAR * irr[o] / H_E)
            else:
                back_T.append(T_out)
        back_T = np.array(back_T)
        kb_idx = np.array([b[0] for b in self.back_src]); kb_H = np.array([b[1] for b in self.back_src])

        surf_idx = np.array([s[0] for s in self.surf]); surf_A = np.array([s[1] for s in self.surf])
        floor_A = np.where([s[2] for s in self.surf], surf_A, 0.0)
        w_area = surf_A / surf_A.sum(); w_floor = floor_A / floor_A.sum()
        sol_split = 0.6 * w_floor + 0.4 * w_area  # share of transmitted solar per surface
        rad_split = w_area

        dt = p["dt"]; sub = int(round(3600 / dt))
        x = np.full(self.n, 18.0)
        hod = hours % 24
        heat_on = ((hod >= 7) & (hod < 9)) | ((hod >= 16) & (hod < 23))
        t_set = np.where(heat_on, p["t_set"], p["t_setback"])
        out = {k: np.zeros(8760) for k in ("T_air", "T_op", "T_mrt", "Q_heat", "ach")}
        T_op_prev, T_air_prev = 20.0, 20.0
        rng = range(8760) if days is None else range(days[0] * 24, days[1] * 24)
        Cdt = self.C / dt
        for h in rng:
            day_open = 7 <= hod[h] < 23
            want = T_op_prev > p["t_open"] and T_out[h] < T_air_prev
            ach = p["ach_base"]
            if want and day_open:
                ach += p["ach_day"]
            elif want and p["night_vent"]:
                ach += p["ach_night"]
            Ainv, u = self._system(ach)
            src = np.zeros(self.n)
            src[0] += self.H_win * T_out[h] + 0.33 * ach * self.V * T_out[h] + 0.5 * q_int[h]
            np.add.at(src, kb_idx, kb_H * back_T[:, h])
            np.add.at(src, surf_idx, sol_split * q_sol[h] + rad_split * 0.5 * q_int[h])
            acc = np.zeros(5)
            for _ in range(sub):
                x0 = Ainv @ (Cdt * x + src)
                Q = min(max((t_set[h] - x0[0]) / u[0], 0.0), p["q_max"])
                x = x0 + Q * u
                acc += (x[0], 0.5 * (x[0] + x[1]), x[1], Q, ach)
            acc /= sub
            out["T_air"][h], out["T_op"][h], out["T_mrt"][h], out["Q_heat"][h], out["ach"][h] = acc
            T_air_prev, T_op_prev = acc[0], acc[1]
        out["T_out"] = T_out
        return out

    def kappa_summary(self):
        """Effective (ISO 13786 kappa_1 x area) and total heat capacity per m2 floor."""
        k1 = kt = 0.0
        for role, e, A, face, o in self.groups:
            mult = 2 if face == "both" else 1
            k1 += e.iso()["kappa1"] * A * mult
            kt += e.kappa_tot * A
        return k1 / self.p["floor_area"], kt / self.p["floor_area"]

    def fabric_H(self):
        H = self.H_win
        for role, e, A, face, o in self.groups:
            if e.back in ("ext", "ground"):
                H += e.iso()["U"] * A
        return H


def metrics(out, floor_area=90.0, warmup_days=14):
    hours = np.arange(8760); hod = hours % 24
    day = hours // 24
    may_sep = (day >= 120) & (day < 273)
    T_rm = wx.running_mean(out["T_out"])
    T_max = 0.33 * T_rm + 21.8
    dT = np.round(out["T_op"] - T_max)
    occ = may_sep & (hod >= 9) & (hod < 22)
    night = (hod >= 22) | (hod < 7)
    q = out["Q_heat"][day >= warmup_days] if warmup_days else out["Q_heat"]
    jul = (day >= 181) & (day < 212)
    swing = (out["T_op"][jul].reshape(-1, 24).max(1) - out["T_op"][jul].reshape(-1, 24).min(1)).mean()
    return dict(
        heat_kwh_m2=out["Q_heat"].sum() / 1000 / floor_area,
        heat_peak_kw=out["Q_heat"].max() / 1000,
        tm59a_pct=100 * (dT[occ] >= 1).sum() / occ.sum(),
        tm59b_h=int((out["T_op"][night] > 26).sum()),
        dh26=float(np.clip(out["T_op"][may_sep] - 26, 0, None).sum()),
        h28=int((out["T_op"] > 28).sum()),
        T_op_max=float(out["T_op"].max()),
        jul_swing=float(swing),
    )
