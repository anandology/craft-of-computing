/// <reference types="@cloudflare/workers-types" />

// Quizzes come from quizzes/*.yml via scripts/build.mjs. Filename is the slug:
// quizzes/q0.yml -> /q0 to vote, /q0/results to watch.
import quizzes from "./quizzes.json";
import qrcode from "qrcode-generator";

type Question = { id: string; q: string; opts?: string[] };
type Quiz = { title: string; questions: Question[] };

const QUIZZES = quizzes as Record<string, Quiz>;
const MAX_ANSWER = 64;

export interface Env {
  DB: D1Database;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname.replace(/\/+$/, "");
    if (path === "") return page(indexPage());

    const [slug, action] = path.slice(1).split("/");
    const quiz = QUIZZES[slug];
    if (!quiz) return notFound();

    if (!action && req.method === "GET") return page(votePage(slug, quiz));
    if (action === "vote" && req.method === "POST") return vote(req, env, slug, quiz);
    if (action === "mine" && req.method === "GET")
      return mine(env, slug, url.searchParams.get("voter") ?? "");
    if (action === "results" && req.method === "GET") return page(resultsPage(slug, quiz));
    if (action === "slide" && req.method === "GET")
      return page(slidePage(slug, quiz, url.origin, url.searchParams.get("q") ?? undefined));
    if (action === "results.json" && req.method === "GET") return results(env, slug);

    return notFound();
  },
};

// --- handlers --------------------------------------------------------------

async function vote(req: Request, env: Env, slug: string, quiz: Quiz): Promise<Response> {
  let body: any;
  try {
    body = await req.json();
  } catch {
    return json({ error: "bad json" }, 400);
  }

  // Voter id is a UUID minted in the browser and kept in localStorage, so
  // resubmitting replaces the earlier answers instead of double-counting.
  const voter = String(body?.voter ?? "");
  if (!/^[0-9a-f-]{36}$/i.test(voter)) return json({ error: "bad voter" }, 400);

  const answers = body?.answers ?? {};
  const stmt = env.DB.prepare(
    "INSERT OR REPLACE INTO votes (quiz, voter, qid, answer) VALUES (?, ?, ?, ?)"
  );

  const batch: D1PreparedStatement[] = [];
  for (const q of quiz.questions) {
    const raw = answers[q.id];
    if (typeof raw !== "string") continue;
    const a = raw.trim().replace(/\s+/g, " ").slice(0, MAX_ANSWER);
    if (!a) continue;
    if (q.opts && !q.opts.includes(a)) continue; // ignore anything not offered
    batch.push(stmt.bind(slug, voter, q.id, a));
  }
  if (batch.length) await env.DB.batch(batch);

  return json({ ok: true, saved: batch.length });
}

// One voter's own answers, so reopening the page shows what they already said.
// The voter id is an unguessable UUID that never leaves their browser, which is
// all that keeps this from being a way to read someone else's answers.
async function mine(env: Env, slug: string, voter: string): Promise<Response> {
  if (!/^[0-9a-f-]{36}$/i.test(voter)) return json({ answers: {} });

  const { results: rows } = await env.DB.prepare(
    "SELECT qid, answer FROM votes WHERE quiz = ? AND voter = ?"
  )
    .bind(slug, voter)
    .all<{ qid: string; answer: string }>();

  const answers: Record<string, string> = {};
  for (const r of rows ?? []) answers[r.qid] = r.answer;
  return json({ answers });
}

async function results(env: Env, slug: string): Promise<Response> {
  // Group case-insensitively so "Telugu" and "telugu" land in one bucket.
  const { results: rows } = await env.DB.prepare(
    `SELECT qid, LOWER(answer) AS answer, COUNT(*) AS n
       FROM votes WHERE quiz = ?
      GROUP BY qid, LOWER(answer)
      ORDER BY n DESC`
  )
    .bind(slug)
    .all<{ qid: string; answer: string; n: number }>();

  const total = await env.DB.prepare(
    `SELECT COUNT(DISTINCT voter) AS n FROM votes WHERE quiz = ?`
  )
    .bind(slug)
    .first<{ n: number }>();

  const counts: Record<string, { answer: string; n: number }[]> = {};
  for (const r of rows ?? []) (counts[r.qid] ??= []).push({ answer: r.answer, n: r.n });

  return json({ voters: total?.n ?? 0, counts });
}

// --- responses -------------------------------------------------------------

