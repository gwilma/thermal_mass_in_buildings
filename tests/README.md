# Test cases for the thermal mass models

```
python3 -m pip install pytest
python3 -m pytest tests                  # everything, about 70 s
python3 -m pytest tests -m "not slow"    # skip the full-year runs
```

The JavaScript tests need `node` and the Excel tests need LibreOffice; each
group is skipped when its tool is missing. Last full run: 281 passed and
2 expected failures (the BESTEST case 900 loads described below).

Each test checks a model against one of three kinds of reference:

- **Published**: a case from a standard, with the standard's reference values.
- **Analytical**: a closed-form solution from the heat conduction literature.
- **Consistency**: a property the model must have, such as energy
  conservation, linearity or Python-JavaScript-Excel agreement.

## Published reference cases

### ISO 13786 Annex D, case D.1: 200 mm concrete wall

λ 1.8 W/mK, ρ 2400 kg/m³, c 1000 J/kgK, Rsi 0.13, Rse 0.04, 24 h period.
The reference values are as reproduced on QuickField's ISO 13786 validation
page; I could not reach the standard's own text.

| Quantity | Reference | Python | Web apps | Excel |
|---|---|---|---|---|
| Penetration depth δ, m | 0.144 | 0.1436 | | |
| U, W/m²K | 3.56 | 3.557 | 3.557 | 3.557 |
| \|Y11\| internal admittance, W/m²K | 5.70 | 5.704 | 5.704 | 5.704 |
| \|Y22\| external admittance, W/m²K | 11.59 | 11.592 | | |
| \|Y12\| periodic transmittance, W/m²K | 1.83 | 1.827 | 1.827 | 1.827 |
| Time shift of Y12, h | about 5.7 | 5.68 | 5.68 | 5.68 |

All three implementations reproduce every reference value to its quoted
precision. The Excel check types the wall into the Build-up Explorer's Custom
row and recalculates.

### ANSI/ASHRAE Standard 140 (IEA BESTEST), cases 600, 900, 600FF and 900FF

The test building is an 8 × 6 × 2.7 m single zone with 12 m² of south glazing,
200 W of internal gains and 0.5 ACH. Heating is on below 20 °C and cooling
above 27 °C; the FF cases run free-floating. The weather is Denver TMY3
(725650, from climate.onebuilding.org), the file the 2020 and later editions
use.

The cases run on the house model's own engine, `room.py`, through
`models/bestest.py`. Glazing solar uses the Standard's double clear glass (Fresnel
angular transmittance) and a Perez sky. Results:

| Case and metric | Range | Fine mesh | Five-node | Result |
|---|---|---|---|---|
| 600 annual heating, MWh | 3.75–4.98 | 4.76 | 5.39 | pass |
| 600 annual cooling, MWh | 5.00–6.83 | 6.72 | 7.55 | pass |
| 900 annual heating, MWh | 1.379–1.814 | 1.88 | 2.34 | 3% high (expected failure) |
| 900 annual cooling, MWh | 2.267–2.714 | 3.05 | 3.68 | 12% high (expected failure) |
| 900FF maximum, °C | 43.3–46.0 | 44.9 | 47.4 | pass |
| 900FF minimum, °C | 0.6–2.2 | 1.4 | −1.1 | pass |
| 600FF maximum / minimum, °C | (no range found) | 65.8 / −11.4 | 78.1 / −12.6 | |
| Heating ratio 900/600 | 0.28–0.48 | 0.39 | | pass |
| Cooling ratio 900/600 | 0.33–0.54 | 0.45 | | pass |

Sources for the ranges:

- **Case 600:** ANSI/ASHRAE 140-2020 Addendum b, Tables A3-1 and A3-2.
- **Case 900 and 900FF:** 140-2023 Annex B8, as transcribed by the fluxion
  project (github.com/anchapin/fluxion, PR 4414). I have not checked these
  against the Standard itself.
- **Ratios:** the widest ratios the ranges above allow.

The fine mesh passes every case with a published range except the
heavyweight 900 loads. They are kept as expected failures with the numbers
in the reason, so a fix shows up as an unexpected pass. Likely causes:

- The model has no long-wave exchange with the sky.
- Interior surface coefficients are fixed rather than calculated.
- No solar is reflected back out of the window.
- The Annex B8 values are a secondary transcription.

The five-node lump overstates every load. That is the whole-building
symptom of its too-high daily admittance behind linings (the model 2
finding), and a test pins it.

## Analytical cases

