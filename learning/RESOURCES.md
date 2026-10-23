# Thermal Mass and Building Physics Resources

## Knowledge

- [Book: _A Heat Transfer Textbook_, 6th ed. (2024), J.H. Lienhard IV & J.H. Lienhard V](https://ahtt.mit.edu/)
  Free from the authors (MIT). Rigorous, readable heat transfer. Use for: rate laws (ch. 1), thermal resistance (ch. 2), transient and periodic conduction (ch. 5), radiation (ch. 10).
- [Course: _Energy in buildings_, The Open University (OpenLearn)](https://www.open.edu/openlearn/nature-environment/energy-buildings/content-section-0)
  Free, short, UK-focused. Use for: U-values, heat loss coefficients, ventilation loss and the 0.33 nV rule ([section 3.3](https://www.open.edu/openlearn/nature-environment/energy-buildings/content-section-3.3)).
- Standard: EN ISO 13786:2017, _Dynamic thermal characteristics: calculation methods_
  The matrix method for admittance, decrement factor, time lag and kappa_1. Use for: lesson 4 and any build-up comparison. Implemented and checked in the project's `physics/iso13786.py`.
- Standard: EN ISO 6946:2017, _Thermal resistance and thermal transmittance_
  Surface resistances (Rsi 0.10/0.13/0.17) and U-value method. Use for: surface coefficients.
- Standard: EN ISO 52016-1:2017, hourly method with multi-node elements and mass distribution classes. Use for: lesson 6.
- Book: CIBSE Guide A (2015), _Environmental design_, chapter 5
  The UK admittance method. Probably in the Max Fordham library. Use for: admittance, surface factor, cyclic heat balance.
- Report: HEM-TP-07 v2.0, _Calculating thermal mass within the Home Energy Model_ (DESNZ)
  Gwilym has a copy. Use for: how HEM places mass in five nodes per element.
- Paper: Roberts et al. (2019), _Predictions of summertime overheating: comparison of dynamic thermal models and measurements in synthetically occupied test houses_, BSERT 40(4) 512-552, doi:10.1177/0143624419847349 (CC BY)
  In the project uploads. Use for: lesson 6 and 7, how far models are from measurements.
- Paper: Peeters, Beausoleil-Morrison & Novoselac (2011), _Internal convective heat transfer modeling: critical review_, Energy and Buildings 43
  Use for: why h_c is uncertain and how tools differ.
- Book: Davies, M.G. (2004), _Building Heat Transfer_, Wiley. Use for: deeper theory of admittance and RC networks.
- Report: Milbank & Harrington-Lynn (1974), _Thermal response and the admittance procedure_, BRE CP 61/74. Use for: origin of the admittance method.
- Project: `physics/thermal-mass-physics.md` and the shared models in `/mnt/project-files/models/` (Build-up Explorer, Conduction Lab, House Simulator, Mass Sweeps). Checked against ISO 13786 Annex D and ASHRAE 140. Use for: worked numbers and interactive demos in later lessons.
- Project: `/mnt/project-files/literature/thermal-mass-quantity-and-diminishing-returns.md` and the summary PDF. Use for: lesson 7.

## Wisdom (Communities)

- ReMass workshop and consortium, Oxford, 29-30 Oct 2026
  The best place to test this: modellers and experimentalists working on exactly this question. Use for: arguing about model gaps and what measurements show.
- [CIBSE Building Simulation Group](https://www.cibse.org/get-involved/special-interest-groups/building-simulation-group/)
  UK practitioners and researchers; regular evening talks (one listed for 19 Nov 2026). Use for: how practice models mass, HEM and TM59 questions.
- IBPSA-England
  The UK chapter of the international building simulation association; ran a joint symposium with CIBSE in 2025. Use for: research-side discussion.
- [BLDG-SIM mailing list (onebuilding.org)](https://onebuilding.org/)
  Long-running list for simulation users. Current activity not verified. Use for: tool-specific questions.

## Gaps

- No free, authoritative online text on the admittance method; CIBSE Guide A and ISO 13786 are paywalled.
- No primary source yet for indoor h_c design values beyond Peeters et al.; CIBSE Guide A ch. 3 would fill this.
- Couldn't open web pages from the teaching environment on 2026-10-23, so chapter numbers in Lienhard are from memory and search snippets, not checked against the PDF.
