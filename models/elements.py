"""Turn a build-up into a 1D node chain (shared by models 2 and 3).

Two discretisations of the same element:
  "fd"    vertex-centred finite differences, cells no thicker than dx
  "5node" the ISO 52016-1 / HEM five-node lump: conductances 6/Rc, 3/Rc,
          3/Rc, 6/Rc between nodes and the total areal heat capacity
          placed on the nodes by mass distribution class (I, E, IE, D, M)

Node 0 is always the room-side surface. Capacities are J/m2K and
conductances W/m2K, per m2 of element. The far-side connection is left to
the caller except for ground floors, whose 1 m of soil is appended (in both
modes) and whose last node is tied to the ground temperature with
`back_g`.
"""
import math
import numpy as np

from buildups import MAT, L

CLASSES = {  # fraction of kappa_tot on nodes from the EXTERNAL node to the internal node
    "I": [0, 0, 0, 0, 1], "E": [1, 0, 0, 0, 0], "IE": [.5, 0, 0, 0, .5],
    "D": [1/8, 1/4, 1/4, 1/4, 1/8], "M": [0, 0, 1, 0, 0],
}


class Chain:
    def __init__(self, C, g, back_g):
        self.C = np.asarray(C, float)   # node capacities, len n
        self.g = np.asarray(g, float)   # conductances between node k and k+1, len n-1
        self.back_g = back_g            # conductance from last node to the far-side temperature
        self.n = len(self.C)


def _fd_cells(layers, dx):
    cells = []  # (conductance W/m2K, capacity J/m2K)
    for lay in layers:
        if len(lay) == 2:
            cells.append((1.0 / lay[1], 0.0))
        else:
            _, d, lam, rho, c = lay
            n = max(1, math.ceil(d / dx - 1e-9))
            h = d / n
            cells += [(lam / h, rho * c * h)] * n
    return cells


def _cells_to_chain(cells):
    n = len(cells) + 1
    C = np.zeros(n)
    for k, (_, cap) in enumerate(cells):
        C[k] += cap / 2; C[k + 1] += cap / 2
    return C, [g for g, _ in cells]


def soil_cells(dx=0.05):
    return _fd_cells([L("clay soil", 1.0)], dx)


def chain(el, mode="fd", dx=0.005, cls=None, rse=None):
    """Node chain for Element `el`. `rse` overrides the external surface
    resistance (the room model uses it to put sol-air on the back node)."""
    rse = el.rse if rse is None else rse
    if mode == "fd":
        cells = _fd_cells(el.layers, dx)
        if el.back == "ground":
            cells += soil_cells()
        C, g = _cells_to_chain(cells)
    elif mode == "5node":
        Rc = sum(l[1] if len(l) == 2 else l[1] / l[2] for l in el.layers)
        kap = sum(l[3] * l[4] * l[1] for l in el.layers if len(l) == 5)
        frac = CLASSES[cls or el.cls][::-1]  # reverse: node 0 is internal here
        C = [f * kap for f in frac]
        g = [6 / Rc, 3 / Rc, 3 / Rc, 6 / Rc]
        if el.back == "ground":
            sc = soil_cells()
            Cs, gs = _cells_to_chain(sc)
            C = list(C[:-1]) + [C[-1] + Cs[0]] + list(Cs[1:])
            g = g + gs
        C = np.array(C, float)
    else:
        raise ValueError(mode)
    if el.back == "ext":
        back_g = 1.0 / rse if rse > 0 else 1e6
    elif el.back == "ground":
        back_g = 1e6
    else:
        back_g = 0.0  # adiabatic, or "room" (the room model couples it)
    return Chain(C, g, back_g)


def conductance_matrix(ch):
    n = ch.n
    G = np.zeros((n, n))
    for k, gk in enumerate(ch.g):
        G[k, k] += gk; G[k + 1, k + 1] += gk; G[k, k + 1] -= gk; G[k + 1, k] -= gk
    G[-1, -1] += ch.back_g
    return G


def admittance(el, mode="fd", dx=0.005, cls=None, period=86400.0):
    """|Y| (W/m2K) with a 1 K sinusoidal room temperature, far side steady.
    For a "room"-backed element the far face sees a steady room via Rsi."""
    ch = chain(el, mode, dx, cls)
    w = 2 * math.pi / period
    A = conductance_matrix(ch).astype(complex) + 1j * w * np.diag(ch.C)
    if el.back == "room":
        A[-1, -1] += 1 / el.rsi
    A[0, 0] += 1 / el.rsi
    b = np.zeros(ch.n, complex); b[0] = 1 / el.rsi
    th = np.linalg.solve(A, b)
    Y = (1 - th[0]) / el.rsi
    return abs(Y), math.degrees(np.angle(Y)) / 15 * period / 86400


def step_response(el, Troom, dt, mode="fd", dx=0.005, cls=None, Tback=0.0):
    """Implicit-Euler response of an element to a room air temperature series
    (via Rsi), far side at Tback. Returns heat flux into the surface, W/m2."""
    ch = chain(el, mode, dx, cls)
    G = conductance_matrix(ch)
    if el.back == "room":
        G[-1, -1] += 1 / el.rsi
    G[0, 0] += 1 / el.rsi
    A = np.diag(ch.C / dt) + G
    Ainv = np.linalg.inv(A)
    th = np.full(ch.n, Tback, float)
    q = np.empty(len(Troom))
    for i, Tr in enumerate(Troom):
        b = ch.C / dt * th
        b[0] += Tr / el.rsi
        b[-1] += ch.back_g * Tback + (Tback / el.rsi if el.back == "room" else 0.0)
        th = Ainv @ b
        q[i] = (Tr - th[0]) / el.rsi
    return q
