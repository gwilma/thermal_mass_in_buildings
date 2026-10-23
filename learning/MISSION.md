# Mission: Thermal mass and building physics

_Confirmed by Gwilym, 2026-10-23: "Both A, B, and C. I don't just want to be able to defend numbers, I want a full understanding of the topic."_

## Why

Gwilym wants a full, first-principles understanding of thermal mass in buildings. He wants it for three uses at once. First, his ReMass talk ("Thermal mass in current engineering practice", Oxford, 29 October 2026), where he wants to hold his own with researchers. Second, judging thermal mass in real projects as an engineer. Third, building and auditing models of it himself.

## Success looks like

Physics (the core)
- Writes the room heat balance and sizes each term in watts without notes.
- Derives the heat diffusion equation and explains penetration depth, effusivity and diffusivity from it.
- Calculates admittance, kappa_1, decrement factor and time lag for a build-up, and explains what each one means physically.
- Explains the time constant tau = C/H and how much a building attenuates swings.

Practice
- Estimates peak summer temperatures and the effect of exposing mass or night ventilation by hand, before modelling.
- Reads overheating results (TM59, TM52) and model outputs critically, and spots when a claimed mass benefit won't happen.
- Knows when mass helps and when it hurts (constant setpoints, warm nights, bedrooms, intermittent heating), with evidence.

Modelling
- Builds a finite-difference wall model and an RC zone model from scratch and checks them against ISO 13786 Annex D.
- Explains how the admittance method, 5R1C, ISO 52016 and HEM's five-node elements represent mass, and where each goes wrong.
- Audits the project's own models and code.

## Constraints

- The ReMass talk is on 29 October, so Part A (the physics) comes first and fits in about six days. Parts B and C run after.
- Lessons stay short (about 20 minutes) even though the course is long.
- Web pages can't be fetched from the teaching environment; facts come from the project's checked notes and models, plus web search.
- Gwilym works in building services engineering (Max Fordham), so examples should look like engineering problems.

## Out of scope

- Hygrothermal (moisture) modelling beyond a mention.
- Phase change materials in depth.
- Embodied carbon calculation methods (only as a limit on adding mass).
