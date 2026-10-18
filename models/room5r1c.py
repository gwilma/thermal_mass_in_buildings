"""ISO 13790 / ISO 52016-style 5R1C hourly model of the same house.

This is the simplified model the Excel workbook implements cell by cell.
It takes geometry, glazing, ventilation, gains and controls from a
room.Room object, and collapses the fabric to one mass node:

  C_m  = sum of kappa_1 x A over every room-facing surface (ISO 13786 daily
         areal heat capacity, both faces of the intermediate floor)
  A_m  = C_m^2 / sum(kappa_1^2 x A)       H_tr,ms = 9.1 A_m
  H_tr,is = 3.45 A_t with A_t = 4.5 A_f   H_tr,em from the opaque U x A
  H_tr,w  = windows U x A                 operative T = 0.3 air + 0.7 surface

Ground-floor loss goes to the annual mean temperature: the external
temperature seen by the mass node is the H-weighted mean of the outdoor
and ground temperatures. Opaque solar uses alpha x Rse x U x A x I.
Crank-Nicolson, 1 h steps (ISO 13790 Annex C). Window opening and heating
control follow room.py, using the previous hour's temperatures.
"""
import numpy as np

import weather as wx
from room import Room, internal_gains, ORIENT_AZ, ALPHA_SOLAR, metrics

R_SE = 0.04


def params(room):
    p = room.p
    Af = p["floor_area"]; At = 4.5 * Af
    k1A = k1sqA = 0.0
    H_out = H_g = 0.0
    opaque_sol = {o: 0.0 for o in "SNEW"}
    for role, e, A, face, o in room.groups:
        r = e.iso()
        mult = 2 if face == "both" else 1
        k1A += r["kappa1"] * 1000 * A * mult
        k1sqA += (r["kappa1"] * 1000) ** 2 * A * mult
        if e.back == "ext":
            H_out += r["U"] * A
            if role == "wall":
                opaque_sol[o] += ALPHA_SOLAR * R_SE * r["U"] * A
        elif e.back == "ground":
            H_g += r["U"] * A
    Cm = k1A; Am = Cm ** 2 / k1sqA
    return dict(Af=Af, At=At, Cm=Cm, Am=Am, H_is=3.45 * At, H_ms=9.1 * Am, H_w=room.H_win,
                H_op=H_out + H_g, H_out=H_out, H_g=H_g, opaque_sol=opaque_sol, V=room.V)


def run(room, w):
    p = room.p; q = params(room)
    H_ms, H_is, H_w = q["H_ms"], q["H_is"], q["H_w"]
    H_em = 1 / (1 / q["H_op"] - 1 / H_ms)
    T_out = w["T"]; T_g = T_out.mean()
    theta_em = (q["H_out"] * T_out + q["H_g"] * T_g) / q["H_op"]
    irr = {o: wx.plane_irradiance(w, 90, ORIENT_AZ[o]) for o in "SNEW"}
    q_sol = np.zeros(8760)
    for o, Aw in room.windows.items():
        q_sol += Aw * (1 - p["frame"]) * p["g_win"] * np.where(irr[o] > 150, p["shade"], 1.0) * irr[o]
    q_sol += sum(q["opaque_sol"][o] * irr[o] for o in "SNEW")
    q_int = internal_gains(np.arange(8760)) * p["gains_scale"]
    phi_ia = 0.5 * q_int
    f_st = 1 - q["Am"] / q["At"] - H_w / (9.1 * q["At"])
    phi_st = f_st * (0.5 * q_int + q_sol)
    phi_m = q["Am"] / q["At"] * (0.5 * q_int + q_sol)
    hod = np.arange(8760) % 24
    heat_on = ((hod >= 7) & (hod < 9)) | ((hod >= 16) & (hod < 23))
    t_set = np.where(heat_on, p["t_set"], p["t_setback"])
    Cm = q["Cm"] / 3600
    out = {k: np.zeros(8760) for k in ("T_air", "T_op", "T_s", "T_m", "Q_heat", "ach")}
    Tm_prev, T_op_prev, T_air_prev = 18.0, 20.0, 20.0
    for h in range(8760):
        want = T_op_prev > p["t_open"] and T_out[h] < T_air_prev
        ach = p["ach_base"] + (p["ach_day"] if want and 7 <= hod[h] < 23 else (p["ach_night"] if want and p["night_vent"] else 0.0))
        H_ve = 0.33 * ach * q["V"]
        H1 = 1 / (1 / H_ve + 1 / H_is); H2 = H1 + H_w; H3 = 1 / (1 / H2 + 1 / H_ms)
        te, tsup = theta_em[h], T_out[h]
        den = Cm + 0.5 * (H3 + H_em)
        # temperatures with no heating
        phi_mtot = phi_m[h] + H_em * te + H3 * (phi_st[h] + H_w * tsup + H1 * (phi_ia[h] / H_ve + tsup)) / H2
        Tm_t = (Tm_prev * (Cm - 0.5 * (H3 + H_em)) + phi_mtot) / den
        Tm = 0.5 * (Tm_t + Tm_prev)
        Ts = (H_ms * Tm + phi_st[h] + H_w * tsup + H1 * (tsup + phi_ia[h] / H_ve)) / (H_ms + H_w + H1)
        Ta = (H_is * Ts + H_ve * tsup + phi_ia[h]) / (H_is + H_ve)
        # sensitivities to 1 W of convective heating
        dTm_t = H3 * H1 / (H2 * H_ve) / den
        dTs = (H_ms * 0.5 * dTm_t + H1 / H_ve) / (H_ms + H_w + H1)
        dTa = (H_is * dTs + 1) / (H_is + H_ve)
        Q = min(max((t_set[h] - Ta) / dTa, 0.0), p["q_max"])
        Tm_t += Q * dTm_t; Tm = 0.5 * (Tm_t + Tm_prev); Ts += Q * dTs; Ta += Q * dTa
        Top = 0.3 * Ta + 0.7 * Ts
        out["T_air"][h], out["T_op"][h], out["T_s"][h], out["T_m"][h], out["Q_heat"][h], out["ach"][h] = Ta, Top, Ts, Tm, Q, ach
        Tm_prev, T_op_prev, T_air_prev = Tm_t, Top, Ta
    out["T_out"] = T_out
    return out


if __name__ == "__main__":
    from room import PACKAGES
    W = {v: wx.get(v) for v in ("typical", "hot")}
    for name in PACKAGES:
        r = Room(name)
        q = params(r)
        m1 = metrics(run(r, W["typical"])); m2 = metrics(run(Room(name, night_vent=True), W["hot"]))
        print(f"{name:52s} Cm/Af={q['Cm']/q['Af']/1000:5.0f} Am/Af={q['Am']/q['Af']:.2f} heat={m1['heat_kwh_m2']:.1f} peak={m1['heat_peak_kw']:.2f} dh26nv={m2['dh26']:.0f} b={m2['tm59b_h']}")
