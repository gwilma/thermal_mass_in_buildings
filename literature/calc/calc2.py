import math
from calc import kappa, mats
# peak thickness & 90%-of-peak thickness, 24h
for m,(l,r,c) in mats.items():
    best=max(((kappa(l,r,c,d/1000,86400)[0],d) for d in range(1,301)))
    d90=next(d for d in range(1,301) if kappa(l,r,c,d/1000,86400)[0]>=0.9*best[0])
    print(f"{m}: peak {best[0]:.0f} at {best[1]} mm; 90% by {d90} mm")
