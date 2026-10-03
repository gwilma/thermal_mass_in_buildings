# How much thermal mass is worth having in a low-energy building?

*Literature review and standards-based assessment. Prepared 3 October 2026.*

## Summary

- **The energy benefit of thermal mass is real but modest, and it shrinks as buildings get better insulated.** The broadest review (Verbeke & Audenaert 2018) puts the effect on heating and cooling demand at "a few percent for most cases", with insulation and solar gain mattering far more. Simulation studies of whole houses typically find 3–12% (ORNL, Kosny et al.; Han et al. 2025), and Nordic life-cycle work finds the heating saving "small" (Dodoo et al. 2012).
- **Diminishing returns show up at three scales**, and each has a fairly well-defined knee:
  1. **Thickness of a single exposed layer.** For the daily (24 h) cycle, dense concrete or brick stops adding useful storage at about **75–100 mm**, and about **90% of the maximum is reached by ~50 mm**. Beyond ~100 mm the diurnal storage actually falls slightly (Ma & Wang 2012; calculation below). Thicker mass (≈150–300 mm) only pays when you want to buffer multi-day hot spells.
  2. **Exposed area.** Because the surface film caps how fast heat can enter any surface (≈100 kJ/m²K per m² of surface on a daily cycle, set by the internal surface resistance alone), *area* of exposed mass matters more than depth once you are past ~50–100 mm.
  3. **Whole-building heat capacity.** Using the ISO 13790 monthly method, most of the achievable heating benefit is captured at a "medium" to "heavy" class (**≈165–260 kJ/m²K of floor area**, roughly SAP "medium"). Going from 165 to 370 kJ/m²K adds only ~1–1.5 kWh/m²·yr in a Passivhaus-level dwelling.
- **There are regimes where more mass is worse**, not merely less useful: intermittently heated buildings (Reilly & Kinnane 2017; Hoes et al. 2011; de Vaan et al. 2008), hot-humid climates with small diurnal swings (Mora Juárez 2014), and summer conditions without night purge ventilation (Jimenez-Bescos 2017).
- **The strongest remaining case for mass in low-energy buildings is summer comfort and load-shifting**, not winter heating kWh: reducing overheating hours when paired with night ventilation, and letting a heat pump coast through several hours of off-peak or cut-off periods (Dominković et al. 2018; Johra et al. 2019).
- **A practical answer:** aim for roughly 50–100 mm of dense material, *exposed* on as many internal surfaces as is practical (soffits, floors, party/partition walls), to reach a medium–heavy whole-house class. Beyond that, extra mass buys little energy and costs embodied carbon (Hacker et al. 2008; Dodoo et al. 2012).

## 1. What the literature says about magnitude

