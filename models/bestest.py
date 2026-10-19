"""ANSI/ASHRAE Standard 140 (IEA BESTEST) building fabric cases on the room model.

Cases 600 (lightweight) and 900 (heavyweight), with ideal heating and
cooling, and their free-float versions 600FF and 900FF. The building is a
single 8 x 6 x 2.7 m zone with 12 m2 of south glazing, Denver weather
(TMY3 725650, the file the 2020 and later editions of Standard 140 use).

This runs the same Room engine as the house model (room.py, fine-mesh or
five-node elements, air and radiant star nodes) through its generic-zone
options. Known simplifications against the full specification:

  * Perez anisotropic sky for all sunlit surfaces (the house uses isotropic)
  * no long-wave exchange with the sky (sol-air uses solar only), which
    makes heating loads a little low and free-float minima a little high
  * fixed combined surface coefficients from the Standard's own table for
    programs that cannot calculate them
  * window solar uses Fresnel angular transmittance for the specified
    double clear glazing; no solar is reflected back out of the window
  * hourly weather, 15 minute steps
"""
import math, os
import numpy as np

import weather as wx
from buildups import Element, R
from room import Room

HERE = os.path.dirname(os.path.abspath(__file__))
EPW_DENVER = os.path.join(HERE, "weather_data", "USA_CO_Denver.Intl.AP.725650_TMY3.epw")

# Layers, inside to outside: (name, d m, lambda W/mK, rho kg/m3, c J/kgK)
PLASTERBOARD = lambda d: ("plasterboard", d, 0.16, 950, 840)
FIBREGLASS = lambda d: ("fibreglass quilt", d, 0.04, 12, 840)
SIDING = ("wood siding", 0.009, 0.14, 530, 900)
DECK = ("roof deck", 0.019, 0.14, 530, 900)

# Combined surface coefficients for programs with fixed values (W/m2K)
H_IN_WALL, H_IN_CEIL, H_IN_FLOOR = 8.29, 9.26, 6.13
H_OUT = 29.3

GLASS = dict(n=1.526, K=19.6, d=0.003175)  # refractive index, extinction 1/m, pane thickness
SHGC_NORMAL, U_WIN = 0.789, 3.0


def _elements(case):
    heavy = case.startswith("9")
    if heavy:
        wall = [("concrete block", 0.100, 0.51, 1400, 1000), ("foam insulation", 0.0615, 0.04, 10, 1400), SIDING]
        floor = [("concrete slab", 0.080, 1.13, 1400, 1000), R("floor insulation", 1.007 / 0.04)]
    else:
        wall = [PLASTERBOARD(0.012), FIBREGLASS(0.066), SIDING]
        floor = [("timber flooring", 0.025, 0.14, 650, 1200), R("floor insulation", 1.003 / 0.04)]
    roof = [PLASTERBOARD(0.010), FIBREGLASS(0.1118), DECK]
    return (Element("BW", "BESTEST wall", "wall", wall, "ext", rsi=1 / H_IN_WALL, rse=1 / H_OUT),
            Element("BF", "BESTEST floor", "floor", floor, "ext", rsi=1 / H_IN_FLOOR, rse=1 / H_OUT),
            Element("BR", "BESTEST roof", "ceiling", roof, "ext", rsi=1 / H_IN_CEIL, rse=1 / H_OUT))


def pane_tau(theta):
    """Solar transmittance of the specified double clear glazing at incidence
    theta (rad): Fresnel reflection, Bouguer absorption, two panes with
    inter-reflection (the standard's own derivation of its glazing data)."""
    n, K, d = GLASS["n"], GLASS["K"], GLASS["d"]
    th2 = np.arcsin(np.sin(theta) / n)
    with np.errstate(invalid="ignore", divide="ignore"):
        rs = (np.sin(th2 - theta) / np.sin(th2 + theta)) ** 2
        rp = (np.tan(th2 - theta) / np.tan(th2 + theta)) ** 2
    small = theta < 1e-6
    r0 = ((n - 1) / (n + 1)) ** 2
    rs = np.where(small, r0, rs); rp = np.where(small, r0, rp)
    a = np.exp(-K * d / np.cos(th2))
    taus = []
    for r in (rs, rp):
        t1 = (1 - r) ** 2 * a / (1 - (r * a) ** 2)          # one pane
        r1 = r + (1 - r) ** 2 * r * a ** 2 / (1 - (r * a) ** 2)
        taus.append(t1 ** 2 / (1 - r1 ** 2))                 # two panes
    return 0.5 * (taus[0] + taus[1])


