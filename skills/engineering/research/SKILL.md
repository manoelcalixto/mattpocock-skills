---
name: research
description: Research a question from primary sources and save cited findings as a Markdown note in the repository. Use when the user requests a reusable repository research note or delegates primary-source reading to a Codex subagent.
---

When Codex collaboration tools are available, spin up a **subagent** to do the research while you continue only work that does not depend on its findings. Give it the question, output requirements, repository path, and expected destination; subagents share the filesystem, so assign a unique output file.

When collaboration tools are unavailable, do the same research in the current task and tell the user that background execution was unavailable. Do not weaken the source or citation requirements.

Its job:

1. Split the question into its material parts. Investigate every part against **primary sources** — official docs, source code, specs, first-party APIs — rather than secondary write-ups. Mark any part that primary sources do not resolve.
2. Write the findings to a single Markdown file, citing the owning primary source for every material factual claim.
3. Save it where the repo already keeps research notes. If there is no convention, use `docs/research/<YYYY-MM-DD>-<question-slug>.md`; when that name exists, append `-2`, `-3`, and so on instead of overwriting it.

Before completing, wait for the subagent when one was used and inspect the note. Verify that every material part of the question is answered or explicitly unresolved, every material factual claim has a primary-source citation, and the file exists at the reported path. Repair any deficiency, then report the path and a short findings summary.
