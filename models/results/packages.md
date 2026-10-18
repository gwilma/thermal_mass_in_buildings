# Model 3: construction packages in one house

Two-storey semi, 90 m², same windows, ventilation, gains and controls in every case; only the fabric changes. Fine-mesh elements. κ₁ is ISO 13786 daily areal heat capacity × area, per m² floor. Heating: Heathrow TMYx 2011-2025. Overheating: the same file morphed into a hot (DSY-like) year, single zone, TM59-style indicators: (a) % of occupied hours May–Sep at ΔT ≥ 1 K (limit 3%), (b) night hours above 26 °C (limit 32). DH26 is degree-hours above 26 °C, May–Sep.

| Package | κ₁ kJ/m²K | H W/K | Heat kWh/m² | Peak kW | (a) % day vent | (b) h day vent | DH26 day vent | (a) % +night vent | (b) h +night vent | DH26 +night vent | DH26 2050 +night vent | July swing K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Timber frame, suspended timber floor | 71 | 62 | 26.3 | 5.83 | 16.0 | 249 | 3069 | 13.4 | 134 | 2257 | 4569 | 5.3 |
| Timber frame, screed ground floor | 90 | 59 | 21.4 | 5.55 | 11.8 | 253 | 2562 | 9.0 | 121 | 1722 | 3792 | 4.2 |
| SIPs, screed ground floor | 98 | 50 | 18.3 | 5.36 | 12.1 | 266 | 2661 | 8.6 | 124 | 1709 | 3806 | 4.0 |
| ICF, screed ground floor | 108 | 56 | 19.0 | 5.18 | 8.9 | 207 | 2151 | 6.3 | 101 | 1344 | 3339 | 3.6 |
| Masonry (aircrete, dabs), stud partitions | 125 | 54 | 18.5 | 5.14 | 9.3 | 269 | 2306 | 5.8 | 111 | 1386 | 3371 | 3.2 |
| Hempcrete, screed ground floor | 130 | 57 | 19.7 | 5.26 | 8.7 | 248 | 2211 | 5.7 | 108 | 1327 | 3284 | 3.1 |
| Masonry (dense block, dabs), stud partitions | 139 | 56 | 18.8 | 4.99 | 7.3 | 241 | 2068 | 5.0 | 100 | 1193 | 3130 | 3.0 |
| Lined CLT, CLT floor | 143 | 53 | 17.6 | 5.02 | 8.5 | 314 | 2311 | 5.1 | 116 | 1312 | 3277 | 2.8 |
| Exposed CLT, CLT floor | 147 | 55 | 18.1 | 5.03 | 8.3 | 311 | 2260 | 5.1 | 117 | 1280 | 3223 | 2.7 |
| Solid brick + internal insulation | 169 | 61 | 23.1 | 5.44 | 8.8 | 298 | 2406 | 5.3 | 121 | 1402 | 3487 | 2.8 |
| Solid brick + external insulation | 214 | 64 | 24.0 | 5.19 | 5.6 | 267 | 1986 | 4.2 | 114 | 1071 | 3049 | 2.2 |
| Solid brick, uninsulated | 220 | 217 | 87.3 | 6.00 | 4.9 | 136 | 1363 | 4.5 | 95 | 1047 | 2488 | 2.4 |
| Masonry (dense block, wet plaster), block partitions | 245 | 56 | 18.8 | 4.37 | 5.3 | 283 | 1826 | 3.4 | 108 | 923 | 2720 | 1.9 |
| Heavyweight: dense masonry, exposed slab floors | 295 | 55 | 18.5 | 4.08 | 3.7 | 315 | 1545 | 0.9 | 119 | 683 | 2405 | 1.3 |

## Five-node vs fine mesh at whole-house level

Same runs with every element as the five-node lump (class from the library). Differences are five-node minus fine mesh.

