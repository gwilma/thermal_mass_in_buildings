"""Workbook 3: House Simulator, the 5R1C model in cell formulas.

One row per hour for a year (ISO 13790 Annex C, Crank-Nicolson), using the
same house, gains, ventilation rules and heating schedule as models/room.py.
Matches models/room5r1c.py.
"""
import os
import numpy as np
from openpyxl.chart import BarChart, LineChart, Reference

from xlcommon import *  # noqa: F401,F403
from buildups import LIB
from room import PACKAGES, GAINS_PROFILE, Room, DEFAULTS
import weather as wx

N = 8760
H0 = 6  # first data row on Hourly / Weather


def inputs_sheet(wb):
    ws = sheet(wb, "Inputs", {"A": 36, "B": 16, "C": 64})
    put(ws, "A1", "House Simulator: inputs", F_T)
    note(ws, "A2", "Blue cells are inputs. Results are on the Results sheet; allow a few seconds to recalculate the 8,760 hours.")
    rows = [
        ("Construction package", "Masonry (dense block, dabs), stud partitions", "pick from the Packages sheet"),
        ("Weather year", "hot", "typical, hot or hot2050 (morphs of Heathrow TMYx 2011-2025)"),
        ("Glazing area multiplier", 1.0, "1 = 18 m² (10 front, 6 back, 2 side)"),
        ("Window g-value", DEFAULTS["g_win"], ""),
        ("Frame fraction", DEFAULTS["frame"], ""),
        ("Blind factor when > 150 W/m² on glass", 1.0, "1 = no blinds; 0.3 = blinds cut 70%"),
        ("Front faces", "S", "S, N, E or W"),
        ("Background ventilation, ACH", DEFAULTS["ach_base"], ""),
        ("Day purge, ACH (07-23)", DEFAULTS["ach_day"], "windows open when operative > threshold and outdoors is cooler"),
        ("Night ventilation (Yes/No)", "No", ""),
        ("Night ventilation, ACH (23-07)", DEFAULTS["ach_night"], ""),
        ("Window opening threshold, °C", DEFAULTS["t_open"], ""),
        ("Internal gains multiplier", 1.0, "1 = 298 W mean, profile on the Parameters sheet"),
        ("Heating setpoint, °C", DEFAULTS["t_set"], "07-09 and 16-23"),
        ("Setback, °C", DEFAULTS["t_setback"], "other hours"),
        ("Heating capacity, W", DEFAULTS["q_max"], ""),
        ("Floor area, m²", DEFAULTS["floor_area"], "two storeys"),
        ("Storey height, m", DEFAULTS["storey_h"], ""),
        ("External wall height, m", DEFAULTS["wall_h"], ""),
        ("Frontage, m", DEFAULTS["width"], ""),
        ("Depth, m", DEFAULTS["depth"], ""),
        ("Partition wall area, m² (one face)", DEFAULTS["partition_area"], ""),
        ("Window U-value, W/m²K", DEFAULTS["U_win"], ""),
    ]
    for i, (lab, v, n) in enumerate(rows):
        r = 4 + i
        put(ws, f"A{r}", lab, bold=True); inp(ws, f"B{r}", v); note(ws, f"C{r}", n)
    dv_list(ws, "B4", "=Packages!$A$5:$A$19")
    dv_list(ws, "B5", '"typical,hot,hot2050"')
    dv_list(ws, "B10", '"S,N,E,W"')
    dv_list(ws, "B13", '"Yes,No"')
    return {lab: f"Inputs!$B${4 + i}" for i, (lab, _, _) in enumerate(rows)}


def elements_sheet(wb):
    ws = sheet(wb, "Elements", {"A": 8, "B": 54, "C": 11, "D": 11, "E": 13})
    put(ws, "A1", "Element properties (ISO 13786, 24 h)", F_T)
    note(ws, "A2", "From the Build-up Explorer workbook (Library results sheet). Edit to try other values; U includes the far-side boundary.")
    header(ws, 4, 1, ["Key", "Build-up", "Far side", "U W/m²K", "κ₁ kJ/m²K"])
    for i, (k, e) in enumerate(LIB.items()):
        r = 5 + i; res = e.iso()
        put(ws, f"A{r}", k, bold=True); put(ws, f"B{r}", e.name); put(ws, f"C{r}", e.back)
        inp(ws, f"D{r}", round(res["U"], 6), "0.000"); inp(ws, f"E{r}", round(res["kappa1"], 6), "0.0")
    return 5, 4 + len(LIB)