| Study | Method & setting | Finding on quantity/benefit |
|---|---|---|
| Verbeke & Audenaert 2018, *Renew. Sust. Energy Rev.* 82:2300–2318 | Review across climates and building uses | Mass inside insulation usually helps comfort and energy, but the effect on demand is "a few percent for most cases"; insulation and solar gains dominate. Notes inconsistency between simulation tools. |
| Kosny, Petrie, Gawin et al. (ORNL), c. 2001 | >10,000 DOE-2.1E runs, 16 massive wall types, 10 US climates | Whole-building savings up to ~8% (Minneapolis) and 5–18% (Bakersfield); ICF walls averaged 6–8%. Mass must be in good contact with the interior; walls with insulation on the inside performed much worse. The "dynamic benefit" peaked for wall R-values of 2.3–3.0 m²K/W. |
| Han et al. 2025, *Advances in Applied Energy* | 76 rooms in 18 Beijing buildings measured, plus EnergyPlus | 4–12% annual savings from *arranging* mass well; misapplied mass raised energy use by 1–20% in daytime-use buildings. Placement beats quantity. |
| Dodoo, Gustavsson & Sathre 2012, *Applied Energy* 92:462–472 | Hourly simulation, concrete vs timber frame, Sweden | Heating saving from mass is small; timber frame wins on life-cycle primary energy. |
| Reilly & Kinnane 2017, *Applied Energy* 198:108–121 | Finite-element transient vs steady-state | Madrid summer: heavy blockwork used 42% less energy than steady-state predicts (timber: 7%). Belfast with intermittent heating: heavy walls used 2–3.7× the steady-state prediction; effective U-values rose from 0.15–0.23 to 0.46–0.62 W/m²K. |
| Hoes, Trcka, Hensen & Hoekstra Bonnema 2011, *Energy Conversion and Management* 52(6) | Simulated five-zone Dutch low-energy house (Apeldoorn), heating 21 °C occupied / 14 °C unoccupied, effective mass 5, 50 or 100 kg/m² of room surface | Whole house, evening-only occupancy: lightweight (5 kg/m²) needed 15.9 kWh/m²·yr of heating vs 18.5 for heavyweight (100 kg/m²), about 14% less. Day-and-evening occupancy reversed it: heavyweight needed 20.9 vs 25.0, about 16% less. Lightweight had far more weighted overheating hours (699 vs 7 evening; 2,850 vs 196 day-and-evening). The optimum mass varied by zone, season and occupancy, which motivates their adaptable ('HATS') concept. |
| de Vaan, Spoorenberg & Wiedenhoff 2008 | Dutch heating simulations | Lightweight uses less heating energy as long as the night setback is below ~15 °C; above that, heavyweight wins. |
| Mantesi, Cook, Glass & Hopfe 2015, *Building Simulation* | Six simulation tools compared | Tool-to-tool spread is consistently larger for high-mass cases (up to ~10% on cooling). Treat claimed mass benefits of a few percent with caution. |
| Mora Juárez 2014 (Chalmers MSc) | Parametric, Mexico City vs Veracruz | Mass helps in temperate highland climates, is a liability in tropical ones: useful only when the free-running temperature sits within comfort limits. |
| Kalogirou, Florides & Tassou 2002, *Renewable Energy* 27:353–368 | TRNSYS, Cyprus | South thermal (Trombe) wall: ~47% heating load cut in the zone, optimum wall thickness ~25 cm. Passive-solar walls are the case where thicker mass is justified. |
| Huntington (NZ), AccuRateNZ | Auckland passive duplex | Adding a 190 mm block party wall and 120 mm concrete mid-floor improved annual energy by 23% vs lightweight; cutting the concrete by 25% gave intermediate results. |

**Reading across these:** in heated, well-insulated, continuously occupied dwellings, the heating benefit of moving from light to heavy is a few kWh/m²·yr. That is a large *percentage* of a Passivhaus heating demand but a small absolute quantity. The benefit grows with solar gain and with summer cooling need, and turns negative under intermittent heating.

## 2. Where diminishing returns set in

### 2.1 Thickness: the penetration-depth limit

Heat entering a surface on a periodic cycle decays with depth. The periodic penetration depth is δ = √(λT/πρc). Following ISO 13786, I calculated the effective areal heat capacity of a single layer exposed on one face, backed by insulation, including the internal surface resistance (Rsi = 0.13 m²K/W). Script: `calc.py` (method only; inputs are standard textbook properties).

**Daily (24 h) cycle, effective areal heat capacity in kJ/m²K per m² of exposed surface:**

| Material | δ (mm) | 25 mm | 50 mm | 75 mm | 100 mm | 150 mm | 200 mm | 300 mm | Peak at | 90% of peak by |
|---|---|---|---|---|---|---|---|---|---|---|
| Dense concrete | 129 | 50 | 74 | 82 | **83** | 81 | 78 | 75 | ~100 mm | ~52 mm |
| Clay brick | 110 | 40 | 63 | 71 | **72** | 68 | 65 | 64 | ~93 mm | ~54 mm |
| Gypsum plaster/board | 87 | 22 | 38 | 44 | **44** | 41 | 39 | 39 | ~87 mm | ~57 mm |
| Timber/CLT | 68 | 19 | 31 | **33** | 32 | 29 | 29 | 29 | ~72 mm | ~48 mm |
| Aerated concrete | 83 | 15 | 26 | 31 | **32** | 29 | 28 | 28 | ~88 mm | ~59 mm |

**7-day cycle (buffering a hot spell or a cold week):**

| Material | δ (mm) | 50 mm | 100 mm | 150 mm | 200 mm | 300 mm |
|---|---|---|---|---|---|---|
| Dense concrete | 342 | 113 | 216 | 296 | 349 | 388 |
| Clay brick | 291 | 87 | 167 | 231 | 272 | 296 |

