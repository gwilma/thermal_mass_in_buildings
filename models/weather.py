"""Hourly weather for the room model.

`london(variant)` is the default: Heathrow TMYx 2011-2025 from
climate.onebuilding.org, with optional hot and 2050s morphs.

`read_epw(path)` reads any EnergyPlus weather file (CIBSE TRY/DSY files
converted to EPW, Prometheus UKCP18 future files, onebuilding.org TMYx).

`synthetic(variant, seed)` makes a London-like year when no file is to
hand (kept as a fallback). It is a stand-in, not a design weather year: monthly means are
approximately Heathrow 1991-2020, and the stochastic day-to-day variation is
tuned by eye. Variants:
  "typical"     no heatwave
  "hot"         DSY-like: warmer summer (+1.5 K Jun-Aug) and a 7-day
                mid-July heatwave peaking at about 35 C
  "hot2050"     "hot" plus a UKCP18-style 2050s shift (+2.5 K Jun-Aug,
                +1.5 K otherwise); illustrative, not a UKCP18 projection

Returns a dict of hourly arrays (8760): T (air C), GHI, DHI, DNI (W/m2),
and the solar position (cos zenith, azimuth from south, rad).
"""
import math, os
import numpy as np

LAT, LON = 51.48, -0.45  # Heathrow

# Approximate Heathrow 1991-2020 monthly means (C) and mean daily ranges (K)
T_MON = [5.6, 5.9, 8.1, 10.6, 14.0, 17.1, 19.3, 19.0, 16.1, 12.5, 8.6, 6.1]
DTR_MON = [5.5, 6.0, 7.5, 9.0, 9.5, 9.5, 9.5, 9.0, 8.5, 7.0, 5.5, 5.0]
# Approximate London global horizontal irradiation, kWh/m2/day
H_MON = [0.70, 1.35, 2.35, 3.70, 4.70, 5.10, 5.00, 4.20, 3.00, 1.75, 0.90, 0.55]
MDAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def solar_position(hours):
    """hours: hour-of-year at mid-interval (0.5 .. 8759.5), GMT."""
    doy = hours // 24 + 1
    B = 2 * np.pi * (doy - 81) / 364
    decl = np.radians(23.45) * np.sin(2 * np.pi * (284 + doy) / 365)
    eot = 9.87 * np.sin(2 * B) - 7.53 * np.cos(B) - 1.5 * np.sin(B)  # minutes
    solar_time = (hours % 24) + (4 * LON + eot) / 60
    ha = np.radians(15 * (solar_time - 12))
    lat = math.radians(LAT)
    cosz = np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(ha)
    sinz = np.sqrt(np.clip(1 - cosz ** 2, 0, 1))
    with np.errstate(invalid="ignore", divide="ignore"):
        cosaz = (np.sin(decl) - cosz * np.sin(lat)) / (sinz * np.cos(lat) + 1e-12)
    az_from_north = np.arccos(np.clip(cosaz, -1, 1))
    az_from_north = np.where(ha > 0, 2 * np.pi - az_from_north, az_from_north)
    az = az_from_north - np.pi  # from south, west positive
    I0 = 1361 * (1 + 0.033 * np.cos(2 * np.pi * doy / 365))
    return cosz, az, I0


def erbs(kt):
    return np.where(kt <= 0.22, 1 - 0.09 * kt,
                    np.where(kt <= 0.8, 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4, 0.165))


def _monthly_to_daily(vals):
    """Smooth daily curve through monthly means (3-harmonic fit)."""
    mid = np.cumsum(MDAYS) - np.array(MDAYS) / 2
    X = lambda d: np.column_stack([np.ones_like(d)] + [f(2 * np.pi * k * d / 365) for k in (1, 2, 3) for f in (np.cos, np.sin)])
    coef, *_ = np.linalg.lstsq(X(mid), np.array(vals, float), rcond=None)
    return X(np.arange(365) + 0.5) @ coef