def packages_sheet(wb):
    ws = sheet(wb, "Packages", {"A": 52, "B": 9, "C": 9, "D": 9, "E": 9, "F": 9, "G": 9})
    put(ws, "A1", "Construction packages", F_T)
    note(ws, "A2", "Element keys from the Elements sheet. The last row is yours to edit.")
    header(ws, 4, 1, ["Package", "Walls", "Ground floor", "Intermediate floor", "Partitions", "Party wall", "Ceiling"])
    roles = ["wall", "ground", "inter", "part", "party", "ceil"]
    for i, (name, pk) in enumerate(list(PACKAGES.items()) + [("Custom package", PACKAGES["Masonry (dense block, wet plaster), block partitions"])]):
        r = 5 + i
        f = inp if name == "Custom package" else put
        f(ws, f"A{r}", name)
        for j, ro in enumerate(roles):
            f(ws, f"{col(2 + j)}{r}", pk[ro])


def parameters_sheet(wb, I, el_first, el_last):
    ws = sheet(wb, "Parameters", {"A": 34, "B": 13, "C": 12, "D": 12, "E": 12, "F": 12, "G": 13, "H": 15, "I": 15, "J": 13, "K": 13, "L": 13})
    put(ws, "A1", "Derived parameters (5R1C, ISO 13790 Annex C)", F_T)
    pk = f"MATCH({I['Construction package']},Packages!$A$5:$A$19,0)"
    EK = f"Elements!$A${el_first}:$A${el_last}"
    look = lambda key, c: f"INDEX(Elements!${c}${el_first}:${c}${el_last},MATCH({key},{EK},0))"
    # orientation table
    header(ws, 4, 1, ["Orientation", "Role", "Gross wall m²", "Window m²", "Net wall m²", "Opaque solar W per W/m²"])
    rot = {"S": ("N", "E"), "N": ("S", "W"), "E": ("W", "S"), "W": ("E", "N")}
    put(ws, "H4", "Front", F_B); put(ws, "I4", "Back", F_B); put(ws, "J4", "Side", F_B)
    for i, (f_, (b_, s_)) in enumerate(rot.items()):
        put(ws, f"H{5 + i}", f_); put(ws, f"I{5 + i}", b_); put(ws, f"J{5 + i}", s_)
    fr = I["Front faces"]
    back = f"INDEX($I$5:$I$8,MATCH({fr},$H$5:$H$8,0))"; side = f"INDEX($J$5:$J$8,MATCH({fr},$H$5:$H$8,0))"
    g = I["Glazing area multiplier"]; wall_key = f"INDEX(Packages!$B$5:$B$19,{pk})"
    for i, o in enumerate("SNEW"):
        r = 5 + i
        put(ws, f"A{r}", o, bold=True)
        put(ws, f"B{r}", f'=IF(A{r}={fr},"front",IF(A{r}={back},"back",IF(A{r}={side},"side","party")))')
        put(ws, f"C{r}", f'=IF(OR(B{r}="front",B{r}="back"),{I["Frontage, m"]}*{I["External wall height, m"]},IF(B{r}="side",{I["Depth, m"]}*{I["External wall height, m"]},0))', fmt="0.0")
        put(ws, f"D{r}", f'=IF(B{r}="front",10,IF(B{r}="back",6,IF(B{r}="side",2,0)))*{g}', fmt="0.0")
        put(ws, f"E{r}", f"=C{r}-D{r}", fmt="0.0")
        put(ws, f"F{r}", f"=0.6*0.04*{look(wall_key, 'D')}*E{r}", fmt="0.000")
    # element groups
    header(ws, 11, 1, ["Group", "Element", "Area m²", "U", "κ₁ kJ/m²K", "Far side", "Faces", "κ₁A J/K", "κ₁²A", "H to outdoor W/K", "H to ground W/K"])
    groups = [("Walls (net)", 2, "=SUM(E5:E8)"), ("Ground floor", 3, f"={I['Floor area, m²']}/2"), ("Intermediate floor", 4, f"={I['Floor area, m²']}/2"),
              ("Partitions (both faces)", 5, f"=2*{I['Partition wall area, m² (one face)']}"), ("Party wall", 6, f"={I['Depth, m']}*{I['External wall height, m']}"),
              ("Ceiling", 7, f"={I['Floor area, m²']}/2")]
    for i, (lab, c, area) in enumerate(groups):
        r = 12 + i
        key = f"INDEX(Packages!${col(c)}$5:${col(c)}$19,{pk})"
        put(ws, f"A{r}", lab); put(ws, f"B{r}", f"={key}")
        put(ws, f"C{r}", area, fmt="0.0")
        put(ws, f"D{r}", f"={look(f'B{r}', 'D')}", fmt="0.000"); put(ws, f"E{r}", f"={look(f'B{r}', 'E')}", fmt="0.0")
        put(ws, f"F{r}", f"={look(f'B{r}', 'C')}")
        put(ws, f"G{r}", 2 if lab.startswith("Intermediate") else 1)
        put(ws, f"H{r}", f"=E{r}*1000*C{r}*G{r}", fmt="#,##0")
        put(ws, f"I{r}", f"=(E{r}*1000)^2*C{r}*G{r}", fmt="0.00E+00")
        put(ws, f"J{r}", f'=IF(F{r}="ext",D{r}*C{r},0)', fmt="0.0")
        put(ws, f"K{r}", f'=IF(F{r}="ground",D{r}*C{r},0)', fmt="0.0")
    # scalars
    P = {}
    sc = [("Af floor area m²", f"={I['Floor area, m²']}", "0.0"), ("At = 4.5 Af m²", "=B20*4.5", "0.0"),
          ("Cm J/K", "=SUM(H12:H17)", "#,##0"), ("Am m²", "=B22^2/SUM(I12:I17)", "0.0"),
          ("H_tr,is W/K", "=3.45*B21", "0.0"), ("H_tr,ms W/K", "=9.1*B23", "0.0"),
          ("H_tr,w W/K", f"={I['Window U-value, W/m²K']}*SUM(D5:D8)", "0.0"),
          ("H to outdoor (opaque) W/K", "=SUM(J12:J17)", "0.0"), ("H to ground W/K", "=SUM(K12:K17)", "0.0"),
          ("H_op W/K", "=B27+B28", "0.0"), ("H_tr,em W/K", "=1/(1/B29-1/B25)", "0.0"),
          ("Volume m³", f"={I['Floor area, m²']}*{I['Storey height, m']}", "0.0"),
          ("f_st (share of solar+rad to surface node)", "=1-B23/B21-B26/(9.1*B21)", "0.000"),
          ("Am/At", "=B23/B21", "0.000"), ("Ground temperature °C", f"=AVERAGE(Weather!$E${H0}:$E${H0 + N - 1})", "0.00"),
          ("Cm / 3600", "=B22/3600", "0.0"), ("κ₁ per m² floor kJ/m²K", "=B22/1000/B20", "0.0"),
          ("Fabric H incl. windows W/K", "=B29+B26", "0.0")]
    for i, (lab, f, fmt) in enumerate(sc):
        r = 20 + i
        put(ws, f"A{r}", lab); out(ws, f"B{r}", f, fmt)
        P[lab.split(" ")[0] if not lab.startswith("H to") else lab] = f"Parameters!$B${r}"
    # gains profile
    put(ws, "D20", "Hour", F_B); put(ws, "E20", "Gains W", F_B)
    for h in range(24):
        put(ws, f"D{21 + h}", h); inp(ws, f"E{21 + h}", int(GAINS_PROFILE[h]))
    note(ws, "D46", "Internal gains profile; half convective (to air), half radiant.")
    names = {"Af": 20, "At": 21, "Cm": 22, "Am": 23, "His": 24, "Hms": 25, "Hw": 26, "Hout": 27, "Hg": 28, "Hop": 29, "Hem": 30, "V": 31, "fst": 32, "AmAt": 33, "Tg": 34, "Cm3600": 35}
    return {k: f"Parameters!$B${v}" for k, v in names.items()}