What this shows:

- **Diurnally, the useful depth is ~50–100 mm for every common material.** Beyond the peak, storage falls slightly because heat from the previous cycle interferes. This matches Ma & Wang (2012, *Energy and Buildings*), who found an optimal thickness for interior planar mass beyond which there is "no rationale" for more material as thermal mass, and the Concrete Centre's position that 100 mm gives useful diurnal mass.
- **The surface film is the real cap.** Even infinitely conductive mass could not exceed ~106 kJ/m²K per m² of surface on a 24 h cycle at Rsi = 0.13. Dense concrete reaches ~80% of that ceiling. So once you have ~50–100 mm, more *area* helps and more *depth* does not.
- **A slab exposed on both faces** can use roughly twice this depth (≈150–200 mm) before thickness stops paying.
- **Deeper mass only matters for longer cycles.** For a multi-day heatwave, concrete keeps adding capacity out to ~200–300 mm, which is the Concrete Centre's argument for 300 mm slabs in naturally ventilated offices. For dwellings with a daily heating and occupancy pattern, the diurnal figure is the one that matters.
- **Coverings decouple the mass.** Carpet, dry-lining on dabs, suspended ceilings and raised floors add surface resistance and cut these values sharply. "Exposed" is a precondition, not a detail.

### 2.2 Whole-building heat capacity: the gain-utilisation limit

Heating benefit from mass comes mostly from using solar and internal gains that would otherwise overheat the space. In the ISO 13790 monthly method, the gain utilisation factor depends on the building time constant τ = C/H. It approaches its ceiling asymptotically, which is the textbook form of diminishing returns.

I ran the ISO 13790 monthly method for an illustrative 100 m² dwelling in a London-like climate (20 °C setpoint, 2.1 W/m² internal gains, south glazing g = 0.5). Inputs are approximate. The *shape* of the result matters more than the absolute values. Script: `iso.py`.

**Annual space heating, kWh/m²·yr, against internal heat capacity per m² of floor (kJ/m²K):**

| Fabric (H per m² floor) | 50 | 80 (v. light) | 110 (light) | 165 (medium) | 260 (heavy) | 370 (v. heavy) | 500 |
|---|---|---|---|---|---|---|---|
| 2006-regs-ish (1.8 W/m²K), 10% glazing | 97.8 | 96.0 | 94.7 | 93.1 | 91.7 | 90.9 | 90.4 |
| Good low-energy (1.0), 12% glazing | 39.3 | 37.0 | 35.6 | 34.0 | 32.8 | 32.1 | 31.8 |
| Passivhaus-level (0.65), 15% glazing | 15.2 | 13.1 | 11.8 | 10.5 | 9.6 | 9.1 | 8.9 |
| Passivhaus-level, 25% south glazing | 10.0 | 7.7 | 6.4 | 5.0 | 3.9 | 3.3 | 3.0 |

**Share of the total 50→500 benefit captured:** ~30% by 80, ~50% by 110, **~70–75% by 165, ~85–90% by 260**, ~95% by 370, in every case.

What this shows:

- **The knee sits between "medium" and "heavy"** (≈165–260 kJ/m²K per m² of floor). In the Passivhaus case, going from very light to medium saves ~2.6 kWh/m²·yr. Medium to very heavy saves another ~1.4.
- **More glazing raises the value of mass but does not move the knee much.** That matches passive-solar rules of thumb, which scale exposed mass area to glazing area (3:1 to 9:1, with at least 100 mm thickness; 2030 Palette).
- **Translating to construction:** a dwelling has roughly 2.5–3.5 m² of internal surface per m² of floor. At ~80 kJ/m²K per m² of exposed dense masonry (section 2.1), reaching ~250 kJ/m²K of floor means exposing dense material over most surfaces (floors, ceilings, party and partition walls). Plasterboard on timber frame lands around 80–110, which is "very light" to "light". This roughly matches SAP's thermal mass parameter bands (low ≈100, medium ≈250, high ≈450 kJ/m²K; worth checking against the current SAP/HEM documents).
- **Caveat:** the monthly method assumes continuous heating. It cannot capture the intermittent-heating penalty in section 3, and it is a simplified model. Use these as indicative of shape, not as design numbers.

