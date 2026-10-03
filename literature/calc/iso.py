# ISO 13790 monthly method, illustrative 100 m2 dwelling, London-like climate
Te=[5.2,5.3,7.6,9.9,13.3,16.4,18.7,18.5,15.7,12.0,8.0,5.5]
Isouth=[50,65,85,95,100,95,100,100,90,75,50,40]   # kWh/m2 month, south vertical (approx)
days=[31,28,31,30,31,30,31,31,30,31,30,31]
Af=100; Ti=20; qint=2.1  # W/m2 internal gains (PHPP-type)
def heat(Hspec, glaz_frac, Cm_kJ):
    H=Hspec*Af; C=Cm_kJ*1000*Af
    tau=C/H/3600; a=1+tau/15
    tot=0
    for m in range(12):
        Ql=H*(Ti-Te[m])*24*days[m]/1000
        if Ql<=0: continue
        Qg=qint*Af*24*days[m]/1000 + Isouth[m]*glaz_frac*Af*0.5*0.75
        g=Qg/Ql
        eta = a/(a+1) if abs(g-1)<1e-9 else (1-g**a)/(1-g**(a+1))
        tot+=max(0,Ql-eta*Qg)
    return tot/Af, tau
cases=[("2006 regs-ish house",1.8,0.10),("Good low-energy house",1.0,0.12),("Passivhaus-level",0.65,0.15),("Passivhaus, large south glazing",0.65,0.25)]
Cms=[50,80,110,165,260,370,500]
print("case | "+" | ".join(str(c) for c in Cms))
for name,Hs,gf in cases:
    row=[heat(Hs,gf,c) for c in Cms]
    print(name,"|"," | ".join(f"{q:.1f} (τ{t:.0f}h)" for q,t in row))
    base=row[0][0]; full=row[-1][0]
    print("   share of total 50→500 saving achieved:", " | ".join(f"{(base-q)/(base-full)*100:.0f}%" for q,_ in row))
