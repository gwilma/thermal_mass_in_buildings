"""Assemble the standalone web apps.

Each app in src/*.html carries placeholders for the shared CSS, the model
core (core.js), the UI helpers (ui.js), the embedded weather year and the
precomputed Python results. Writes:
  dist/<app>.html      complete standalone pages (open from disk)
  artifact/<app>.html  the same page without the document skeleton (for publishing)
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
MODELS = os.path.join(HERE, "..", "models")
APPS = ["buildup", "conduction", "room", "sweeps"]


def weather_string():
    sys.path.insert(0, MODELS)
    import weather as wx
    w = wx.read_epw(wx.EPW_LONDON)
    enc = lambda a, k: ",".join(str(int(round(v * k))) for a_ in [a] for v in a_)
    return "|".join([f"{wx.LAT},{wx.LON},London Heathrow TMYx 2011-2025",
                     enc(w["T"], 10), enc(w["GHI"], 1), enc(w["DNI"], 1), enc(w["DHI"], 1)])


def results_json():
    res = os.path.join(MODELS, "results")
    num = lambda v: float(v) if v not in ("", None) else None
    rows = []
    for r in csv.DictReader(open(os.path.join(res, "packages.csv"))):
        rows.append({k: (v if k in ("package", "mode") else num(v)) for k, v in r.items()})
    sweeps = json.load(open(os.path.join(res, "sweeps.json"))) if os.path.exists(os.path.join(res, "sweeps.json")) else None
    return json.dumps({"packages": rows, "sweeps": sweeps}, separators=(",", ":"))


def main():
    css = open(os.path.join(SRC, "ui.css")).read()
    core = open(os.path.join(SRC, "core.js")).read()
    ui = open(os.path.join(SRC, "ui.js")).read()
    wstr = weather_string()
    rjson = results_json()
    for d in ("dist", "artifact"):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    for app in APPS:
        p = os.path.join(SRC, f"{app}.html")
        if not os.path.exists(p):
            continue
        body = open(p).read()
        body = (body.replace("{{STYLE}}", css).replace("{{CORE}}", core).replace("{{UI}}", ui)
                .replace("{{WEATHER}}", wstr).replace("{{RESULTS}}", rjson))
        open(os.path.join(HERE, "artifact", f"{app}.html"), "w").write(body)
        # standalone: put everything up to the first <div class="wrap"> in head
        i = body.index('<div class="wrap">')
        full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + body[:i] + "</head>\n<body>\n" + body[i:] + "\n</body>\n</html>\n")
        open(os.path.join(HERE, "dist", f"{app}.html"), "w").write(full)
        print(app, f"{len(full) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
