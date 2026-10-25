/* Thermal mass course: sidebar calculator, shared by every lesson.

   Include with <script src="../assets/calc.js" defer></script>. It adds itself:
   docked in the right-hand sidebar on wide screens, and as a pull-up panel behind
   a "Calculator" button on narrow ones.

   Expressions: + - * / ^ and brackets, also × ÷ −. Numbers like 7,200 or 5.67e-8.
   Functions: sqrt exp ln log sin cos tan atan abs. Constants: pi, ans.
   "Use as answer" copies the result into the exercise box you last clicked. */
(function () {
  "use strict";

  const FUNCS = {
    sqrt: Math.sqrt, exp: Math.exp, ln: Math.log, log: Math.log10,
    sin: Math.sin, cos: Math.cos, tan: Math.tan, atan: Math.atan, abs: Math.abs,
  };
  let ans = 0;

  // ---- parser: recursive descent, no eval ----
  function tokenize(src) {
    const s = src
      .replace(/(\d),(?=\d{3}\b)/g, "$1")
      .replace(/[×·]/g, "*").replace(/÷/g, "/").replace(/[−–]/g, "-").replace(/√/g, "sqrt")
      .replace(/π/g, "pi").replace(/\*\*/g, "^");
    const out = [];
    const re = /\s*(?:(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z]+)|([-+*/^()]))/y;
    let m;
    re.lastIndex = 0;
    while (re.lastIndex < s.length) {
      const start = re.lastIndex;
      if (/^\s*$/.test(s.slice(start))) break;
      m = re.exec(s);
      if (!m) throw new Error(`Can't read "${s.slice(start).trim().slice(0, 8)}"`);
      if (m[1]) out.push({ t: "n", v: parseFloat(m[1]) });
      else if (m[2]) out.push({ t: "id", v: m[2].toLowerCase() });
      else out.push({ t: m[3] });
    }
    return out;
  }

  function evaluate(src) {
    const tk = tokenize(src);
    let i = 0;
    const peek = () => tk[i] && tk[i].t;
    const take = (t) => { if (peek() !== t) throw new Error(t === ")" ? "Missing )" : `Expected ${t}`); return tk[i++]; };

    function expr() {
      let v = term();
      while (peek() === "+" || peek() === "-") v = tk[i++].t === "+" ? v + term() : v - term();
      return v;
    }
    function term() {
      let v = unary();
      for (;;) {
        if (peek() === "*") { i++; v *= unary(); }
        else if (peek() === "/") { i++; v /= unary(); }
        else if (peek() === "n" || peek() === "id" || peek() === "(") v *= unary(); // 2pi, 3(4+5)
        else return v;
      }
    }
    function unary() {
      if (peek() === "-") { i++; return -unary(); }
      if (peek() === "+") { i++; return unary(); }
      return power();
    }
    function power() {
      const b = primary();
      if (peek() === "^") { i++; return Math.pow(b, unary()); }
      return b;
    }
    function primary() {
      const tok = tk[i];
      if (!tok) throw new Error("Incomplete");
      if (tok.t === "n") { i++; return tok.v; }
      if (tok.t === "(") { i++; const v = expr(); take(")"); return v; }
      if (tok.t === "id") {
        i++;
        if (tok.v === "pi") return Math.PI;
        if (tok.v === "ans") return ans;
        if (tok.v === "e" ) return Math.E;
        const f = FUNCS[tok.v];
        if (!f) throw new Error(`Unknown "${tok.v}"`);
        take("("); const v = expr(); take(")");
        return f(v);
      }
      throw new Error(`Unexpected ${tok.t}`);
    }

    if (!tk.length) throw new Error("Empty");
    const v = expr();
    if (i < tk.length) throw new Error(`Unexpected ${tk[i].t === "n" ? tk[i].v : tk[i].t}`);
    if (!Number.isFinite(v)) throw new Error("Not a finite number");
    return v;
  }

  function fmt(v) {
    if (v === 0) return "0";
    const a = Math.abs(v);
    if (a >= 1e9 || a < 1e-4) return v.toExponential(4).replace(/\.?0+e/, "e");
    return String(Number(v.toPrecision(6)));
  }

  // ---- storage: per-viewer convenience only ----
  const KEY = "tm-course-calc-tape";
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save(t) { try { localStorage.setItem(KEY, JSON.stringify(t.slice(0, 12))); } catch (e) { /* ignore */ } }

  // ---- UI ----
  const KEYS = [
    ["7", "8", "9", "÷"], ["4", "5", "6", "×"], ["1", "2", "3", "−"],
    ["0", ".", "e", "+"], ["(", ")", "^", "√("], ["ans", "π", "⌫", "C"],
  ];

  function build() {
    const panel = document.createElement("aside");
    panel.className = "calcpad";
    panel.setAttribute("aria-label", "Calculator");
    panel.innerHTML = `
      <div class="calcpad-head">
        <span class="label">Calculator</span>
        <button type="button" class="calcpad-close" aria-label="Close calculator">Close</button>
      </div>
      <input id="calcpad-expr" class="calcpad-expr" autocomplete="off" spellcheck="false"
        inputmode="text" placeholder="30*0.1*2400*1000*2" aria-label="Expression">
      <output class="calcpad-out" for="calcpad-expr" aria-live="polite">&nbsp;</output>
      <div class="calcpad-keys">${KEYS.flat().map((k) =>
        `<button type="button" data-k="${k}"${k === "C" || k === "⌫" ? ' class="fn"' : ""}>${k === "√(" ? "√" : k}</button>`).join("")}
        <button type="button" data-k="=" class="eq">=</button>
      </div>
      <button type="button" class="calcpad-use" disabled>Use as answer</button>
      <ol class="calcpad-tape" aria-label="Recent results"></ol>
      <p class="calcpad-help">Type or tap. <span class="mono">^</span> powers, <span class="mono">sqrt( )</span>, <span class="mono">pi</span>, <span class="mono">ans</span>. 1&nbsp;kWh = 3.6&nbsp;MJ.</p>`;

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "calcpad-toggle";
    toggle.textContent = "Calculator";
    toggle.setAttribute("aria-expanded", "false");

    document.body.append(panel, toggle);
    document.body.classList.add("has-calcpad");

    const input = panel.querySelector(".calcpad-expr");
    const out = panel.querySelector(".calcpad-out");
    const tapeEl = panel.querySelector(".calcpad-tape");
    const use = panel.querySelector(".calcpad-use");
    let tape = load();
    let lastTarget = null;
    let lastValue = null;

    function renderTape() {
      tapeEl.innerHTML = "";
      tape.forEach((row) => {
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type = "button";
        b.innerHTML = `<span class="x"></span><span class="v"></span>`;
        b.querySelector(".x").textContent = row.x;
        b.querySelector(".v").textContent = "= " + row.v;
        b.title = "Put this expression back in the calculator";
        b.addEventListener("click", () => { input.value = row.x; input.focus(); });
        li.appendChild(b);
        tapeEl.appendChild(li);
      });
    }

    function run() {
      const x = input.value.trim();
      if (!x) return;
      try {
        const v = evaluate(x);
        ans = v;
        lastValue = fmt(v);
        out.textContent = lastValue;
        out.classList.remove("err");
        tape.unshift({ x, v: lastValue });
        tape = tape.slice(0, 12);
        save(tape);
        renderTape();
        input.select();
        use.disabled = !lastTarget;
      } catch (e) {
        out.textContent = e.message;
        out.classList.add("err");
      }
    }

    function insert(text) {
      const s = input.selectionStart ?? input.value.length;
      const e = input.selectionEnd ?? input.value.length;
      input.value = input.value.slice(0, s) + text + input.value.slice(e);
      const p = s + text.length;
      input.focus();
      input.setSelectionRange(p, p);
    }

    panel.querySelector(".calcpad-keys").addEventListener("click", (ev) => {
      const k = ev.target.closest("button")?.dataset.k;
      if (!k) return;
      if (k === "=") run();
      else if (k === "C") { input.value = ""; out.innerHTML = "&nbsp;"; input.focus(); }
      else if (k === "⌫") {
        const s = input.selectionStart, e = input.selectionEnd;
        if (s !== e) insert("");
        else if (s > 0) { input.value = input.value.slice(0, s - 1) + input.value.slice(s); input.setSelectionRange(s - 1, s - 1); input.focus(); }
      } else insert(k);
    });
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); run(); } });

    // Remember the exercise box the learner last used, for "Use as answer".
    document.addEventListener("focusin", (e) => {
      if (e.target.matches(".calc-row input:not(:disabled)")) {
        lastTarget = e.target;
        use.disabled = lastValue === null;
        use.textContent = "Use as answer";
      }
    });
    use.addEventListener("click", () => {
      if (!lastTarget || lastValue === null) return;
      lastTarget.value = lastValue;
      lastTarget.focus();
      use.textContent = "Copied to your answer";
      if (document.body.classList.contains("calcpad-open") && !wide.matches) setOpen(false);
    });

    const wide = window.matchMedia("(min-width: 84rem)");
    function setOpen(open) {
      document.body.classList.toggle("calcpad-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      if (open) input.focus();
    }
    toggle.addEventListener("click", () => setOpen(!document.body.classList.contains("calcpad-open")));
    panel.querySelector(".calcpad-close").addEventListener("click", () => { setOpen(false); toggle.focus(); });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && document.body.classList.contains("calcpad-open")) { setOpen(false); toggle.focus(); }
    });

    renderTape();
  }

  window.courseCalc = { evaluate, fmt };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
