# Thermal mass web apps

Four standalone single-file HTML apps, one per model in `../models`. Open
any file in `dist/` in a browser; nothing is installed and no server is
needed (fonts come from Google Fonts when online, with system fallbacks).

| App | File | Model |
|-----|------|-------|
| Build-up Explorer | `dist/buildup.html` | 1: ISO 13786 properties and the five-node class for 29 build-ups, plus a custom layer editor |
| Conduction Lab | `dist/conduction.html` | 2: fine-mesh against five-node conduction under a daily cycle |
| House Simulator | `dist/room.html` | 3: hourly full-year house on Heathrow TMYx, fine mesh, five-node or 5R1C |
| Mass Sweeps | `dist/sweeps.html` | 4: the sweeps, precomputed results plus live re-runs |

`src/core.js` is a JavaScript port of the Python models and matches them to
rounding. `python3 build.py` inlines `src/` and the weather file into
`dist/` (complete documents) and `artifact/` (body-only copies for
publishing as claude.ai artifacts).