### 2.3 Overheating: mass needs a heat sink

- **Night ventilation is what makes summer mass work.** Jimenez-Bescos (2017, *Energy Procedia*) found that night ventilation of at least ~8 air changes per hour was needed for significant overheating reduction in a London room with exposed mass. Under future climates the reduction was below 3–8%. Without a heat sink, mass just stores heat.
- **Adding layers gives diminishing returns.** Rodrigues, Sougkakis & Gillott (2016) added 1–3 layers of fibreboard, PCM board or concrete to a super-insulated timber house. Concrete outperformed the boards, but the gains from successive layers diminished. Large relative improvements sometimes meant tiny absolute changes (a 50% relative cut equalled 0.3% of hours).
- **Occupant evidence is modestly positive.** In 26 European offices, occupants of heavyweight buildings were 1.5× more likely to report comfort, but only in naturally ventilated buildings (Gauthier, Teli, James & Stamp).
- **For UK housing under climate change,** Kendrick et al. (2012, *Energy and Buildings* 48:40–49) compared structural systems. Hacker et al. (2008, *Energy and Buildings* 40:375–384) found heavier construction reduced overheating and cooling-related CO₂. Their life-cycle results are in section 4.

## 3. When more mass is a penalty

1. **Intermittent heating.** Offices heated only in the day, homes heated only in the evening, and deep night setbacks all lose stored heat when no one benefits. The heating plant also has to recharge the mass every morning. Reilly & Kinnane measured 2–3.7× steady-state energy in Belfast. Hoes et al. (2011) found lightweight needed ~14% less heating than heavyweight with evening-only occupancy, but ~16% more with day-and-evening occupancy. De Vaan et al. found the crossover at a ~15 °C night setpoint.
2. **Hot-humid climates with small diurnal swings.** There is no cool night to discharge into, so lightweight, ventilated construction is preferable (Mora Juárez 2014).
3. **Mass outside the insulation.** It is decoupled from the room and adds little or harms (Kosny et al.; Reilly & Kinnane on internal vs external insulation).
4. **Misplaced mass.** Han et al. found mass in the wrong rooms or orientations raised energy use by up to 20% in daytime-use buildings.

## 4. Embodied carbon trade-off

- **Hacker et al. 2008 (UK, Arup):** the heaviest case had up to 15% higher initial embodied CO₂. Over 100 years, operational savings in a warming south-east England climate gave up to 17% lower life-cycle CO₂ (2006-era fabric, U ≈ 0.27 W/m²K; reported via GreenSpec). With today's lower-carbon grids and better fabric, the operational side of that balance shrinks.
- **Dodoo et al. 2012 (Sweden):** the heating saving from mass did not offset concrete's production energy. Timber frame had lower life-cycle primary energy.
- **Implication:** because the operational benefit saturates around a medium–heavy class, mass beyond that point is mostly embodied-carbon cost. Mass that is already needed for structure, acoustics or fire (party walls, floor slabs, screeds) is the "free" mass worth exposing. Adding mass for its own sake beyond ~50–100 mm per surface is hard to justify.

## 5. Value beyond kWh: load-shifting

As grids electrify, mass is increasingly valued as storage rather than for annual savings.

- **Dominković et al. 2018 (*Energy*):** flexible heating load from building mass equalled 5.5–7.7% of district heating demand. Well-insulated new buildings could ride through supply cut-offs of up to ~6 h without comfort loss.
- **Johra, Heiselberg & Le Dréau 2019 (*Energy and Buildings*):** envelope insulation dominated heating flexibility. In low-mass dwellings, furniture and contents raised the time constant by up to 42% and flexibility by ~21%. Johra & Heiselberg (2017) argue that models ignoring furniture mis-state the dynamics of lightweight buildings.

For heat-pump homes on time-of-use tariffs, this storage value probably keeps rising beyond the energy-saving knee, but with the same per-surface depth limit. Shifting a load over several hours draws on roughly the same 50–150 mm.

## 6. Bottom line