def weather_sheet(wb, I):
    ws = sheet(wb, "Weather", {"A": 8, "B": 6, "C": 6, "D": 6, "E": 10, "F": 10, "G": 10, "H": 10, "I": 10, "J": 10})
    put(ws, "A1", "Hourly weather: London Heathrow TMYx 2011-2025 (climate.onebuilding.org)", F_B)
    note(ws, "A2", "T recorded is the file's dry-bulb temperature. Column E applies the chosen morph. Irradiance on vertical planes is from the Python model (isotropic sky, albedo 0.2). Paste another EPW's values into D and G:J to use it.")
    note(ws, "A3", "hot: +1.5 K Jun-Aug and a 4 K raised-cosine heatwave over 15-21 July. hot2050: hot plus 2.5 K Jun-Aug and 1.5 K otherwise.")
    header(ws, 5, 1, ["hour", "day", "hod", "T recorded °C", "T used °C", "month", "I south W/m²", "I north", "I east", "I west"])
    w = wx.read_epw(wx.EPW_LONDON)
    irr = {o: wx.plane_irradiance(w, 90, a) for o, a in (("S", 0), ("N", 180), ("E", -90), ("W", 90))}
    month = np.repeat(np.arange(1, 13), [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    v = I["Weather year"]
    for h in range(N):
        r = H0 + h
        ws[f"A{r}"] = h; ws[f"B{r}"] = h // 24; ws[f"C{r}"] = h % 24
        ws[f"D{r}"] = round(float(w["T"][h]), 1)
        d = f"(A{r}/24)"
        ws[f"E{r}"] = (f'=D{r}+IF({v}="typical",0,1.5*AND({d}>=151,{d}<243)+IF(AND({d}>=195,{d}<202),2*(1-COS(2*PI()*({d}-195)/7)),0))'
                       f'+IF({v}="hot2050",IF(AND({d}>=151,{d}<243),2.5,1.5),0)')
        ws[f"F{r}"] = int(month[h // 24])
        for j, o in enumerate("SNEW"):
            ws[f"{col(7 + j)}{r}"] = round(float(irr[o][h]), 1)
    ws.freeze_panes = f"A{H0}"


def hourly_sheet(wb, I, P):
    cols = ["hour", "hod", "T out", "θ_em", "solar gain W", "internal gain W", "φ_ia", "φ_st", "φ_m", "setpoint", "open windows?", "ACH",
            "H_ve", "H_tr1", "H_tr2", "H_tr3", "denominator", "φ_m,tot", "θ_m,t (no heat)", "θ_s (no heat)", "θ_air (no heat)",
            "dθ_m,t/dQ", "dθ_s/dQ", "dθ_air/dQ", "Heating W", "θ_m,t", "θ_s", "θ_air", "θ_op", "T_rm", "occupied May-Sep", "over limit", "night > 26", "K·h > 26"]
    ws = sheet(wb, "Hourly", {col(i + 1): 10 for i in range(len(cols))})
    put(ws, "A1", "Hourly 5R1C calculation (one row per hour)", F_B)
    note(ws, "A2", "ISO 13790 Annex C. Heating is solved from the linear response of θ_air to 1 W of convective heat. Window opening uses the previous hour's θ_op and θ_air.")
    note(ws, "A3", "Starting values: θ_m = 18 °C, previous θ_op = previous θ_air = 20 °C.")
    header(ws, 5, 1, cols)
    p = P
    sol_terms = []
    for j, o in enumerate("SNEW"):
        Ic = col(7 + j)
        sol_terms.append(f"Parameters!$D${5 + j}*(1-{I['Frame fraction']})*{I['Window g-value']}*IF(Weather!{Ic}{{r}}>150,{I['Blind factor when > 150 W/m² on glass']},1)*Weather!{Ic}{{r}}+Parameters!$F${5 + j}*Weather!{Ic}{{r}}")
    sol = "+".join(sol_terms)
    for h in range(N):
        r = H0 + h; pr = r - 1
        first = h == 0
        Tm_prev = "18" if first else f"Z{pr}"
        Top_prev = "20" if first else f"AC{pr}"
        Ta_prev = "20" if first else f"AB{pr}"
        f = {
            "A": f"=Weather!A{r}", "B": f"=Weather!C{r}", "C": f"=Weather!E{r}",
            "D": f"=({p['Hout']}*C{r}+{p['Hg']}*{p['Tg']})/{p['Hop']}",
            "E": "=" + sol.replace("{r}", str(r)),
            "F": f"=INDEX(Parameters!$E$21:$E$44,B{r}+1)*{I['Internal gains multiplier']}",
            "G": f"=0.5*F{r}", "H": f"={p['fst']}*(0.5*F{r}+E{r})", "I": f"={p['AmAt']}*(0.5*F{r}+E{r})",
            "J": f"=IF(OR(AND(B{r}>=7,B{r}<9),AND(B{r}>=16,B{r}<23)),{I['Heating setpoint, °C']},{I['Setback, °C']})",
            "K": f"=IF(AND({Top_prev}>{I['Window opening threshold, °C']},C{r}<{Ta_prev}),1,0)",
            "L": f'={I["Background ventilation, ACH"]}+IF(AND(K{r}=1,B{r}>=7,B{r}<23),{I["Day purge, ACH (07-23)"]},IF(AND(K{r}=1,{I["Night ventilation (Yes/No)"]}="Yes"),{I["Night ventilation, ACH (23-07)"]},0))',
            "M": f"=0.33*L{r}*{p['V']}", "N": f"=1/(1/M{r}+1/{p['His']})", "O": f"=N{r}+{p['Hw']}", "P": f"=1/(1/O{r}+1/{p['Hms']})",
            "Q": f"={p['Cm3600']}+0.5*(P{r}+{p['Hem']})",
            "R": f"=I{r}+{p['Hem']}*D{r}+P{r}*(H{r}+{p['Hw']}*C{r}+N{r}*(G{r}/M{r}+C{r}))/O{r}",
            "S": f"=({Tm_prev}*({p['Cm3600']}-0.5*(P{r}+{p['Hem']}))+R{r})/Q{r}",
            "T": f"=({p['Hms']}*0.5*(S{r}+{Tm_prev})+H{r}+{p['Hw']}*C{r}+N{r}*(C{r}+G{r}/M{r}))/({p['Hms']}+{p['Hw']}+N{r})",
            "U": f"=({p['His']}*T{r}+M{r}*C{r}+G{r})/({p['His']}+M{r})",
            "V": f"=P{r}*N{r}/(O{r}*M{r})/Q{r}",
            "W": f"=({p['Hms']}*0.5*V{r}+N{r}/M{r})/({p['Hms']}+{p['Hw']}+N{r})",
            "X": f"=({p['His']}*W{r}+1)/({p['His']}+M{r})",
            "Y": f"=MIN(MAX((J{r}-U{r})/X{r},0),{I['Heating capacity, W']})",
            "Z": f"=S{r}+Y{r}*V{r}", "AA": f"=T{r}+Y{r}*W{r}", "AB": f"=U{r}+Y{r}*X{r}", "AC": f"=0.3*AB{r}+0.7*AA{r}",
            "AD": f"=INDEX(Daily!$D$6:$D$370,Weather!B{r}+1)",
            "AE": f"=IF(AND(Weather!B{r}>=120,Weather!B{r}<273,B{r}>=9,B{r}<22),1,0)",
            "AF": f"=IF(AE{r}=1,IF(ROUND(AC{r}-(0.33*AD{r}+21.8),0)>=1,1,0),0)",
            "AG": f"=IF(AND(OR(B{r}>=22,B{r}<7),AC{r}>26),1,0)",
            "AH": f"=IF(AND(Weather!B{r}>=120,Weather!B{r}<273),MAX(AC{r}-26,0),0)",
        }
        for c, v in f.items():
            ws[f"{c}{r}"] = v
    ws.freeze_panes = f"C{H0}"


def daily_sheet(wb):
    ws = sheet(wb, "Daily", {"A": 6, "B": 10, "C": 12, "D": 12, "E": 12, "F": 12, "G": 10})
    put(ws, "A1", "Daily values: outdoor mean, running mean (CIBSE TM52/TM59, α = 0.8) and operative range", F_B)
    header(ws, 5, 1, ["day", "month", "T out mean", "T_rm", "θ_op max", "θ_op min", "swing K"])
    for d in range(365):
        r = 6 + d; a, b = H0 + 24 * d, H0 + 24 * d + 23
        ws[f"A{r}"] = d; ws[f"B{r}"] = f"=Weather!F{a}"
        ws[f"C{r}"] = f"=AVERAGE(Weather!E{a}:E{b})"
        ws[f"D{r}"] = "=C6" if d == 0 else f"=0.2*C{r - 1}+0.8*D{r - 1}"
        ws[f"E{r}"] = f"=MAX(Hourly!AC{a}:AC{b})"; ws[f"F{r}"] = f"=MIN(Hourly!AC{a}:AC{b})"; ws[f"G{r}"] = f"=E{r}-F{r}"


def results_sheet(wb, I, P):
    ws = sheet(wb, "Results", {"A": 40, "B": 14, "C": 4, "D": 8, "E": 14, "F": 14})
    put(ws, "A1", "House Simulator: results", F_T)
    put(ws, "A2", f'={I["Construction package"]}&" · "&{I["Weather year"]}&" weather"', F_B)
    last = H0 + N - 1
    hr = lambda c: f"Hourly!{c}{H0}:{c}{last}"
    rows = [("Space heating, kWh/m² a year", f"=SUM({hr('Y')})/1000/{P['Af']}", "0.0"),
            ("Peak heating, kW (hourly mean)", f"=MAX({hr('Y')})/1000", "0.00"),
            ("TM59 (a) style: % occupied hours ≥ 1 K over limit (limit 3%)", f"=SUM({hr('AF')})/SUM({hr('AE')})*100", "0.0"),
            ("TM59 (b) style: night hours > 26 °C (limit 32)", f"=SUM({hr('AG')})", "0"),
            ("Degree-hours above 26 °C, May-Sep", f"=SUM({hr('AH')})", "#,##0"),
            ("Peak operative temperature, °C", f"=MAX({hr('AC')})", "0.0"),
            ("Hours above 28 °C operative", f'=COUNTIF({hr("AC")},">28")', "0"),
            ("Mean daily operative swing in July, K", "=AVERAGE(Daily!G187:G217)", "0.0"),
            ("κ₁ per m² floor, kJ/m²K", "=Parameters!B36", "0"),
            ("Cm J/K · Am m²", '=TEXT(Parameters!B22,"#,##0")&" · "&TEXT(Parameters!B23,"0.0")', None)]
    for i, (lab, f, fmt) in enumerate(rows):
        put(ws, f"A{4 + i}", lab); out(ws, f"B{4 + i}", f, fmt, True)
    # monthly heating
    put(ws, "D3", "Month", F_B); put(ws, "E3", "Heating kWh/m²", F_B)
    for m in range(12):
        r = 4 + m
        ws[f"D{r}"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m]
        ws[f"E{r}"] = f"=SUMIFS({hr('Y')},Weather!F{H0}:F{last},{m + 1})/1000/{P['Af']}"; ws[f"E{r}"].number_format = "0.0"
    bc = BarChart(); bc.title = "Space heating by month"; bc.y_axis.title = "kWh/m²"
    bc.add_data(Reference(ws, min_col=5, min_row=3, max_row=15), titles_from_data=True)
    bc.set_categories(Reference(ws, min_col=4, min_row=4, max_row=15)); bc.height = 7; bc.width = 14; bc.legend = None
    ws.add_chart(bc, "H3")
    # heatwave fortnight chart from Hourly rows (days 189..204)
    a, b = H0 + 189 * 24, H0 + 205 * 24 - 1
    put(ws, "A17", "Heatwave fortnight (8-23 July)", F_B)
    header(ws, 18, 1, ["hour of year", "T out", "θ_op", "θ_air"])
    for i, h in enumerate(range(a, b + 1)):
        r = 19 + i
        ws[f"A{r}"] = f"=Hourly!A{h}"; ws[f"B{r}"] = f"=Hourly!C{h}"; ws[f"C{r}"] = f"=Hourly!AC{h}"; ws[f"D{r}"] = f"=Hourly!AB{h}"
    lc = LineChart(); lc.title = "Heatwave fortnight"; lc.y_axis.title = "°C"
    lc.add_data(Reference(ws, min_col=2, max_col=3, min_row=18, max_row=18 + (b - a + 1)), titles_from_data=True)
    lc.set_categories(Reference(ws, min_col=1, min_row=19, max_row=18 + (b - a + 1))); lc.x_axis.tickLblSkip = 48; lc.height = 8; lc.width = 22
    ws.add_chart(lc, "H19")
    return ws


def python_sheet(wb):
    import csv
    ws = sheet(wb, "Python check", {"A": 52, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13, "G": 13, "H": 13})
    put(ws, "A1", "Reference results from the Python models (default inputs)", F_T)
    note(ws, "A2", "5R1C columns should match this workbook with default inputs. The full model keeps every layer and so shows more benefit from deep mass in a heatwave.")
    header(ws, 4, 1, ["Package", "5R1C heat kWh/m² (typical)", "5R1C peak kW (typical)", "5R1C DH26 (hot)", "5R1C DH26 (hot + night vent)",
                      "Full model heat (typical)", "Full model DH26 (hot)", "Full model DH26 (hot + night vent)"])
    rows = [r for r in csv.DictReader(open(os.path.join(MODELS, "results", "packages.csv"))) if r["mode"] == "fd"]
    for i, r in enumerate(rows):
        rr = 5 + i
        put(ws, f"A{rr}", r["package"])
        for j, k in enumerate(["r5_heat", "r5_peak", "r5_day_dh26", "r5_nv_dh26", "heat_kwh_m2", "hot_day_dh26", "hot_nv_dh26"]):
            put(ws, f"{col(2 + j)}{rr}", round(float(r[k]), 2), fmt="0.00" if "peak" in k else "0.0" if "heat" in k else "#,##0")


def build(path):
    wb = new_wb()
    readme(wb, "House Simulator (thermal mass toolkit, model 3, Excel twin)", [
        "What it does:",
        "Runs a 90 m² two-storey semi for a year, hour by hour, and reports space heating, peak heating and summer overheating indicators.",
        "This workbook uses the 5R1C method (ISO 13790 Annex C, also the basis of ISO 52016-1's simple hourly method): one mass node, one surface node and one air node. The fabric's dynamic behaviour enters through Cm = Σ κ₁A, the ISO 13786 daily areal heat capacity of every room-facing surface.",
        "The web app and Python model can also run the full layer-by-layer model. The 5R1C tracks it well for heating; it understates what deep mass does over a multi-day heatwave because it keeps only the daily store (see the Python check sheet).",
        "",
        "How to use it:",
        "1. Inputs: choose the construction package, weather year, glazing, blinds, ventilation, gains and heating setpoints.",
        "2. Results: heating, peak, TM59-style indicators, degree-hours, a monthly heating chart and a heatwave chart.",
        "3. Packages and Elements: edit or add constructions; element U and κ₁ come from the Build-up Explorer workbook.",
        "",
        "Assumptions: same as models/room.py. Windows open for purge (07-23) when the previous hour's operative temperature is above the threshold and outdoors is cooler than the room; night ventilation (23-07) on the same rule if switched on. Heating is convective, 07-09 and 16-23, setback otherwise. Internal gains are half convective, half radiant. Ground-floor loss goes to the annual mean outdoor temperature.",
        "TM59 criteria are meant per room; applied to one zone they are indicators for comparing cases, not an assessment.",
        "",
        "Recalculation: about 300,000 formulas. Excel recalculates in a few seconds; if calculation is set to manual, press F9.",
    ])
    I = inputs_sheet(wb)
    el_first, el_last = elements_sheet(wb)
    packages_sheet(wb)
    P = parameters_sheet(wb, I, el_first, el_last)
    results_sheet(wb, I, P)
    weather_sheet(wb, I)
    hourly_sheet(wb, I, P)
    daily_sheet(wb)
    python_sheet(wb)
    order = ["Read me", "Inputs", "Results", "Parameters", "Packages", "Elements", "Hourly", "Daily", "Weather", "Python check"]
    wb._sheets = [wb[n] for n in order]
    wb.save(path)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    build(os.path.join(HERE, "out", "house-simulator.xlsx"))
    print("written")
