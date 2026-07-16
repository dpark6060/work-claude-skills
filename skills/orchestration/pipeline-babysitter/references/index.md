# Pipeline Babysitter References

* [Failure Report Template](failure-report-template.md) - Format definition for the failure-report.md written by the babysitter before dispatching to a sub-agent. Sub-agents read this file as their sole source of context.
* [Flywheel Gear Repo Conventions](gear-repo-conventions.md) - Flywheel gear repository structure, pre-commit hooks, CI patterns, and common pipeline failure causes. Load this on first check to understand the repo you're babysitting.
* [Lint & Export Fix](lint-fix.md) - How to fix linting and export failures in a Flywheel gear pipeline. All linting AND requirements/pyproject exports are pre-commit hooks — a single pre-commit run handles everything.
* [Merge Conflict Resolution](conflict-resolve.md) - How to detect, resolve, and push merge conflict fixes. Covers auto-resolve patterns and escalation for uncertain conflicts.
* [Pipeline Babysitter Setup & Permissions](setup-and-permissions.md) - Permissions and directories to pre-approve so the pipeline babysitter loop runs without pausing for approval on every command.
* [Pipeline Failures Template](pipeline-failures-template.md) - Templates for creating pipeline_failures/ docs in a gear repo.
* [Pipeline Status & Failure Classification](pipeline-status.md) - How to check pipeline status, retrieve job logs, and classify failure types.
