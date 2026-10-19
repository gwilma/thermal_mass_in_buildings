# Thermal mass models

Four connected Python models for exploring thermal mass in common UK
build-ups. They reuse `physics/iso13786.py`. Requires numpy and matplotlib.

```
cd models
python3 conduction.py   # model 2 (fast)
python3 buildups.py     # model 1 table (uses model 2 for the five-node column)
python3 packages.py     # model 3, 14 construction packages (~1 min)
python3 sweeps.py       # model 4 (~3 min)
```

Web apps of all four models are in `../apps` and Excel workbooks in `../excel`.

Outputs go to `results/`, as Markdown tables, CSV files and PNG figures.

| # | File | What it is |
|---|------|-----------|
| 1 | `buildups.py` | 29 build-ups (15 external walls, 4 ground floors, 3 intermediate floors, 5 partitions and party walls, 2 roofs). Each gets U, daily Y, decrement, lag, κ₁ and κ_tot, plus an ISO 52016 / HEM mass class. The class is picked by rule from where the mass sits relative to the insulation. |
| 2 | `elements.py`, `conduction.py` | Any build-up becomes a fine-mesh finite-difference chain or a five-node lump (conductances 6/Rc, 3/Rc, 3/Rc, 6/Rc). The script compares both against ISO 13786 by period, and in the time domain on a hot day. |
| 3 | `room.py`, `weather.py`, `packages.py` | Hourly single-zone model of a 90 m² two-storey semi. Elements can run fine-mesh or five-node. It has an air node with furniture and a radiant star node, sol-air on the walls, glazing with optional blinds, purge and night ventilation, and an intermittent heating schedule. Outputs are heating, peak load, TM59-style overheating indicators and degree-hours. `packages.py` compares 14 construction packages. |
| 3b | `room5r1c.py` | The same house as an ISO 13790 5R1C model (one mass node), for comparison and as the engine of the Excel house workbook. |
| 3c | `bestest.py` | ASHRAE Standard 140 cases 600, 900, 600FF and 900FF on the same room engine, for validation. |
| 4 | `sweeps.py` | A. Thickness of an exposed dense layer from 0 to 300 mm, with the envelope held fixed. B. Mass × night-ventilation grid. C. Morris screening of eight inputs. |

## Validation

`../tests` holds 283 test cases; see `../tests/README.md`. In summary:

- **ISO 13786 Annex D, case D.1:** reproduced exactly in Python, the web
  apps and Excel.
- **Analytical cases:** fine mesh and five-node match the classical
  conduction solutions.
- **ASHRAE Standard 140 (BESTEST):** `bestest.py` runs the room model on
  Denver TMY3.
  - Lightweight case 600: heating 4.76 MWh and cooling 6.72 MWh, both inside
    the published ranges.
  - Heavyweight case 900: free-float temperatures are inside the range, but
    heating (1.88 MWh) and cooling (3.05 MWh) are 3% and 12% above it.
  - The five-node lump overstates all loads, consistent with finding 1.

## Main findings

Weather is the Heathrow TMYx 2011-2025 file, with hot and 2050s years made
by morphing it (see the caveats). Treat the overheating numbers as relative.

1. **The ISO 13786 maths is right, and the five-node lump is not reliable
   element by element.** The fine mesh converges on the ISO 13786 closed
   form to within 0.1% for all 29 build-ups. Against that reference, the
   five-node daily |Y| is about 2× too high where mass sits behind a lining:
   board-on-dabs dense block 2.1×, aircrete on dabs 2.7×, lined CLT 2.7×,
   exposed CLT 2.8×, carpeted screed 2.2×. The cause is the lump itself: the
   class puts κ_tot (or half of it) on the surface node, ahead of the dab
   void, lining, carpet or the depth that a daily wave actually reaches. The
   error also runs the other way: |Y| comes out about 0.3× for timber frame
   and internal wall insulation, where class E puts all the mass on the
   brick outside the insulation. No single class fixes every case. This confirms the earlier `hem_nodes.py` result independently
   of HEM's code. It does not confirm what HEM's code actually does, which
   still needs its source. See `results/conduction.md` and
   `fivenode_vs_fd.png`.
