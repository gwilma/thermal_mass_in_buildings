/* Thermal mass course: practice components shared by every lesson.

   Multiple choice (options are shuffled, so position gives no clue):
     <div class="q" data-answer="2">            <- 1-based index of the right <li>
       <p class="q-stem">Question</p>
       <ol class="q-options"><li>…</li><li>…</li></ol>
       <div class="q-why">Explanation shown after answering</div>
     </div>

   Numeric exercise (relative tolerance, default 5%):
     <div class="calc" data-answer="4.0" data-tol="0.05" data-unit="kWh">
       <p>Question</p>
       <div class="working">Worked solution, revealed after a right answer or on request</div>
     </div>

   Prediction (pretest; the guess is echoed later in the lesson):
     <div class="predict" data-id="ratio" data-unit="×"><p>Question</p></div>
     … <span data-echo="ratio"></span>

   A score line is written into any element with class "score". */
(function () {
  "use strict";

  const results = new Map(); // element -> true (right first time) | false
  const guesses = {};

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function updateScore() {
    const total = document.querySelectorAll(".q, .calc").length;
    const done = results.size;
    const first = [...results.values()].filter(Boolean).length;
    document.querySelectorAll(".score").forEach((el) => {
      el.textContent = done === 0
        ? `${total} questions. Answer from memory before scrolling back up.`
        : `${first} of ${done} right first time (${total - done} still to answer).`;
    });
  }

  function verdict(ok, text) {
    const v = document.createElement("span");
    v.className = "q-verdict " + (ok ? "ok" : "no");
    v.textContent = text;
    return v;
  }

  function initChoice(q) {
    const answer = Number(q.dataset.answer);
    const list = q.querySelector(".q-options");
    const why = q.querySelector(".q-why");
    if (why) why.hidden = true;
    const items = [...list.children].map((li, i) => ({ html: li.innerHTML, right: i + 1 === answer }));
    list.innerHTML = "";
    shuffle(items).forEach((item) => {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = item.html;
      b.addEventListener("click", () => {
        if (item.right) {
          b.classList.add("is-right");
          list.querySelectorAll("button").forEach((x) => (x.disabled = true));
          if (!results.has(q)) results.set(q, true);
          if (why) { why.prepend(verdict(true, "Right.")); why.hidden = false; }
        } else {
          b.classList.add("is-wrong");
          b.disabled = true;
          if (!results.has(q)) results.set(q, false);
        }
        updateScore();
      });
      li.appendChild(b);
      list.appendChild(li);
    });
  }

  function initCalc(c, n) {
    const answer = Number(c.dataset.answer);
    const tol = Number(c.dataset.tol || 0.05);
    const unit = c.dataset.unit || "";
    const working = c.querySelector(".working");
    if (working) working.hidden = true;

    const row = document.createElement("div");
    row.className = "calc-row";
    const id = c.id ? c.id + "-in" : "calc-in-" + n;
    row.innerHTML =
      `<input id="${id}" inputmode="decimal" autocomplete="off" placeholder="your answer" aria-label="Your answer">` +
      `<span class="unit">${unit}</span>` +
      `<button type="button" class="btn">Check</button>` +
      `<button type="button" class="btn ghost">Show working</button>`;
    const fb = document.createElement("p");
    fb.className = "feedback";
    fb.setAttribute("aria-live", "polite");
    if (working) working.before(row, fb); else c.append(row, fb);

    const input = row.querySelector("input");
    const [check, show] = row.querySelectorAll("button");
    let tries = 0;

    function reveal() { if (working) working.hidden = false; show.hidden = true; }

    function run() {
      const v = Number(String(input.value).replace(/,/g, "").trim());
      if (!input.value.trim() || Number.isNaN(v)) { fb.className = "feedback no"; fb.textContent = "Enter a number."; return; }
      tries++;
      const err = (v - answer) / Math.abs(answer);
      if (Math.abs(err) <= tol) {
        fb.className = "feedback ok";
        fb.textContent = `Right: ${c.dataset.answer} ${unit}.`;
        if (!results.has(c)) results.set(c, true);
        reveal();
      } else {
        if (!results.has(c)) results.set(c, false);
        fb.className = "feedback no";
        const factor = v / answer;
        let hint = err > 0 ? "Too high." : "Too low.";
        const near = (f) => Math.abs(factor / f - 1) < 0.08;
        if (near(1000) || near(0.001)) hint += " Out by a factor of 1000: check kJ against MJ, or mm against m.";
        else if (near(3.6) || near(1 / 3.6) || near(3600) || near(1 / 3600)) hint += " Check the conversion between joules and watt-hours (1 kWh = 3.6 MJ).";
        else if (near(2) || near(0.5)) hint += " Out by a factor of two: check the temperature difference.";
        if (c.dataset.hint) hint += " " + c.dataset.hint;
        if (tries >= 2) hint += " You can show the working now.";
        fb.textContent = hint;
      }
      updateScore();
    }
    check.addEventListener("click", run);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") run(); });
    show.addEventListener("click", () => { if (!results.has(c)) results.set(c, false); reveal(); updateScore(); });
  }

  function initPredict(p) {
    const id = p.dataset.id;
    const unit = p.dataset.unit || "";
    const row = document.createElement("div");
    row.className = "calc-row";
    row.innerHTML =
      `<input id="predict-${id}" inputmode="decimal" autocomplete="off" placeholder="your guess" aria-label="Your guess">` +
      `<span class="unit">${unit}</span><button type="button" class="btn ghost">Lock in guess</button>`;
    const fb = document.createElement("p");
    fb.className = "feedback";
    p.append(row, fb);
    const input = row.querySelector("input");
    row.querySelector("button").addEventListener("click", () => {
      const v = input.value.trim();
      if (!v) { fb.textContent = "Type any number, a rough guess is the point."; return; }
      guesses[id] = v;
      input.disabled = true;
      fb.className = "feedback ok";
      fb.textContent = "Locked in. You'll see the real answer further down.";
      document.querySelectorAll(`[data-echo="${id}"]`).forEach((el) => (el.textContent = `${v} ${unit}`.trim()));
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".q").forEach(initChoice);
    document.querySelectorAll(".calc").forEach(initCalc);
    document.querySelectorAll(".predict").forEach(initPredict);
    updateScore();
  });
})();
