---
name: ste-writing
description: Rewrite prose (docs, READMEs, PR descriptions, error messages, release notes, comments — never code) into ASD-STE100 Simplified Technical English to remove "AI slop". Use when asked to make writing not sound like AI, make docs clear or plain, enforce a controlled writing style, or write technical documentation that reads human. Two modes — strict (procedures/safety) and STE-flavored (general prose).
---

# ste-writing

Write prose in ASD-STE100 Simplified Technical English. This applies to documentation, READMEs, pull-request text, error messages, release notes, and comments. It does not apply to code, identifiers, or command syntax. It is not for marketing copy, essays, or anything that needs a voice — STE strips voice on purpose.

## Rules

WORDS
- Use one name for one thing. Do not call the same item by two different names.
- Use the short common word: start (not begin/commence/initiate), use (not utilize/leverage), help (not facilitate), make sure (not ensure), before (not prior to), after (not subsequent to), about (not regarding/concerning), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover).
- Give each word one meaning. "fall" means to move down, not to decrease.
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- American spelling.

VERBS
- Active voice. "the parser reads the file", not "the file is read by the parser".
- Use a verb for an action. "analyze the log", not "perform an analysis of the log".
- No stacked auxiliaries. Not "it is important to note that this may help to improve". Write "this improves X".
- No "-ing" main verb where a simple tense works.
- No phrasal verbs ("spin up", "set up" as a verb) where a single verb exists.

SENTENCES
- One instruction per sentence. Max 20 words (instruction), max 25 (descriptive).
- No contractions. Use articles: a, an, the, this, these.

PUNCTUATION
- No semicolons. Write two sentences. (Note: the em dash is not banned by STE, only the semicolon is — add "no em dash" yourself if you want it gone.)

STRUCTURE
- One topic per paragraph, max six sentences. For steps, use a numbered vertical list, one action per item, imperative form. Put a condition before its command.

Write only the requested text. No preamble, no summary, no closing remarks.

## Modes

- **strict** — procedures, runbooks, safety text, error messages. Apply every rule and both
  length caps. Use only words from the ASD-STE100 dictionary (Issue 8, Part 2; about 900
  approved words), each in its approved meaning, plus the technical names and technical verbs
  the domain needs (STE Rules 1.5 and 1.12).
- **STE-flavored** — general prose (READMEs, PR descriptions, docs). Apply the sentence,
  paragraph, active-voice, and no-phrasal-verb rules. The dictionary is not enforced, so the text
  keeps enough range to read naturally, and contractions are allowed.

## Linter

`scripts/ste-lint.py` checks the mechanical subset. Python 3, no dependencies.

```
python3 scripts/ste-lint.py draft.md          # one or more files, or a glob
python3 scripts/ste-lint.py < draft.md        # stdin, returns full JSON
```

The score is violations per 100 words. Lower is cleaner. Lint the draft, apply this skill, lint again. The delta is the signal, not the absolute number. Em dashes are counted and reported separately because STE does not ban them.

Free official standard (do not paste it in full; it is copyrighted): https://asd-ste100.org
