# The physics of thermal mass in operation

*A working summary: governing equations, the main analytical and numerical solutions, and how to characterise the thermal mass of a build-up. Worked numbers come from [`iso13786.py`](iso13786.py), which implements the EN ISO 13786 matrix method and was checked against an independent finite-difference simulation (agreement to two decimal places for admittance, decrement factor and time lag).*

---

## 1. What thermal mass actually does

"Thermal mass" is shorthand for the ability of the building fabric to **store and release sensible heat over the timescale of the driving loads**. In operation it does three things:

1. **Attenuates** temperature swings. A heat gain that would raise room temperature quickly is partly absorbed into surfaces, so the peak is lower.
2. **Delays** the response. Heat stored during the day is released hours later, shifting peaks (useful for overheating and for shifting heating/cooling demand in time).
3. **Couples** the room to a longer memory. The room temperature depends on the history of gains, weather and ventilation over hours to days, not just the present moment.

Three conditions must all hold for mass to do useful work:

- **Capacity**: the material must hold heat ($\rho c$ large).
- **Accessibility**: heat must be able to get into and out of it on the timescale of interest. This depends on the material's conductivity, the surface heat transfer coefficient, and anything (linings, carpets, suspended ceilings, furniture) between the room and the mass.
- **A driving temperature swing**: mass only exchanges heat when its surface temperature differs from the room's. A room held at a fixed setpoint 24 h a day with no free-running periods makes little use of its mass. Mass "works" through *temperature variation*, whether that comes from gains, solar, night ventilation, or deliberately allowed setpoint drift.

The rest of this note puts equations behind these three conditions.

---

## 2. Governing equations

### 2.1 Conduction in the fabric

Fourier's law for the conductive heat flux $q$ (W/m²):

$$
\mathbf{q} = -\lambda \nabla \theta
$$

Conservation of energy in a solid with no internal sources gives the heat diffusion equation. For a wall or slab, one-dimensional treatment through the thickness $x$ is almost always adequate:

$$
\rho c \,\frac{\partial \theta}{\partial t} = \frac{\partial}{\partial x}\!\left(\lambda \frac{\partial \theta}{\partial x}\right)
\quad\xrightarrow{\ \lambda\ \text{constant}\ }\quad
\frac{\partial \theta}{\partial t} = \alpha\,\frac{\partial^2 \theta}{\partial x^2},
\qquad \alpha = \frac{\lambda}{\rho c}
$$

| Symbol | Quantity | Units |
|---|---|---|
| $\lambda$ | thermal conductivity | W/(m·K) |
| $\rho$ | density | kg/m³ |
| $c$ | specific heat capacity | J/(kg·K) |
| $\rho c$ | volumetric heat capacity | J/(m³·K) |
| $\alpha = \lambda/\rho c$ | thermal diffusivity: how fast a temperature change *spreads* | m²/s |
| $b = \sqrt{\lambda\rho c}$ | thermal effusivity: how readily a surface *exchanges* heat with what touches it | J/(m²·K·s½) |

