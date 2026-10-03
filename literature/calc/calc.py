import cmath, math
# Part 1: periodic penetration depth and effective areal heat capacity of a layer with adiabatic back (ISO 13786 style)
mats = {"Dense concrete":(1.4,2300,1000),"Clay brick":(0.77,1750,1000),"Gypsum plaster/board":(0.25,900,1000),"Timber/CLT":(0.13,480,1600),"Aerated concrete block":(0.15,600,1000)}
Rsi=0.13
def kappa(lam,rho,c,d,T):
    w=2*math.pi/T; delta=math.sqrt(lam*T/(math.pi*rho*c))
    if d==0: return 0,delta
    k=(1+1j)/delta
    Y=lam*k*cmath.tanh(k*d)            # layer admittance, adiabatic back
    Yt=1/(Rsi+1/Y)                     # include internal surface resistance
    return abs(Yt)/w/1000, delta       # kJ/m2K
for T,label in [(86400,"24 h"),(7*86400,"7 day")]:
    print("\n== period",label)
    ds=[0.0125,0.025,0.05,0.075,0.1,0.15,0.2,0.3]
    print("material | delta(mm) | "+" | ".join(f"{int(d*1000)}mm" for d in ds))
    for m,(l,r,c) in mats.items():
        vals=[kappa(l,r,c,d,T)[0] for d in ds]
        print(m,"|",round(kappa(l,r,c,0.1,T)[1]*1000),"|"," | ".join(f"{v:.0f}" for v in vals))
    # thickness for 90% of infinite-thickness value
    for m,(l,r,c) in mats.items():
        inf=kappa(l,r,c,5,T)[0]
        d=0.001
        while kappa(l,r,c,d,T)[0]<0.9*inf: d+=0.001
        print(f"  {m}: max {inf:.0f} kJ/m2K, 90% reached at {d*1000:.0f} mm")
print("cap from Rsi alone, 24h:",round(1/Rsi/(2*math.pi/86400)/1000),"kJ/m2K")
