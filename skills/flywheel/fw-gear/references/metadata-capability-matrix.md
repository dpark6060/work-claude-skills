---
type: Library Reference
title: fw-gear Metadata Capability Matrix
description: What context.metadata can and cannot write in fw-gear 0.3.1 — the api-key requirement, the destination-and-up hierarchy rule, and a per-field file-vs-container matrix.
tags: [fw-gear, metadata, tags, qc, hierarchy, api-key]
timestamp: 2026-07-23T00:00:00Z
---

# fw-gear Metadata Capability Matrix

Quick-reference for deciding, before you write a gear, whether `context.metadata`
(the `.metadata.json` writer) can do what you need — or whether you're forced to the
SDK. All findings verified against **fw-gear 0.3.1** (source read + live probe).

For the how-to (method signatures, examples), see [gear-metadata.md](gear-metadata.md).

## The open question: does `context.metadata` need an `api-key`? (UNRESOLVED)

**Status: code and docs contradict each other; needs a live engine run to settle.
Do NOT treat "requires api-key" as fact.**

The source path says yes: all six write methods — `update_container`,
`update_file_metadata`, `add_file_tags`, `add_qc_result`, `add_qc_result_to_analysis`,
`update_zip_member_count` — funnel through `_validate_container_type`, which resolves the
real destination via `config.get_destination_container()` (or `get_destination_parent()`
for analysis). In the source that call raises when there's no client:

```
RuntimeError: Config.get_destination_container: Requires authenticated API key.
Please add `api-key` input to your manifest
```

And `get_client()` sources a client **only** from an `api-key` input — there is no
env-var / CLI-cred / ambient path anywhere in the package. So by the code, no api-key
input → `context.client is None` → the write raises before touching `.metadata.json`.

But the fw-gear docs say no: `getting_started.md` puts `update_container` and
`add_qc_result` under **"Adding Metadata" with no api-key input**, and presents
`context.client` as a **separate** "Using the SDK Client" pattern that "requires api-key
input." The documented intent is that metadata writes are keyless.

Evidence from the repo (verified against main @ 0.3.9-dev + release notes):
- The strict validation was **added in fw-gear 0.3.0** ("Metadata class now validates
  container types more strictly"); legacy `flywheel-gear-toolkit` had none, which is why
  keyless `.metadata.json` always worked before.
- The `get_destination_container()` call in the validator is **still present unchanged**
  on main and every release through 0.3.7 — no fix, no rollback of it.

Two ways this resolves, only distinguishable on a real engine run:
1. The engine supplies a client for destination resolution even without an api-key input
   → docs right, keyless works.
2. It doesn't → the 0.3.0 validation quietly broke the keyless path → you get the
   RuntimeError above.

**Cannot be reproduced locally** — `get_destination_container()` is a live API call, so a
local run fails for lack of a server regardless. **Resolve it by running the gear on the
engine with no api-key input, writing a tag/QC result, and reading the job log for
`Requires authenticated API key`.** Until confirmed, the safe default for a
metadata-writing gear is to include the `api-key` input — but don't design around it as
settled fact.

Key-free escape hatch if the RuntimeError turns out real: hand-write `.metadata.json`
into the output dir with plain `json.dump`. The engine still ingests it; you skip the
helpers and enforce the hierarchy rule yourself.

## Directional rule: destination and UP, never down

`.metadata.json` reaches the gear's **destination container and everything above it**.
Never a child.

```
project            ▲  reachable (parent, up)
└─ subject         │  reachable (parent, up)
   └─ session      │  reachable (parent, up)
      └─ acquisition  ★ DESTINATION — reachable (this level + its files)
         └─ (anything below the destination) ✗ NOT reachable via .metadata.json
```

The destination level for a file-triggered gear is set by which file/container is
selected **first** at launch. Misclicking a higher-level file pins the destination
above where you meant, and the intended target becomes an unreachable child:

```
ValueError: Container type acquisition is outside the hierarchy that can be
updated via .metadata.json
```

## Where can you write? (target × mechanism)

| Target relative to destination | `context.metadata` (`.metadata.json`) | SDK (`context.client`) |
|---|---|---|
| **Destination level** (+ its files) | ✅ allowed — api-key maybe required (see open question) | ✅ api-key required |
| **Above** (session/subject/project + files) | ✅ allowed — api-key maybe required | ✅ api-key required |
| **Below** (child acquisition, etc.) | ❌ `ValueError`, never allowed | ✅ api-key required |
| **Outside the hierarchy** (other subjects/projects) | ❌ never allowed | ✅ api-key required |

Writing **output files** to `/flywheel/v0/output/` is the one operation that is
unambiguously key-free — but that's saving files, not writing metadata.

## What can you write? (field × target)

Derived from `engine_metadata_schema.json` (the schema the validator enforces) plus the
method surface.

| Item | On a **file** | On a **container** | Method / notes |
|---|---|---|---|
| **tags** | ✅ | ✅ *(not subject)* | file: `add_file_tags` (reads + unions existing). container: `update_container(tags=[...])` (overwrites, no union). No `tags` field on the subject schema. |
| **info** (custom metadata) | ✅ | ✅ | `update_file_metadata(info={...})` / `update_container(info={...})`. Deep-merges by default. |
| **QC results** (`info.qc.<gear>`) | ✅ | analysis only | `add_qc_result` (file), `add_qc_result_to_analysis`. On a normal acq/session container, write plain `info` instead. |
| **modality** | ✅ | ❌ | File-only field. |
| **classification** | ✅ | ❌ | File-only. |
| **type / mimetype** | ✅ | ❌ | File-only. |
| **zip_member_count** | ✅ | ❌ | `update_zip_member_count`. |
| **label** | ❌ | ✅ | Container-only (`update_container(label=...)`). |
| **timestamp / timezone** | ❌ | ✅ *(session, acq, analysis)* | Container-only. Not on subject/project. |
| **measurement** | ❌ | ✅ *(acquisition only)* | `update_container("acquisition", measurement=...)`. |
| **uid** | ❌ | ✅ *(session, acquisition)* | |
| **demographics** (age, weight, sex, race, ethnicity, first/lastname, code) | ❌ | ✅ *(subject/session)* | Schema-constrained (e.g. `sex` ∈ `male\|female\|other\|unknown`). |
| **notes** | ❌ | ❌ | No `notes` field in the schema anywhere — SDK only. |
| **files/attachments** (upload a new file) | — | — | Not a metadata op. Put the file in `/flywheel/v0/output/`; the metadata entry only annotates a file that exists. |

## Three caveats that bite

1. **The api-key question above applies to all of these.** Whether a field is writable
   is separate from whether the write needs a client — see the unresolved api-key
   question at the top of this file.
2. **Writes are additive, not destructive.** `deep=True` (default) merges; `add_file_tags`
   only unions. There is **no primitive to remove a single tag or clear one info key**.
   `deep=False` overwrites the *entire* subdict wholesale, not one key. Targeted deletes
   need the SDK.
3. **File fields are a closed set** (`additionalProperties: false` on the file schema) —
   an unknown/typo'd file field fails validation. Container fields are looser: unknown
   keys are silently ignored, so a misspelled `tag` (vs `tags`) just vanishes with no
   error.