def synthetic(variant="typical", seed=1):
    rng = np.random.default_rng(seed)
    hours = np.arange(8760) + 0.5
    cosz, az, I0 = solar_position(hours)
    day = (hours // 24).astype(int)
    hod = hours % 24

    # Daily clearness: AR(1) in a logit space, mean set per month afterwards
    z = np.zeros(365); e = rng.normal(0, 1, 365)
    for d in range(1, 365):
        z[d] = 0.55 * z[d - 1] + math.sqrt(1 - 0.55**2) * e[d]
    clear = 1 / (1 + np.exp(-(0.2 + 1.1 * z)))  # 0..1 sky clearness index

    # Clear-sky GHI (Haurwitz), scaled per month to the target irradiation
    ghi_cs = np.where(cosz > 0, 1098 * cosz * np.exp(-0.057 / np.maximum(cosz, 1e-3)), 0.0)
    frac = 0.25 + 0.75 * clear[day]
    ghi = ghi_cs * frac
    m_of_day = np.repeat(np.arange(12), MDAYS)
    for m in range(12):
        sel = m_of_day[day] == m
        target = H_MON[m] * MDAYS[m] * 1000
        ghi[sel] *= target / ghi[sel].sum()
    ghi = np.minimum(ghi, 0.95 * I0 * np.maximum(cosz, 0))
    kt = np.where(cosz > 0.02, ghi / (I0 * np.maximum(cosz, 0.02)), 0)
    dhi = np.where(cosz > 0.02, erbs(kt) * ghi, ghi)
    dni = np.where(cosz > 0.02, (ghi - dhi) / np.maximum(cosz, 0.02), 0)

    # Temperature: smooth seasonal mean + AR(1) anomaly tied to clearness in summer
    tmean = _monthly_to_daily(T_MON)
    dtr = _monthly_to_daily(DTR_MON)
    season = np.cos(2 * np.pi * (np.arange(365) - 196) / 365)  # +1 mid-July, -1 mid-Jan
    a = np.zeros(365); n = rng.normal(0, 1, 365)
    for d in range(1, 365):
        a[d] = 0.7 * a[d - 1] + math.sqrt(1 - 0.49) * 2.2 * n[d]
    anom = a + 1.6 * season * (clear - clear.mean()) / clear.std()
    anom -= np.array([anom[m_of_day == m].mean() for m in m_of_day])  # keep monthly means
    Td = tmean + anom
    rng_d = dtr * (0.55 + 0.9 * clear)

    if variant in ("hot", "hot2050"):
        summer = (np.arange(365) >= 151) & (np.arange(365) < 243)
        Td = Td + 1.5 * summer
        hw = np.arange(193, 200)  # 13-19 July
        Td[hw] = [22.0, 24.5, 26.5, 28.5, 29.5, 27.0, 23.5]
        rng_d[hw] = [11, 12, 12.5, 13, 13, 12, 10]
        clear[hw] = 0.97
        for d in hw:  # clear skies during the heatwave
            sel = day == d
            ghi[sel] = ghi_cs[sel] * 0.97
            k = np.where(cosz[sel] > 0.02, ghi[sel] / (I0[sel] * np.maximum(cosz[sel], 0.02)), 0)
            dhi[sel] = np.where(cosz[sel] > 0.02, erbs(k) * ghi[sel], ghi[sel])
            dni[sel] = np.where(cosz[sel] > 0.02, (ghi[sel] - dhi[sel]) / np.maximum(cosz[sel], 0.02), 0)
    if variant == "hot2050":
        summer = (np.arange(365) >= 151) & (np.arange(365) < 243)
        Td = Td + np.where(summer, 2.5, 1.5)

    # Diurnal shape: minimum near 05:00, maximum near 15:00 (smooth, asymmetric)
    ph = 2 * np.pi * (hod - 15) / 24
    shape = 0.5 * np.cos(ph) + 0.12 * np.cos(2 * ph - 0.6)
    shape = shape / (shape.max() - shape.min())
    T = Td[day] + rng_d[day] * shape
    return dict(T=T, GHI=ghi, DHI=dhi, DNI=dni, cosz=cosz, az=az, name=f"synthetic-{variant}")


EPW_LONDON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_data",
                          "GBR_ENG_London-Heathrow.Intl.AP.037720_TMYx.2011-2025.epw")
