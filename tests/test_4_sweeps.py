"""Model 4: parameter sweeps and Morris screening.

Known solutions: for a linear function the Morris elementary effects are the
coefficients exactly; for the Sobol g-function (Saltelli et al., Global
Sensitivity Analysis: The Primer, 2008, section 3.4) the importance of each
input falls as its coefficient a_i rises, and Morris mu* must rank them in
that order. The sweep construction and the published sweep results are
checked against what the physics requires.
"""
import json, math, os
import numpy as np
import pytest

import sweeps
from buildups import Element, L
from conftest import ROOT
from room import Room

SW = json.load(open(os.path.join(ROOT, "models", "results", "sweeps.json")))


def test_morris_linear_function_exact():
    """f = sum a_i x_i: every elementary effect is a_i, so mu = a_i,
    mu* = |a_i| and sigma = 0."""
    a = np.array([3.0, -2.0, 0.5, 0.0, 10.0])
    st = sweeps.elementary_effects(lambda x: {"y": float(a @ x)}, len(a), ("y",), r=8)
    for ai, (mu_star, mu, sigma) in zip(a, st["y"]):
        assert mu == pytest.approx(ai) and mu_star == pytest.approx(abs(ai)) and sigma == pytest.approx(0, abs=1e-9)


def test_morris_detects_interaction():
    """f = x0 x1 + 3 x2: the interacting pair has sigma > 0, the additive
    input has sigma = 0 and mu = 3."""
    st = sweeps.elementary_effects(lambda x: {"y": x[0] * x[1] + 3 * x[2]}, 3, ("y",), r=20)["y"]
    assert st[0][2] > 0.1 and st[1][2] > 0.1
    assert st[2][1] == pytest.approx(3.0) and st[2][2] == pytest.approx(0.0, abs=1e-9)


def test_morris_sobol_g_function_ranking():
    """Sobol g-function, a = (0, 1, 4.5, 9, 99, 99): first-order importance
    falls with a_i, and inputs with a = 99 are nearly inert."""
    a = np.array([0, 1, 4.5, 9, 99, 99])
    g = lambda x: {"y": float(np.prod((np.abs(4 * x - 2) + a) / (1 + a)))}
    mu_star = [s[0] for s in sweeps.elementary_effects(g, len(a), ("y",), r=50, levels=4, seed=1)["y"]]
    assert mu_star[0] > mu_star[1] > mu_star[2] > mu_star[3] > max(mu_star[4:])
    assert max(mu_star[4:]) < 0.05 * mu_star[0]


def test_mass_overrides_add_capacity_linearly():
    """The sweep adds dense concrete of thickness t to the ground floor,
    intermediate floor, partitions and party wall, so kappa_tot per m2 of floor
    rises by rho c t x (sum of those areas) / floor area, exactly."""
    rm0 = Room(sweeps.BASE, overrides=sweeps.mass_overrides(0.05))
    rm1 = Room(sweeps.BASE, overrides=sweeps.mass_overrides(0.15))
    roles = {"ground", "inter", "part", "party"}
    A = sum(g[2] for g in rm0.groups if g[0] in roles)
    dk = (rm1.kappa_summary()[1] - rm0.kappa_summary()[1]) * 1000
    assert dk == pytest.approx(2400 * 1000 * 0.10 * A / 90.0, rel=1e-9)


def test_exposed_slab_kappa1_saturates_at_semi_infinite_limit():
    """kappa_1 of an exposed slab stops growing beyond a few penetration
    depths and tends to the semi-infinite value |1 / (Rsi + 1/Ys)| / omega,
    which is why sweep A's kappa_1 flattens near 100 to 150 mm."""
    w = 2 * math.pi / 86400
    lam, rho, c, rsi = 2.0, 2400, 1000, 0.17
    Ys = (1 + 1j) * lam / math.sqrt(lam * 86400 / (math.pi * rho * c))
    lim = abs(1 / (rsi + 1 / Ys)) / w / 1000
    k = [Element("x", "slab", "floor", [L("dense concrete", t)], "adiabatic").iso()["kappa1"] for t in (0.1, 0.15, 0.3, 1.0)]
    assert k[-1] == pytest.approx(lim, rel=1e-4)
    assert abs(k[2] - lim) / lim < 0.05


def test_published_sweep_b_monotone_in_ventilation():
    """More night ventilation never increases degree-hours at a fixed mass."""
    dh = np.array(SW["B"]["dh26"])
    assert np.all(np.diff(dh, axis=0) <= 1e-6)


def test_published_sweep_b_monotone_in_mass():
    """At every ventilation rate, more exposed mass lowers degree-hours above 26 C."""
    dh = np.array(SW["B"]["dh26"])
    assert np.all(np.diff(dh, axis=1) <= 1e-6)


def test_published_sweep_a_diminishing_returns():
    """Sweep A: each extra millimetre buys less July swing reduction once t is
    beyond about one penetration depth (the thickness optimum in the README)."""
    A = SW["A"]
    t = np.array([r["t"] for r in A]); sw = np.array([r["hot_nv_swing"] for r in A])
    gain_per_mm = -np.diff(sw) / np.diff(t * 1000)
    late = gain_per_mm[t[1:] > 0.1]
    assert np.all(late < 0.02) and gain_per_mm[:3].max() > 5 * late.max()


@pytest.mark.slow
def test_sweep_point_reproduces_published_value(london):
    """One point of sweep B re-run from scratch matches sweeps.json."""
    from room import metrics
    m = metrics(Room(sweeps.BASE, overrides=sweeps.mass_overrides(0.1), night_vent=True, ach_night=2).run(london["hot"]))
    j = SW["B"]["t"].index(0.1); i = SW["B"]["ach"].index(2)
    assert m["dh26"] == pytest.approx(SW["B"]["dh26"][i][j], rel=1e-9)
