"""Model 1: build-up library and ISO 13786 calculator.

Published reference: ISO 13786:2007 Annex D, case D.1 (as reproduced by
QuickField's ISO 13786 validation page). Analytical references: the
semi-infinite solid, a lumped thin layer and a pure resistance, for which
ISO 13786's matrix method has closed-form answers.
"""
import cmath, math
import numpy as np
import pytest

from iso13786 import characterise, layer_matrix, mul, res_matrix
from buildups import LIB, Element, L, R, mass_class
from elements import admittance

T = 86400.0
W = 2 * math.pi / T


# --- published case -----------------------------------------------------------
def test_iso13786_annex_d1_concrete_wall():
    """ISO 13786 Annex D, case D.1: 200 mm homogeneous concrete
    (lambda 1.8, rho 2400, c 1000), Rsi 0.13, Rse 0.04, 24 h period.
    Reference values: delta 0.144 m, U 3.56, |Y11| 5.70, |Y22| 11.59,
    |Y12| 1.83 W/m2K, time shift of Y12 about -5.7 h."""
    r = characterise([("concrete", 0.200, 1.8, 2400, 1000)])
    delta = math.sqrt(1.8 * T / (math.pi * 2400 * 1000))
    assert delta == pytest.approx(0.144, abs=5e-4)
    assert r["U"] == pytest.approx(3.56, abs=0.005)
    assert r["Y"] == pytest.approx(5.70, abs=0.005)
    assert r["Y22"] == pytest.approx(11.59, abs=0.005)
    assert r["Y12"] == pytest.approx(1.83, abs=0.005)
    assert r["lag_h"] == pytest.approx(5.7, abs=0.05)


# --- analytical cases ---------------------------------------------------------
def test_semi_infinite_solid_admittance():
    """A layer many penetration depths thick behaves as a semi-infinite solid:
    surface admittance (1 + i) lambda / delta, modulus b sqrt(omega) with b the
    thermal effusivity, leading the temperature by 45 degrees (3 h in 24 h).
    With a surface resistance the admittance is 1 / (Rsi + 1 / Ys)."""
    lam, rho, c, rsi = 2.0, 2400, 1000, 0.13
    b = math.sqrt(lam * rho * c)
    Ys = b * math.sqrt(W) * cmath.exp(1j * math.pi / 4)
    r0 = characterise([("thick", 2.0, lam, rho, c)], rsi=1e-9, rse=0.04)
    assert r0["Y"] == pytest.approx(abs(Ys), rel=1e-6)
    assert r0["Y_lead_h"] == pytest.approx(3.0, abs=1e-4)
    r1 = characterise([("thick", 2.0, lam, rho, c)], rsi=rsi, rse=0.04)
    Y = 1 / (rsi + 1 / Ys)
    assert r1["Y"] == pytest.approx(abs(Y), rel=1e-6)
    assert r1["Y_lead_h"] == pytest.approx(math.degrees(cmath.phase(Y)) / 15, abs=1e-4)
    # deep mass: kappa_1 tends to |Y| / omega
    assert r1["kappa1"] * 1000 == pytest.approx(abs(Y) / W, rel=1e-5)


def test_lumped_thin_layer():
    """A thin, highly conductive layer is a lumped capacity C between Rsi and
    Rse, for which Z11 = 1 + i w C Rse and Z12 = -(Rsi + Rse + i w C Rsi Rse)."""
    C, R1, R2 = 2.0e4, 0.13, 0.04
    r = characterise([("plate", 0.01, 1.0e4, 2000, 1000)], rsi=R1, rse=R2)
    Z11 = 1 + 1j * W * C * R2
    Z12 = -(R1 + R2 + 1j * W * C * R1 * R2)
    assert r["Y"] == pytest.approx(abs(-Z11 / Z12), rel=1e-4)
    assert r["Y12"] == pytest.approx(abs(-1 / Z12), rel=1e-4)
    assert r["kappa1"] * 1000 == pytest.approx(abs((Z11 - 1) / Z12) / W, rel=1e-4)


