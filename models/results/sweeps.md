# Model 4: sweeps

Base: 'Timber frame, screed ground floor' envelope with an exposed dense layer of thickness t on the ground floor, intermediate floor (slab of thickness t), partitions (2t thick) and party wall. t = 0 swaps in board and chipboard. Synthetic weather.

## A. Diminishing returns

| t mm | κ₁ kJ/m²K per m² floor | κ_tot | heat kWh/m² | peak kW | DH26 hot day | DH26 hot +nv | DH26 2050 +nv | (b) h hot +nv | T_op max hot +nv | July swing +nv K |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 69 | 337 | 26.9 | 5.45 | 3956 | 2862 | 5644 | 170 | 39.5 | 6.7 |
| 10 | 84 | 353 | 27.2 | 5.68 | 3846 | 2635 | 5399 | 201 | 38.8 | 5.8 |
| 25 | 163 | 452 | 26.5 | 5.17 | 3611 | 2122 | 4813 | 257 | 36.5 | 3.5 |
| 50 | 234 | 618 | 26.2 | 4.98 | 3292 | 1754 | 4395 | 246 | 34.6 | 2.4 |
| 75 | 263 | 784 | 26.0 | 4.87 | 3043 | 1505 | 4121 | 214 | 33.5 | 2.0 |
| 100 | 273 | 950 | 26.0 | 4.81 | 2852 | 1317 | 3916 | 201 | 32.5 | 1.8 |
| 150 | 275 | 1282 | 26.0 | 4.74 | 2594 | 1072 | 3637 | 168 | 31.1 | 1.6 |
| 200 | 271 | 1614 | 26.0 | 4.71 | 2409 | 910 | 3440 | 147 | 30.2 | 1.5 |
| 300 | 263 | 2278 | 26.2 | 4.69 | 2094 | 688 | 3137 | 142 | 29.3 | 1.5 |

## B. Degree-hours above 26 °C (hot year): rows night ventilation ACH, columns t mm

| ACH \ t | 0 | 25 | 50 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|
| 0 | 3956 | 3611 | 3292 | 2852 | 2594 | 2409 | 2094 |
| 0.5 | 3532 | 3100 | 2743 | 2274 | 1993 | 1815 | 1540 |
| 1 | 3232 | 2702 | 2321 | 1859 | 1574 | 1388 | 1145 |
| 2 | 2862 | 2122 | 1754 | 1317 | 1072 | 910 | 688 |
| 3 | 2668 | 1760 | 1396 | 1018 | 799 | 649 | 449 |
| 5 | 2476 | 1346 | 998 | 703 | 525 | 405 | 252 |

Night hours above 26 °C:

| ACH \ t | 0 | 25 | 50 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|
| 0 | 320 | 402 | 416 | 455 | 452 | 437 | 440 |
| 0.5 | 284 | 334 | 366 | 363 | 375 | 375 | 338 |
| 1 | 246 | 307 | 333 | 308 | 287 | 267 | 271 |
| 2 | 170 | 257 | 246 | 201 | 168 | 147 | 142 |
| 3 | 141 | 195 | 162 | 124 | 118 | 125 | 107 |
| 5 | 105 | 122 | 109 | 87 | 78 | 72 | 52 |

## C. Morris screening (10 trajectories, 4 levels; μ* = mean |elementary effect| over the full range of each input)

Ranges: exposed mass t (m) 0.0–0.3; glazing area × 0.5–1.5; blind factor (closed) 0.2–1.0; day purge ACH 0.0–6.0; night vent ACH 0.0–4.0; background ACH 0.3–1.0; internal gains × 0.6–1.4; wall insulation (m MW) 0.09–0.24.

**Degree-hours > 26 °C, hot year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| day purge ACH | 4261.3 | -4261.3 | 8059.6 |
| blind factor (closed) | 2779.4 | +2779.4 | 5765.4 |
| glazing area × | 2564.8 | +2564.8 | 2244.5 |
| internal gains × | 1229.8 | +1229.8 | 2024.1 |
| night vent ACH | 1123.5 | -1123.5 | 886.4 |
| background ACH | 942.1 | -941.0 | 1883.0 |
| exposed mass t (m) | 885.4 | -885.4 | 604.3 |
| wall insulation (m MW) | 186.3 | +146.2 | 500.1 |

**Night hours > 26 °C, hot year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| day purge ACH | 338.1 | -338.1 | 392.0 |
| glazing area × | 314.4 | +314.4 | 279.3 |
| night vent ACH | 228.0 | -228.0 | 184.6 |
| blind factor (closed) | 187.9 | +187.9 | 164.2 |
| internal gains × | 113.2 | +113.2 | 162.8 |
| background ACH | 104.4 | -104.4 | 183.0 |
| exposed mass t (m) | 92.4 | -79.8 | 71.7 |
| wall insulation (m MW) | 9.6 | +4.8 | 19.1 |

**Space heating kWh/m², typical year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| background ACH | 27.4 | +27.4 | 3.7 |
| internal gains × | 11.0 | -11.0 | 1.6 |
| wall insulation (m MW) | 8.3 | -8.3 | 2.7 |
| blind factor (closed) | 6.2 | -6.2 | 2.6 |
| day purge ACH | 2.9 | +2.9 | 2.3 |
| glazing area × | 1.2 | +0.2 | 1.5 |
| exposed mass t (m) | 0.7 | -0.0 | 1.0 |
| night vent ACH | 0.1 | +0.0 | 0.2 |

**Peak heating kW, typical year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| background ACH | 1.0 | +1.0 | 0.2 |
| glazing area × | 0.4 | +0.4 | 0.1 |
| exposed mass t (m) | 0.4 | -0.4 | 0.4 |
| internal gains × | 0.2 | -0.2 | 0.0 |
| wall insulation (m MW) | 0.2 | -0.2 | 0.1 |
| blind factor (closed) | 0.1 | +0.0 | 0.1 |
| day purge ACH | 0.0 | +0.0 | 0.0 |
| night vent ACH | 0.0 | +0.0 | 0.0 |

