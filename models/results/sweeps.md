# Model 4: sweeps

Base: 'Timber frame, screed ground floor' envelope with an exposed dense layer of thickness t on the ground floor, intermediate floor (slab of thickness t), partitions (2t thick) and party wall. t = 0 swaps in board and chipboard. Heathrow TMYx weather (hot and 2050s years are morphed).

## A. Diminishing returns

| t mm | κ₁ kJ/m²K per m² floor | κ_tot | heat kWh/m² | peak kW | DH26 hot day | DH26 hot +nv | DH26 2050 +nv | (b) h hot +nv | T_op max hot +nv | July swing +nv K |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 69 | 337 | 23.8 | 5.70 | 2825 | 2107 | 4289 | 122 | 38.9 | 5.3 |
| 10 | 84 | 353 | 23.6 | 5.90 | 2697 | 1896 | 3999 | 134 | 38.3 | 4.7 |
| 25 | 163 | 452 | 21.3 | 5.61 | 2388 | 1407 | 3345 | 128 | 36.3 | 2.9 |
| 50 | 234 | 618 | 20.2 | 4.96 | 2054 | 1101 | 2927 | 120 | 34.1 | 2.0 |
| 75 | 263 | 784 | 20.0 | 4.55 | 1803 | 913 | 2661 | 113 | 32.6 | 1.7 |
| 100 | 273 | 950 | 19.9 | 4.32 | 1598 | 771 | 2465 | 112 | 31.7 | 1.6 |
| 150 | 275 | 1282 | 19.9 | 4.08 | 1291 | 549 | 2183 | 111 | 30.4 | 1.4 |
| 200 | 271 | 1614 | 19.9 | 4.06 | 1084 | 389 | 1991 | 98 | 29.4 | 1.3 |
| 300 | 263 | 2278 | 20.1 | 4.06 | 825 | 192 | 1755 | 74 | 28.2 | 1.2 |

## B. Degree-hours above 26 °C (hot year): rows night ventilation ACH, columns t mm

| ACH \ t | 0 | 25 | 50 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|
| 0 | 2825 | 2388 | 2054 | 1598 | 1291 | 1084 | 825 |
| 0.5 | 2539 | 2012 | 1684 | 1262 | 987 | 796 | 544 |
| 1 | 2342 | 1749 | 1424 | 1041 | 795 | 614 | 379 |
| 2 | 2107 | 1407 | 1101 | 771 | 549 | 389 | 192 |
| 3 | 1972 | 1195 | 907 | 617 | 420 | 279 | 114 |
| 5 | 1827 | 944 | 697 | 456 | 301 | 189 | 76 |

Night hours above 26 °C:

| ACH \ t | 0 | 25 | 50 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|---|
| 0 | 225 | 285 | 309 | 289 | 271 | 267 | 277 |
| 0.5 | 175 | 221 | 211 | 200 | 188 | 177 | 170 |
| 1 | 151 | 173 | 168 | 158 | 140 | 140 | 120 |
| 2 | 122 | 128 | 120 | 112 | 111 | 98 | 74 |
| 3 | 105 | 109 | 94 | 93 | 78 | 70 | 31 |
| 5 | 86 | 83 | 73 | 64 | 56 | 45 | 13 |

## C. Morris screening (10 trajectories, 4 levels; μ* = mean |elementary effect| over the full range of each input)

Ranges: exposed mass t (m) 0.0–0.3; glazing area × 0.5–1.5; blind factor (closed) 0.2–1.0; day purge ACH 0.0–6.0; night vent ACH 0.0–4.0; background ACH 0.3–1.0; internal gains × 0.6–1.4; wall insulation (m MW) 0.09–0.24.

**Degree-hours > 26 °C, hot year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| day purge ACH | 3534.0 | -3534.0 | 7747.5 |
| blind factor (closed) | 2198.0 | +2198.0 | 5403.1 |
| glazing area × | 1639.7 | +1639.7 | 1480.4 |
| internal gains × | 1126.2 | +1126.2 | 2058.9 |
| background ACH | 843.2 | -840.3 | 1992.9 |
| exposed mass t (m) | 751.9 | -751.9 | 488.2 |
| night vent ACH | 603.9 | -603.9 | 450.8 |
| wall insulation (m MW) | 193.9 | +167.0 | 543.8 |

**Night hours > 26 °C, hot year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| day purge ACH | 326.4 | -326.4 | 523.7 |
| glazing area × | 249.3 | +249.3 | 238.6 |
| night vent ACH | 152.7 | -152.7 | 136.5 |
| blind factor (closed) | 138.3 | +138.3 | 221.6 |
| internal gains × | 132.4 | +132.4 | 222.5 |
| background ACH | 120.3 | -119.7 | 237.6 |
| exposed mass t (m) | 77.5 | -77.5 | 54.8 |
| wall insulation (m MW) | 23.7 | +20.1 | 64.4 |

**Space heating kWh/m², typical year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| background ACH | 26.3 | +26.3 | 4.6 |
| blind factor (closed) | 10.6 | -10.6 | 3.5 |
| internal gains × | 10.3 | -10.3 | 2.1 |
| wall insulation (m MW) | 7.9 | -7.9 | 2.7 |
| day purge ACH | 3.1 | +3.1 | 2.4 |
| glazing area × | 3.0 | -1.9 | 2.8 |
| exposed mass t (m) | 1.5 | -1.1 | 3.2 |
| night vent ACH | 0.1 | -0.0 | 0.2 |

**Peak heating kW, typical year**

| Input | μ* | μ (signed) | σ |
|---|---|---|---|
| background ACH | 1.5 | +1.5 | 0.7 |
| exposed mass t (m) | 0.6 | -0.6 | 0.6 |
| internal gains × | 0.4 | -0.4 | 0.1 |
| wall insulation (m MW) | 0.4 | -0.4 | 0.3 |
| glazing area × | 0.3 | +0.3 | 0.2 |
| blind factor (closed) | 0.2 | -0.1 | 0.3 |
| day purge ACH | 0.0 | +0.0 | 0.0 |
| night vent ACH | 0.0 | +0.0 | 0.0 |

