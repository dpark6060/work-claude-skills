---
type: Code Manifest
title: "Flywheel code index — provenance"
description: "Provenance for the code index — source repos, commit SHAs, card counts, and how to regenerate."
tags: [flywheel, code-index, provenance]
timestamp: 2026-07-15T00:00:00Z
---
# Flywheel code index — provenance

Total cards: **487**. Ground-truth source/template snippets, no LLM paraphrase.

| Repo | Commit | Cards |
| --- | --- | --- |
| bids-client | 0e08b4a (1.2.34) | 457 |
| curate-bids | d140625 (2.2.19_1.2.34-4-gd140625) | 18 |
| relabel-container | 7fea0e8 (0.6.1) | 12 |

## Regenerate (latest repo versions)

```bash
python scripts/build_code_index.py --pull
```

Search it with `python scripts/search_code.py "<query>"`.
