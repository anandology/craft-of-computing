CREATE TABLE IF NOT EXISTS votes (
  quiz   TEXT NOT NULL,
  voter  TEXT NOT NULL,
  qid    TEXT NOT NULL,
  answer TEXT NOT NULL,
  PRIMARY KEY (quiz, voter, qid)
);

CREATE INDEX IF NOT EXISTS votes_quiz ON votes (quiz);