HEATWAVE_DAYS = (195, 202)  # 15-21 July, the file's own "week nearest max temperature"


def london(variant="typical"):
    """Heathrow TMYx 2011-2025 (climate.onebuilding.org), optionally morphed:
      "typical"  the file as is
      "hot"      +1.5 K Jun-Aug and a +4 K raised-cosine heatwave bump over
                 15-21 July (peak about 37 C), a DSY-like stress year
      "hot2050"  "hot" plus +2.5 K Jun-Aug and +1.5 K otherwise, an
                 illustrative 2050s shift (not a UKCP18 projection)
    Solar is left as in the file. For design work use CIBSE TRY/DSY or
    Prometheus UKCP18 files through read_epw()."""
    w = read_epw(EPW_LONDON)
    w["name"] = f"london-tmyx-{variant}"
    if variant in ("hot", "hot2050"):
        d = np.arange(8760) / 24.0
        summer = (d >= 151) & (d < 243)
        a, b = HEATWAVE_DAYS
        x = np.clip((d - a) / (b - a), 0, 1)
        bump = np.where((d >= a) & (d < b), 4.0 * 0.5 * (1 - np.cos(2 * np.pi * x)), 0.0)
        w["T"] = w["T"] + 1.5 * summer + bump
        if variant == "hot2050":
            w["T"] = w["T"] + np.where(summer, 2.5, 1.5)
    return w


def get(variant="typical", source="london"):
    return london(variant) if source == "london" else synthetic(variant)


def read_epw(path):
    T, ghi, dni, dhi = [], [], [], []
    with open(path, encoding="latin-1") as fh:
        for i, line in enumerate(fh):
            if i < 8:
                if i == 0:
                    hdr = line.split(",")
                continue
            p = line.split(",")
            T.append(float(p[6])); ghi.append(float(p[13])); dni.append(float(p[14])); dhi.append(float(p[15]))
    global LAT, LON
    LAT, LON = float(hdr[6]), float(hdr[7])
    cosz, az, _ = solar_position(np.arange(8760) + 0.5)
    return dict(T=np.array(T[:8760]), GHI=np.array(ghi[:8760]), DNI=np.array(dni[:8760]),
                DHI=np.array(dhi[:8760]), cosz=cosz, az=az, name=path)


def plane_irradiance(w, tilt_deg, azimuth_deg, albedo=0.2):
    """Isotropic-sky irradiance on a plane. azimuth from south, west positive."""
    b = math.radians(tilt_deg); g = math.radians(azimuth_deg)
    sinz = np.sqrt(np.clip(1 - w["cosz"] ** 2, 0, 1))
    cos_inc = w["cosz"] * math.cos(b) + sinz * math.sin(b) * np.cos(w["az"] - g)
    beam = w["DNI"] * np.clip(cos_inc, 0, None) * (w["cosz"] > 0)
    return beam + w["DHI"] * (1 + math.cos(b)) / 2 + w["GHI"] * albedo * (1 - math.cos(b)) / 2


def running_mean(T, alpha=0.8):
    """CIBSE TM52/TM59 exponentially weighted running mean of daily means."""
    Td = T.reshape(-1, 24).mean(axis=1)
    trm = np.empty_like(Td); trm[0] = Td[0]
    for d in range(1, len(Td)):
        trm[d] = (1 - alpha) * Td[d - 1] + alpha * trm[d - 1]
    return np.repeat(trm, 24)


if __name__ == "__main__":
    for v in ("typical", "hot", "hot2050"):
        w = london(v)
        T = w["T"].reshape(-1, 24)
        mon = np.repeat(np.arange(12), MDAYS)
        print(v, "annual mean %.1f, max %.1f, min %.1f, GHI %.0f kWh/m2" % (w["T"].mean(), w["T"].max(), w["T"].min(), w["GHI"].sum() / 1000))
        print("  monthly means", [round(T[mon == m].mean(), 1) for m in range(12)])
        print("  hours > 28 C:", int((w["T"] > 28).sum()), " south vertical kWh/m2:", round(plane_irradiance(w, 90, 0).sum() / 1000))