| Question | Answer from the evidence |
|---|---|
| How much heating energy does mass save in a low-energy dwelling? | A few percent, or a few kWh/m²·yr. Larger percentages in Passivhaus-level fabric, but small in absolute terms. |
| Useful depth per exposed surface (daily cycle)? | ~50–100 mm of dense material; little or nothing beyond ~100 mm on one face (~150–200 mm for a slab exposed on both faces). |
| Whole-house level where returns diminish? | ~165–260 kJ/m²K per m² of floor (medium to heavy). Above ~260, under 15% of the remaining benefit is left. |
| When is deeper mass justified? | Multi-day heatwave buffering in night-ventilated buildings, and passive-solar/Trombe walls (~250 mm). |
| When is more mass harmful? | Intermittent heating, deep setbacks, hot-humid climates, mass outside the insulation, or summer mass with no night purge. |
| What matters more than quantity? | Insulation, solar control and glazing, exposure (no coverings), placement inside the insulation, night ventilation, and matching to occupancy. |

## Sources

- Verbeke, S. & Audenaert, A. (2018). Thermal inertia in buildings: A review of impacts across climate and building use. *Renewable and Sustainable Energy Reviews* 82, 2300–2318. [IDEAS](https://ideas.repec.org/a/eee/rensus/v82y2018ip3p2300-2318.html) · [Antwerp repository](https://repository.uantwerpen.be/link/irua/147988)
- Kosny, J., Petrie, T., Gawin, D., Childs, P., Desjarlais, A. & Christian, J. (c. 2001). Thermal Mass – Energy Savings Potential in Residential Buildings. ORNL. [PDF](https://www.buildingstudies.org/pdf/energy_studies/ORNL_Thermal-Mass_Energy_Savings_Potential_in_Residential_Buildings.pdf)
- Han et al. (2025). Enhancing building energy efficiency with thermal mass optimization. *Advances in Applied Energy*. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666792425000186)
- Dodoo, A., Gustavsson, L. & Sathre, R. (2012). Effect of thermal mass on life cycle primary energy balances of a concrete- and a wood-frame building. *Applied Energy* 92, 462–472. [IDEAS](https://ideas.repec.org/a/eee/appene/v92y2012icp462-472.html)
- Reilly, A. & Kinnane, O. (2017). The impact of thermal mass on building energy consumption. *Applied Energy* 198, 108–121. [QUB PDF](https://pureadmin.qub.ac.uk/ws/files/131698229/impact_of_thermal_mass.pdf)
- Hoes, P., Trcka, M., Hensen, J.L.M. & Hoekstra Bonnema, B. (2011). Investigating the potential of a novel low-energy house concept with hybrid adaptable thermal storage. *Energy Conversion and Management* 52(6). PDF in `papers/hoes-2011-low-energy-house-adaptable-thermal-storage.pdf`. (An earlier version of this review cited figures from a 2012 Hoes presentation, which could not be retrieved; they have been replaced with figures from this paper.)
- de Vaan, C., Spoorenberg, H. & Wiedenhoff, J. (2008). Myth: heavy buildings have lower energy demand. [KTGO](https://www.ktgo.nl/expertpost/20081107-myth-heavy-buildings-have-lower-energy-demand-part-1/amp)
- Mantesi, E., Cook, M., Glass, J. & Hopfe, C. (2015). Review of the assessment of thermal mass in whole building simulation tools. *Building Simulation 2015*. [PDF](https://publications.ibpsa.org/proceedings/bs/2015/papers/bs2015_2193.pdf)
- Mora Juárez, C.E. (2014). Impact of Thermal Mass on Energy and Comfort: a parametric study in a temperate and a tropical climate. Chalmers. [Link](https://odr.chalmers.se/items/95ad1b90-db3a-404b-a2ba-3561a265d725/full)
- Kalogirou, S.A., Florides, G. & Tassou, S. (2002). Energy analysis of buildings employing thermal mass in Cyprus. *Renewable Energy* 27(3), 353–368. [Abstract](https://sel.me.wisc.edu/trnsys/validation/abstracts/renewableenergy/51.htm)
- Huntington, K. Passive overheating: does internal thermal mass make a difference? [EBOSS](https://eboss.co.nz/detailed/keith-huntington/passive-overheating-does-internal-thermal-mass-make-a-difference)
- Ma, P. & Wang, L.-S. (2012). Effective heat capacity of interior planar thermal mass (iPTM) subject to periodic heating and cooling. *Energy and Buildings*. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378778811005664)
- The Concrete Centre. Is 100mm of concrete enough in naturally-ventilated buildings? [Link](https://concretecentre.com/Performance-Sustainability/Thermal-Mass/100mm-of-concrete-to-achieve-thermal-mass.aspx)
- 2030 Palette. Direct gain heat storage. [Link](https://2030palette.org/direct-gain-heat-storage/)
- Jimenez-Bescos, C. (2017). An evaluation on the effect of night ventilation on thermal mass to reduce overheating in future climate scenarios. *Energy Procedia*. [Westminster](https://westminsterresearch.westminster.ac.uk/item/w9585/an-evaluation-on-the-effect-of-night-ventilation-on-thermal-mass-to-reduce-overheating-in-future-climate-scenarios)
- Rodrigues, L., Sougkakis, V. & Gillott, M. (2016). Investigating the potential of adding thermal mass to mitigate overheating in a super-insulated low-energy timber house. [Nottingham](https://nottingham-repository.worktribe.com/index.php/OutputFile/805241)
- Gauthier, S., Teli, D., James, P. & Stamp, S. Are heavyweight buildings more comfortable? [UCL PDF](https://discovery-pp.ucl.ac.uk/10104703/1/Are%20heavyweight%20buildings%20more%20comfortable.pdf)
- Kendrick, C., Ogden, R., Wang, X. & Baiche, B. (2012). Thermal mass in new build UK housing: a comparison of structural systems in a future weather scenario. *Energy and Buildings* 48, 40–49. [Record](https://structurae.info/fr/litterature/article-de-revue/thermal-mass-in-new-build-uk-housing-a-comparison-of-structural-systems-in-a-future-weather-scenario) (abstract not read)
- Hacker, J.N., De Saulles, T.P., Minson, A.J. & Holmes, M.J. (2008). Embodied and operational carbon dioxide emissions from housing: a case study on the effects of thermal mass and climate change. *Energy and Buildings* 40(3), 375–384. [UCL record](https://www.ucl.ac.uk/bartlett/energy/publications/2008/jan/embodied-and-operational-carbon-dioxide-emissions-housing-case-study-effects) · figures via [GreenSpec](https://greenspec.co.uk/building-design/concrete-exploiting-thermal-mass/)
- Dominković, D.F., Gianniou, P., Münster, M., Heller, A. & Rode, C. (2018). Utilizing thermal building mass for storage in district heating systems. *Energy* 153, 949–966. [IDEAS](https://ideas.repec.org/a/eee/energy/v153y2018icp949-966.html)
- Johra, H., Heiselberg, P. & Le Dréau, J. (2019). Influence of envelope, structural thermal mass and indoor content on the building heating energy flexibility. *Energy and Buildings*. [AAU](https://vbn.aau.dk/en/publications/influence-of-envelope-structural-thermal-mass-and-indoor-content-)
- Johra, H. & Heiselberg, P. (2017). Influence of internal thermal mass on the indoor thermal dynamics and integration of phase change materials in furniture for building energy storage: a review. *Renewable and Sustainable Energy Reviews* 69, 19–32. [IDEAS](https://ideas.repec.org/a/eee/rensus/v69y2017icp19-32.html)
- Rodrigues, E. et al. (2019). Thermal transmittance effect on energy consumption of Mediterranean buildings with different thermal mass. *Applied Energy* 252. [IDEAS](https://ideas.repec.org/a/eee/appene/v252y2019ic25.html)
- Standards used for the calculations: ISO 13786 (dynamic thermal characteristics) and ISO 13790 (monthly method, gain utilisation factor and heat-capacity classes). Home Energy Model's treatment of mass: [HEM](https://home-energy-model.co.uk/technical/thermal-mass/)

## Method notes and limits

- **Source access:** several sources were read only as abstracts or secondary summaries (Hacker et al. via GreenSpec, Kendrick et al. as a citation). Their numbers should be checked against the originals before anyone quotes them.
- **Calculation inputs:** the calculations use standard textbook material properties and an approximate London monthly climate. They show the shape of the diminishing-returns curve, not design values. Scripts are in `calc/` next to this file.