def test_pure_resistance():
    """Without heat capacity there is no dynamics: |Y| = U, f = 1, no lag, kappa = 0."""
    r = characterise([R("insulation", 2.0), R("cavity", 0.18)])
    U = 1 / (0.13 + 2.0 + 0.18 + 0.04)
    assert r["U"] == pytest.approx(U)
    assert r["Y"] == pytest.approx(U)
    assert r["f"] == pytest.approx(1.0)
    assert min(r["lag_h"], 24 - r["lag_h"]) == pytest.approx(0.0, abs=1e-9)
    assert r["kappa1"] == pytest.approx(0.0, abs=1e-12)


def test_matrix_reciprocity():
    """Every ISO 13786 layer matrix has determinant 1, so the chain does too, and
    the periodic transmittance is the same whichever side is heated."""
    for d, lam, rho, c in [(0.1, 1.13, 2000, 1000), (0.15, 0.035, 30, 1030), (0.0125, 0.21, 700, 1000)]:
        Z = layer_matrix(d, lam, rho, c)
        assert abs(Z[0][0] * Z[1][1] - Z[0][1] * Z[1][0] - 1) < 1e-9
    layers = LIB["W1"].layers
    a = characterise(layers, rsi=0.13, rse=0.04)
    b = characterise(list(reversed(layers)), rsi=0.04, rse=0.13)
    assert a["Y12"] == pytest.approx(b["Y12"], rel=1e-9)
    assert a["Y22"] == pytest.approx(b["Y"], rel=1e-9)
    assert a["kappa2"] == pytest.approx(b["kappa1"], rel=1e-9)


# --- library ------------------------------------------------------------------
@pytest.mark.parametrize("key", [k for k in sorted(LIB) if LIB[k].back == "ext"])
def test_library_u_value_is_iso6946_sum(key):
    """U from the matrix method equals the ISO 6946 resistance sum."""
    e = LIB[key]
    Rt = e.rsi + e.rse + sum(l[1] if len(l) == 2 else l[1] / l[2] for l in e.layers)
    assert e.iso()["U"] == pytest.approx(1 / Rt, rel=1e-12)


@pytest.mark.parametrize("key", sorted(LIB))
def test_library_kappa_tot(key):
    """kappa_tot is the sum of rho c d over the layers; kappa_1 and |Y| are positive."""
    e = LIB[key]
    assert e.kappa_tot * 1000 == pytest.approx(sum(l[1] * l[3] * l[4] for l in e.layers if len(l) == 5))
    r = e.iso()
    assert r["kappa1"] > 0
    assert r["Y"] > 0


@pytest.mark.parametrize("key", sorted(LIB))
def test_fine_mesh_converges_to_iso13786(key):
    """Model 2's fine mesh at 2 mm reproduces ISO 13786 daily |Y| to 0.5%."""
    e = LIB[key]
    Y_fd, _ = admittance(e, "fd", dx=0.002)
    assert Y_fd == pytest.approx(e.iso()["Y"], rel=5e-3)


def test_mass_class_rule():
    """The five-node class follows where heat capacity sits relative to the
    insulation (our reading of the ISO 52016-1 classes)."""
    ins = L("mineral wool", 0.15)
    dense = L("dense block", 0.1)
    assert mass_class([dense, ins]) == "I"        # mass on the room side
    assert mass_class([ins, dense]) == "E"        # mass outside the insulation
    assert mass_class([dense, ins, dense]) == "IE"
    assert mass_class([dense]) == "D"             # uniform, no insulation
    assert mass_class([L("EPS", 0.07), L("dense concrete", 0.15), L("EPS", 0.07)]) == "M"
    assert LIB["W8"].cls == "I" and LIB["W5"].cls == "E" and LIB["W10"].cls == "M"
