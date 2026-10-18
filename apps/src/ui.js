// Shared UI helpers: SVG charts, number formatting, worker runner.
"use strict";
const UI = (() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fmt = (v, d = 1) => (v === null || v === undefined || Number.isNaN(v)) ? "–" : Number(v).toLocaleString("en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
  const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const NS = "http://www.w3.org/2000/svg";

  function niceTicks(lo, hi, n = 5) {
    if (hi === lo) { hi = lo + 1; }
    const span = hi - lo, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
    const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => span / s <= n) || 10 * mag;
    const start = Math.ceil(lo / step - 1e-9) * step, out = [];
    for (let v = start; v <= hi + step * 1e-6; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function el(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  }
  function legend(host, series) {
    const lg = document.createElement("div"); lg.className = "legend";
    lg.innerHTML = series.filter(s => s.name).map(s => `<span><i style="background:${s.color};${s.dash ? "height:2px;background:repeating-linear-gradient(90deg," + s.color + " 0 4px,transparent 4px 7px)" : ""}"></i>${esc(s.name)}</span>`).join("");
    host.appendChild(lg);
  }

  // Line chart. series: [{name, x: [], y: [], color, dash, width}]
  function line(host, opt) {
    host.innerHTML = "";
    const W = Math.max(320, host.clientWidth || 640), H = opt.height || 260;
    const m = { l: 52, r: 14, t: 10, b: 38 };
    const all = opt.series.flatMap(s => s.x.map((x, i) => [x, s.y[i]])).filter(p => Number.isFinite(p[1]));
    let x0 = opt.xMin ?? Math.min(...all.map(p => p[0])), x1 = opt.xMax ?? Math.max(...all.map(p => p[0]));
    let y0 = opt.yMin ?? Math.min(...all.map(p => p[1])), y1 = opt.yMax ?? Math.max(...all.map(p => p[1]));
    if (opt.yZero) y0 = Math.min(0, y0);
    const pad = (y1 - y0) * 0.06 || 1; if (opt.yMin === undefined && !opt.yZero) y0 -= pad; if (opt.yMax === undefined) y1 += pad;
    const lx = v => opt.xLog ? Math.log10(v) : v;
    const X = v => m.l + (lx(v) - lx(x0)) / (lx(x1) - lx(x0)) * (W - m.l - m.r);
    const Y = v => H - m.b - (v - y0) / (y1 - y0) * (H - m.t - m.b);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opt.label || "chart" });
    const yt = niceTicks(y0, y1, opt.yTicks || 5);
    for (const v of yt) {
      el("line", { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), class: "grid" }, svg);
      const t = el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end" }, svg); t.textContent = opt.yFmt ? opt.yFmt(v) : fmt(v, Math.abs(yt[1] - yt[0]) < 1 ? 1 : 0);
    }
    let xt = opt.xTickVals || (opt.xLog ? [1, 2, 4, 8, 12, 24, 48, 96, 168].filter(v => v >= x0 && v <= x1) : niceTicks(x0, x1, opt.xTicks || 6));
    const minGap = opt.xFmt ? 52 : 34;  // drop tick labels that would collide on narrow screens
    { const kept = []; for (const v of xt) if (!kept.length || X(v) - X(kept[kept.length - 1]) >= minGap) kept.push(v); xt = kept; }
    for (const v of xt) {
      el("line", { x1: X(v), x2: X(v), y1: H - m.b, y2: H - m.b + 4, class: "axis" }, svg);
      const t = el("text", { x: X(v), y: H - m.b + 16, "text-anchor": "middle" }, svg); t.textContent = opt.xFmt ? opt.xFmt(v) : fmt(v, 0);
    }
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, class: "axis" }, svg);
    if (opt.xLabel) { const t = el("text", { x: (m.l + W - m.r) / 2, y: H - 4, "text-anchor": "middle", class: "ttl" }, svg); t.textContent = opt.xLabel; }
    if (opt.yLabel) { const t = el("text", { x: 12, y: (m.t + H - m.b) / 2, "text-anchor": "middle", class: "ttl", transform: `rotate(-90 12 ${(m.t + H - m.b) / 2})` }, svg); t.textContent = opt.yLabel; }
    for (const b of opt.bands || []) el("rect", { x: X(b.x0), y: m.t, width: Math.max(0, X(b.x1) - X(b.x0)), height: H - m.t - m.b, fill: b.color, opacity: b.opacity ?? 0.08 }, svg);
    for (const r of opt.hlines || []) {
      el("line", { x1: m.l, x2: W - m.r, y1: Y(r.y), y2: Y(r.y), stroke: r.color, "stroke-dasharray": "4 3", "stroke-width": 1 }, svg);
      if (r.label) { const t = el("text", { x: W - m.r - 4, y: Y(r.y) - 4, "text-anchor": "end" }, svg); t.textContent = r.label; }
    }
    for (const s of opt.series) {
      let d = "", pen = false;
      s.x.forEach((x, i) => { const y = s.y[i]; if (!Number.isFinite(y)) { pen = false; return; } d += (pen ? "L" : "M") + X(x).toFixed(1) + "," + Y(y).toFixed(1); pen = true; });
      el("path", { d, fill: "none", stroke: s.color, "stroke-width": s.width || 1.8, "stroke-dasharray": s.dash ? "5 4" : "none", "stroke-linejoin": "round" }, svg);
      if (s.dots) s.x.forEach((x, i) => el("circle", { cx: X(x), cy: Y(s.y[i]), r: 2.8, fill: s.color }, svg));
    }
    host.appendChild(svg);
    // hover readout
    const tip = document.createElement("div"); tip.className = "tip"; tip.hidden = true; host.appendChild(tip);
    const cross = el("line", { y1: m.t, y2: H - m.b, class: "axis", "stroke-width": 1, visibility: "hidden" }, svg);
    svg.addEventListener("pointermove", ev => {
      const r = svg.getBoundingClientRect(), px = (ev.clientX - r.left) * W / r.width;
      if (px < m.l || px > W - m.r) { tip.hidden = true; cross.setAttribute("visibility", "hidden"); return; }
      const ref = opt.series[0]; let best = 0, bd = Infinity;
      ref.x.forEach((x, i) => { const dd = Math.abs(X(x) - px); if (dd < bd) { bd = dd; best = i; } });
      const xv = ref.x[best];
      cross.setAttribute("x1", X(xv)); cross.setAttribute("x2", X(xv)); cross.setAttribute("visibility", "visible");
      tip.innerHTML = `<div>${esc(opt.xFmtTip ? opt.xFmtTip(xv) : (opt.xFmt ? opt.xFmt(xv) : fmt(xv, 2)))}</div>` +
        opt.series.filter(s => s.name).map(s => { const j = s.x.indexOf(xv); const v = j >= 0 ? s.y[j] : NaN; return `<div style="color:${s.color}">${esc(s.name)}: ${fmt(v, opt.tipDigits ?? 2)}</div>`; }).join("");
      tip.hidden = false;
      const left = (X(xv) / W) * r.width; tip.style.left = Math.min(left + 12, r.width - tip.offsetWidth - 4) + "px"; tip.style.top = "8px";
    });
    svg.addEventListener("pointerleave", () => { tip.hidden = true; cross.setAttribute("visibility", "hidden"); });
    if (!opt.noLegend) legend(host, opt.series);
  }

  // Horizontal grouped bars. labels: [], series: [{name, values, color}]
  function hbar(host, opt) {
    host.innerHTML = "";
    const ns = opt.series.length, W = Math.max(320, host.clientWidth || 640), rowH = opt.rowH || (ns > 1 && opt.valueLabels ? 34 : 26);
    const labW = Math.min(opt.labelWidth || 260, W * 0.48);
    const m = { l: labW + 8, r: 40, t: 6, b: 34 }, H = m.t + m.b + rowH * opt.labels.length;
    const vmax = opt.xMax ?? Math.max(...opt.series.flatMap(s => s.values), ...(opt.refs || []).map(r => r.x)) * 1.05;
    const X = v => m.l + v / vmax * (W - m.l - m.r);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opt.label || "bar chart" });
    for (const v of niceTicks(0, vmax, W < 520 ? 3 : 5)) {
      el("line", { x1: X(v), x2: X(v), y1: m.t, y2: H - m.b, class: "grid" }, svg);
      const t = el("text", { x: X(v), y: H - m.b + 16, "text-anchor": "middle" }, svg); t.textContent = fmt(v, 0);
    }
    if (opt.xLabel) { const t = el("text", { x: (m.l + W - m.r) / 2, y: H - 3, "text-anchor": "middle", class: "ttl" }, svg); t.textContent = opt.xLabel; }
    const bh = (rowH - 6) / ns;
    opt.labels.forEach((lab, i) => {
      const y = m.t + i * rowH;
      const t = el("text", { x: m.l - 8, y: y + rowH / 2 + 4, "text-anchor": "end", class: "ttl" }, svg);
      t.textContent = lab.length > labW / 6.2 ? lab.slice(0, Math.floor(labW / 6.2) - 1) + "…" : lab;
      const tt = el("title", {}, t); tt.textContent = lab;
      opt.series.forEach((s, k) => {
        const v = s.values[i];
        el("rect", { x: m.l, y: y + 3 + k * bh, width: Math.max(0, X(v) - m.l), height: bh - 1, fill: s.color, rx: 1.5 }, svg);
        if (opt.valueLabels) { const vt = el("text", { x: X(v) + 4, y: y + 3 + k * bh + bh / 2 + 3.5 }, svg); vt.textContent = fmt(v, opt.digits ?? 0); }
      });
    });
    for (const r of opt.refs || []) {
      el("line", { x1: X(r.x), x2: X(r.x), y1: m.t, y2: H - m.b, stroke: r.color || css("--fg"), "stroke-dasharray": "4 3" }, svg);
      if (r.label) { const t = el("text", { x: X(r.x) + 4, y: m.t + 10 }, svg); t.textContent = r.label; }
    }
    host.appendChild(svg);
    if (ns > 1) legend(host, opt.series);
  }

  // Heatmap as a table. rows/cols labels, Z[row][col]
  function heat(host, { rows, cols, Z, rowTitle, colTitle, digits = 0, color = "--heat" }) {
    const vals = Z.flat(), lo = Math.min(...vals), hi = Math.max(...vals);
    let h = `<div class="scroll"><table class="data"><thead><tr><th class="l">${esc(rowTitle)} \\ ${esc(colTitle)}</th>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>`;
    Z.forEach((r, i) => {
      h += `<tr><td class="l">${esc(rows[i])}</td>` + r.map(v => {
        const f = hi > lo ? (v - lo) / (hi - lo) : 0;
        return `<td style="background:color-mix(in srgb, var(${color}) ${Math.round(8 + 62 * f)}%, var(--panel));color:${f > 0.6 ? "var(--panel)" : "var(--fg)"}">${fmt(v, digits)}</td>`;
      }).join("") + "</tr>";
    });
    host.innerHTML = h + "</tbody></table></div>";
  }

  // Run work in a Web Worker built from the core source; falls back to the main thread.
  function makeWorker(coreSrc, handlerSrc) {
    try {
      const blob = new Blob([coreSrc + "\n" + handlerSrc], { type: "text/javascript" });
      const w = new Worker(URL.createObjectURL(blob));
      return w;
    } catch (e) { return null; }
  }

  function decodeWeather(s) {
    const [meta, T, G, Dn, Dh] = s.split("|");
    const dec = (str, k) => Float64Array.from(str.split(",").map(v => +v / k));
    const [lat, lon, ...name] = meta.split(",");
    return { T: dec(T, 10), GHI: dec(G, 1), DNI: dec(Dn, 1), DHI: dec(Dh, 1), lat: +lat, lon: +lon, name: name.join(",") };
  }

  function themeColors() {
    return { heat: css("--heat"), cool: css("--cool"), mass: css("--mass"), fg: css("--fg"), muted: css("--muted"), line: css("--line"), ok: css("--ok"), bad: css("--bad"), warn: css("--warn") };
  }
  function onTheme(fn) {
    const mq = matchMedia("(prefers-color-scheme: dark)"); mq.addEventListener?.("change", fn);
    new MutationObserver(fn).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(fn, 150); });
  }
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } },
  };
  return { $, $$, esc, fmt, css, line, hbar, heat, makeWorker, decodeWeather, themeColors, onTheme, store, niceTicks };
})();
