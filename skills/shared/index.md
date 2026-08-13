# Shared References

* [Architecture Plan Format](plan_format.md) - Canonical template for architecture plan files produced by code-architect and change-planner and consumed by code-architect-reviewer.
* [Claude Skills Best Practices](claude-skills-best-practices.md) - Canonical rulebook for authoring skills — token efficiency, lean SKILL.md, progressive disclosure, and consistent behavior.
* [Community Insights: Real-World Skill Patterns](community-insights.md) - Field reports and practitioner-discovered patterns for building, optimizing, and debugging skills — companion to the canonical best-practices guide.
* [Open Knowledge Format (OKF) v0.1](okf-spec.md) - Vendored copy of the OKF v0.1 spec — markdown-plus-frontmatter knowledge bundles, concept documents, index.md and log.md conventions.
* [Output Conventions](output-conventions.md) - Where skills write their output files — the shared claude-work/ directory convention all skills must follow.

# Operational Knowledge

* [Flywheel Instance Access](flywheel/instance-access.md) - The one place that says how to reach a live Flywheel instance — the ~/.fw/config.yml profile inventory, how to pick a profile for a site, and how to build an SDK / FWClient / raw-HTTP client from it.
* [Headless Connector Loading](harness/headless-connectors.md) - Operational rule for headless `claude -p` runs — a missing `mcp__claude_ai_*` tool at startup does not mean the connector is unavailable; only a failed call proves that.

# Subdirectories

* [Skill Authoring](skill-authoring/index.md) - Companion files to the skills best-practices rulebook: directory structure, frontmatter reference, behavior patterns, evaluation, and skill-creator alignment.
* [Tools](tools/index.md) - Operational runbooks and constants for external tools — Atlassian/Jira access and board fields, the Jira→Clockify sync, and GitLab code search plus the glab wrapper scripts.
