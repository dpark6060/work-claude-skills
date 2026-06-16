If you read this file, say "I have read the SDK use rules".

- Trust fw-file and Flywheel SDK library methods rather than adding redundant validation or manual processing.
- Use proper SDK models (e.g., AdhocAnalysisInput) — check SDK source or docs before guessing at types.
- When working with Flywheel gears, always check existing patterns in the codebase for auth, client
  initialization, and metadata handling.
- Before writing any finder/filter query (`fw.<containers>.find()`, `fw.<containers>.find_first()`), read `FinderBehaviors.md` in this directory for quoting rules and known gotchas.

## Investigating an unfamiliar/obscure SDK call (hard-won)
The generated SDK is thin and lies in predictable ways. When digging into a call:
- **Check the installed version first** (`importlib.metadata.version("flywheel-sdk")`) and
  confirm it matches the docs/instance you're working against. Wrappers, models, and
  behavior differ across versions; verifying on the wrong version wastes a whole pass.
- **"Is this endpoint wrapped?" → grep the source for the path string**, e.g.
  `call_api('/bulk/move/sessions'`, not `dir(fw)`/`inspect`. Dynamic delegation hides
  real methods from `dir()`. Every generated wrapper contains its endpoint path
  verbatim in a `call_api(...)`, so grepping paths enumerates the true surface
  regardless of method name. `hasattr` is OK as a secondary check (it fires
  `__getattr__`); calling it live is the only proof.
- **Don't trust declared return/response types or docstrings — verify against the live
  instance.** Observed reality diverging from the declared type is common (a call
  declared to return an object returned a bare `int`; a `jobs=True` inflate flag did
  nothing; a documented enum result came back as a 409 instead). The behavior you
  observe wins over the annotation.
- **Discover valid enum/param values by sending a bogus one and reading the 422** — the
  server usually lists them (`expected: site|group|project|none|null`). Faster than
  hunting the model.
- **Don't extrapolate across sibling endpoints.** Same family, inconsistent contracts:
  one returns a list, the next a `{success, error}` dict; identical body shapes wrapped
  for one resource and not another; params that exist but are unimplemented and 500.
  Verify each one.
- **An empty/"success" response can be a footgun.** Some calls do destructive or
  silent work (relabel, skip, re-parent) and report nothing back. If a write call's
  return doesn't prove what happened, re-fetch and check, or do a dry run first.
- **Some endpoints are device-only** (`upsert_*`): a user key gets
  `403 Invalid session type (user), expected one of (device)`. Note the auth class
  before assuming a user key works.