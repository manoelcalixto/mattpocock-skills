---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a cited Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated while other work continues.
---

# Research

Investigate the question against **primary sources**: official documentation, source code, specifications, papers, or first-party APIs. Trace every material claim back to the source that owns it rather than relying on secondary summaries.

Write one cited Markdown report where the repository already keeps research notes. If there is no convention, choose a sensible directory and a unique, descriptive filename. State the final path.

## Delegation

If already running as a subagent, do the research directly. Never spawn another research agent.

At the root, use the `orchestrate-agents` skill to dispatch one read-only/background research worker when multi-agent tools are available. Give it a self-contained question, source constraints, the unique output path, and instructions not to change branches, commit, or spawn children. In V2 use a descriptive `research_<topic>` task name and `fork_turns="none"`; in V1 use `fork_context=false`.

Continue useful root work while it reads and wait only when the report becomes a blocker. Verify the finished report's citations and claims before relying on it. If multi-agent tools are unavailable, research inline and produce the same artifact.

## Report contract

Include:

- The question and concise answer.
- Findings grouped by decision-relevant theme.
- Direct links or repository references beside the claims they support.
- Uncertainties, version constraints, or conflicting primary sources.
- A short implications section explaining what the result changes for the surrounding task.

Do not create a branch for the report. The shared working directory is the source of truth.
