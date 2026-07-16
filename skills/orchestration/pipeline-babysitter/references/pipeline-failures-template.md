---
type: Template
title: Pipeline Failures Template
name: pipeline-failures-template
description: Templates for creating pipeline_failures/ docs in a gear repo.
tags: [pipeline, template, gear]
timestamp: 2026-07-15T00:00:00Z
---

# Pipeline Failures Template

When a repo has no `pipeline_failures/` directory, create it with these three files.
Replace `<gear-name>` with the project name from `manifest.json`.

---

## pipeline_failures/lint.md

```markdown
# Lint Pipeline Failures — <gear-name>

Known failures for the `lint` stage (`lint:pre-commit` job).
Babysitter: if you encounter a new lint failure not listed here, append an entry
using the template at the bottom.

---

<!-- No known failures yet. Add entries as they are encountered. -->

## Template

\`\`\`markdown
## <hook-name> — <short description>

**Job:** `lint:pre-commit` (<hook name>)
**Symptom in log:**
\`\`\`
<paste the key error lines>
\`\`\`

**Root cause:** <explanation>

**Fix:** <what to change and where>
\`\`\`
```

---

## pipeline_failures/build.md

```markdown
# Build Pipeline Failures — <gear-name>

Known failures for the `build` stage (`test:gear` job).
Babysitter: if you encounter a new build failure not listed here, append an entry
using the template at the bottom.

---

<!-- No known failures yet. Add entries as they are encountered. -->

## Template

\`\`\`markdown
## <short description>

**Job:** `test:gear`
**Symptom in log:**
\`\`\`
<paste the key error lines>
\`\`\`

**Root cause:** <explanation>

**Fix:** <what to change and where>
\`\`\`
```

---

## pipeline_failures/publish.md

```markdown
# Publish Pipeline Failures — <gear-name>

Known failures for the `publish` stage (`publish:docker` job).
Babysitter: if you encounter a new publish failure not listed here, append an entry
using the template at the bottom.

---

<!-- No known failures yet. Add entries as they are encountered. -->

## Template

\`\`\`markdown
## <short description>

**Job:** `publish:docker`
**Symptom in log:**
\`\`\`
<paste the key error lines>
\`\`\`

**Root cause:** <explanation>

**Fix:** <what to change and where>
\`\`\`
```