const page = (body: string) =>
  new Response(body, {
    headers: { "content-type": "text/html;charset=utf-8", "cache-control": "no-store" },
  });

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });

const notFound = () => new Response("Not found", { status: 404 });

// Safe to drop inside a <script> tag.
const embed = (data: unknown) =>
  JSON.stringify(data).replace(/</g, "\\u003c").replace(/>/g, "\\u003e");

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// --- pages -----------------------------------------------------------------

const CSS = `
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font: 17px/1.5 system-ui, sans-serif; margin: 0 auto; padding: 24px 20px 64px;
       max-width: 760px; }
h1 { font-size: 1.4rem; margin: 0 0 4px; }
h2 { font-size: 1.05rem; font-weight: 600; margin: 0 0 12px; }
.q { margin: 28px 0 0; }
input[type=text] { width: 100%; padding: 12px; font: inherit; border-radius: 8px;
                   border: 1px solid color-mix(in srgb, currentColor 30%, transparent);
                   background: transparent; color: inherit; }
label { display: flex; gap: 10px; align-items: center; padding: 11px 12px; cursor: pointer;
        border-radius: 8px; margin-bottom: 6px;
        border: 1px solid color-mix(in srgb, currentColor 20%, transparent); }
label:has(:checked) { border-color: #4f7cff; background: color-mix(in srgb, #4f7cff 12%, transparent); }
button { font: inherit; font-weight: 600; padding: 14px 28px; width: 100%; cursor: pointer;
         margin-top: 28px; border: 0; border-radius: 8px; background: #4f7cff; color: #fff; }
button:disabled { opacity: .45; cursor: default; }
.progress { height: 4px; border-radius: 2px; margin: 16px 0 8px;
            background: color-mix(in srgb, currentColor 15%, transparent); }
.progress i { display: block; height: 100%; width: 0; border-radius: 2px;
              background: #4f7cff; transition: width .3s ease; }
.nav { display: flex; gap: 10px; }
.nav button { flex: 1; }
.nav button.sec { flex: 0 0 auto; width: auto; padding: 14px 20px; background: transparent;
                  color: inherit; border: 1px solid color-mix(in srgb, currentColor 25%, transparent); }
.status { min-height: 1.3em; font-size: .8rem; opacity: .55; margin: 12px 0 0; }
.review { list-style: none; padding: 0; margin: 0; }
.review li { display: flex; justify-content: space-between; gap: 16px; padding: 12px 0;
             border-bottom: 1px solid color-mix(in srgb, currentColor 12%, transparent); }
.review b { font-weight: 600; text-align: right; }
.review button { width: auto; margin: 0; padding: 4px 0; background: none; color: #4f7cff;
                 font-size: .85rem; font-weight: 500; }
.bar { display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: center;
       margin-bottom: 7px; }
.bar span { position: relative; padding: 8px 10px; border-radius: 6px; z-index: 1;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar span::before { content: ""; position: absolute; inset: 0 auto 0 0; z-index: -1;
                    width: var(--w, 0%); background: color-mix(in srgb, #4f7cff 35%, transparent);
                    border-radius: 6px; transition: width .4s ease; }
.bar b { font-variant-numeric: tabular-nums; opacity: .7; font-weight: 600; }
.muted { opacity: .6; font-size: .85rem; margin: 0 0 8px; }
a { color: #4f7cff; }

/* --- slide: results at 2/3, join panel at 1/3, sized for a projector --- */
body:has(.slide) { max-width: none; padding: 0; height: 100vh; overflow: hidden; }
.slide { display: grid; grid-template-columns: 2fr 1fr; height: 100vh; }
.panel { padding: 3.5vh 3vw; overflow: hidden;
         display: flex; flex-direction: column; justify-content: center; }
.panel h1 { font-size: clamp(1.5rem, 2.6vw, 3rem); margin: 0 0 3vh; }
.panel .q { margin: 0 0 3.2vh; }
.panel h2 { font-size: clamp(1rem, 1.5vw, 1.9rem); margin: 0 0 1.4vh; opacity: .75;
            font-weight: 500; }
/* Counts sit in text ink beside the bar, so identity never rests on the fill. */
.panel .bar { margin-bottom: .9vh; gap: 1.2vw; }
.panel .bar span { padding: .9vh 1vw; font-size: clamp(.95rem, 1.5vw, 1.9rem); }
.panel .bar span::before { background: color-mix(in srgb, #4f7cff 42%, transparent); }
.panel .bar b { font-size: clamp(.95rem, 1.5vw, 1.9rem); opacity: .85; }

.join { display: flex; flex-direction: column; align-items: center; justify-content: center;
        gap: 2.5vh; padding: 3vh 2vw;
        background: color-mix(in srgb, currentColor 6%, transparent);
        border-left: 1px solid color-mix(in srgb, currentColor 12%, transparent); }
.join .qr { background: #fff; padding: 1.4vh; border-radius: 12px; line-height: 0;
            box-shadow: 0 2px 16px rgb(0 0 0 / .14); }
.join .qr svg { width: min(22vw, 34vh); height: auto; display: block; }
.join .url { margin: 0; font-size: clamp(.9rem, 1.35vw, 1.7rem); font-weight: 600;
             text-align: center; overflow-wrap: anywhere; }
.join .count { margin: 0; font-size: clamp(1.6rem, 3.4vw, 4rem); font-weight: 700;
               line-height: 1; }
.join .count small { display: block; font-size: clamp(.7rem, 1vw, 1.1rem); font-weight: 500;
                     opacity: .55; margin-top: .6vh; letter-spacing: .04em;
                     text-transform: uppercase; }

/* Recessive: the room is looking at the bars, not at the controls.
   Not .nav — that class already belongs to the vote page's stepper. */
.join .step { display: flex; align-items: center; gap: 1.2vw; opacity: .55; line-height: 1; }
.join .step:hover { opacity: 1; }
.join .step button { font: inherit; line-height: 1; cursor: pointer; width: auto;
                     margin: 0;  /* the global button rule carries a 28px top margin */
                     font-size: clamp(1.1rem, 1.8vw, 2.2rem); padding: .2em .5em;
                     color: inherit; background: none; border-radius: 8px;
                     border: 1px solid color-mix(in srgb, currentColor 22%, transparent); }
.join .step #pos { font-size: clamp(.75rem, 1.1vw, 1.2rem); font-variant-numeric: tabular-nums;
                   letter-spacing: .04em; }

/* Stacks if the slide is ever opened on a phone. */
@media (max-width: 700px) {
  .slide { grid-template-columns: 1fr; grid-template-rows: 1fr auto; }
  .join { border-left: 0; border-top: 1px solid color-mix(in srgb, currentColor 12%, transparent);
          flex-direction: row; gap: 4vw; }
}
`;

