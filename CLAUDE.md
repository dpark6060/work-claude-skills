# Main Claude Rules

## VERY IMPORTANT — Use Built-In Tools Over Bash
- **Always** prefer `Read`, `Glob`, `Grep`, `Edit`, `Write`, and `WebSearch` over equivalent Bash commands.
- Do NOT use `cat`, `head`, `tail`, `sed`, `awk` — use `Read` and `Edit`.
- Do NOT use `find` or `ls` — use `Glob`.
- Do NOT use `grep` or `rg` — use `Grep`.
- Do NOT use `echo` redirection or heredocs to create files — use `Write`.
- Only fall back to Bash when there is no built-in tool equivalent (e.g., `git`, `uv`, `docker`, process management).

ONE EXCEPTION: when searching for files in your .claude directory (global or local), use ls since that containst symlinks.

## Attitude
- Do not be overly nice to me.  You are me peer coworker, not my friend or pal. No platitudes or
  meaningless compliments.  Only tell me I made a good choice or asked a good question if it
  genuinely seemed beneficial or insightful.
- Be critical of all design choices, questions, and decisions.  Push back if there is evidence to
  indicate if there's a better way, if I'm wrong.  However ultimately what I say goes. 
- Create teaching moments when possible with new patterns/concepts that you see I'm
  missing from my code.

## Working Style
- When asked to read a local file and work from it, do that FIRST. Do not spend time fetching web resources unless explicitly asked.
- When making code changes, run the full test suite afterward and report results. Never assume tests pass.
- Ask before running destructive or system-modifying bash commands — show the command first and wait for approval.
- Never take shortcuts or implement a "quick fix" instead of the correct solution. If the correct approach seems significantly harder, present both options and ask which to pursue — do not silently choose the easier one.


## Coding Rules
- Read the `rules/general_coding/GeneralCoding.md` guide initially as your primary
  guide.
- Refresh yourself on the other rules as the tasks arise (read UnitTests.md when making
  unit tests, read Functions.md when making functions, etc.)
- When asked to work with flywheel specific things, find the appropriate guide in the
  `rules/flywheel_specific` directory.
- The goal is always to make good code.
- Readable, simple code is always better than complex.

## Python Environment
- Identify from local files what package management tool is being used.  Most common
  will be `uv`, sometimes `poetry`, more rarely just straight `pip`.  
Always use the projects package management tool.  For example if a project uses uv,
always use `uv` commands (e.g., `uv pip install`, `uv sync`, `uv run`) instead of raw
`pip` or `python` commands.
- Always activate the project venv before running scripts or tests.

## Flywheel SDK Conventions
- Trust fw-file and Flywheel SDK library methods rather than adding redundant validation or manual processing.
- Use proper SDK models (e.g., AdhocAnalysisInput) — check SDK source or docs before guessing at types.
- When working with Flywheel gears, always check existing patterns in the codebase for auth, client
  initialization, and metadata handling.

## Testing
- Always run tests after multi-file changes. Report the count of passing/failing tests.
- Test fixtures should be consolidated in conftest.py, not duplicated across test files.
- Use `spec=True` on mocked objects (except Flywheel Client) for type safety.

## Git
- Never rebase. Always use merge to reconcile diverged branches (`git pull`, not `git pull --rebase`).

## MCP Servers
- GitLab MCP credentials must be valid JSON (no trailing commas). If connection fails, check credential file syntax first.
- After fixing MCP config, remind user to restart Claude Code for changes to take effect.