Two properties matter, not one. **Diffusivity** governs how deep a disturbance penetrates in a given time. **Effusivity** governs how much heat a surface absorbs for a given surface temperature swing. Dense concrete has high values of both; timber has low values of both; mineral wool has *high* diffusivity but negligible effusivity (heat gets in fast but there's almost nothing to store it in).

At an interface between layers in perfect contact, temperature and heat flux are continuous. A contact resistance or air gap is modelled as a thermal resistance $R$ with no capacity.

### 2.2 Surface boundary conditions

At the **internal surface**, heat arrives by convection from the room air, longwave radiation exchange with other surfaces, and absorbed shortwave (solar, lighting) and radiant gains:

$$
-\lambda \left.\frac{\partial \theta}{\partial x}\right|_{s}
= h_c(\theta_{a} - \theta_s) + \sum_j h_{r,j}(\theta_{s,j} - \theta_s) + q_{sw} + q_{rad}
$$

The longwave term is linearised from Stefan–Boltzmann:

$$
h_r \approx 4\,\varepsilon\,\sigma\,\bar{T}^3 \approx 5\text{–}5.5\ \text{W/(m}^2\text{K)} \quad \text{at room temperatures, } \varepsilon \approx 0.9
$$

Convective coefficients are much smaller and strongly dependent on the flow regime:

| Situation | Typical $h_c$ (W/m²K) |
|---|---|
| Natural convection, vertical wall | 1.5–3 |
| Ceiling, heat flowing *up* into it (warm air under cool slab, i.e. night-cooled soffit during the day) | 3–5 |
| Ceiling, heat flowing *down* (warm slab over cooler air) | 0.5–1 |
| Mixed/forced convection, night ventilation jets, ceiling fans | 4–10+ |

The design value $R_{si} = 0.13$ m²K/W (EN ISO 6946, horizontal flow) corresponds to a combined $h_c + h_r \approx 7.7$ W/m²K. **This surface coefficient is the single biggest throttle on how much mass a room can use** (section 4.4).

At the **external surface**, solar absorption is conveniently folded into a *sol-air temperature*:

$$
\theta_{sa} = \theta_e + \frac{a\,I_{sol}}{h_e} - \frac{\varepsilon\,\Delta q_{lw}}{h_e},
\qquad q_{e} = h_e\,(\theta_{sa} - \theta_{s,e})
$$

where $a$ is solar absorptance, $I_{sol}$ incident irradiance, $h_e \approx 25$ W/m²K and $\Delta q_{lw}$ the net longwave loss to sky (≈ 60–100 W/m² for a clear sky on a roof).

### 2.3 The zone energy balance

The fabric equations are coupled through the room air node:

$$
\rho_a c_a V\,\frac{d\theta_a}{dt}
= \sum_i h_{c,i} A_i\,(\theta_{s,i} - \theta_a)
+ \dot{m}\,c_a\,(\theta_{e} - \theta_a)
+ \Phi_{conv} + \Phi_{HVAC}
$$

The air term on the left is tiny: a 50 m³ room holds about 60 kJ/K of air, compared with several MJ/K in a concrete soffit. Room air temperature is therefore effectively set by the surfaces, the ventilation, and convective gains, with the fabric doing nearly all the storage. Comfort depends on **operative temperature**, roughly the mean of air and mean radiant temperature:

$$
\theta_{op} \approx \tfrac{1}{2}(\theta_a + \bar\theta_{r})
$$

so cool massive surfaces help comfort directly through radiation, not only by cooling the air.

Ventilation heat flow $\dot m c_a(\theta_e-\theta_a)$ is the main way stored heat leaves a free-running building at night. Night ventilation discharges the mass **only via the surface convective coefficient**: the air passing the soffit must actually be warmed by it. That is why air speed over the surface and the slab–air temperature difference govern night-cooling performance.

---

## 3. Analytical solutions and what they reveal

### 3.1 Step change on a semi-infinite solid

If the surface of a thick solid at $\theta_0$ is suddenly held at $\theta_s$:

$$
\frac{\theta(x,t)-\theta_s}{\theta_0-\theta_s} = \operatorname{erf}\!\left(\frac{x}{2\sqrt{\alpha t}}\right),
\qquad
q_s(t) = \frac{b\,(\theta_s-\theta_0)}{\sqrt{\pi t}}
$$

The disturbance reaches a depth of order $\sqrt{\alpha t}$. Surface heat flux is proportional to **effusivity** $b$ and decays as $t^{-1/2}$. Two practical points follow: diffusion depth grows only as the square root of time, and a high-$b$ surface keeps soaking up heat for hours.

### 3.2 Periodic forcing: the thermal wave

Buildings are mostly driven by a daily cycle. For a surface temperature $\theta_s = \hat\theta \cos\omega t$ on a semi-infinite solid, with $\omega = 2\pi/T$:

$$
\theta(x,t) = \hat\theta\, e^{-x/\delta}\cos\!\left(\omega t - \frac{x}{\delta}\right),
\qquad
\delta = \sqrt{\frac{2\alpha}{\omega}} = \sqrt{\frac{\lambda T}{\pi\rho c}}
$$

$\delta$ is the **periodic penetration depth**. At depth $\delta$ the swing is reduced to $1/e$ (37 %) and delayed by $T/2\pi$ (3.8 h for a 24 h cycle). At $3\delta$ it is down to 5 %.

| Material | $\alpha$ (mm²/s) | $b$ (J/m²Ks½) | $\delta$, 1 h | $\delta$, 24 h | $\delta$, 7 days |
|---|---|---|---|---|---|
| Dense concrete (λ 2.0, ρ 2400, c 1000) | 0.83 | 2190 | 31 mm | **151 mm** | 401 mm |
| Brick (0.77, 1700, 800) | 0.57 | 1020 | 25 mm | **125 mm** | 330 mm |
| Dense block (1.13, 2000, 1000) | 0.56 | 1500 | | **125 mm** | |
| Rammed earth (1.0, 1900, 900) | 0.58 | 1310 | | **127 mm** | |
| Aerated block (0.15, 600, 1000) | 0.25 | 300 | | **83 mm** | |
| Plasterboard (0.21, 700, 1000) | 0.30 | 380 | | **91 mm** | |
| CLT, softwood (0.13, 470, 1600) | 0.17 | 310 | 14 mm | **69 mm** | 182 mm |
| Mineral wool (0.035, 30, 1030) | 1.13 | 33 | | 176 mm | |

The surface heat flux leads the surface temperature by $T/8$ (3 h for a daily cycle) and has amplitude

$$
\hat q_s = b\sqrt{\omega}\;\hat\theta_s
$$

So effusivity is the property that sets a material's intrinsic, surface-resistance-free "admittance" ($b\sqrt\omega \approx 18.7$ W/m²K for dense concrete at 24 h).

### 3.3 Finite layers and multilayer build-ups: the transfer matrix

For a layer of finite thickness $d$, the periodic solution links the complex amplitudes of temperature and heat flux on its two faces through a 2×2 matrix. With $\xi = d/\delta$:

$$
\begin{pmatrix}\hat\theta_2\\ \hat q_2\end{pmatrix}
= \mathbf{Z}
\begin{pmatrix}\hat\theta_1\\ \hat q_1\end{pmatrix},
\qquad
\mathbf{Z} = \begin{pmatrix} Z_{11} & Z_{12}\\ Z_{21} & Z_{22}\end{pmatrix}
$$

$$
\begin{aligned}
Z_{11} = Z_{22} &= \cosh\xi\cos\xi + i\,\sinh\xi\sin\xi \\
Z_{12} &= -\frac{\delta}{2\lambda}\big[\sinh\xi\cos\xi + \cosh\xi\sin\xi + i(\cosh\xi\sin\xi - \sinh\xi\cos\xi)\big] \\
Z_{21} &= -\frac{\lambda}{\delta}\big[\sinh\xi\cos\xi - \cosh\xi\sin\xi + i(\sinh\xi\cos\xi + \cosh\xi\sin\xi)\big]
\end{aligned}
$$

A pure resistance (surface film, cavity, insulation treated as massless) is $\begin{pmatrix}1 & -R\\ 0 & 1\end{pmatrix}$. A whole build-up is the product of its layer matrices, from internal to external:

$$
\mathbf{Z} = \mathbf{Z}_{se}\,\mathbf{Z}_N \cdots \mathbf{Z}_2\,\mathbf{Z}_1\,\mathbf{Z}_{si}
$$

This is the method of EN ISO 13786, and it is exact for linear, one-dimensional, sinusoidal conditions. Everything in section 5.2 is derived from the four elements of $\mathbf Z$. Because the problem is linear, any periodic weather and gains can be decomposed into harmonics (24 h, 12 h, 8 h, …) and treated separately, which is the basis of the CIBSE admittance method.

### 3.4 Lumped capacitance, Biot and Fourier numbers

When temperature inside an element is close to uniform, the element can be treated as a single capacitance. The test is the **Biot number**, which compares internal conductive resistance with the surface resistance:

$$
\mathrm{Bi} = \frac{h\,L}{\lambda}
$$

with $L$ the depth heat must travel (half the thickness for a slab exposed both sides). If $\mathrm{Bi} \lesssim 0.1$ the element behaves as a lump with time constant

$$
\tau = \frac{\rho c L}{h}, \qquad \theta(t) - \theta_\infty = (\theta_0 - \theta_\infty)\,e^{-t/\tau}
$$

The **Fourier number** $\mathrm{Fo} = \alpha t / L^2$ is dimensionless time: for $\mathrm{Fo}\ll 1$ the element still behaves as semi-infinite; for $\mathrm{Fo}\gtrsim 1$ the whole depth has responded.

For a 200 mm concrete slab with $h = 7.7$ W/m²K, $\mathrm{Bi} \approx 0.77$, so it is *not* a lump: the surface and core temperatures differ substantially within a day. That non-uniformity is exactly why admittance, not total capacity, governs diurnal behaviour.

### 3.5 The whole building as an RC circuit

At the scale of a building, the simplest useful model is one capacitance $C$ (J/K) connected to outside through a total heat-loss coefficient $H = H_{tr} + H_{ve}$ (W/K):

$$
C\,\frac{d\theta_i}{dt} = \Phi_{gains} + \Phi_{HVAC} - H(\theta_i - \theta_e),
\qquad \tau = \frac{C}{H}
$$

Response to a steady sinusoidal driver of period $T$:

$$
\frac{\hat\theta_i}{\hat\theta_{\text{no mass}}} = \frac{1}{\sqrt{1+(\omega\tau)^2}},
\qquad \text{phase lag} = \frac{\arctan(\omega\tau)}{\omega}
$$

This gives the right intuition: as $\tau$ grows past about 4 h ($\omega\tau > 1$ for a daily cycle), swings attenuate strongly and the lag tends to 6 h. Typical building time constants range from under 10 hours (lightweight, leaky) to over 100 hours (heavyweight, well insulated). The time constant also sets **how long the building takes to warm up or cool down**: preheat periods, the intermittent-heating penalty, and how many hours a heat pump can be switched off (demand flexibility) before the temperature drifts out of the comfort band.

The single-node model is too crude for diurnal work because, as section 3.4 showed, mass is not isothermal. Practical models add nodes: the EN ISO 13790 / 52016-1 **5R1C** model separates air, surface and mass nodes. EN ISO 52016-1's hourly method gives each element several capacitive nodes, with its mass split according to a *mass distribution class* (section 5.4).

---

## 4. What the physics implies in operation

### 4.1 Only a skin of the fabric participates in the daily cycle

On a 24 h cycle, admittance and $\kappa_1$ for a layer backed by insulation increase with thickness until about $0.6$–$0.7\,\delta$, then **level off and fall slightly**. Values are $Y$ (W/m²K) / $\kappa_1$ (kJ/m²K):

| Exposed layer | 25 mm | 50 mm | 75 mm | 100 mm | 150 mm | 200 mm | 300 mm |
|---|---|---|---|---|---|---|---|
| Dense concrete | 3.7 / 52 | 5.5 / 76 | 6.1 / 85 | **6.3 / 87** | 6.2 / 86 | 6.1 / 84 | 5.8 / 80 |
| Dense block | 3.2 / 45 | 5.0 / 69 | 5.6 / 77 | **5.7 / 79** | 5.5 / 77 | 5.3 / 73 | 5.2 / 71 |
| Rammed earth | 2.9 / 40 | 4.5 / 63 | 5.2 / 73 | **5.4 / 75** | 5.3 / 73 | 5.1 / 70 | 4.9 / 68 |
| Brick | 2.4 / 33 | 3.9 / 54 | 4.7 / 65 | **4.9 / 68** | 4.8 / 67 | 4.6 / 63 | 4.4 / 61 |
| CLT (softwood) | 1.3 / 19 | 2.1 / 30 | **2.3 / 33** | 2.3 / 32 | 2.1 / 29 | 2.1 / 29 | 2.1 / 29 |
| Aerated block | 1.1 / 16 | 1.9 / 26 | 2.2 / 31 | **2.2 / 32** | 2.1 / 29 | 2.0 / 28 | 2.0 / 28 |

*(Each layer is backed by 100 mm PIR, with $R_{si} = 0.13$.)*

This is the physical basis of the familiar "**first 100 mm**" rule for dense materials (and roughly 50–75 mm for timber). A 200 mm slab holds 480 kJ/m²K in total but exchanges only about 85 kJ/m²K per kelvin of daily swing. The deeper mass is not wasted: it comes into play over **longer periods**. For example, the same 200 mm slab has $\kappa_1 = 84$ kJ/m²K on a 24 h cycle, but on a 7-day cycle (a heatwave, or a weekend setback) its $\kappa_1$ rises to about 360 kJ/m²K (220 on a 3-day cycle), because the penetration depth in concrete is 400 mm on that timescale.

### 4.2 The surface coefficient caps the benefit

Even an infinitely conductive, infinitely thick surface cannot have admittance above $1/R_{si} \approx 7.7$ W/m²K. Semi-infinite concrete has an intrinsic $b\sqrt\omega = 18.7$ W/m²K, but behind $R_{si} = 0.13$ its admittance falls to **5.8 W/m²K**. Hence:

- Improving the surface coupling (exposed soffits, airflow across them, coffered or profiled soffits that add area, ceiling fans) often adds more effective mass than adding thickness.
- Anything that adds resistance at the surface throttles access hard. A **plasterboard-on-dabs lining** over dense block cuts admittance from 5.2 to 3.2 W/m²K and $\kappa_1$ from 72 to 44 kJ/m²K. Carpets and underlay, raised floors, suspended ceilings and acoustic panels do the same.
- At short periods (sub-hourly gains, a sunny hour on a floor), the surface coefficient dominates even more. Admittance of the 200 mm slab rises only to 7.3 W/m²K at a 1 h period.

### 4.3 Placement relative to insulation

Mass that faces the room and sits **inside the insulation** is what moderates internal conditions. Mass outside the insulation (e.g. the outer leaf of a cavity wall) contributes to decrement and lag of heat flowing *through* the element, but very little to admittance. For a well-insulated envelope, transmission is so small that decrement and lag matter little. **For modern construction the internal surface is where the action is**: internal walls, floors and soffits often provide most of a building's accessible mass.

### 4.4 Charging and discharging pathways

- **Radiant gains** (solar patches, people, equipment, radiant heating and cooling) land directly on surfaces and are absorbed by mass with no convective step. Sunlit massive floors are the most direct storage path.
- **Convective gains** must first warm the air, then reach surfaces via $h_c$, which is small.
- **Night ventilation** removes heat only at the rate $h_c A(\theta_s - \theta_a)$. A soffit at 25 °C cooled by 18 °C air with $h_c = 3$ W/m²K discharges about 21 W/m². Doubling the air speed over the surface matters more than doubling the airflow if the air short-circuits past the slab. The ventilation must also carry the heat away: $\dot m c_a(\theta_{a} - \theta_e)$.
- **Embedded pipes** (thermally activated building systems) bypass the surface bottleneck by charging the mass from inside.

A daily energy budget follows from $\kappa_1$. For the exposed 200 mm concrete soffit, a 4 K peak-to-peak surface-side swing stores about $84 \times 4 \approx 340$ kJ/m², or **≈ 95 Wh/m² of soffit per cycle**. That's the scale of daytime gain that can be absorbed and then purged.

### 4.5 Comfort, heating and the downsides

- In free-running and mixed-mode buildings, mass lowers peak operative temperature and delays it into the evening and night. That is helpful in offices; it can be unhelpful in **bedrooms** if the night purge is poor, because stored heat comes back at night.
- In continuously heated buildings, mass has little effect on annual heat demand by itself. Its benefit is utilising intermittent solar and internal gains (raising the *gain utilisation factor*, in EN ISO 52016 / 13790 terms), and allowing load shifting.
- With **intermittent heating** (occupied a few hours a day), heavy, exposed mass increases warm-up time and energy, since the mass has to be heated too. Internal insulation or lightweight linings respond faster.
- Mass cannot dump heat it has no sink for: in a long, hot spell with warm nights, it delays and averages, but the average still rises. Multi-day behaviour depends on total accessible capacity and on night-time sink temperatures.

### 4.6 Second-order effects worth knowing

- **Temperature-dependent properties and moisture**: $\lambda$ rises with moisture content; hygroscopic materials (earth, timber, lime plaster) also buffer latent heat via moisture sorption. The coupled heat and moisture equations (e.g. EN 15026, Künzel model) are needed to capture this.
- **Phase change materials** add a latent term: $\rho\,\partial h/\partial t = \nabla\cdot(\lambda\nabla\theta)$ with an enthalpy–temperature curve that is steep over the melt range. They help only if the room actually cycles through the melt range daily, and their thinness makes surface coupling even more decisive.
- **Two- and three-dimensional effects** (slab edges, ground coupling) add long-period storage. The ground behaves as a semi-infinite solid with seasonal penetration depth of a few metres (EN ISO 13370).

---

## 5. Characterising the thermal mass of a build-up

No single number captures thermal mass. The metrics below answer different questions, and they rank build-ups differently.

### 5.1 Total areal heat capacity

$$
\kappa_{tot} = \sum_j \rho_j c_j d_j \quad [\text{kJ/(m}^2\text{K)}]
$$

This is easy to calculate but **overstates useful mass**, because it ignores accessibility. Using it, a 200 mm concrete soffit (480 kJ/m²K) looks six times better than 100 mm CLT (80 kJ/m²K), when on a daily cycle it is about 2.6 times better. It is relevant for multi-day and seasonal behaviour.

### 5.2 EN ISO 13786 dynamic thermal characteristics

From the build-up matrix $\mathbf Z$ (section 3.3), with side 1 internal:

| Quantity | Definition | Meaning |
|---|---|---|
| **Internal (thermal) admittance** $Y_{11}$ | $\lvert -Z_{11}/Z_{12}\rvert$, W/m²K | Heat flux amplitude into the internal surface per K of internal temperature swing, with the outside held steady. **The headline metric for diurnal mass.** |
| Admittance time shift | $\frac{T}{2\pi}\arg(Y_{11})$, h | How far the stored heat flow *leads* the room temperature. It is about 1 h for dense materials and 2–3 h for timber or lightweight block. |
| **Periodic thermal transmittance** $Y_{12}$ | $\lvert -1/Z_{12}\rvert$, W/m²K | Flux at the inside surface per K of *external* swing. |
| **Decrement factor** $f$ | $\lvert Y_{12}\rvert / U$ | Fraction of the steady-state U-value that a daily swing transmits. |
| **Time lag** $\Delta t$ | $-\frac{T}{2\pi}\arg(Y_{12})$, h | Delay between external and internal peaks. |
| **Internal areal heat capacity** $\kappa_1$ | $\frac{T}{2\pi}\left\lvert\frac{Z_{11}-1}{Z_{12}}\right\rvert$, kJ/m²K | Effective storage per m² per K of swing at period $T$. Roughly $\lvert Y_{11}\rvert/\omega$. |
| Surface factor $F$ (CIBSE) | $\approx 1 - R_{si}\,Y_{11}$ (complex, so it has a phase) | Fraction of radiant gain on the surface that is re-released to the room straight away. |

Worked values for representative build-ups (24 h period, $R_{si} = 0.13$, $R_{se} = 0.04$; floor uses $R_{si} = 0.17$):

| Build-up (inside → outside) | U | $Y$ | Y lead (h) | $f$ | lag (h) | $\kappa_1$ | $\kappa_{tot}$ |
|---|---|---|---|---|---|---|---|
| Exposed 200 mm concrete soffit, 100 mm PIR | 0.21 | **6.1** | 0.8 | 0.17 | 8.2 | **84** | 484 |
| 13 mm plaster, 100 mm dense block, 150 mm MW, brick | 0.21 | **5.2** | 1.4 | 0.25 | 9.9 | **72** | 360 |
| Same but plasterboard on dabs instead of wet plaster (dab cavity R = 0.1 assumed) | 0.21 | **3.2** | 1.0 | 0.16 | 10.5 | **44** | 352 |
| 13 mm plaster, 100 mm aerated block, 150 mm MW, brick | 0.19 | **2.8** | 2.7 | 0.36 | 10.1 | **40** | 220 |
| Exposed 100 mm CLT, 150 mm MW | 0.19 | **2.3** | 2.3 | 0.41 | 7.1 | **32** | 80 |
| 65 mm screed on 100 mm PIR (floor) | 0.21 | **4.6** | 1.9 | 0.49 | 5.2 | **63** | 134 |
| 300 mm rammed earth, uninsulated | 2.13 | **4.9** | 1.2 | 0.32 | 8.7 | **76** | 513 |
| Plasterboard on 150 mm MW timber frame | 0.22 | **0.75** | 4.4 | 0.98 | 1.4 | **11** | 13 |

*Units: U, Y in W/m²K; κ in kJ/m²K. Material properties are typical book values and are listed in `iso13786.py`.*

These numbers show the main points of section 4: the lining matters as much as the core; κ_tot misranks build-ups; and the floor screed, though thin, is a useful store because it is directly exposed.

### 5.3 Simplified "effective thickness" rules

Before the matrix method became routine, and still in simplified standards, the effective capacity is estimated by summing $\rho c d$ only over an *effective thickness* measured from the internal surface. The simplified methods in EN ISO 13786 Annex A (which also underlie the κ values tabulated for SAP) take the smallest of:

- half the total thickness of the element,
- the thickness up to the first insulating layer (the standard sets a conductivity threshold for what counts as insulating), and
- 100 mm.

This is a reasonable proxy for κ₁ for dense, wet-finished construction. It cannot represent the throttling effect of linings and cavities, which the matrix method captures.

### 5.4 Whole-building indicators used in calculation methods

| Indicator | Definition | Where used |
|---|---|---|
| **Thermal Mass Parameter (TMP)** | $\sum \kappa_j A_j / \text{TFA}$, kJ/(m²K) per m² floor. Default bands: low 100, medium 250, high 450 | SAP 2012/10 (UK). Feeds the gain utilisation factor and the time constant. |
| **Internal heat capacity $C_m$ and time constant** | $C_m = \sum \kappa_j A_j$; $\tau = C_m / H$ | EN ISO 13790 / 52016-1. Default classes from very light to very heavy ($C_m$ from about 80 to 370 kJ/K per m² of floor in 13790). |
| **Element areal capacity and mass distribution class** | Each opaque element has a capacity class (e.g. 50 to 250 kJ/m²K) and a class saying where the mass sits: internal (I), external (E), split (IE), distributed (D), or middle (M) | EN ISO 52016-1 hourly method, and the UK Home Energy Model, which builds on it. The class sets how the element's capacity is placed across its nodes. |
| **Admittance sum $\sum A Y$** | Total room admittance, W/K | CIBSE admittance method: the swing in room temperature is $\tilde\theta \approx \tilde\Phi / (\sum AY + \tilde H_{v})$ |

Note that the TMP and the 52016 classes are based on areal heat capacity, not admittance. That means two build-ups with the same κ but different surface coupling or lining can look identical. Explicit layer-by-layer input avoids this.

### 5.5 Material-level indicators

For comparing materials (rather than build-ups): effusivity $b$ (fast surface exchange), diffusivity $\alpha$ (how deep and fast heat penetrates), volumetric capacity $\rho c$, and the derived penetration depth $\delta$ at the period of interest. Ideal diurnal storage materials have **high $b$**. Their optimal exposed thickness is of the order of $0.5$–$0.7\,\delta$.

### 5.6 Measurement

In situ and laboratory characterisation generally uses one of:

- **Heat-flux plate + surface and air temperature logging**, fitting admittance or an RC model to measured periodic data (e.g. guarded hot box with sinusoidal forcing, or in situ with natural cycles).
- **Co-heating and cool-down tests**: after a steady heated period, heating is cut and the temperature decay is fitted for the whole-building time constant $\tau = C/H$. With $H$ from the co-heating test, the effective capacity $C$ follows.
- **Grey-box system identification**: fitting low-order RC networks (e.g. 2R2C or 3R2C) to monitored data from occupied or synthetically occupied houses gives an effective capacity and its coupling resistance.

The effective capacity from such tests depends on the timescale of the forcing, consistent with section 4.1.

---

## 6. Numerical methods in simulation tools

| Method | Idea | Notes |
|---|---|---|
| **Finite difference / finite volume** | Discretise each layer into nodes and step through time | Explicit stepping is stable only if $\mathrm{Fo}_{cell} = \alpha\Delta t/\Delta x^2 \le 0.5$ (thin, conductive layers need small steps); implicit or Crank–Nicolson schemes are unconditionally stable. Handles PCMs, variable properties and moisture. Used by ESP-r, the EnergyPlus CondFD option and WUFI. |
| **Response factors / conduction transfer functions** | Precompute the element's response to a unit pulse, then superpose | Fast and exact for linear, constant-property layers. EnergyPlus default; IES and TAS are similar. |
| **Lumped RC networks** | Few nodes per element or zone | Fast and transparent; accuracy depends on how the capacity is split and coupled. Used by EN ISO 52016-1, HEM, 5R1C, and grey-box models. |
| **Harmonic / admittance** | Treat mean and swing separately using $Y$, $f$, $F$ | Hand-calculable; assumes periodic steady state and linearity. Used by CIBSE Guide A. |

Common sources of model error for mass: the choice of internal convection algorithm (fixed vs. temperature-difference dependent $h_c$), how furniture and internal partitions are represented, treatment of linings and air gaps, solar distribution on floors, and assumed ventilation airflows at night. These are often larger than any error from the conduction solution itself.

---

## 7. Key relationships at a glance

$$
\begin{aligned}
&\text{Diffusion:} && \partial_t\theta = \alpha\,\partial_{xx}\theta, \quad \alpha = \lambda/\rho c \\
&\text{Penetration depth:} && \delta = \sqrt{\lambda T/(\pi\rho c)} \quad (\approx 150\text{ mm concrete}, 70\text{ mm timber at 24 h}) \\
&\text{Surface exchange (no film):} && \lvert Y\rvert = b\sqrt{\omega}, \quad b = \sqrt{\lambda\rho c} \\
&\text{Surface-film ceiling:} && \lvert Y\rvert < 1/R_{si} \approx 7.7\ \text{W/m}^2\text{K} \\
&\text{Effective storage per cycle:} && \kappa_1 \approx \lvert Y_{11}\rvert/\omega \\
&\text{Lumping test:} && \mathrm{Bi} = hL/\lambda \lesssim 0.1 \\
&\text{Building time constant:} && \tau = C/H; \ \text{attenuation } 1/\sqrt{1+(\omega\tau)^2}
\end{aligned}
$$

---

## References

- EN ISO 13786:2017 *Thermal performance of building components: dynamic thermal characteristics: calculation methods.*
- EN ISO 52016-1:2017 *Energy performance of buildings: energy needs for heating and cooling, internal temperatures and sensible and latent heat loads: calculation procedures.* (Replaces EN ISO 13790:2008.)
- EN ISO 6946:2017 *Building components and building elements: thermal resistance and thermal transmittance.*
- CIBSE Guide A (2015), *Environmental design*, chapter 5 (thermal response and the admittance method).
- Milbank, N.O. and Harrington-Lynn, J. (1974), *Thermal response and the admittance procedure*, BRE CP 61/74.
- Carslaw, H.S. and Jaeger, J.C. (1959), *Conduction of Heat in Solids*, 2nd ed., Oxford.
- Davies, M.G. (2004), *Building Heat Transfer*, Wiley.
- Incropera, F.P. et al., *Fundamentals of Heat and Mass Transfer* (transient conduction chapters).
- BRE (2014), *SAP 2012: The Government's Standard Assessment Procedure*, Table 1e (κ values and TMP).
