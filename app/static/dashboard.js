/* Live progress for one quiz. Polls the server; holds no state of its own
   beyond the last payload, so leaving it open all class costs nothing. */

const POLL_MS = 2000;
const IDLE_MS = 3 * 60 * 1000;
const STALE_MS = 15 * 1000;

const $ = id => document.getElementById(id);
let latest = null;
let lastUpdate = 0;

function ago(t) {
  const s = Math.round((Date.now() - t) / 1000);
  if (s < 60) return s + " s ago";
  return Math.round(s / 60) + " min ago";
}

async function poll() {
  try {
    const r = await fetch(PROGRESS_URL, { cache: "no-store" });
    if (!r.ok) throw new Error(r.status);
    latest = await r.json();
    lastUpdate = Date.now();
    draw(latest);
  } catch (e) {
    // Leave the last good picture on screen; the stamp says it has gone stale.
  }
  stamp();
}

function stamp() {
  const el = $("stamp");
  if (!lastUpdate) { el.textContent = "updating…"; return; }
  const stale = Date.now() - lastUpdate > STALE_MS;
  el.classList.toggle("stale", stale);
  el.textContent = stale ? "no update for " + ago(lastUpdate) : "updated just now";
}

function draw(data) {
  const students = data.students || [];
  const nq = data.questions;
  const now = Date.now();
  const seen = s => Date.parse(s.last_seen) || 0;

  const started = students.length;
  const done = students.filter(s => s.finished).length;
  const idle = students.filter(s => !s.finished && now - seen(s) > IDLE_MS).length;

  $("m-started").textContent = started;
  $("m-started-sub").textContent = data.roll ? "of " + data.roll + " on the roll" : "";
  $("m-done").textContent = done;
  $("m-done-sub").textContent = started
    ? Math.round(done / started * 100) + "% of those started"
    : "";
  $("m-idle").textContent = idle;
  // Amber only when there is actually someone to go and help.
  $("m-idle").parentElement.classList.toggle("alert", idle > 0);

  /* how many students are past each question */
  const bars = $("qbars");
  bars.innerHTML = "";
  for (let q = 1; q <= nq; q++) {
    const n = students.filter(s => s.answered >= q).length;
    const pct = started ? Math.round(n / started * 100) : 0;
    const row = document.createElement("div");
    row.className = "qrow";
    row.innerHTML =
      '<span class="qid">Q' + q + '</span>' +
      '<span class="track"><span style="width:' + pct + '%"></span></span>' +
      '<span class="num">' + n + ' · ' + pct + '%</span>';
    bars.appendChild(row);
  }

  /* finished, then most recently active, then whoever has gone quiet */
  const finished = students.filter(s => s.finished).sort((a, b) => seen(b) - seen(a));
  const rest = students.filter(s => !s.finished);
  const active = rest.filter(s => now - seen(s) <= IDLE_MS).sort((a, b) => seen(b) - seen(a));
  const stuck = rest.filter(s => now - seen(s) > IDLE_MS).sort((a, b) => seen(a) - seen(b));

  const box = $("rows");
  box.innerHTML = "";
  finished.forEach(s => box.appendChild(rowEl(s, nq, "done", "✓")));
  active.forEach(s => box.appendChild(rowEl(s, nq, "", "")));
  stuck.forEach(s => box.appendChild(rowEl(s, nq, "idle", "◷")));
  $("empty").hidden = started > 0;
}

function rowEl(s, nq, cls, mark) {
  const el = document.createElement("div");
  el.className = "row " + cls;
  const pct = nq ? Math.round(s.answered / nq * 100) : 0;
  el.innerHTML =
    '<span class="mark">' + mark + '</span>' +
    '<span class="who"><span class="name"></span><span class="mail"></span></span>' +
    '<span class="seen">' + ago(Date.parse(s.last_seen) || Date.now()) + '</span>' +
    '<span class="meter"><span style="width:' + pct + '%"></span></span>' +
    '<span class="score">' + s.answered + '/' + nq + '</span>';
  // Names and emails are typed by students, so they go in as text, never HTML.
  el.querySelector(".name").textContent = s.name;
  el.querySelector(".mail").textContent = s.email;
  return el;
}

poll();
setInterval(poll, POLL_MS);
setInterval(stamp, 1000);
