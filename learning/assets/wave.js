/* Thermal mass course: thermal wave explorer.

   <div class="wave" data-material="dense concrete" data-period="24"></div>

   Plots the periodic solution for a semi-infinite solid whose surface swings
   ±2 K: theta(x,t) = 2 exp(-x/delta) cos(wt - x/delta), with
   delta = sqrt(lambda T / (pi rho c)). Material values match the project's
   ISO 13786 calculator (typical book values). */
(function () {
  "use strict";

  const MATERIALS = {
    "dense concrete": [2.0, 2400, 1000],
    "brick": [0.77, 1700, 800],
    "dense block": [1.13, 2000, 1000],
    "rammed earth": [1.0, 1900, 900],
    "aerated block": [0.15, 600, 1000],
    "plasterboard": [0.21, 700, 1000],
    "CLT (softwood)": [0.13, 470, 1600],
    "mineral wool": [0.035, 30, 1030],
  };
  const PERIODS = { "1 hour": 1, "24 hours": 24, "3 days": 72, "7 days": 168 };
  const AMP = 2; // K, surface swing amplitude

  function props(name, hours) {
    const [lam, rho, c] = MATERIALS[name];
    const T = hours * 3600;
    const alpha = lam / (rho * c);
    const delta = Math.sqrt(lam * T / (Math.PI * rho * c));
    const b = Math.sqrt(lam * rho * c);
    const w = 2 * Math.PI / T;
    return { lam, rho, c, T, alpha, delta, b, w };
  }

  function el(tag, attrs, text) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function init(root, n) {
    const id = "wave" + n;
    const startMat = root.dataset.material || "dense concrete";
    const startP = Number(root.dataset.period || 24);
    root.innerHTML = `
      <div class="wave-controls">
        <label>Material <select id="${id}-m">${Object.keys(MATERIALS).map((m) =>
          `<option${m === startMat ? " selected" : ""}>${m}</option>`).join("")}</select></label>
        <label>Period <select id="${id}-p">${Object.entries(PERIODS).map(([k, v]) =>
          `<option value="${v}"${v === startP ? " selected" : ""}>${k}</option>`).join("")}</select></label>
        <label class="wave-time">Time in cycle <input id="${id}-t" type="range" min="0" max="1" step="0.01" value="0.25"></label>
      </div>
      <div class="wave-plot"></div>
      <dl class="wave-read"></dl>`;
    const mSel = root.querySelector(`#${id}-m`);
    const pSel = root.querySelector(`#${id}-p`);
    const tIn = root.querySelector(`#${id}-t`);
    const plot = root.querySelector(".wave-plot");
    const read = root.querySelector(".wave-read");

    function draw() {
      const P = props(mSel.value, Number(pSel.value));
      const phase = Number(tIn.value) * 2 * Math.PI;
      const W = 640, H = 260, L = 46, R = 16, Tp = 18, B = 40;
      const xmaxMm = Math.max(300, Math.ceil((3 * P.delta * 1000) / 100) * 100);
      const sx = (mm) => L + (mm / xmaxMm) * (W - L - R);
      const sy = (k) => Tp + ((AMP - k) / (2 * AMP)) * (H - Tp - B);
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Temperature swing against depth" });

      // first 100 mm band
      svg.append(el("rect", { x: sx(0), y: Tp, width: sx(100) - sx(0), height: H - Tp - B, class: "dg-panel" }));
      svg.append(el("text", { x: sx(50), y: Tp + 14, class: "dg-small", "text-anchor": "middle" }, "first 100 mm"));
      // axes and grid
      for (let k = -2; k <= 2; k++) {
        svg.append(el("line", { x1: L, x2: W - R, y1: sy(k), y2: sy(k), class: "dg-muted", "stroke-width": k === 0 ? 1 : 0.4, "stroke-dasharray": k === 0 ? "" : "2 4" }));
        svg.append(el("text", { x: L - 8, y: sy(k) + 4, class: "dg-small", "text-anchor": "end" }, (k > 0 ? "+" : "") + k));
      }
      const step = xmaxMm <= 400 ? 50 : xmaxMm <= 800 ? 100 : 200;
      for (let mm = 0; mm <= xmaxMm; mm += step) {
        svg.append(el("text", { x: sx(mm), y: H - B + 16, class: "dg-small", "text-anchor": "middle" }, String(mm)));
      }
      svg.append(el("text", { x: (L + W - R) / 2, y: H - 6, class: "dg-small", "text-anchor": "middle" }, "depth from surface, mm"));
      svg.append(el("text", { x: 12, y: Tp + (H - Tp - B) / 2, class: "dg-small", "text-anchor": "middle", transform: `rotate(-90 12 ${Tp + (H - Tp - B) / 2})` }, "swing, K"));

      // envelope and profile
      const N = 160;
      let up = "", dn = "", prof = "";
      for (let i = 0; i <= N; i++) {
        const mm = (i / N) * xmaxMm, x = mm / 1000;
        const env = AMP * Math.exp(-x / P.delta);
        const v = env * Math.cos(phase - x / P.delta);
        up += (i ? "L" : "M") + sx(mm).toFixed(1) + " " + sy(env).toFixed(1);
        dn += (i ? "L" : "M") + sx(mm).toFixed(1) + " " + sy(-env).toFixed(1);
        prof += (i ? "L" : "M") + sx(mm).toFixed(1) + " " + sy(v).toFixed(1);
      }
      svg.append(el("path", { d: up, class: "dg-cool", "stroke-width": 1.3, "stroke-dasharray": "5 4" }));
      svg.append(el("path", { d: dn, class: "dg-cool", "stroke-width": 1.3, "stroke-dasharray": "5 4" }));
      svg.append(el("path", { d: prof, class: "dg-heat", "stroke-width": 2.4 }));

      // delta marker
      const dmm = P.delta * 1000;
      if (dmm <= xmaxMm) {
        svg.append(el("line", { x1: sx(dmm), x2: sx(dmm), y1: Tp, y2: H - B, class: "dg-ink", "stroke-width": 1 }));
        svg.append(el("text", { x: sx(dmm) + 5, y: sy(-1.75), class: "dg-text" }, `δ = ${dmm.toFixed(0)} mm`));
      }
      plot.replaceChildren(svg);

      const at100 = AMP * Math.exp(-0.1 / P.delta);
      const lag100 = (0.1 / P.delta) / P.w / 3600;
      const fmt = (v, d) => v.toLocaleString("en-GB", { maximumFractionDigits: d, minimumFractionDigits: d });
      read.innerHTML = `
        <div><dt>Penetration depth <var>δ</var></dt><dd>${fmt(dmm, 0)} mm</dd></div>
        <div><dt>Diffusivity <var>α</var></dt><dd>${fmt(P.alpha * 1e6, 2)} mm²/s</dd></div>
        <div><dt>Effusivity <var>b</var></dt><dd>${fmt(P.b, 0)} J/m²K s<sup>½</sup></dd></div>
        <div><dt>Swing at 100 mm</dt><dd>±${fmt(at100, 2)} K</dd></div>
        <div><dt>Delay at 100 mm</dt><dd>${fmt(lag100, 1)} h</dd></div>
        <div><dt>Heat capacity <var>ρc</var></dt><dd>${fmt(P.rho * P.c / 1e6, 2)} MJ/m³K</dd></div>`;
    }
    [mSel, pSel, tIn].forEach((x) => x.addEventListener("input", draw));
    draw();
  }

  function start() { document.querySelectorAll(".wave").forEach(init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
