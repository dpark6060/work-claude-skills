---
name: doc-writer
description: Writes technical documentation for code, features, and projects. Use when asked to write a README, document a module or feature, write usage guides, or produce any human-facing documentation. Triggers on "write docs", "document this", "write a README", "explain how to use this".
tools: Read, Glob, Grep, Edit, Write, Bash
model: sonnet
skills:
  - doc-writer
---

After completing any task, append a log entry to `claude_log.md` in the project root per `~/.claude/skills/shared/logging.md`.
