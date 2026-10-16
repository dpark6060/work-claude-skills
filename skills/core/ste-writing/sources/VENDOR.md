Vendored ASD-STE100 writing kit

Source: https://github.com/woosal1337/blog/tree/main/videos/ep01-the-cure-for-ai-slop
Upstream commit: 1de95f861304d71f028f7cc6ef3f171bb2c59f05
Vendored: 2026-07-28

Mapping from upstream:
  ste-writing-skill.md          -> ../SKILL.md
  ste-lint.py                   -> ../scripts/ste-lint.py
  README.md                     -> upstream-README.md
  before-after-samples.md       -> before-after-samples.md

Not vendored (removed 2026-10-16): experiment-results.md, experiment-results-openai.md,
run-openai.py. They are the author's experiment data and reproduction script; fetch them
from the upstream commit above if the linter's numbers need re-deriving.

Nothing in this sources/ directory is loaded by the skill. It is kept for provenance.

Refresh with:
  BASE=https://raw.githubusercontent.com/woosal1337/blog/main/videos/ep01-the-cure-for-ai-slop
  curl -sL $BASE/ste-writing-skill.md -o ../SKILL.md
  curl -sL $BASE/ste-lint.py -o ../scripts/ste-lint.py

Note: the upstream skill file has no reference to the linter (they were siblings
in a flat blog folder). If you re-pull SKILL.md, re-add the "Linter" section
pointing at scripts/ste-lint.py.

The ASD-STE100 spec itself is copyrighted and is NOT vendored. Free registration
at https://asd-ste100.org.