const shell = (title: string, body: string, script = "") => `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title><style>${CSS}</style></head>
<body>${body}${script ? `<script>${script}</script>` : ""}</body></html>`;

function indexPage(): string {
  const items = Object.entries(QUIZZES)
    .map(
      ([slug, q]) =>
        `<li><a href="/${slug}">${esc(q.title)}</a> &middot; ` +
        `<a class="muted" href="/${slug}/results">results</a></li>`
    )
    .join("");
  return shell("Quiz", `<h1>Quiz</h1><ul>${items}</ul>`);
}

function votePage(slug: string, quiz: Quiz): string {
  const body = `<h1>${esc(quiz.title)}</h1>
<div class="progress"><i id="pbar"></i></div>
<p class="muted" id="step">&nbsp;</p>
<div id="app"></div>
<p class="status" id="status"></p>`;

  const script = `
const QUIZ = ${embed(quiz.questions)};
const app = document.getElementById("app");
const pbar = document.getElementById("pbar");
const step = document.getElementById("step");
const status = document.getElementById("status");

let voter = localStorage.getItem("voter");
if (!voter) { voter = crypto.randomUUID(); localStorage.setItem("voter", voter); }

const answers = {};   // qid -> answer, mirrored from the server on load
let i = 0;

// Each answer is saved on its own the moment it is given, so a student who
// wanders off midway still counts for the questions they did answer.
let pending = 0;
async function save(qid, value) {
  if (answers[qid] === value) return;
  answers[qid] = value;
  pending++;
  status.textContent = "Saving\\u2026";
  const one = {}; one[qid] = value;
  try {
    const r = await fetch("/${slug}/vote", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ voter, answers: one }),
    });
    if (!r.ok) throw new Error();
    if (--pending === 0) {
      status.textContent = "Saved";
      setTimeout(() => { if (status.textContent === "Saved") status.textContent = ""; }, 1500);
    }
  } catch {
    pending--;
    status.textContent = "Couldn't save \\u2014 check your connection";
  }
}

function progress(done) {
  pbar.style.width = (done / QUIZ.length) * 100 + "%";
  step.textContent = done < QUIZ.length ? "Question " + (done + 1) + " of " + QUIZ.length : "";
}

function go(n) { i = Math.max(0, Math.min(QUIZ.length, n)); render(); }

function render() {
  if (i >= QUIZ.length) return review();
  const q = QUIZ[i];
  progress(i);

  const wrap = document.createElement("div");
  const h = document.createElement("h2"); h.textContent = q.q; wrap.append(h);

  let read;
  if (q.opts) {
    for (const o of q.opts) {
      const l = document.createElement("label");
      const input = document.createElement("input");
      input.type = "radio"; input.name = q.id; input.value = o;
      input.checked = answers[q.id] === o;
      // Picking an option advances on its own, Typeform style.
      input.onchange = () => { save(q.id, o); setTimeout(() => go(i + 1), 250); };
      const s = document.createElement("span"); s.textContent = o;
      l.append(input, s); wrap.append(l);
    }
    read = () => (wrap.querySelector("input:checked") || {}).value || "";
  } else {
    const input = document.createElement("input");
    input.type = "text"; input.maxLength = ${MAX_ANSWER}; input.autocomplete = "off";
    input.value = answers[q.id] || "";
    input.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); next(); } };
    wrap.append(input);
    read = () => input.value;
    setTimeout(() => input.focus(), 0);
  }

  function next() {
    const v = read().trim();
    if (v) save(q.id, v);
    go(i + 1);
  }

  const nav = document.createElement("div"); nav.className = "nav";
  const back = document.createElement("button");
  back.type = "button"; back.className = "sec"; back.textContent = "Back";
  back.disabled = i === 0;
  back.onclick = () => { const v = read().trim(); if (v) save(q.id, v); go(i - 1); };
  const fwd = document.createElement("button");
  fwd.type = "button";
  fwd.textContent = i === QUIZ.length - 1 ? "Done" : "Next";
  fwd.onclick = next;
  nav.append(back, fwd);
  wrap.append(nav);

  app.replaceChildren(wrap);
}

function review() {
  progress(QUIZ.length);
  const wrap = document.createElement("div");
  const h = document.createElement("h2");
  h.textContent = "That's everything \\u2014 thanks!";
  wrap.append(h);

  const ul = document.createElement("ul"); ul.className = "review";
  QUIZ.forEach((q, n) => {
    const li = document.createElement("li");
    const left = document.createElement("div");
    const t = document.createElement("div"); t.textContent = q.q;
    const edit = document.createElement("button");
    edit.type = "button"; edit.textContent = "Change";
    edit.onclick = () => go(n);
    left.append(t, edit);
    const b = document.createElement("b");
    b.textContent = answers[q.id] || "\\u2014";
    li.append(left, b); ul.append(li);
  });
  wrap.append(ul);

  const p = document.createElement("p"); p.className = "muted";
  p.style.marginTop = "20px";
  p.append("Your answers are saved. ");
  const a = document.createElement("a");
  a.href = "/${slug}/results"; a.textContent = "See the results";
  p.append(a);
  wrap.append(p);

  app.replaceChildren(wrap);
}

// Load whatever this voter said before, then open at the first gap.
(async () => {
  try {
    const r = await fetch("/${slug}/mine?voter=" + encodeURIComponent(voter));
    Object.assign(answers, (await r.json()).answers || {});
  } catch { /* offline: start empty rather than block */ }
  const gap = QUIZ.findIndex((q) => !answers[q.id]);
  go(gap === -1 ? QUIZ.length : gap);
})();`;
  return shell(quiz.title, body, script);
}

