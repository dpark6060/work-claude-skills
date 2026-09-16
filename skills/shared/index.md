# Shared References

* [Architecture Plan Format](plan_format.md) - Canonical template for architecture plan files produced by code-architect and change-planner and consumed by code-architect-reviewer.
* [Claude Skills Best Practices](claude-skills-best-practices.md) - Canonical rulebook for authoring skills — token efficiency, lean SKILL.md, progressive disclosure, and consistent behavior.
* [Community Insights: Real-World Skill Patterns](community-insights.md) - Field reports and practitioner-discovered patterns for building, optimizing, and debugging skills — companion to the canonical best-practices guide.
* [Open Knowledge Format (OKF) v0.1](okf-spec.md) - Vendored copy of the OKF v0.1 spec — markdown-plus-frontmatter knowledge bundles, concept documents, index.md and log.md conventions.
* [Output Conventions](output-conventions.md) - Where skills write their output files — the shared claude-work/ directory convention all skills must follow.

# Subdirectories

* [Coding Standards](coding/index.md) - Python coding standards shared by code-writer, code-reviewer, test-writer, and fw-gear: general structure, functions, classes, unit tests.
* [Skill Authoring](skill-authoring/index.md) - Companion files to the skills best-practices rulebook: directory structure, frontmatter reference, behavior patterns, evaluation, and skill-creator alignment.
* [Writing](writing/index.md) - Style rules for anything a skill posts for humans to read — Jira comments, Slack reports, MR descriptions.
* [Tools](tools/index.md) - Reaching external systems: the Atlassian connector (Jira/Confluence) and GitLab code search plus MR/pipeline wrappers.
* [Harness](harness/index.md) - How the Claude Code harness itself behaves — connector loading, allowlists, and unattended-run rules.
* [Flywheel](flywheel/index.md) - Live instance access, SDK use and investigation procedure, finder quoting gotchas, and example-code conventions.
