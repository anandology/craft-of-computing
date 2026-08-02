// quizzes/*.yml -> src/quizzes.json
// Runs before deploy, so a typo in the YAML fails here rather than in class.
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { parse } from "yaml";

const SRC = "quizzes";
const OUT = "src/quizzes.json";

const quizzes = {};

for (const file of readdirSync(SRC).filter((f) => /\.ya?ml$/.test(f)).sort()) {
  const slug = basename(file).replace(/\.ya?ml$/, "");
  if (!/^[a-z0-9-]+$/.test(slug)) throw new Error(`${file}: slug must be [a-z0-9-]`);

  const quiz = parse(readFileSync(join(SRC, file), "utf8"));
  if (!quiz?.title) throw new Error(`${file}: missing title`);
  if (!Array.isArray(quiz.questions) || !quiz.questions.length)
    throw new Error(`${file}: needs at least one question`);

  const seen = new Set();
  for (const q of quiz.questions) {
    if (!q.id || !q.q) throw new Error(`${file}: every question needs "id" and "q"`);
    if (seen.has(q.id)) throw new Error(`${file}: duplicate question id "${q.id}"`);
    seen.add(q.id);
    if (q.opts && (!Array.isArray(q.opts) || q.opts.length < 2))
      throw new Error(`${file}: "${q.id}" opts must be a list of 2 or more`);
  }

  quizzes[slug] = { title: quiz.title, questions: quiz.questions };
}

writeFileSync(OUT, JSON.stringify(quizzes, null, 2) + "\n");
console.log(`${OUT}: ${Object.keys(quizzes).length} quizzes (${Object.keys(quizzes).join(", ")})`);
