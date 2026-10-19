// Thermal mass models: JavaScript port of models/*.py (build-up library,
// ISO 13786, five-node and fine-mesh element chains, single-zone room model,
// 5R1C, metrics, sweeps). Works in a page or a Web Worker; no dependencies.
"use strict";
const TM = (() => {
  const DAY = 86400;

  // ---- materials and build-up library (models/buildups.py) -----------------
  const MAT = {
    "dense concrete": [2.0, 2400, 1000], "precast plank": [1.6, 2200, 1000], "screed": [1.15, 2000, 1000],
    "brick": [0.77, 1700, 800], "dense block": [1.13, 2000, 1000], "medium block": [0.51, 1400, 1000],
    "aerated block": [0.15, 600, 1000], "gypsum plaster": [0.5, 1300, 1000], "lime plaster": [0.7, 1600, 1000],
    "render": [0.8, 1800, 1000], "plasterboard": [0.21, 700, 1000], "CLT": [0.13, 470, 1600],
    "OSB": [0.13, 650, 1700], "chipboard": [0.14, 650, 1700], "timber": [0.13, 500, 1600],
    "mineral wool": [0.035, 30, 1030], "mineral wool + studs": [0.040, 60, 1200], "PIR": [0.022, 30, 1400],
    "EPS": [0.032, 20, 1450], "wood fibre": [0.038, 160, 2100], "hempcrete": [0.07, 330, 1500],
    "rammed earth": [1.0, 1900, 900], "carpet + underlay": [0.06, 200, 1300], "clay soil": [1.5, 1500, 2000],
  };
  const AIR_CAVITY = 0.18, DAB_VOID = 0.10, SERVICE_VOID = 0.17;
  const L = (name, d) => [name, d, ...MAT[name]];
  const R = (name, r) => [name, r];
  const isMass = l => l.length === 5;

  function massClass(layers) {
    const caps = layers.map(l => isMass(l) ? l[3] * l[4] * l[1] : 0);
    const ins = [];
    layers.forEach((l, i) => { if (isMass(l) && l[2] < 0.08 && l[1] > 0.04) ins.push(i); });
    const tot = caps.reduce((a, b) => a + b, 0) || 1;
    if (!ins.length) return "D";
    const first = ins[0], last = ins[ins.length - 1];
    let inner = 0, outer = 0, middle = 0;
    caps.forEach((c, i) => {
      if (i < first) inner += c; else if (i > last) outer += c; else if (!ins.includes(i)) middle += c;
    });
    inner /= tot; outer /= tot; middle /= tot;
    if (middle >= 0.5) return "M";
    if (inner >= 0.5 && outer < 0.2) return "I";
    if (outer >= 0.5 && inner < 0.2) return "E";
    if (inner >= 0.2 && outer >= 0.2) return "IE";
    return "D";
  }

  class Element {
    constructor(key, name, kind, layers, back, opts = {}) {
      this.key = key; this.name = name; this.kind = kind; this.layers = layers; this.back = back;
      this.rsi = opts.rsi ?? ({ floor: 0.17, ceiling: 0.10 }[kind] ?? 0.13);
      this.rse = back === "ext" ? (opts.rse ?? 0.04) : 0.0;
      this.cls = opts.cls || massClass(layers);
    }
    get kappaTot() { return this.layers.filter(isMass).reduce((a, l) => a + l[3] * l[4] * l[1], 0) / 1000; }
    iso(period = DAY) {
      let layers = this.layers.slice(), rse = this.rse;
      if (this.back === "adiabatic") { layers.push(R("adiabatic", 1e6)); rse = 0; }
      else if (this.back === "room") rse = this.rsi;
      else if (this.back === "ground") { layers.push(L("clay soil", 1.0)); rse = 0; }
      return characterise(layers, this.rsi, rse, period);
    }
  }

  const E = (k, n, kind, layers, back, o) => new Element(k, n, kind, layers, back, o);
  const LIB_LIST = [
    E("W1", "Cavity: wet plaster, 100 dense block, 150 MW, brick", "wall", [L("gypsum plaster", .013), L("dense block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W2", "Cavity: board on dabs, 100 dense block, 150 MW, brick", "wall", [L("plasterboard", .0125), R("dab void", DAB_VOID), L("dense block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W3", "Cavity: wet plaster, 100 aircrete, 150 MW, brick", "wall", [L("gypsum plaster", .013), L("aerated block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W4", "Cavity: board on dabs, 100 aircrete, 150 MW, brick", "wall", [L("plasterboard", .0125), R("dab void", DAB_VOID), L("aerated block", .1), L("mineral wool", .15), L("brick", .102)], "ext"),
    E("W5", "Timber frame: board, 140 MW studs, OSB, cavity, brick", "wall", [L("plasterboard", .0125), L("mineral wool + studs", .14), L("OSB", .009), R("cavity", AIR_CAVITY), L("brick", .102)], "ext"),
    E("W6", "Timber frame: board, 140 MW studs, 60 wood fibre, render", "wall", [L("plasterboard", .0125), L("mineral wool + studs", .14), L("wood fibre", .06), L("render", .01)], "ext"),
    E("W7", "SIPs: board, OSB, 142 PUR, OSB, ventilated cladding", "wall", [L("plasterboard", .0125), R("service void", SERVICE_VOID), L("OSB", .015), L("PIR", .142), L("OSB", .015)], "ext"),
    E("W8", "Exposed 100 CLT, 160 wood fibre, render", "wall", [L("CLT", .1), L("wood fibre", .16), L("render", .01)], "ext"),
    E("W9", "Lined CLT: board, 100 CLT, 160 MW, cladding", "wall", [L("plasterboard", .0125), R("service void", SERVICE_VOID), L("CLT", .1), L("mineral wool", .16)], "ext"),
    E("W10", "ICF: board on dabs, 70 EPS, 150 concrete, 70 EPS, render", "wall", [L("plasterboard", .0125), R("dab void", DAB_VOID), L("EPS", .07), L("dense concrete", .15), L("EPS", .07), L("render", .01)], "ext"),
    E("W11", "Solid 215 brick, wet plaster, uninsulated", "wall", [L("gypsum plaster", .013), L("brick", .215)], "ext"),
    E("W12", "Solid brick + IWI: board, 80 PIR, 215 brick", "wall", [L("plasterboard", .0125), L("PIR", .08), L("brick", .215)], "ext"),
    E("W13", "Solid brick + EWI: plaster, 215 brick, 100 EPS, render", "wall", [L("gypsum plaster", .013), L("brick", .215), L("EPS", .1), L("render", .01)], "ext"),
    E("W14", "Hempcrete: lime plaster, 300 hempcrete, lime render", "wall", [L("lime plaster", .015), L("hempcrete", .3), L("render", .015)], "ext"),
    E("W15", "Exposed 300 rammed earth, 120 wood fibre, render", "wall", [L("rammed earth", .3), L("wood fibre", .12), L("render", .01)], "ext"),
    E("F1", "65 screed on 100 PIR on slab", "floor", [L("screed", .065), L("PIR", .1), L("dense concrete", .1)], "ground"),
    E("F2", "Suspended timber: 22 chipboard, 150 MW, vented void", "floor", [L("chipboard", .022), L("mineral wool + studs", .15)], "ext"),
    E("F3", "Exposed 150 slab (polished) on 120 PIR", "floor", [L("dense concrete", .15), L("PIR", .12)], "ground"),
    E("F4", "Carpet on 65 screed on 100 PIR on slab", "floor", [L("carpet + underlay", .012), L("screed", .065), L("PIR", .1), L("dense concrete", .1)], "ground"),
    E("I1", "Timber joist: 22 chipboard, void, 12.5 board ceiling", "floor", [L("chipboard", .022), R("joist void", AIR_CAVITY), L("plasterboard", .0125)], "room"),
    E("I2", "Concrete: 50 screed, 150 plank, exposed soffit", "floor", [L("screed", .05), L("precast plank", .15)], "room"),
    E("I3", "Exposed 160 CLT floor, 50 screed on top", "floor", [L("screed", .05), L("CLT", .16)], "room"),
    E("P1", "Stud partition: 12.5 board each side (half)", "partition", [L("plasterboard", .0125), R("half void", AIR_CAVITY / 2)], "adiabatic"),
    E("P2", "100 dense block, wet plaster both sides (half)", "partition", [L("gypsum plaster", .013), L("dense block", .05)], "adiabatic"),
    E("P3", "100 aircrete, wet plaster both sides (half)", "partition", [L("gypsum plaster", .013), L("aerated block", .05)], "adiabatic"),
    E("P4", "Party wall: plaster, 100 dense block leaf (cavity behind)", "partition", [L("gypsum plaster", .013), L("dense block", .1)], "adiabatic"),
    E("P5", "Party wall: board, 90 MW studs (timber frame twin stud)", "partition", [L("plasterboard", .025), L("mineral wool + studs", .09)], "adiabatic"),
    E("R1", "12.5 board ceiling under 300 MW (cold loft)", "ceiling", [L("plasterboard", .0125), L("mineral wool", .3)], "ext"),
    E("R2", "Exposed 200 concrete roof slab, 150 PIR", "ceiling", [L("dense concrete", .2), L("PIR", .15)], "ext"),
  ];
  const LIB = Object.fromEntries(LIB_LIST.map(e => [e.key, e]));

  // ---- complex numbers and ISO 13786 (physics/iso13786.py) -----------------
  const C = (re, im = 0) => [re, im];
  const cadd = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const csub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const cdiv = (a, b) => { const d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
  const cabs = a => Math.hypot(a[0], a[1]);
  const carg = a => Math.atan2(a[1], a[0]);

  function layerMatrix(d, lam, rho, c, period) {
    const delta = Math.sqrt(lam * period / (Math.PI * rho * c)), x = d / delta;
    const ch = Math.cosh(x), sh = Math.sinh(x), co = Math.cos(x), si = Math.sin(x);
    const z11 = C(ch * co, sh * si);
    const k12 = -delta / (2 * lam), k21 = -lam / delta;
    const z12 = C(k12 * (sh * co + ch * si), k12 * (ch * si - sh * co));
    const z21 = C(k21 * (sh * co - ch * si), k21 * (sh * co + ch * si));
    return [[z11, z12], [z21, z11]];
  }
  const resMatrix = r => [[C(1), C(-r)], [C(0), C(1)]];
  const mmul = (a, b) => [
    [cadd(cmul(a[0][0], b[0][0]), cmul(a[0][1], b[1][0])), cadd(cmul(a[0][0], b[0][1]), cmul(a[0][1], b[1][1]))],
    [cadd(cmul(a[1][0], b[0][0]), cmul(a[1][1], b[1][0])), cadd(cmul(a[1][0], b[0][1]), cmul(a[1][1], b[1][1]))]];

  function characterise(layers, rsi = 0.13, rse = 0.04, period = DAY) {
    let Z = resMatrix(rsi), Rt = rsi + rse, kap = 0;
    for (const l of layers) {
      if (!isMass(l)) { Z = mmul(resMatrix(l[1]), Z); Rt += l[1]; }
      else { const [, d, lam, rho, c] = l; Z = mmul(layerMatrix(d, lam, rho, c, period), Z); Rt += d / lam; kap += rho * c * d; }
    }
    Z = mmul(resMatrix(rse), Z);
    const U = 1 / Rt;
    const Y11 = cdiv(C(-Z[0][0][0], -Z[0][0][1]), Z[0][1]);
    const Y12 = cdiv(C(-1), Z[0][1]);
    const k1 = period / (2 * Math.PI) * cabs(cdiv(csub(Z[0][0], C(1)), Z[0][1]));
    const lead = y => period / (2 * Math.PI) * carg(y) / 3600;
    const lag = ((-lead(Y12)) % 24 + 24) % 24;
    return { U, Y: cabs(Y11), Y_lead_h: lead(Y11), f: cabs(Y12) / U, lag_h: lag, kappa1: k1 / 1000, total_C: kap / 1000 };
  }

  function libRow(e) {
    const r = e.iso();
    return { key: e.key, name: e.name, kind: e.kind, back: e.back, cls: e.cls,
      U: (e.back === "ext" || e.back === "ground") ? r.U : NaN, Y: r.Y, Y_lead_h: r.Y_lead_h,
      f: e.back === "ext" ? r.f : NaN, lag_h: e.back === "ext" ? r.lag_h : NaN, kappa1: r.kappa1, kappa_tot: e.kappaTot };
  }

  // ---- element node chains (models/elements.py) ---------------------------
  const CLASSES = { I: [0, 0, 0, 0, 1], E: [1, 0, 0, 0, 0], IE: [.5, 0, 0, 0, .5], D: [1 / 8, 1 / 4, 1 / 4, 1 / 4, 1 / 8], M: [0, 0, 1, 0, 0] };

  function fdCells(layers, dx) {
    const cells = [];
    for (const l of layers) {
      if (!isMass(l)) { cells.push([1 / l[1], 0]); continue; }
      const [, d, lam, rho, c] = l;
      const n = Math.max(1, Math.ceil(d / dx - 1e-9)), h = d / n;
      for (let i = 0; i < n; i++) cells.push([lam / h, rho * c * h]);
    }
    return cells;
  }
  function cellsToChain(cells) {
    const Cn = new Array(cells.length + 1).fill(0);
    cells.forEach(([, cap], k) => { Cn[k] += cap / 2; Cn[k + 1] += cap / 2; });
    return [Cn, cells.map(c => c[0])];
  }
  const soilCells = () => fdCells([L("clay soil", 1.0)], 0.05);

  function chain(el, mode = "fd", dx = 0.005, cls = null, rse = null) {
    rse = rse ?? el.rse;
    let Cn, g;
    if (mode === "fd") {
      let cells = fdCells(el.layers, dx);
      if (el.back === "ground") cells = cells.concat(soilCells());
      [Cn, g] = cellsToChain(cells);
    } else {
      const Rc = el.layers.reduce((a, l) => a + (isMass(l) ? l[1] / l[2] : l[1]), 0);
      const kap = el.layers.filter(isMass).reduce((a, l) => a + l[3] * l[4] * l[1], 0);
      const frac = CLASSES[cls || el.cls].slice().reverse();
      Cn = frac.map(f => f * kap); g = [6 / Rc, 3 / Rc, 3 / Rc, 6 / Rc];
      if (el.back === "ground") {
        const [Cs, gs] = cellsToChain(soilCells());
        Cn = Cn.slice(0, -1).concat([Cn[4] + Cs[0]], Cs.slice(1)); g = g.concat(gs);
      }
    }
    const backG = el.back === "ext" ? (rse > 0 ? 1 / rse : 1e6) : el.back === "ground" ? 1e6 : 0;
    return { C: Cn, g, backG, n: Cn.length };
  }

  // Complex tridiagonal solve (Thomas) for the chain admittance.
  function admittance(el, mode = "fd", dx = 0.005, cls = null, period = DAY) {
    const ch = chain(el, mode, dx, cls), n = ch.n, w = 2 * Math.PI / period;
    const a = [], b = [], c = [], d = [];
    for (let k = 0; k < n; k++) {
      let diag = 0;
      if (k > 0) diag += ch.g[k - 1];
      if (k < n - 1) diag += ch.g[k];
      if (k === n - 1) diag += ch.backG + (el.back === "room" ? 1 / el.rsi : 0);
      if (k === 0) diag += 1 / el.rsi;
      b.push(C(diag, w * ch.C[k])); a.push(C(k > 0 ? -ch.g[k - 1] : 0)); c.push(C(k < n - 1 ? -ch.g[k] : 0));
      d.push(C(k === 0 ? 1 / el.rsi : 0));
    }
    for (let k = 1; k < n; k++) {
      const m = cdiv(a[k], b[k - 1]);
      b[k] = csub(b[k], cmul(m, c[k - 1])); d[k] = csub(d[k], cmul(m, d[k - 1]));
    }
    const x = new Array(n); x[n - 1] = cdiv(d[n - 1], b[n - 1]);
    for (let k = n - 2; k >= 0; k--) x[k] = cdiv(csub(d[k], cmul(c[k], x[k + 1])), b[k]);
    const Y = cdiv(csub(C(1), x[0]), C(el.rsi));
    return { Y: cabs(Y), lead_h: carg(Y) * 180 / Math.PI / 15 * period / DAY };
  }

  // Implicit Euler, tridiagonal: heat flux into the surface (W/m2) for a room
  // air temperature series via Rsi, far side at Tback. Also returns profiles.
  function stepResponse(el, Troom, dt, mode = "fd", dx = 0.005, cls = null, Tback = 0, keepEvery = 0) {
    const ch = chain(el, mode, dx, cls), n = ch.n;
    const lo = new Float64Array(n), di = new Float64Array(n), up = new Float64Array(n);
    for (let k = 0; k < n; k++) {
      di[k] = ch.C[k] / dt + (k > 0 ? ch.g[k - 1] : 0) + (k < n - 1 ? ch.g[k] : 0);
      if (k > 0) lo[k] = -ch.g[k - 1];
      if (k < n - 1) up[k] = -ch.g[k];
    }
    di[0] += 1 / el.rsi;
    di[n - 1] += ch.backG + (el.back === "room" ? 1 / el.rsi : 0);
    // pre-factorise (Thomas)
    const cp = new Float64Array(n), den = new Float64Array(n);
    den[0] = di[0]; cp[0] = up[0] / den[0];
    for (let k = 1; k < n; k++) { den[k] = di[k] - lo[k] * cp[k - 1]; cp[k] = up[k] / den[k]; }
    let th = new Float64Array(n).fill(Tback);
    const q = new Float64Array(Troom.length), dp = new Float64Array(n), profiles = [];
    for (let i = 0; i < Troom.length; i++) {
      for (let k = 0; k < n; k++) {
        let rhs = ch.C[k] / dt * th[k];
        if (k === 0) rhs += Troom[i] / el.rsi;
        if (k === n - 1) rhs += ch.backG * Tback + (el.back === "room" ? Tback / el.rsi : 0);
        dp[k] = (rhs - (k > 0 ? lo[k] * dp[k - 1] : 0)) / den[k];
      }
      th[n - 1] = dp[n - 1];
      for (let k = n - 2; k >= 0; k--) th[k] = dp[k] - cp[k] * th[k + 1];
      q[i] = (Troom[i] - th[0]) / el.rsi;
      if (keepEvery && i % keepEvery === 0) profiles.push(Float64Array.from(th));
    }
    return { q, profiles, chain: ch };
  }

  // ---- weather (models/weather.py) ----------------------------------------
  let LAT = 51.4792, LON = -0.4506, TZ = 0;  // TZ: clock time zone, hours from GMT
  function solarPosition(hours) {
    const n = hours.length, cosz = new Float64Array(n), az = new Float64Array(n);
    const lat = LAT * Math.PI / 180;
    for (let i = 0; i < n; i++) {
      const h = hours[i], doy = Math.floor(h / 24) + 1;
      const B = 2 * Math.PI * (doy - 81) / 364;
      const decl = 23.45 * Math.PI / 180 * Math.sin(2 * Math.PI * (284 + doy) / 365);
      const eot = 9.87 * Math.sin(2 * B) - 7.53 * Math.cos(B) - 1.5 * Math.sin(B);
      const st = (h % 24) + (4 * (LON - 15 * TZ) + eot) / 60;
      const ha = 15 * (st - 12) * Math.PI / 180;
      const cz = Math.sin(lat) * Math.sin(decl) + Math.cos(lat) * Math.cos(decl) * Math.cos(ha);
      const sz = Math.sqrt(Math.min(Math.max(1 - cz * cz, 0), 1));
      let ca = (Math.sin(decl) - cz * Math.sin(lat)) / (sz * Math.cos(lat) + 1e-12);
      let azn = Math.acos(Math.min(Math.max(ca, -1), 1));
      if (ha > 0) azn = 2 * Math.PI - azn;
      cosz[i] = cz; az[i] = azn - Math.PI;
    }
    return { cosz, az };
  }

  function parseEpw(text) {
    const lines = text.split(/\r?\n/);
    const hdr = lines[0].split(",");
    const T = new Float64Array(8760), GHI = new Float64Array(8760), DNI = new Float64Array(8760), DHI = new Float64Array(8760);
    let i = 0;
    for (let k = 8; k < lines.length && i < 8760; k++) {
      const p = lines[k].split(",");
      if (p.length < 16) continue;
      T[i] = +p[6]; GHI[i] = +p[13]; DNI[i] = +p[14]; DHI[i] = +p[15]; i++;
    }
    if (i < 8760) throw new Error(`The file has ${i} hourly rows; an EPW year needs 8760.`);
    return { T, GHI, DNI, DHI, lat: +hdr[6], lon: +hdr[7], tz: +hdr[8] || 0, name: `${hdr[1]} (${hdr[4] || "EPW"})` };
  }

  function withSun(w) {
    LAT = w.lat ?? LAT; LON = w.lon ?? LON; TZ = w.tz ?? 0;
    const hours = new Float64Array(8760).map((_, i) => i + 0.5);
    const s = solarPosition(hours);
    return Object.assign({}, w, s);
  }

  const HEATWAVE_DAYS = [195, 202];
  function morph(w, variant) {
    const T = Float64Array.from(w.T);
    if (variant === "hot" || variant === "hot2050") {
      const [a, b] = HEATWAVE_DAYS;
      for (let i = 0; i < 8760; i++) {
        const d = i / 24, summer = d >= 151 && d < 243;
        const x = Math.min(Math.max((d - a) / (b - a), 0), 1);
        const bump = d >= a && d < b ? 4 * 0.5 * (1 - Math.cos(2 * Math.PI * x)) : 0;
        T[i] += (summer ? 1.5 : 0) + bump;
        if (variant === "hot2050") T[i] += summer ? 2.5 : 1.5;
      }
    }
    return Object.assign({}, w, { T, variant });
  }

  function planeIrradiance(w, tiltDeg, azDeg, albedo = 0.2) {
    const b = tiltDeg * Math.PI / 180, g = azDeg * Math.PI / 180, out = new Float64Array(8760);
    for (let i = 0; i < 8760; i++) {
      const cz = w.cosz[i], sz = Math.sqrt(Math.min(Math.max(1 - cz * cz, 0), 1));
      const ci = cz * Math.cos(b) + sz * Math.sin(b) * Math.cos(w.az[i] - g);
      const beam = cz > 0 ? w.DNI[i] * Math.max(ci, 0) : 0;
      out[i] = beam + w.DHI[i] * (1 + Math.cos(b)) / 2 + w.GHI[i] * albedo * (1 - Math.cos(b)) / 2;
    }
    return out;
  }

  function runningMean(T, alpha = 0.8) {
    const nd = T.length / 24, Td = new Float64Array(nd);
    for (let d = 0; d < nd; d++) { let s = 0; for (let h = 0; h < 24; h++) s += T[d * 24 + h]; Td[d] = s / 24; }
    const trm = new Float64Array(nd); trm[0] = Td[0];
    for (let d = 1; d < nd; d++) trm[d] = (1 - alpha) * Td[d - 1] + alpha * trm[d - 1];
    const out = new Float64Array(T.length);
    for (let i = 0; i < T.length; i++) out[i] = trm[Math.floor(i / 24)];
    return out;
  }

  // ---- room model (models/room.py) -----------------------------------------
  const HR = 5.13, H_E = 25.0, ALPHA_SOLAR = 0.6;
  const PACKAGES = {
    "Timber frame, suspended timber floor": { wall: "W5", ground: "F2", inter: "I1", part: "P1", party: "P5", ceil: "R1" },
    "Timber frame, screed ground floor": { wall: "W5", ground: "F1", inter: "I1", part: "P1", party: "P5", ceil: "R1" },
    "SIPs, screed ground floor": { wall: "W7", ground: "F1", inter: "I1", part: "P1", party: "P5", ceil: "R1" },
    "Lined CLT, CLT floor": { wall: "W9", ground: "F1", inter: "I3", part: "P1", party: "P5", ceil: "R1" },
    "Exposed CLT, CLT floor": { wall: "W8", ground: "F1", inter: "I3", part: "P1", party: "P5", ceil: "R1" },
    "Masonry (aircrete, dabs), stud partitions": { wall: "W4", ground: "F1", inter: "I1", part: "P1", party: "P4", ceil: "R1" },
    "Masonry (dense block, dabs), stud partitions": { wall: "W2", ground: "F1", inter: "I1", part: "P1", party: "P4", ceil: "R1" },
    "Masonry (dense block, wet plaster), block partitions": { wall: "W1", ground: "F1", inter: "I1", part: "P2", party: "P4", ceil: "R1" },
    "Heavyweight: dense masonry, exposed slab floors": { wall: "W1", ground: "F3", inter: "I2", part: "P2", party: "P4", ceil: "R1" },
    "ICF, screed ground floor": { wall: "W10", ground: "F1", inter: "I1", part: "P1", party: "P4", ceil: "R1" },
    "Hempcrete, screed ground floor": { wall: "W14", ground: "F1", inter: "I1", part: "P1", party: "P4", ceil: "R1" },
    "Solid brick, uninsulated": { wall: "W11", ground: "F2", inter: "I1", part: "P2", party: "P4", ceil: "R1" },
    "Solid brick + internal insulation": { wall: "W12", ground: "F2", inter: "I1", part: "P2", party: "P4", ceil: "R1" },
    "Solid brick + external insulation": { wall: "W13", ground: "F2", inter: "I1", part: "P2", party: "P4", ceil: "R1" },
  };
  const DEFAULTS = {
    floor_area: 90, storey_h: 2.4, wall_h: 5.2, width: 6.0, depth: 7.5,
    win: { S: 10, N: 6, E: 2 }, front: "S", U_win: 1.4, g_win: 0.6, frame: 0.25, shade: 1.0,
    ach_base: 0.5, ach_day: 3.0, ach_night: 2.0, night_vent: false, t_open: 22.0,
    partition_area: 60, gains_scale: 1.0, t_set: 21, t_setback: 16, q_max: 6000,
    mode: "fd", dx: 0.01, dt: 900, overrides: null,
  };
  const ORIENT_AZ = { S: 0, W: 90, N: 180, E: -90 };
  const GAINS_PROFILE = [...Array(7).fill(250), 400, 400, ...Array(9).fill(150), ...Array(5).fill(600), 250];

  function invert(A, n) {
    const M = new Float64Array(n * 2 * n);
    for (let i = 0; i < n; i++) { for (let j = 0; j < n; j++) M[i * 2 * n + j] = A[i * n + j]; M[i * 2 * n + n + i] = 1; }
    const w = 2 * n;
    for (let c = 0; c < n; c++) {
      let p = c, best = Math.abs(M[c * w + c]);
      for (let r = c + 1; r < n; r++) { const v = Math.abs(M[r * w + c]); if (v > best) { best = v; p = r; } }
      if (p !== c) for (let j = 0; j < w; j++) { const t = M[c * w + j]; M[c * w + j] = M[p * w + j]; M[p * w + j] = t; }
      const inv = 1 / M[c * w + c];
      for (let j = 0; j < w; j++) M[c * w + j] *= inv;
      for (let r = 0; r < n; r++) {
        if (r === c) continue;
        const f = M[r * w + c]; if (f === 0) continue;
        for (let j = 0; j < w; j++) M[r * w + j] -= f * M[c * w + j];
      }
    }
    const out = new Float64Array(n * n);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) out[i * n + j] = M[i * w + n + j];
    return out;
  }

  class Room {
    constructor(pkg, kw = {}) {
      const p = Object.assign({}, DEFAULTS, kw); this.p = p;
      const pk = typeof pkg === "string" ? PACKAGES[pkg] : pkg;
      const ov = p.overrides || {};
      const el = role => ov[role] || LIB[pk[role]];
      const Afl = p.floor_area / 2;
      const rot = { S: ["S", "N", "E"], N: ["N", "S", "W"], E: ["E", "W", "S"], W: ["W", "E", "N"] }[p.front];
      const gross = { [rot[0]]: p.width * p.wall_h, [rot[1]]: p.width * p.wall_h, [rot[2]]: p.depth * p.wall_h };
      const win = {}; ["S", "N", "E"].forEach((o, i) => { win[rot[i]] = p.win[o]; });
      this.windows = win;
      const groups = Object.keys(gross).map(o => ["wall", el("wall"), gross[o] - win[o], "single", o]);
      groups.push(["ground", el("ground"), Afl, "single", null], ["inter", el("inter"), Afl, "both", null],
        ["part", el("part"), 2 * p.partition_area, "single", null], ["party", el("party"), p.depth * p.wall_h, "single", null],
        ["ceil", el("ceil"), Afl, "single", null]);
      this.groups = groups;
      let n = 2; const chains = [], off = [];
      for (const [, e] of groups) { const ch = chain(e, p.mode, p.dx); chains.push(ch); off.push(n); n += ch.n; }
      this.n = n; this.chains = chains; this.off = off;
      const Cv = new Float64Array(n), G = new Float64Array(n * n);
      Cv[0] = 10e3 * p.floor_area;
      const couple = (i, j, h) => { G[i * n + i] += h; G[j * n + j] += h; G[i * n + j] -= h; G[j * n + i] -= h; };
      this.surf = []; this.backSrc = [];
      groups.forEach(([role, e, A, face], gi) => {
        const ch = chains[gi], k0 = off[gi];
        for (let k = 0; k < ch.n; k++) Cv[k0 + k] += A * ch.C[k];
        for (let k = 0; k < ch.n - 1; k++) couple(k0 + k, k0 + k + 1, A * ch.g[k]);
        const faces = [[k0, e.rsi, role === "ground" || role === "inter"]];
        if (face === "both") faces.push([k0 + ch.n - 1, 0.10, false]);
        for (const [k, rsi, floorTop] of faces) {
          const hc = Math.max(1 / rsi - HR, 0.5);
          couple(k, 0, hc * A); couple(k, 1, HR * A);
          this.surf.push([k, A, floorTop]);
        }
        if (ch.backG > 0) { const kb = k0 + ch.n - 1; G[kb * n + kb] += A * ch.backG; this.backSrc.push([kb, A * ch.backG, gi]); }
      });
      this.H_win = p.U_win * Object.values(win).reduce((a, b) => a + b, 0);
      G[0] += this.H_win;
      this.V = p.floor_area * p.storey_h;
      this.C = Cv; this.G = G; this._inv = new Map();
    }
    _system(ach) {
      if (!this._inv.has(ach)) {
        const n = this.n, A = Float64Array.from(this.G);
        for (let i = 0; i < n; i++) A[i * n + i] += this.C[i] / this.p.dt;
        A[0] += 0.33 * ach * this.V;
        const Ainv = invert(A, n), u = new Float64Array(n);
        for (let i = 0; i < n; i++) u[i] = Ainv[i * n];
        this._inv.set(ach, [Ainv, u]);
      }
      return this._inv.get(ach);
    }
    inputs(w) {
      const p = this.p;
      const irr = {}; for (const o of "SNEW") irr[o] = planeIrradiance(w, 90, ORIENT_AZ[o]);
      const qSol = new Float64Array(8760);
      for (const [o, Aw] of Object.entries(this.windows))
        for (let h = 0; h < 8760; h++) qSol[h] += Aw * (1 - p.frame) * p.g_win * (irr[o][h] > 150 ? p.shade : 1) * irr[o][h];
      const qInt = new Float64Array(8760).map((_, h) => GAINS_PROFILE[h % 24] * p.gains_scale);
      let Tm = 0; for (let h = 0; h < 8760; h++) Tm += w.T[h]; Tm /= 8760;
      return { irr, qSol, qInt, Tground: Tm };
    }
    run(w, onProgress) {
      const p = this.p, n = this.n, T_out = w.T;
      const { irr, qSol, qInt, Tground } = this.inputs(w);
      const nb = this.backSrc.length;
      const backT = this.backSrc.map(([, , gi]) => {
        const [role, e, , , o] = this.groups[gi];
        if (e.back === "ground") return new Float64Array(8760).fill(Tground);
        if (role === "wall") return new Float64Array(8760).map((_, h) => T_out[h] + ALPHA_SOLAR * irr[o][h] / H_E);
        return T_out;
      });
      const sA = this.surf.reduce((a, s) => a + s[1], 0), fA = this.surf.reduce((a, s) => a + (s[2] ? s[1] : 0), 0);
      const solSplit = this.surf.map(s => 0.6 * (s[2] ? s[1] / fA : 0) + 0.4 * s[1] / sA);
      const radSplit = this.surf.map(s => s[1] / sA);
      const dt = p.dt, sub = Math.round(3600 / dt);
      let x = new Float64Array(n).fill(18), x0 = new Float64Array(n);
      const rhs = new Float64Array(n), src = new Float64Array(n), Cdt = this.C.map(c => c / dt);
      const out = { T_air: new Float64Array(8760), T_op: new Float64Array(8760), T_mrt: new Float64Array(8760), Q_heat: new Float64Array(8760), ach: new Float64Array(8760) };
      let Topp = 20, Tap = 20;
      for (let h = 0; h < 8760; h++) {
        const hod = h % 24;
        const tset = ((hod >= 7 && hod < 9) || (hod >= 16 && hod < 23)) ? p.t_set : p.t_setback;
        const want = Topp > p.t_open && T_out[h] < Tap;
        let ach = p.ach_base;
        if (want && hod >= 7 && hod < 23) ach += p.ach_day; else if (want && p.night_vent) ach += p.ach_night;
        const [Ainv, u] = this._system(ach);
        src.fill(0);
        src[0] = this.H_win * T_out[h] + 0.33 * ach * this.V * T_out[h] + 0.5 * qInt[h];
        for (let b = 0; b < nb; b++) src[this.backSrc[b][0]] += this.backSrc[b][1] * backT[b][h];
        this.surf.forEach((s, i) => { src[s[0]] += solSplit[i] * qSol[h] + radSplit[i] * 0.5 * qInt[h]; });
        let a0 = 0, a1 = 0, a2 = 0, a3 = 0;
        for (let s = 0; s < sub; s++) {
          for (let i = 0; i < n; i++) rhs[i] = Cdt[i] * x[i] + src[i];
          for (let i = 0; i < n; i++) { let acc = 0; const r = i * n; for (let j = 0; j < n; j++) acc += Ainv[r + j] * rhs[j]; x0[i] = acc; }
          const Q = Math.min(Math.max((tset - x0[0]) / u[0], 0), p.q_max);
          for (let i = 0; i < n; i++) x[i] = x0[i] + Q * u[i];
          a0 += x[0]; a1 += 0.5 * (x[0] + x[1]); a2 += x[1]; a3 += Q;
        }
        out.T_air[h] = a0 / sub; out.T_op[h] = a1 / sub; out.T_mrt[h] = a2 / sub; out.Q_heat[h] = a3 / sub; out.ach[h] = ach;
        Tap = out.T_air[h]; Topp = out.T_op[h];
        if (onProgress && h % 730 === 0) onProgress(h / 8760);
      }
      out.T_out = T_out;
      return out;
    }
    kappaSummary() {
      let k1 = 0, kt = 0;
      for (const [, e, A, face] of this.groups) { k1 += e.iso().kappa1 * A * (face === "both" ? 2 : 1); kt += e.kappaTot * A; }
      return [k1 / this.p.floor_area, kt / this.p.floor_area];
    }
    fabricH() {
      let H = this.H_win;
      for (const [, e, A] of this.groups) if (e.back === "ext" || e.back === "ground") H += e.iso().U * A;
      return H;
    }
  }

  // ---- 5R1C (models/room5r1c.py) -------------------------------------------
  const R_SE = 0.04;
  function params5r1c(room) {
    const p = room.p, Af = p.floor_area, At = 4.5 * Af;
    let k1A = 0, k1sqA = 0, Hout = 0, Hg = 0; const opaqueSol = { S: 0, N: 0, E: 0, W: 0 };
    for (const [role, e, A, face, o] of room.groups) {
      const r = e.iso(), mult = face === "both" ? 2 : 1;
      k1A += r.kappa1 * 1000 * A * mult; k1sqA += (r.kappa1 * 1000) ** 2 * A * mult;
      if (e.back === "ext") { Hout += r.U * A; if (role === "wall") opaqueSol[o] += ALPHA_SOLAR * R_SE * r.U * A; }
      else if (e.back === "ground") Hg += r.U * A;
    }
    const Cm = k1A, Am = Cm * Cm / k1sqA;
    return { Af, At, Cm, Am, H_is: 3.45 * At, H_ms: 9.1 * Am, H_w: room.H_win, H_op: Hout + Hg, H_out: Hout, H_g: Hg, opaqueSol, V: room.V };
  }
  function run5r1c(room, w) {
    const p = room.p, q = params5r1c(room);
    const { H_ms, H_is, H_w } = q, H_em = 1 / (1 / q.H_op - 1 / H_ms);
    const { irr, qSol: qWin, qInt, Tground } = room.inputs(w);
    const qSol = Float64Array.from(qWin);
    for (const o of "SNEW") for (let h = 0; h < 8760; h++) qSol[h] += q.opaqueSol[o] * irr[o][h];
    const fst = 1 - q.Am / q.At - H_w / (9.1 * q.At), Cm = q.Cm / 3600;
    const out = { T_air: new Float64Array(8760), T_op: new Float64Array(8760), T_s: new Float64Array(8760), T_m: new Float64Array(8760), Q_heat: new Float64Array(8760), ach: new Float64Array(8760) };
    let Tmp = 18, Topp = 20, Tap = 20;
    for (let h = 0; h < 8760; h++) {
      const hod = h % 24, To = w.T[h];
      const tset = ((hod >= 7 && hod < 9) || (hod >= 16 && hod < 23)) ? p.t_set : p.t_setback;
      const want = Topp > p.t_open && To < Tap;
      const ach = p.ach_base + (want && hod >= 7 && hod < 23 ? p.ach_day : (want && p.night_vent ? p.ach_night : 0));
      const Hve = 0.33 * ach * q.V, H1 = 1 / (1 / Hve + 1 / H_is), H2 = H1 + H_w, H3 = 1 / (1 / H2 + 1 / H_ms);
      const te = (q.H_out * To + q.H_g * Tground) / q.H_op, ts = To;
      const pia = 0.5 * qInt[h], pst = fst * (0.5 * qInt[h] + qSol[h]), pm = q.Am / q.At * (0.5 * qInt[h] + qSol[h]);
      const den = Cm + 0.5 * (H3 + H_em);
      const pmt = pm + H_em * te + H3 * (pst + H_w * ts + H1 * (pia / Hve + ts)) / H2;
      let Tmt = (Tmp * (Cm - 0.5 * (H3 + H_em)) + pmt) / den;
      let Ts = (H_ms * 0.5 * (Tmt + Tmp) + pst + H_w * ts + H1 * (ts + pia / Hve)) / (H_ms + H_w + H1);
      let Ta = (H_is * Ts + Hve * ts + pia) / (H_is + Hve);
      const dTmt = H3 * H1 / (H2 * Hve) / den, dTs = (H_ms * 0.5 * dTmt + H1 / Hve) / (H_ms + H_w + H1), dTa = (H_is * dTs + 1) / (H_is + Hve);
      const Q = Math.min(Math.max((tset - Ta) / dTa, 0), p.q_max);
      Tmt += Q * dTmt; Ts += Q * dTs; Ta += Q * dTa;
      const Top = 0.3 * Ta + 0.7 * Ts;
      out.T_air[h] = Ta; out.T_op[h] = Top; out.T_s[h] = Ts; out.T_m[h] = 0.5 * (Tmt + Tmp); out.Q_heat[h] = Q; out.ach[h] = ach;
      Tmp = Tmt; Topp = Top; Tap = Ta;
    }
    out.T_out = w.T;
    return out;
  }

  // ---- metrics (room.metrics) ----------------------------------------------
  function metrics(out, floorArea = 90) {
    const Trm = runningMean(out.T_out);
    let heat = 0, peak = 0, occ = 0, occOver = 0, nb = 0, dh = 0, h28 = 0, tmax = -1e9, swing = 0;
    for (let h = 0; h < 8760; h++) {
      const d = Math.floor(h / 24), hod = h % 24, ms = d >= 120 && d < 273, Top = out.T_op[h];
      heat += out.Q_heat[h]; peak = Math.max(peak, out.Q_heat[h]);
      if (ms && hod >= 9 && hod < 22) { occ++; if (Math.round(Top - (0.33 * Trm[h] + 21.8)) >= 1) occOver++; }
      if ((hod >= 22 || hod < 7) && Top > 26) nb++;
      if (ms) dh += Math.max(Top - 26, 0);
      if (Top > 28) h28++;
      tmax = Math.max(tmax, Top);
    }
    for (let d = 181; d < 212; d++) {
      let mx = -1e9, mn = 1e9;
      for (let k = 0; k < 24; k++) { const v = out.T_op[d * 24 + k]; mx = Math.max(mx, v); mn = Math.min(mn, v); }
      swing += mx - mn;
    }
    return { heat_kwh_m2: heat / 1000 / floorArea, heat_peak_kw: peak / 1000, tm59a_pct: 100 * occOver / occ, tm59b_h: nb, dh26: dh, h28, T_op_max: tmax, jul_swing: swing / 31 };
  }

  // ---- sweeps (models/sweeps.py) -------------------------------------------
  const SWEEP_BASE = "Timber frame, screed ground floor";
  const T_LIST = [0, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3];
  function massOverrides(t, wallMw = 0.14) {
    const ov = { wall: new Element("Wv", "Timber frame (variable MW)", "wall", [L("plasterboard", .0125), L("mineral wool + studs", wallMw), L("OSB", .009), R("cavity", AIR_CAVITY), L("brick", .102)], "ext") };
    if (t <= 0) Object.assign(ov, { ground: new Element("G0", "Chipboard on PIR on slab", "floor", [L("chipboard", .022), L("PIR", .1), L("dense concrete", .1)], "ground"), inter: LIB.I1, part: LIB.P1, party: LIB.P5 });
    else Object.assign(ov, {
      ground: new Element("Gt", "dense on PIR", "floor", [L("dense concrete", t), L("PIR", .1), L("dense concrete", .1)], "ground"),
      inter: new Element("It", "slab", "floor", [L("dense concrete", t)], "room"),
      part: new Element("Pt", "dense wall (half)", "partition", [L("dense concrete", t)], "adiabatic"),
      party: new Element("Qt", "dense leaf", "partition", [L("dense concrete", t)], "adiabatic"),
    });
    return ov;
  }
  const MORRIS_PARAMS = [
    ["exposed mass t (m)", 0.0, 0.3], ["glazing area ×", 0.5, 1.5], ["blind factor (closed)", 0.2, 1.0],
    ["day purge ACH", 0.0, 6.0], ["night vent ACH", 0.0, 4.0], ["background ACH", 0.3, 1.0],
    ["internal gains ×", 0.6, 1.4], ["wall insulation (m MW)", 0.09, 0.24],
  ];
  function morrisRoom(x, extra = {}) {
    const v = x.map((xi, i) => MORRIS_PARAMS[i][1] + xi * (MORRIS_PARAMS[i][2] - MORRIS_PARAMS[i][1]));
    const win = { S: 10 * v[1], N: 6 * v[1], E: 2 * v[1] };
    return Object.assign({ overrides: massOverrides(v[0], v[7]), win, shade: v[2], ach_day: v[3], night_vent: v[4] > 0, ach_night: v[4], ach_base: v[5], gains_scale: v[6] }, extra);
  }
  // Seeded PRNG (mulberry32) for Morris trajectories
  function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function morrisDesign(r = 10, levels = 4, seed = 3) {
    const k = MORRIS_PARAMS.length, delta = levels / (2 * (levels - 1)), R_ = rng(seed);
    const grid = [...Array(levels).keys()].map(i => i / (levels - 1)).filter(g => g <= 1 - delta + 1e-9);
    const trajs = [];
    for (let t = 0; t < r; t++) {
      let x = Array.from({ length: k }, () => grid[Math.floor(R_() * grid.length)]);
      const order = [...Array(k).keys()]; for (let i = k - 1; i > 0; i--) { const j = Math.floor(R_() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
      const pts = [{ x: x.slice(), i: -1 }];
      for (const i of order) { const x2 = x.slice(); x2[i] = x[i] + delta <= 1 + 1e-9 ? x[i] + delta : x[i] - delta; pts.push({ x: x2, i, dx: x2[i] - x[i] }); x = x2; }
      trajs.push(pts);
    }
    return trajs;
  }

  return { MAT, LIB, LIB_LIST, Element, L, R, massClass, characterise, libRow, CLASSES, chain, admittance, stepResponse,
    parseEpw, withSun, morph, planeIrradiance, runningMean, PACKAGES, DEFAULTS, Room, params5r1c, run5r1c, metrics,
    SWEEP_BASE, T_LIST, massOverrides, MORRIS_PARAMS, morrisRoom, morrisDesign, AIR_CAVITY, DAB_VOID, SERVICE_VOID, GAINS_PROFILE };
})();
if (typeof module !== "undefined") module.exports = TM;
