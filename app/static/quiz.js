/* One quiz, one page. The question showing is whatever the URL fragment says,
   so Back, Forward and reload all behave. Answers live in localStorage as
   well as on the server, so a reload mid-quiz picks up where it left off. */

const QUIZ = JSON.parse(document.getElementById("quiz-data").textContent);
const qs = QUIZ.questions;
const STORE = "craft-quiz:" + QUIZ.id;
const LETTERS = "ABCDEFGHIJ";

const $ = id => document.getElementById(id);
const state = { name: "", email: "", i: 0, answers: {}, finished: false };

/* ---------- saved progress ---------- */

function save() {
  try {
    localStorage.setItem(STORE, JSON.stringify(state));
  } catch (e) { /* private browsing, a full disk: not worth stopping the quiz */ }
}

function restore() {
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem(STORE) || "null");
  } catch (e) { return; }
  if (!saved) return;

  state.name = saved.name || "";
  state.email = saved.email || "";
  state.finished = !!saved.finished;
  // Ids the quiz no longer has would be rejected by the server, so drop them.
  const known = new Set(qs.map(q => q.id));
  for (const [id, choice] of Object.entries(saved.answers || {})) {
    if (known.has(id)) state.answers[id] = choice;
  }
  if (state.name) $("f-name").value = state.name;
  if (state.email) $("f-email").value = state.email;
}

/* ---------- talking to the server ---------- */

/* Every ping carries the whole answer set, not just the latest answer, so one
   that never arrives costs nothing: the next one says everything it would have. */
function ping(kind) {
  return fetch(location.pathname, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      kind: kind,
      name: state.name,
      email: state.email,
      index: state.i,
      answers: state.answers,
    }),
    keepalive: true,
  });
}

/* ---------- routing ---------- */

function answeredCount() {
  return qs.filter(q => state.answers[q.id] != null).length;
}

function hashIndex() {
  const m = /^#q(\d+)$/.exec(location.hash);
  if (!m) return null;
  const n = parseInt(m[1], 10) - 1;
  return n >= 0 && n < qs.length ? n : null;
}

function goTo(i) {
  const want = "#q" + (i + 1);
  if (location.hash === want) route();
  else location.hash = want;   // hashchange calls route()
}

function show(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.toggle("on", s.id === id));
  window.scrollTo(0, 0);
}

function route() {
  $("quiz-err").hidden = true;

  if (state.finished) {
    showDone();
    return;
  }

  const i = hashIndex();
  if (i === null || !state.name || !state.email) {
    if (answeredCount() > 0) $("btn-start").textContent = "Continue quiz";
    show("s-start");
    return;
  }

  // Next is disabled until the question is answered, so the furthest anyone
  // can legitimately be is one past their last answer. Typing a bigger number
  // into the URL lands on that question instead.
  const furthest = Math.min(answeredCount(), qs.length - 1);
  if (i > furthest) {
    location.replace("#q" + (furthest + 1));
    return;
  }

  state.i = i;
  save();
  show("s-quiz");
  render();
}

/* ---------- start screen ---------- */

function fail(el, msg) { el.textContent = msg; el.hidden = false; }

$("btn-start").addEventListener("click", () => {
  const name = $("f-name").value.trim();
  const email = $("f-email").value.trim().toLowerCase();
  const err = $("start-err");
  if (!name) return fail(err, "Enter your name.");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return fail(err, "Enter a valid email address.");

  err.hidden = true;
  const first = !state.name;
  state.name = name;
  state.email = email;
  save();
  // Ping before the first question, so someone who fills the form and then
  // stares at Q1 still shows up on the dashboard as started.
  if (first || answeredCount() === 0) ping("start").catch(() => {});
  goTo(Math.min(answeredCount(), qs.length - 1));
});

["f-name", "f-email"].forEach(id =>
  $(id).addEventListener("input", () => { $("start-err").hidden = true; })
);