def window_solar(w, area=12.0):
    """Solar heat gain through the south glazing, W, hourly."""
    sinz = np.sqrt(np.clip(1 - w["cosz"] ** 2, 0, 1))
    cos_inc = np.clip(sinz * np.cos(w["az"]), 0, 1) * (w["cosz"] > 0)
    tau0 = float(pane_tau(np.array(0.0)))
    beam = w["DNI"] * cos_inc
    f_beam = pane_tau(np.arccos(np.clip(cos_inc, 1e-6, 1))) / tau0
    th = np.linspace(0, math.pi / 2 - 1e-4, 400)
    f_diff = float(np.trapezoid(pane_tau(th) * np.cos(th) * np.sin(th), th) * 2 / tau0)
    diffuse = wx.plane_irradiance(w, 90, 0, sky="perez") - beam  # sky (Perez) and ground
    return area * SHGC_NORMAL * (beam * f_beam + diffuse * f_diff)


def air_rho_cp(elev):
    rho = 1.225 * math.exp(-elev / 8434.0)
    return rho, rho * 1005.0


def room(case, mode="fd"):
    wall, floor, roof = _elements(case)
    geometry = [("wall", wall, 8 * 2.7 - 12.0, "single", "S"), ("wall", wall, 8 * 2.7, "single", "N"),
                ("wall", wall, 6 * 2.7, "single", "E"), ("wall", wall, 6 * 2.7, "single", "W"),
                ("floor", floor, 48.0, "single", None), ("ceil", roof, 48.0, "single", "H")]
    rho, rcp = air_rho_cp(1650.0)
    ff = case.endswith("FF")
    return Room(None, geometry=geometry, windows={"S": 12.0}, floor_area=48.0, storey_h=2.7,
                U_win=U_WIN, ach_base=0.5, ach_day=0.0, ach_night=0.0, t_open=1e9,
                gains=200.0, gains_rad=0.6, C_air=129.6 * rcp, rho_cp=rcp / 3600,
                t_set=-1e9 if ff else 20.0, t_setback=-1e9 if ff else 20.0, q_max=1e9,
                t_cool=None if ff else 27.0, mode=mode, sky="perez")


def weather():
    w = wx.read_epw(EPW_DENVER)
    w["q_sol_bestest"] = window_solar(w)
    return w


def run(case, w=None, mode="fd"):
    w = w or weather()
    rm = room(case, mode)
    rm.p["q_sol"] = w["q_sol_bestest"]
    out = rm.run(w)
    return dict(heat_mwh=out["Q_heat"].sum() / 1e6, cool_mwh=out["Q_cool"].sum() / 1e6,
                peak_heat_kw=out["Q_heat"].max() / 1e3, peak_cool_kw=out["Q_cool"].max() / 1e3,
                T_max=float(out["T_air"].max()), T_min=float(out["T_air"].min()),
                T_mean=float(out["T_air"].mean()))


# Acceptance ranges (minimum and maximum of the Standard's example programs)
# for the 725650TY Denver weather. Case 600: ANSI/ASHRAE 140-2020 Addendum b,
# Tables A3-1 and A3-2. Case 900 and 900FF: 140-2023 Annex B8, as transcribed
# by the fluxion project (github.com/anchapin/fluxion PR 4414); not checked
# against the Standard itself.
RANGES = {
    "600": dict(heat_mwh=(3.75, 4.98), cool_mwh=(5.00, 6.83)),
    "900": dict(heat_mwh=(1.379, 1.814), cool_mwh=(2.267, 2.714)),
    "900FF": dict(T_max=(43.3, 46.0), T_min=(0.6, 2.2)),
}

if __name__ == "__main__":
    W = weather()
    print("window solar MWh/yr:", round(W["q_sol_bestest"].sum() / 1e6, 3))
    for c in ("600", "900", "600FF", "900FF"):
        for mode in ("fd", "5node"):
            r = run(c, W, mode)
            print(c, mode, {k: round(v, 3) for k, v in r.items()}, RANGES.get(c, ""))