function resultsPage(slug: string, quiz: Quiz): string {
  const body = `<h1>${esc(quiz.title)}</h1>
<p class="muted"><span id="n">0</span> responses &middot; answer at <b>/${slug}</b></p>
<div id="out"></div>`;
  return shell(quiz.title + " — results", body, pollScript(slug, quiz.questions));
}

// Shared by the results page and the slide: fills #out with a section per
// question and #n with the response count, re-polling every two seconds.
// `start` turns on the slide's stepper: every question is rendered and polled,
// but only one is visible at a time. -1 shows them all.
function pollScript(slug: string, questions: Question[], start = -1): string {
  return `
const QUIZ = ${embed(questions)};
const out = document.getElementById("out");
let cur = ${start};

function show() {
  if (cur < 0) return;
  [...out.children].forEach((el, i) => { el.hidden = i !== cur; });
  document.getElementById("pos").textContent = (cur + 1) + " / " + QUIZ.length;
}
// Clamped, not wrapping: a presenter's clicker should stop at the last question
// rather than silently jump back to the first.
function move(d) { cur = Math.max(0, Math.min(QUIZ.length - 1, cur + d)); show(); }

function bar(label, n, max, cap) {
  const d = document.createElement("div"); d.className = "bar";
  const s = document.createElement("span");
  s.textContent = label;
  // Free text is grouped lowercased; restore capitals for the projector.
  if (cap) s.style.textTransform = "capitalize";
  s.style.setProperty("--w", (max ? (n / max) * 100 : 0) + "%");
  const b = document.createElement("b"); b.textContent = n;
  d.append(s, b); return d;
}

async function tick() {
  let data;
  try { data = await (await fetch("/${slug}/results.json")).json(); }
  catch { return; }  // a dropped poll is not worth showing an error for
  document.getElementById("n").textContent = data.voters;

  const frag = document.createDocumentFragment();
  for (const q of QUIZ) {
    const rows = data.counts[q.id] || [];
    const by = new Map(rows.map((x) => [x.answer, x.n]));
    // Declared order for fixed options, so scales stay in order rather than
    // being resorted by popularity. Free text ranks by count.
    const items = q.opts
      ? q.opts.map((o) => [o, by.get(o.toLowerCase()) || 0])
      : rows.slice(0, 10).map((x) => [x.answer, x.n]);
    const max = Math.max(1, ...items.map((i) => i[1]));

    const sec = document.createElement("div"); sec.className = "q";
    const h = document.createElement("h2"); h.textContent = q.q; sec.append(h);
    if (items.length) {
      for (const [label, n] of items) sec.append(bar(label, n, max, !q.opts));
    } else {
      const p = document.createElement("p"); p.className = "muted";
      p.textContent = "No answers yet."; sec.append(p);
    }
    frag.append(sec);
  }
  out.replaceChildren(frag);
  show();  // sections are rebuilt each poll, so re-apply which one is visible
}

if (cur >= 0) {
  document.getElementById("prev").onclick = () => move(-1);
  document.getElementById("next").onclick = () => move(1);
  // A presentation clicker sends arrows or page keys; take both.
  addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") move(1);
    else if (e.key === "ArrowLeft" || e.key === "PageUp") move(-1);
  });
}

tick(); setInterval(tick, 2000);`;
}

