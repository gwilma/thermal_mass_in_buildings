# Model 2: fine-mesh conduction vs ISO 13786 vs five-node

Fine mesh (2 mm cells) matches the ISO 13786 closed form to within 0.01% for all 29 build-ups (0.7% with 20 mm cells), so it is used as the reference below.

Daily |Y| in W/m²K. 'Absorbed' is heat taken in by 1 m² of element between 09:00 and 18:00 on a hot day (room air 24 ± 4 °C, peak 16:00), kWh/m².

| Key | Build-up | Class | |Y| ISO | |Y| fine mesh | |Y| five-node | ratio | best class (|Y|) | Absorbed fine | Absorbed five-node |
|---|---|---|---|---|---|---|---|---|---|
| W1 | Cavity: wet plaster, 100 dense block, 150 MW, brick | IE | 5.21 | 5.21 | 6.59 | 1.26 | IE (6.59) | 0.157 | 0.200 |
| W2 | Cavity: board on dabs, 100 dense block, 150 MW, brick | IE | 3.16 | 3.16 | 6.55 | 2.07 | D (2.94) | 0.100 | 0.199 |
| W3 | Cavity: wet plaster, 100 aircrete, 150 MW, brick | IE | 2.82 | 2.82 | 5.48 | 1.95 | D (2.14) | 0.095 | 0.169 |
| W4 | Cavity: board on dabs, 100 aircrete, 150 MW, brick | IE | 2.03 | 2.03 | 5.38 | 2.66 | D (2.08) | 0.072 | 0.165 |
| W5 | Timber frame: board, 140 MW studs, OSB, cavity, brick | E | 0.89 | 0.89 | 0.24 | 0.27 | M (0.47) | 0.043 | 0.025 |
| W6 | Timber frame: board, 140 MW studs, 60 wood fibre, render | D | 0.92 | 0.92 | 1.03 | 1.11 | D (1.03) | 0.039 | 0.044 |
| W7 | SIPs: board, OSB, 142 PUR, OSB, ventilated cladding | IE | 1.64 | 1.64 | 1.67 | 1.02 | IE (1.67) | 0.055 | 0.051 |
| W8 | Exposed 100 CLT, 160 wood fibre, render | I | 2.19 | 2.19 | 6.19 | 2.83 | D (1.71) | 0.077 | 0.189 |
| W9 | Lined CLT: board, 100 CLT, 160 MW, cladding | I | 1.82 | 1.82 | 4.88 | 2.68 | D (1.26) | 0.065 | 0.149 |
| W10 | ICF: board on dabs, 70 EPS, 150 concrete, 70 EPS, render | M | 0.75 | 0.75 | 0.41 | 0.54 | M (0.41) | 0.045 | 0.035 |
| W11 | Solid 215 brick, wet plaster, uninsulated | D | 4.25 | 4.25 | 4.72 | 1.11 | D (4.72) | 0.285 | 0.300 |
| W12 | Solid brick + IWI: board, 80 PIR, 215 brick | E | 0.74 | 0.74 | 0.24 | 0.33 | M (0.47) | 0.038 | 0.025 |
| W13 | Solid brick + EWI: plaster, 215 brick, 100 EPS, render | I | 4.32 | 4.32 | 7.30 | 1.69 | D (2.93) | 0.142 | 0.215 |
| W14 | Hempcrete: lime plaster, 300 hempcrete, lime render | D | 2.49 | 2.49 | 2.11 | 0.84 | D (2.11) | 0.088 | 0.077 |
| W15 | Exposed 300 rammed earth, 120 wood fibre, render | I | 4.90 | 4.90 | 7.55 | 1.54 | D (4.05) | 0.173 | 0.220 |
| F1 | 65 screed on 100 PIR on slab | IE | 4.57 | 4.57 | 5.37 | 1.17 | IE (5.37) | 0.127 | 0.146 |
| F2 | Suspended timber: 22 chipboard, 150 MW, vented void | I | 1.72 | 1.72 | 2.27 | 1.32 | IE (1.22) | 0.065 | 0.078 |
| F3 | Exposed 150 slab (polished) on 120 PIR | I | 5.02 | 5.02 | 5.73 | 1.14 | IE (5.35) | 0.127 | 0.146 |
| F4 | Carpet on 65 screed on 100 PIR on slab | IE | 2.50 | 2.50 | 5.38 | 2.15 | D (2.83) | 0.065 | 0.146 |
| I1 | Timber joist: 22 chipboard, void, 12.5 board ceiling | D | 1.74 | 1.74 | 1.64 | 0.94 | IE (1.67) | 0.048 | 0.045 |
| I2 | Concrete: 50 screed, 150 plank, exposed soffit | D | 4.44 | 4.44 | 4.73 | 1.06 | D (4.73) | 0.113 | 0.121 |
| I3 | Exposed 160 CLT floor, 50 screed on top | D | 4.24 | 4.24 | 2.84 | 0.67 | IE (4.56) | 0.117 | 0.080 |
| P1 | Stud partition: 12.5 board each side (half) | D | 0.63 | 0.63 | 0.63 | 1.00 | I (0.63) | 0.012 | 0.013 |
| P2 | 100 dense block, wet plaster both sides (half) | D | 4.96 | 4.96 | 5.19 | 1.05 | M (4.93) | 0.139 | 0.146 |
| P3 | 100 aircrete, wet plaster both sides (half) | D | 2.80 | 2.80 | 2.58 | 0.92 | IE (2.61) | 0.075 | 0.070 |
| P4 | Party wall: plaster, 100 dense block leaf (cavity behind) | D | 5.24 | 5.24 | 5.62 | 1.07 | M (5.06) | 0.141 | 0.153 |
| P5 | Party wall: board, 90 MW studs (timber frame twin stud) | I | 1.57 | 1.57 | 1.70 | 1.08 | I (1.70) | 0.038 | 0.037 |
| R1 | 12.5 board ceiling under 300 MW (cold loft) | D | 0.82 | 0.82 | 0.44 | 0.53 | IE (0.66) | 0.029 | 0.021 |
| R2 | Exposed 200 concrete roof slab, 150 PIR | I | 7.36 | 7.36 | 9.61 | 1.31 | IE (8.67) | 0.207 | 0.263 |

