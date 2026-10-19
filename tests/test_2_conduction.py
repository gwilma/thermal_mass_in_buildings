"""Model 2: fine-mesh and five-node element chains.

Analytical references (Carslaw and Jaeger, Conduction of Heat in Solids,
2nd ed., 1959): surface flux into a semi-infinite solid after a step in
surface temperature (section 2.5), the slab with one face stepped and the
other insulated (section 3.3), the periodic semi-infinite solid (section
2.6), and Newtonian cooling of a lumped body (Biot number << 1).
"""
import math
import numpy as np
import pytest

from buildups import LIB, Element
from elements import CLASSES, admittance, chain, step_response

CONC = ("concrete", None, 2.0, 2400, 1000)
ALPHA = 2.0 / (2400 * 1000)


def slab(d, rsi=1e-5, back="adiabatic", mat=CONC):
    return Element("t", "test", "wall", [(mat[0], d, *mat[2:])], back, rsi=rsi)


def test_semi_infinite_step_flux():
    """Surface stepped by 1 K: q(t) = lambda / sqrt(pi alpha t)."""
    dt, hours = 30.0, 12
    q = step_response(slab(1.0), np.ones(int(hours * 3600 / dt)), dt, dx=0.0025)
    for h in (1, 2, 4, 8, 12):
        t = h * 3600
        exact = 2.0 / math.sqrt(math.pi * ALPHA * t)
        assert q[int(t / dt) - 1] == pytest.approx(exact, rel=0.01), h


def test_slab_step_fourier_series():
    """100 mm slab, room face stepped by 1 K, back insulated:
    q(t) = (2 lambda / L) sum exp(-(2n+1)^2 pi^2 alpha t / 4 L^2)."""
    Ld, dt = 0.1, 5.0
    q = step_response(slab(Ld), np.ones(int(8 * 3600 / dt)), dt, dx=0.002)
    for h in (0.5, 1, 2, 4, 8):
        t = h * 3600
        exact = 2 * 2.0 / Ld * sum(math.exp(-((2 * n + 1) * math.pi / (2 * Ld)) ** 2 * ALPHA * t) for n in range(200))
        assert q[int(t / dt) - 1] == pytest.approx(exact, rel=0.01), h


def test_energy_conservation():
    """Heat taken in after a step equals the rise in stored heat, rho c d x 1 K."""
    dt = 60.0
    q = step_response(slab(0.1), np.ones(int(72 * 3600 / dt)), dt, dx=0.005)
    assert q.sum() * dt == pytest.approx(2400 * 1000 * 0.1, rel=1e-3)


@pytest.mark.parametrize("mode,cls", [("fd", None)] + [("5node", c) for c in CLASSES])
def test_lumped_body_newtonian_cooling(mode, cls):
    """A thin, very conductive plate behind Rsi = 0.13 is a single capacity:
    q(t) = exp(-t / tau) / Rsi with tau = Rsi C. Every five-node class must
    agree, since there is no internal resistance to distribute the mass over."""
    plate = Element("p", "plate", "wall", [("plate", 0.01, 1.0e3, 2000, 1000)], "adiabatic", rsi=0.13)
    tau = 0.13 * 2.0e4
    dt = 5.0
    q = step_response(plate, np.ones(int(3 * tau / dt)), dt, mode=mode, cls=cls, dx=0.005)
    for k in (0.5, 1, 2):
        t = k * tau
        assert q[int(t / dt) - 1] == pytest.approx(math.exp(-t / tau) / 0.13, rel=5e-3)


def test_periodic_semi_infinite_admittance():
    """Daily cycle on a deep slab: Y = 1 / (Rsi + 1 / ((1 + i) lambda / delta))."""
    w = 2 * math.pi / 86400
    delta = math.sqrt(2 * ALPHA / w)
    Ys = (1 + 1j) * 2.0 / delta
    Y = 1 / (0.13 + 1 / Ys)
    Y_fd, lead = admittance(slab(1.0, rsi=0.13), "fd", dx=0.002)
    assert Y_fd == pytest.approx(abs(Y), rel=2e-3)
    assert lead == pytest.approx(math.degrees(np.angle(Y)) / 15, abs=0.02)


def test_fine_mesh_second_order_convergence():
    """Halving the cell size cuts the error against ISO 13786 by about four
    (vertex-centred finite differences are second-order in space)."""
    e = LIB["W1"]
    ref = e.iso()["Y"]
    err = [abs(admittance(e, "fd", dx=dx)[0] - ref) for dx in (0.02, 0.01, 0.005)]
    assert err[0] / err[1] > 3.0 and err[1] / err[2] > 3.0


@pytest.mark.parametrize("key", sorted(LIB))
def test_five_node_conserves_resistance_and_capacity(key):
    """Five-node conductances 6/Rc, 3/Rc, 3/Rc, 6/Rc add in series to 1/Rc,
    and the class only redistributes kappa_tot, never changes it."""
    e = LIB[key]
    Rc = sum(l[1] if len(l) == 2 else l[1] / l[2] for l in e.layers)
    soil = chain(Element("s", "soil only", "floor", [], "ground"), "fd")  # the 1 m of soil appended to ground floors
    extra_C = soil.C.sum() if e.back == "ground" else 0.0
    extra_R = sum(1 / x for x in soil.g) if e.back == "ground" else 0.0
    for cls in CLASSES:
        ch = chain(e, "5node", cls=cls)
        assert sum(1 / x for x in ch.g[:4]) == pytest.approx(Rc, rel=1e-12)
        assert ch.C.sum() - extra_C == pytest.approx(e.kappa_tot * 1000, rel=1e-9)
    fd = chain(e, "fd", dx=0.005)
    assert fd.C.sum() - extra_C == pytest.approx(e.kappa_tot * 1000, rel=1e-9)
    assert sum(1 / x for x in fd.g) - extra_R == pytest.approx(Rc, rel=1e-9)


@pytest.mark.parametrize("key", [k for k in sorted(LIB) if LIB[k].back == "ext"])
@pytest.mark.parametrize("mode", ["fd", "5node"])
def test_steady_state_limit_is_u_value(key, mode):
    """At a very long period both chains carry the steady-state U-value."""
    e = LIB[key]
    Y, _ = admittance(e, mode, dx=0.01, period=1e10)
    assert Y == pytest.approx(e.iso()["U"], rel=1e-4)