// Dark modules on a forced-white card: a QR inverted or tinted by the page
// theme is unreliable on some scanners, and this one is read from across a room.
function qrSvg(text: string): string {
  const qr = qrcode(0, "M");
  qr.addData(text);
  qr.make();
  const n = qr.getModuleCount();
  let d = "";
  for (let r = 0; r < n; r++)
    for (let c = 0; c < n; c++)
      if (qr.isDark(r, c)) d += `M${c} ${r}h1v1h-1z`;
  return `<svg viewBox="0 0 ${n} ${n}" shape-rendering="crispEdges" aria-hidden="true">
<path d="${d}" fill="#000"/></svg>`;
}

// One question fills a slide; four get clipped at 16:9. So the slide polls the
// whole quiz but shows one question, stepped with the arrows or a clicker.
// `?q=<id>` opens at that question, `?q=all` puts them all on one slide.
function slidePage(slug: string, quiz: Quiz, origin: string, only?: string): string {
  const all = only === "all";
  const found = only && !all ? quiz.questions.findIndex((q) => q.id === only) : 0;
  const at = Math.max(0, found);  // an unknown ?q= just opens at the first
  const url = origin + "/" + slug;
  const shown = url.replace(/^https?:\/\//, "");
  const stepped = !all && quiz.questions.length > 1;

  const body = `<div class="slide">
  <div class="panel">
    <h1>${esc(quiz.title)}</h1>
    <div id="out"></div>
  </div>
  <aside class="join">
    <div class="qr">${qrSvg(url)}</div>
    <p class="url">${esc(shown)}</p>
    <p class="count"><span id="n">0</span> <small>responses</small></p>
    ${stepped
      ? `<nav class="step">
      <button id="prev" aria-label="Previous question">&lsaquo;</button>
      <span id="pos"></span>
      <button id="next" aria-label="Next question">&rsaquo;</button>
    </nav>`
      : ""}
  </aside>
</div>`;
  return shell(quiz.title + " — slide", body, pollScript(slug, quiz.questions, stepped ? at : -1));
}

