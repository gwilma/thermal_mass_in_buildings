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

Outputs go to `results/`, as Markdown tables, CSV files and PNG figures.

| # | File | What it is |
|---|------|-----------|
| 1 | `buildups.py` | 29 build-ups (15 external walls, 4 ground floors, 3 intermediate floors, 5 partitions and party walls, 2 roofs). Each gets U, daily Y, decrement, lag, κ₁ and κ_tot, plus an ISO 52016 / HEM mass class. The class is picked by rule from where the mass sits relative to the insulation. |
| 2 | `elements.py`, `conduction.py` | Any build-up becomes a fine-mesh finite-difference chain or a five-node lump (conductances 6/Rc, 3/Rc, 3/Rc, 6/Rc). The script compares both against ISO 13786 by period, and in the time domain on a hot day. |
| 3 | `room.py`, `weather.py`, `packages.py` | Hourly single-zone model of a 90 m² two-storey semi. Elements can run fine-mesh or five-node. It has an air node with furniture and a radiant star node, sol-air on the walls, glazing with optional blinds, purge and night ventilation, and an intermittent heating schedule. Outputs are heating, peak load, TM59-style overheating indicators and degree-hours. `packages.py` compares 14 construction packages. |
| 4 | `sweeps.py` | A. Thickness of an exposed dense layer from 0 to 300 mm, with the envelope held fixed. B. Mass × night-ventilation grid. C. Morris screening of eight inputs. |

## Main findings

These come from synthetic weather (see the caveats), so they are relative
results, not design numbers.

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
   14 packages, five-node minus fine mesh is within ±0.4 kWh/m² for heating
   and ±0.3 kW for peak heating. Overheating degree-hours are within ±8%, and
   the July swing is within about 1 K. Errors in opposite directions on
   different elements largely cancel. See `results/packages.md`.
3. **For daily swing, the useful thickness is about 50 to 100 mm. Hot spells
   keep rewarding more.** The July daily operative swing falls from 6.7 K to
   1.8 K by t = 100 mm, then flattens. That is the 0.7 to 1.1 penetration
   depth result. κ₁ peaks at about 100 mm. Degree-hours above 26 °C keep
   falling to 300 mm, because a multi-day heatwave has periods long enough
   to reach deeper mass. See `diminishing_returns.png`.
4. **Mass only works with night ventilation, and without it mass makes
   nights worse.** With no night ventilation, adding 100 mm of exposed mass
   raises night hours above 26 °C from 320 to 455. With 3 ACH at night,
   the same mass cuts them from 141 to 124, and cuts degree-hours by 62%
   (2668 → 1018). See `mass_x_nightvent.png`.
5. **Mass ranks below ventilation, solar control and glazing.** In the Morris
   screening for summer degree-hours, the order is day purge > blinds >
   glazing area > internal gains > night ventilation ≈ background
   ventilation ≈ exposed mass. Wall insulation comes last.
6. **Annual heating barely changes, but peak heating does.** Going from 0 to
   300 mm of exposed mass changes annual heating by under 1 kWh/m² on about
   26. Peak heating with intermittent heating falls 14%, from 5.45 to
   4.69 kW. Differences in heating between packages come from U-values, not
   mass.

## Caveats

- **Weather is synthetic.** The proxy blocked every weather host tried
  (climate.onebuilding.org, energyplus.net, the JRC PVGIS API and the
  Open-Meteo archive API). `weather.py` makes a London-like year from
  approximate Heathrow monthly means. The "hot" variant adds a DSY-like
  warm summer with a 7-day heatwave peaking at 37 °C. The "hot2050" variant
  adds an illustrative +2.5 K in summer. `weather.read_epw()` takes real
  CIBSE TRY/DSY or Prometheus UKCP18 EPW files, so swap them in once any
  are available.
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
