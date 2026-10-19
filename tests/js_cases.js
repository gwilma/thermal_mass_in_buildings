// Runs the web apps' engine (apps/src/core.js) on the reference cases used by
// the Python tests and prints the results as JSON for test_5_apps_js.py.
"use strict";
const fs = require("fs"), path = require("path");
const TM = require(path.join(__dirname, "..", "apps", "src", "core.js"));
const root = path.join(__dirname, "..");
const out = {};

// ISO 13786 Annex D, case D.1
out.d1 = TM.characterise([["concrete", 0.2, 1.8, 2400, 1000]]);

// semi-infinite admittance (fine mesh) and lumped plate step response
const deep = new TM.Element("t", "deep", "wall", [["concrete", 1.0, 2.0, 2400, 1000]], "adiabatic", { rsi: 0.13 });
out.deepY = TM.admittance(deep, "fd", 0.002);
const plate = new TM.Element("p", "plate", "wall", [["plate", 0.01, 1000, 2000, 1000]], "adiabatic", { rsi: 0.13 });
out.plate = {};
for (const mode of ["fd", "5node"]) {
  const q = TM.stepResponse(plate, new Float64Array(Math.round(3 * 2600 / 5)).fill(1), 5, mode, 0.005, "D").q;
  out.plate[mode] = [259, 519].map(i => q[i]);   // t = 0.5 tau and tau
}

// library: every build-up
out.lib = Object.fromEntries(TM.LIB_LIST.map(e => [e.key, e.iso()]));

// default house on Heathrow TMYx, and a still year for steady state
const london = TM.withSun(TM.parseEpw(fs.readFileSync(path.join(root, "models", "weather_data",
  "GBR_ENG_London-Heathrow.Intl.AP.037720_TMYx.2011-2025.epw"), "latin1")));
const pkg = "Timber frame, suspended timber floor";
const m = TM.metrics(new TM.Room(pkg).run(london));
const mh = TM.metrics(new TM.Room(pkg).run(TM.morph(london, "hot")));
out.house = { heat: m.heat_kwh_m2, peak: m.heat_peak_kw, dh26_hot: mh.dh26 };
const z = new Float64Array(8760);
const still = { T: z, GHI: z, DNI: z, DHI: z, cosz: new Float64Array(8760).fill(-1), az: z };
const rs = new TM.Room(pkg, { t_set: 20, t_setback: 20, t_open: 1e9, q_max: 1e9 });
out.still_fd = rs.run(still).Q_heat[8759];
const q5 = TM.params5r1c(rs);
out.still_5r1c = { Q: TM.run5r1c(rs, still).Q_heat[8759], H_is: q5.H_is, H_op: q5.H_op, H_w: q5.H_w, V: q5.V };

// time zone: Denver solar noon on 21 June
const denver = TM.withSun(TM.parseEpw(fs.readFileSync(path.join(root, "models", "weather_data",
  "USA_CO_Denver.Intl.AP.725650_TMY3.epw"), "latin1")));
let best = -1, hBest = 0;
for (let h = 171 * 24; h < 172 * 24; h++) if (denver.cosz[h] > best) { best = denver.cosz[h]; hBest = h - 171 * 24 + 0.5; }
out.denver_noon_hour = hBest;

process.stdout.write(JSON.stringify(out));