| Model | Case | Known solution | Tolerance |
|---|---|---|---|
| 1 | Semi-infinite solid, periodic | Y = 1/(Rsi + 1/((1+i)λ/δ)), lead 3 h without Rsi | 1e-6 |
| 1 | Thin lumped layer between Rsi and Rse | Z11 = 1 + iωCRse, Z12 = −(Rsi + Rse + iωCRsiRse) | 1e-4 |
| 1 | Pure resistance | \|Y\| = U, f = 1, no lag, κ = 0 | exact |
| 1 | Reciprocity | det Z = 1; Y12 the same from either side; Y22 and κ2 equal the reversed wall's Y11 and κ1 | 1e-9 |
| 1 | U-value of all 18 outdoor-facing build-ups | ISO 6946 resistance sum | 1e-12 |
| 2 | Step on a semi-infinite solid (Carslaw and Jaeger 2.5) | q = λ/√(παt), at 1 to 12 h | 1% |
| 2 | Step on a 100 mm slab with an insulated back (C&J 3.3) | Fourier series, at 0.5 to 8 h | 1% |
| 2 | Lumped plate, fine mesh and all five five-node classes | q = e^(−t/τ)/Rsi, τ = Rsi·C | 0.5% |
| 2 | Deep slab, daily cycle (C&J 2.6) | as model 1 | 0.2% |
| 2 | Energy after a step | ∫q dt = ρcd × 1 K | 0.1% |
| 2 | Mesh convergence | error falls about 4× per halving (second order) | ratio > 3 |
| 2 | Very long period, all outdoor-facing build-ups, both chains | \|Y\| → U | 1e-4 |
| 3 | Steady state, every package, fine mesh and five-node | Q = (ΣUA + windows + 0.33nV) × ΔT, radiant exchange off | 1e-5 |
| 3 | Steady state, 5R1C, every package | Q = [H_ve + 1/(1/H_is + 1/(H_op + H_w))] × ΔT | 1e-6 |
| 3 | Convective gain | 500 W of gain cuts steady heating by 500 W (linearity) | 1e-6 |
| 3 | Solar noon on 21 June, London and Denver | peak at 12:00 local standard time ±10 min, elevation 90 − φ + 23.44° | 0.3° |
| 3 | TM52 running mean | constant in gives constant out; a step decays as 0.8ⁿ | exact |
| 3 | Overheating metrics on a synthetic year | known counts for (a), (b), DH26 and h28 | exact |
| 4 | Morris on a linear function | μ = aᵢ, μ* = \|aᵢ\|, σ = 0 | exact |
| 4 | Morris on x₀x₁ + 3x₂ | σ > 0 for the interacting pair, σ = 0 and μ = 3 for x₂ | exact |
| 4 | Morris on the Sobol g-function (Saltelli et al. 2008) | μ* ranks inputs in order of aᵢ | ordering |
| 4 | κ₁ of a deep exposed slab | semi-infinite limit \|1/(Rsi + 1/Ys)\|/ω | 1e-4 |
| Excel | Conduction Lab, 200 mm insulated slab, 24 ± 4 °C | peak flux = 4\|Y\|, with Y from ISO 13786 | 1% |

## Consistency and regression

- **Re-runs:** every package re-runs to the published `results/packages.csv`
  (heating, 5R1C heating and hot-year DH26), and one point of sweep B
  re-runs to `results/sweeps.json`.
- **Sweep results:** degree-hours fall with night ventilation at every
  thickness, and with thickness at every ventilation rate. Each extra
  millimetre buys less July swing reduction beyond about 100 mm.
- **Sweep construction:** κ_tot rises exactly linearly with the added dense
  layer.
- **Five-node chain:** for every build-up and class, the conductances add in
  series to 1/Rc and the capacities sum to κ_tot.
- **Web apps (`core.js` under node):** every library build-up, the default
  house's heating, peak and hot-year DH26, the still-year runs, and the
  Denver time zone all match Python to 1e-6.
- **Excel:** the Library results sheet matches Python for all 29 build-ups.
  The Conduction Lab matches the Python chain on the same mesh. The House
  Simulator matches Python 5R1C. The Mass Sweeps interpolator matches a hand
  calculation.

## Fixes the tests prompted

- **Solar time:** `weather.solar_position` and the apps' copy ignored the
  EPW time zone. That was harmless for London, which is on GMT, but put
  Denver's noon about 7 hours out, and it would have done the same to any
  file a user uploads to the House Simulator. Both now read the time zone
  from the EPW header.
- **5R1C inputs:** `room5r1c.py` ignored the gains, radiant fraction,
  window-solar and air-property inputs. It now takes them from the room, as
  the full model does. Default results are unchanged.
- **New options:** `room.py` gained generic-zone options for the BESTEST
  cases: custom geometry, ideal cooling, constant gains, given window solar,
  air capacity and air density. `weather.plane_irradiance` gained an
  optional Perez sky. The house defaults are unchanged; the regression test
  proves it.