/* ---------- question screen ---------- */

function renderProgress() {
  const box = $("progress");
  box.innerHTML = "";
  if (qs.length <= 16) {
    qs.forEach((q, n) => {
      const d = document.createElement("span");
      d.className = "dot" + (n === state.i ? " here" : (state.answers[q.id] != null ? " done" : ""));
      box.appendChild(d);
    });
  } else {
    const bar = document.createElement("span");
    bar.className = "bar";
    const fill = document.createElement("span");
    fill.style.width = ((state.i + 1) / qs.length * 100) + "%";
    bar.appendChild(fill);
    box.appendChild(bar);
  }
  const c = document.createElement("span");
  c.className = "count";
  c.textContent = (state.i + 1) + " / " + qs.length;
  box.appendChild(c);
}

function render() {
  const q = qs[state.i];
  $("q-num").textContent = "Q" + (state.i + 1);
  $("q-text").innerHTML = q.question;

  const box = $("q-opts");
  box.innerHTML = "";
  q.options.forEach((opt, n) => {
    const label = document.createElement("label");
    label.className = "opt";

    const input = document.createElement("input");
    input.type = "radio";
    input.name = q.id;
    input.value = n;
    input.checked = state.answers[q.id] === n;
    input.addEventListener("change", () => choose(n));

    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = LETTERS[n] || (n + 1);

    const body = document.createElement("span");
    body.className = "body";
    body.innerHTML = opt;

    label.append(input, chip, body);
    box.appendChild(label);
  });

  $("btn-back").textContent = state.i === 0 ? "← Back to start" : "← Back";
  $("btn-next").disabled = state.answers[q.id] == null;
  $("btn-next").textContent = state.i === qs.length - 1 ? "Finish" : "Next";
  $("q-hint").innerHTML =
    'Press <span class="kbd">' + LETTERS[0] + '</span>–<span class="kbd">' +
    (LETTERS[q.options.length - 1] || q.options.length) +
    '</span> to choose, <span class="kbd">Enter</span> to continue.';
  renderProgress();
}

function choose(n) {
  state.answers[qs[state.i].id] = n;
  save();
  render();
}

$("btn-back").addEventListener("click", () => {
  if (state.i > 0) goTo(state.i - 1);
  else location.hash = "#start";
});

$("btn-next").addEventListener("click", () => {
  if (state.answers[qs[state.i].id] == null) return;
  if (state.i < qs.length - 1) {
    ping("next").catch(() => {});
    goTo(state.i + 1);
  } else {
    finish();
  }
});

document.addEventListener("keydown", e => {
  if (!$("s-quiz").classList.contains("on")) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;

  const q = qs[state.i];
  const n = LETTERS.indexOf(e.key.toUpperCase());
  if (n > -1 && n < q.options.length) {
    choose(n);
    e.preventDefault();
  } else if (e.key === "Enter" && !$("btn-next").disabled) {
    $("btn-next").click();
  }
});

/* ---------- finishing ---------- */

async function finish() {
  const btn = $("btn-next");
  btn.disabled = true;
  btn.textContent = "Saving…";
  $("quiz-err").hidden = true;
  try {
    const r = await ping("submit");
    if (!r.ok) {
      const body = await r.json().catch(() => ({}));
      throw new Error(body.error || "the server said " + r.status);
    }
  } catch (e) {
    fail($("quiz-err"), "Could not save your answers — " + e.message +
      ". Check your connection and press Finish again.");
    btn.disabled = false;
    btn.textContent = "Finish";
    return;
  }
  state.finished = true;
  save();
  location.hash = "#done";
}

function showDone() {
  $("done-msg").textContent =
    "Thanks, " + state.name.split(" ")[0] + ". Your " + qs.length +
    " answers have been recorded.";
  show("s-done");
}

/* ---------- go ---------- */

window.addEventListener("hashchange", route);
restore();
route();