Five-node |Y| for every class (W/m²K):

| Key | I | E | IE | D | M | fine mesh |
|---|---|---|---|---|---|---|
| W1 | 7.36 | 0.21 | 6.59 | 2.99 | 0.42 | 5.21 |
| W2 | 7.35 | 0.21 | 6.55 | 2.94 | 0.41 | 3.16 |
| W3 | 6.90 | 0.19 | 5.48 | 2.14 | 0.37 | 2.82 |
| W4 | 6.85 | 0.19 | 5.38 | 2.08 | 0.36 | 2.03 |
| W5 | 6.44 | 0.24 | 4.68 | 1.97 | 0.47 | 0.89 |
| W6 | 3.58 | 0.19 | 1.96 | 1.03 | 0.37 | 0.92 |
| W7 | 3.13 | 0.14 | 1.67 | 0.83 | 0.28 | 1.64 |
| W8 | 6.19 | 0.19 | 4.32 | 1.71 | 0.38 | 2.19 |
| W9 | 4.88 | 0.17 | 2.93 | 1.26 | 0.34 | 1.82 |
| W10 | 7.41 | 0.21 | 6.72 | 3.15 | 0.41 | 0.75 |
| W11 | 7.02 | 2.18 | 5.80 | 4.72 | 3.39 | 4.25 |
| W12 | 7.24 | 0.24 | 6.25 | 2.73 | 0.47 | 0.74 |
| W13 | 7.30 | 0.28 | 6.41 | 2.93 | 0.54 | 4.32 |
| W14 | 6.75 | 0.22 | 5.20 | 2.11 | 0.44 | 2.49 |
| W15 | 7.55 | 0.28 | 7.18 | 4.05 | 0.54 | 4.90 |
| F1 | 5.74 | 0.21 | 5.37 | 2.82 | 0.40 | 4.57 |
| F2 | 2.27 | 0.24 | 1.22 | 0.83 | 0.45 | 1.72 |
| F3 | 5.73 | 0.18 | 5.35 | 2.76 | 0.34 | 5.02 |
| F4 | 5.74 | 0.20 | 5.38 | 2.83 | 0.39 | 2.50 |
| I1 | 2.19 | 1.40 | 1.67 | 1.64 | 1.66 | 1.74 |
| I2 | 5.68 | 3.18 | 5.17 | 4.73 | 4.08 | 4.44 |
| I3 | 5.45 | 0.68 | 4.56 | 2.84 | 1.23 | 4.24 |
| P1 | 0.63 | 0.63 | 0.63 | 0.63 | 0.63 | 0.63 |
| P2 | 5.70 | 4.31 | 5.26 | 5.19 | 4.93 | 4.96 |
| P3 | 3.12 | 1.75 | 2.61 | 2.58 | 2.34 | 2.80 |
| P4 | 6.91 | 3.96 | 5.86 | 5.62 | 5.06 | 5.24 |
| P5 | 1.70 | 0.39 | 1.04 | 0.91 | 0.70 | 1.57 |
| R1 | 1.29 | 0.11 | 0.66 | 0.44 | 0.22 | 0.82 |
| R2 | 9.61 | 0.14 | 8.67 | 3.90 | 0.28 | 7.36 |