2. **At whole-house level the five-node error mostly washes out.** Across the
   14 packages, five-node minus fine mesh is within -0.4 to +0.8 kWh/m² for
   heating and -0.3 to +0.1 kW for peak heating. Overheating degree-hours are
   within ±6% with day purge only and ±12% with night ventilation, and the
   July swing is within about 0.8 K. Errors in opposite directions on
   different elements largely cancel. See `results/packages.md`.
3. **A single-node 5R1C model (ISO 13790) gets heating right but under-rewards
   deep mass in summer.** `room5r1c.py` runs the same house as one mass node.
   Annual heating is 1% to 10% above the fine mesh. With night ventilation in
   the hot year, it gives the heavyweight house 1208 degree-hours above 26 °C
   against 683 from the fine mesh, and narrows the gap between lightest and
   heaviest packages from 3.3× to 2.0×. One node cannot store a night's coolth
   apart from the day's surface swing.
4. **For daily swing, the useful thickness is about 50 to 100 mm. Hot spells
   keep rewarding more.** With night ventilation, the July daily operative
   swing falls from 5.3 K at t = 0 to 2.0 K at 50 mm and 1.6 K at 100 mm, then
   flattens. That is the 0.7 to 1.1 penetration depth result. κ₁ peaks at
   about 100 to 150 mm. Degree-hours above 26 °C keep falling to 300 mm
   (2107 → 771 at 100 mm → 192), because a multi-day heatwave has periods
   long enough to reach deeper mass. See `diminishing_returns.png`.
5. **Mass needs night ventilation, and without it mass makes nights worse.**
   With no night ventilation, adding exposed mass raises night hours above
   26 °C from 225 (t = 0) to 309 (50 mm) and 289 (100 mm). With 3 ACH at
   night, 100 mm cuts them from 105 to 93 and cuts degree-hours by 69%
   (1972 → 617). See `mass_x_nightvent.png`.
6. **Mass ranks below ventilation, solar control and glazing for overheating.**
   In the Morris screening for summer degree-hours, the order is day purge >
   blinds > glazing area > internal gains > background ventilation > exposed
   mass > night ventilation, with wall insulation last. For peak heating,
   mass is second only to background ventilation.
7. **With real weather, mass saves heating as well as peak load.** Going from
   0 to 50 mm of exposed mass cuts annual heating by 15% (23.8 → 20.2
   kWh/m²); beyond that it flattens at about 19.9 (16%). Peak heating falls
   29%, from 5.70 to 4.06 kW, by 150 mm. Mass lets the house use spring and
   autumn sun that a light house dumps through the windows. Between packages,
   U-values still dominate.

## Caveats

- **Weather.** `weather_data/` holds the Heathrow TMYx 2011-2025 EPW from
  climate.onebuilding.org. The "hot" year adds +1.5 K from June to August
  and a +4 K raised-cosine heatwave over 14 to 21 July. "hot2050" adds
  +2.5 K in summer and +1.5 K otherwise. These are morphs, not CIBSE DSY or
  UKCP18 files; `weather.read_epw()` takes those directly once available.
  `weather.synthetic()` is kept as a fallback.
- The model is a single zone. TM59 criteria are meant per room, so the (a)
  and (b) figures here are indicators. There is no bedroom/living split and
  no cooling.
- Absolute overheating is high because the base case has 18 m² of unshaded
  glazing and blinds are off. Compare cases with each other, not with TM59
  limits.
- The five-node conductances follow ISO 52016-1. Whether HEM uses exactly
  these still needs checking against HEM's source. The mass class is picked
  by a rule; a HEM user would choose it by judgement.
- Material properties are typical design values, not product data.
- Windows are a simple U × A plus g × incident. Ground is 1 m of soil held at
  the annual mean outdoor temperature.