| Package | Heat kWh/m² Δ | Peak kW Δ | DH26 day vent Δ | DH26 +night vent Δ | (b) h +night vent Δ | July swing Δ K |
|---|---|---|---|---|---|---|
| Timber frame, suspended timber floor | +0.8 | -0.15 | +115 (+4%) | +238 (+11%) | -11 | +0.81 |
| Timber frame, screed ground floor | -0.1 | -0.28 | -52 (-2%) | +24 (+1%) | -12 | +0.28 |
| SIPs, screed ground floor | -0.2 | +0.04 | -80 (-3%) | -54 (-3%) | -5 | -0.08 |
| ICF, screed ground floor | -0.4 | -0.32 | -53 (-2%) | -56 (-4%) | -5 | -0.12 |
| Masonry (aircrete, dabs), stud partitions | -0.4 | -0.18 | -105 (-5%) | -165 (-12%) | +6 | -0.65 |
| Hempcrete, screed ground floor | -0.3 | -0.11 | -49 (-2%) | -52 (-4%) | -3 | -0.12 |
| Masonry (dense block, dabs), stud partitions | -0.1 | -0.21 | -0 (-0%) | -75 (-6%) | +10 | -0.61 |
| Lined CLT, CLT floor | +0.2 | -0.04 | -68 (-3%) | -90 (-7%) | +8 | -0.36 |
| Exposed CLT, CLT floor | +0.1 | -0.21 | -132 (-6%) | -149 (-12%) | +2 | -0.49 |
| Solid brick + internal insulation | +0.1 | -0.06 | +28 (+1%) | +38 (+3%) | -2 | +0.15 |
| Solid brick + external insulation | +0.1 | -0.15 | -38 (-2%) | -48 (-4%) | +0 | -0.25 |
| Solid brick, uninsulated | +0.3 | +0.00 | -3 (-0%) | -5 (-0%) | +3 | -0.04 |
| Masonry (dense block, wet plaster), block partitions | +0.1 | -0.03 | +13 (+1%) | -1 (-0%) | +1 | -0.13 |
| Heavyweight: dense masonry, exposed slab floors | +0.1 | +0.07 | +36 (+2%) | +20 (+3%) | +0 | -0.04 |

## Simplified 5R1C (the Excel workbook's model) vs the full model

ISO 13790-style single mass node with C_m = Σ κ₁A. Same weather, gains, ventilation and controls.

| Package | Heat kWh/m² full / 5R1C | Peak kW full / 5R1C | DH26 day vent full / 5R1C | DH26 +night vent full / 5R1C | (b) h +night vent full / 5R1C |
|---|---|---|---|---|---|
| Timber frame, suspended timber floor | 26.3 / 27.4 | 5.83 / 5.86 | 3069 / 3069 | 2257 / 2437 | 134 / 117 |
| Timber frame, screed ground floor | 21.4 / 22.9 | 5.55 / 5.25 | 2562 / 2650 | 1722 / 1946 | 121 / 117 |
| SIPs, screed ground floor | 18.3 / 19.6 | 5.36 / 5.07 | 2661 / 2728 | 1709 / 1883 | 124 / 124 |
| ICF, screed ground floor | 19.0 / 20.8 | 5.18 / 4.92 | 2151 / 2590 | 1344 / 1777 | 101 / 120 |
| Masonry (aircrete, dabs), stud partitions | 18.5 / 19.9 | 5.14 / 4.96 | 2306 / 2566 | 1386 / 1674 | 111 / 125 |
| Hempcrete, screed ground floor | 19.7 / 20.9 | 5.26 / 5.07 | 2211 / 2507 | 1327 / 1640 | 108 / 124 |
| Masonry (dense block, dabs), stud partitions | 18.8 / 20.2 | 4.99 / 4.99 | 2068 / 2497 | 1193 / 1600 | 100 / 126 |
| Lined CLT, CLT floor | 17.6 / 19.2 | 5.02 / 4.89 | 2311 / 2525 | 1312 / 1587 | 116 / 127 |
| Exposed CLT, CLT floor | 18.1 / 19.7 | 5.03 / 4.95 | 2260 / 2492 | 1280 / 1565 | 117 / 127 |
| Solid brick + internal insulation | 23.1 / 23.3 | 5.44 / 5.27 | 2406 / 2625 | 1402 / 1625 | 121 / 134 |
| Solid brick + external insulation | 24.0 / 24.2 | 5.19 / 5.31 | 1986 / 2485 | 1071 / 1482 | 114 / 133 |
| Solid brick, uninsulated | 87.3 / 85.6 | 6.00 / 6.00 | 1363 / 1551 | 1047 / 1246 | 95 / 97 |
| Masonry (dense block, wet plaster), block partitions | 18.8 / 19.2 | 4.37 / 4.49 | 1826 / 2249 | 923 / 1275 | 108 / 121 |
| Heavyweight: dense masonry, exposed slab floors | 18.5 / 18.6 | 4.08 / 4.27 | 1545 / 2228 | 683 / 1208 | 119 / 126 |
