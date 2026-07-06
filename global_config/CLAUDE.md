# Global Claude Rules

## Use Built-In Tools Over Bash
- Prefer `Read`, `Edit`, `Write`, and `WebSearch` over equivalent Bash commands.
- Do NOT use `cat`, `head`, `tail`, `sed`, `awk` — use `Read` and `Edit`.
- Do NOT use `echo` redirection or heredocs to create files — use `Write`.
- Only fall back to Bash when there is no built-in tool equivalent (e.g., `git`, `uv`,
  `docker`, process management).
- Use `find`/`ls` for file discovery and `rg` for content search.

## Writing for Humans (summaries, Slack, reports, PR/MR descriptions)
Write like an engineer typing to a coworker, not like an AI generating a document.
- No AI tells: no em-dashes, no "Here's...", no "Let's dive in", no "In summary", no
  bold-label-colon bullets, no rule-of-three padding, no "Overall, this is solid" wrap-ups.
- Lead with what's broken or surprising. Be concrete — real error strings, status codes,
  field names, observed behavior. Don't hedge ("may", "might") when you tested it and know.
- Default to short. Vary sentence length. Contractions are fine. Only call something good
  if it earns it.

## Working Style
- When asked to read a local file and work from it, do that FIRST. Do not fetch web
  resources unless explicitly asked.
- When making code changes, run the full test suite afterward and report results. Never
  assume tests pass.
- Ask before running destructive or system-modifying bash commands — show the command
  first and wait for approval.
- Never take shortcuts or implement a "quick fix" instead of the correct solution. If the
  correct approach is significantly harder, present both options and ask which to pursue —
  do not silently choose the easier one.

## Python Environment
- Identify the package management tool from local files (`uv`, `poetry`, or `pip`) and
  always use it (e.g., `uv pip install`, `uv sync`, `uv run` for a `uv` project).
- Always activate the project venv before running scripts or tests.

## Testing
- Always run tests after multi-file changes. Report the count of passing/failing tests.
- Consolidate shared fixtures in `conftest.py`, not duplicated across test files.
- Use `spec=True` on mocked objects (except the Flywheel Client) for type safety.

## Flywheel SDK Conventions
- Trust fw-file and Flywheel SDK library methods rather than adding redundant validation
  or manual processing.
- Use proper SDK models (e.g., `AdhocAnalysisInput`) — check SDK source or docs before
  guessing at types.
- When working with Flywheel gears, check existing patterns in the codebase for auth,
  client initialization, and metadata handling.

## Git
- Never rebase. Always use merge to reconcile diverged branches (`git pull`, not
  `git pull --rebase`).
- When creating an MR, sign the description with the model, e.g.:
  `Co-Authored-By: Claude Opus 4.6 (1M context)`.
- Branch names use the format `<TICKET-ID>_<description>` with underscores only — no
  forward slashes. Example: `GEAR-12042_config-parsing`.
