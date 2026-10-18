# Thermal mass Excel workbooks

Excel twins of the four models. Every result is a live formula unless the
Read me sheet says otherwise. Blue-on-yellow cells are inputs.

| Workbook | Model | Notes |
|----------|-------|-------|
| `out/buildup-explorer.xlsx` | 1 | ISO 13786 with Excel complex-number functions, five-node class, 29-row library plus a custom row |
| `out/conduction-lab.xlsx` | 2 | Fine mesh (60 nodes) and five-node chains solved by implicit Euler with MINVERSE, over four days at 300 s steps |
| `out/house-simulator.xlsx` | 3 | The house as an hourly ISO 13790 5R1C model over 8,760 hours, not the full multi-layer model; Python reference results included |
| `out/mass-sweeps.xlsx` | 4 | Sweep results pasted from Python, with derived savings, an interpolator and charts |

Rebuild with `python3 build_buildup.py` (and so on). openpyxl writes
formulas without values, so open in Excel or recalculate with LibreOffice.
All four were recalculated in LibreOffice with zero formula errors and
checked against the Python models.
