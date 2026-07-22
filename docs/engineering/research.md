Quickstart:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Start a new Codex thread and type `$mattpocock-skills:research`.

[Source](https://github.com/manoelcalixto/mattpocock-skills/tree/main/skills/engineering/research)

## What it does

`research` answers a question from primary sources and leaves one cited Markdown report in the repository's existing research location.

At the root it delegates one isolated GPT-5.6 Sol worker at medium effort when Codex MultiAgent V2 is available; inside a subagent it researches directly, preventing recursive agent trees. Without V2 it produces the same artifact inline.

## When to reach for it

Type `$mattpocock-skills:research`, or the agent reaches for it automatically when documentation facts, API behavior, specifications, papers, or source-code evidence would unblock a decision.

Use it for reading legwork. For decision-making after the facts arrive, use [grill-with-docs](https://aihero.dev/skills-grill-with-docs); for turning settled decisions into a buildable document, use [to-spec](https://aihero.dev/skills-to-spec).

## Primary sources

The report follows every material claim to the source that owns it: official docs, source code, standards, papers, or first-party APIs. It records version constraints, conflicts, and uncertainty rather than laundering secondary summaries into facts.

## Safe background work

The delegated worker receives an isolated, self-contained V2 brief and a unique output path. It cannot switch branches, commit, mutate trackers, or spawn another research agent. The root keeps working and uses the event-driven mailbox wait only when the report becomes blocking.

## It's working if

- One Markdown report answers the question and cites claims beside their sources.
- Running inside a subagent never creates a nested research agent.
- Missing MultiAgent V2 tools change latency, not the report contract.

## Where it fits

`research` is a reach-for-it-anytime input to design and planning. [wayfinder](https://aihero.dev/skills-wayfinder) uses it for AFK research tickets, while [orchestrate-agents](https://aihero.dev/skills-orchestrate-agents) supplies the Sol-only MultiAgent V2 contract and adaptive effort policy. [ask-matt](https://aihero.dev/skills-ask-matt) maps the whole set.
