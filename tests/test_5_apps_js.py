"""The web apps' engine (apps/src/core.js) on the same reference cases.

Runs tests/js_cases.js under node and checks it against the published and
analytical values used for the Python models, and against Python itself.
"""
import json, math, os, shutil, subprocess
import numpy as np
import pytest

import room, room5r1c
from buildups import LIB
from conftest import ROOT, still_weather

pytestmark = pytest.mark.js


@pytest.fixture(scope="module")
def js():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    out = subprocess.run([node, os.path.join(ROOT, "tests", "js_cases.js")], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_js_iso13786_annex_d1(js):
    d = js["d1"]
    assert d["U"] == pytest.approx(3.56, abs=0.005)
    assert d["Y"] == pytest.approx(5.70, abs=0.005)
    assert d["f"] * d["U"] == pytest.approx(1.83, abs=0.005)
    assert d["lag_h"] == pytest.approx(5.7, abs=0.05)


def test_js_semi_infinite_admittance(js):
    w = 2 * math.pi / 86400
    Ys = (1 + 1j) * 2.0 / math.sqrt(2 * (2.0 / 2.4e6) / w)
    assert js["deepY"]["Y"] == pytest.approx(abs(1 / (0.13 + 1 / Ys)), rel=2e-3)


@pytest.mark.parametrize("mode", ["fd", "5node"])
def test_js_lumped_plate(js, mode):
    tau = 2600.0
    for q, t in zip(js["plate"][mode], (0.5 * tau, tau)):
        assert q == pytest.approx(math.exp(-t / tau) / 0.13, rel=5e-3)


@pytest.mark.parametrize("key", sorted(LIB))
def test_js_library_matches_python(js, key):
    py, j = LIB[key].iso(), js["lib"][key]
    for k in ("U", "Y", "f", "kappa1"):
        assert j[k] == pytest.approx(py[k], rel=1e-9), k


def test_js_house_matches_python(js, london):
    name = "Timber frame, suspended timber floor"
    m = room.metrics(room.Room(name).run(london["typical"]))
    mh = room.metrics(room.Room(name).run(london["hot"]))
    assert js["house"]["heat"] == pytest.approx(m["heat_kwh_m2"], rel=1e-6)
    assert js["house"]["peak"] == pytest.approx(m["heat_peak_kw"], rel=1e-6)
    assert js["house"]["dh26_hot"] == pytest.approx(mh["dh26"], rel=1e-6)


def test_js_steady_state(js):
    name = "Timber frame, suspended timber floor"
    r = room.Room(name, t_set=20.0, t_setback=20.0, t_open=1e9, q_max=1e9)
    assert js["still_fd"] == pytest.approx(r.run(still_weather(0.0))["Q_heat"][-1], rel=1e-6)
    s = js["still_5r1c"]
    expect = (0.33 * 0.5 * s["V"] + 1 / (1 / s["H_is"] + 1 / (s["H_op"] + s["H_w"]))) * 20.0
    assert s["Q"] == pytest.approx(room5r1c.run(r, still_weather(0.0))["Q_heat"][-1], rel=1e-6)
    assert s["Q"] < expect  # internal gains offset part of the loss


def test_js_time_zone(js):
    """An uploaded EPW in another time zone gets solar noon at about 12:00 local."""
    assert abs(js["denver_noon_hour"] - 12.0) <= 0.5
