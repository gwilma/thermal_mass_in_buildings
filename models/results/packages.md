# Model 3: construction packages in one house

Two-storey semi, 90 m², same windows, ventilation, gains and controls in every case; only the fabric changes. Fine-mesh elements. κ₁ is ISO 13786 daily areal heat capacity × area, per m² floor. Heating: synthetic typical year. Overheating: synthetic hot (DSY-like) year, single zone, TM59-style indicators: (a) % of occupied hours May–Sep at ΔT ≥ 1 K (limit 3%), (b) night hours above 26 °C (limit 32). DH26 is degree-hours above 26 °C, May–Sep.

| Package | κ₁ kJ/m²K | H W/K | Heat kWh/m² | Peak kW | (a) % day vent | (b) h day vent | DH26 day vent | (a) % +night vent | (b) h +night vent | DH26 +night vent | DH26 2050 +night vent | July swing K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Timber frame, suspended timber floor | 71 | 62 | 29.6 | 5.60 | 21.2 | 335 | 4293 | 18.0 | 196 | 3080 | 5990 | 6.7 |
| Timber frame, screed ground floor | 90 | 59 | 25.9 | 5.27 | 17.7 | 337 | 3743 | 13.8 | 202 | 2463 | 5217 | 5.2 |
| SIPs, screed ground floor | 98 | 50 | 22.2 | 5.08 | 17.8 | 357 | 3881 | 13.1 | 210 | 2462 | 5253 | 4.9 |
| ICF, screed ground floor | 108 | 56 | 23.9 | 4.93 | 14.9 | 371 | 3369 | 10.0 | 167 | 2059 | 4754 | 4.4 |
| Masonry (aircrete, dabs), stud partitions | 125 | 54 | 23.4 | 4.82 | 14.6 | 392 | 3544 | 9.0 | 194 | 2092 | 4814 | 3.9 |
| Hempcrete, screed ground floor | 130 | 57 | 24.9 | 4.93 | 13.9 | 386 | 3426 | 8.8 | 187 | 2023 | 4716 | 3.8 |
| Masonry (dense block, dabs), stud partitions | 139 | 56 | 24.1 | 4.65 | 12.5 | 394 | 3293 | 7.4 | 167 | 1872 | 4546 | 3.6 |
| Lined CLT, CLT floor | 143 | 53 | 22.9 | 4.68 | 13.6 | 418 | 3585 | 7.9 | 220 | 2018 | 4746 | 3.4 |
| Exposed CLT, CLT floor | 147 | 55 | 23.6 | 4.67 | 13.1 | 415 | 3524 | 7.5 | 220 | 1976 | 4690 | 3.3 |
| Solid brick + internal insulation | 169 | 61 | 28.7 | 4.96 | 14.6 | 407 | 3724 | 8.5 | 239 | 2174 | 5013 | 3.3 |
| Solid brick + external insulation | 214 | 64 | 30.1 | 4.76 | 10.6 | 412 | 3295 | 5.8 | 207 | 1769 | 4563 | 2.7 |
| Solid brick, uninsulated | 220 | 217 | 94.8 | 6.00 | 6.9 | 293 | 2140 | 4.4 | 178 | 1532 | 3816 | 3.0 |
| Masonry (dense block, wet plaster), block partitions | 245 | 56 | 24.6 | 4.63 | 8.5 | 419 | 3090 | 4.8 | 202 | 1535 | 4186 | 2.2 |
| Heavyweight: dense masonry, exposed slab floors | 295 | 55 | 24.7 | 4.72 | 7.0 | 497 | 2909 | 3.2 | 208 | 1231 | 3898 | 1.5 |

## Five-node vs fine mesh at whole-house level

Same runs with every element as the five-node lump (class from the library). Differences are five-node minus fine mesh.

| Package | Heat kWh/m² Δ | Peak kW Δ | DH26 day vent Δ | DH26 +night vent Δ | (b) h +night vent Δ | July swing Δ K |
|---|---|---|---|---|---|---|
| Timber frame, suspended timber floor | +0.4 | -0.19 | +58 (+1%) | +243 (+8%) | -38 | +1.11 |
| Timber frame, screed ground floor | -0.3 | -0.25 | -82 (-2%) | +15 (+1%) | -33 | +0.45 |
| SIPs, screed ground floor | +0.0 | +0.06 | -84 (-2%) | -63 (-3%) | -3 | -0.09 |
| ICF, screed ground floor | -0.3 | -0.31 | -35 (-1%) | -61 (-3%) | -7 | -0.15 |
| Masonry (aircrete, dabs), stud partitions | +0.2 | -0.06 | -83 (-2%) | -177 (-8%) | +26 | -0.85 |
| Hempcrete, screed ground floor | -0.2 | -0.08 | -45 (-1%) | -60 (-3%) | -5 | -0.16 |
| Masonry (dense block, dabs), stud partitions | +0.3 | -0.01 | +28 (+1%) | -87 (-5%) | +44 | -0.81 |
| Lined CLT, CLT floor | +0.4 | +0.23 | -65 (-2%) | -97 (-5%) | +11 | -0.46 |
| Exposed CLT, CLT floor | +0.2 | +0.14 | -129 (-4%) | -166 (-8%) | +4 | -0.61 |
| Solid brick + internal insulation | -0.1 | -0.00 | +21 (+1%) | +43 (+2%) | -3 | +0.18 |
| Solid brick + external insulation | +0.2 | +0.09 | -31 (-1%) | -66 (-4%) | +9 | -0.31 |
| Solid brick, uninsulated | +0.2 | +0.00 | -2 (-0%) | -9 (-1%) | +3 | -0.05 |
| Masonry (dense block, wet plaster), block partitions | +0.1 | +0.10 | +19 (+1%) | -7 (-0%) | +12 | -0.16 |
| Heavyweight: dense masonry, exposed slab floors | +0.2 | +0.09 | +31 (+1%) | +18 (+1%) | +10 | -0.05 |
