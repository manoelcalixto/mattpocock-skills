## What it does

`grill-with-docs` interviews you about a plan or design until you and the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) share one understanding of it, and writes the vocabulary and confirmed material decisions into your repo while it does. It is the same interview [grill-me](https://aihero.dev/skills-grill-me) runs (a round of questions, then wait, then the next round), pointed at a codebase.

It is **[stateful](https://www.aihero.dev/ai-coding-dictionary/stateful)**. Every other grilling skill leaves the [session](https://www.aihero.dev/ai-coding-dictionary/session) in your head; this one leaves files on disk. A term gets resolved and it lands in `CONTEXT.md` the moment it resolves, not batched at the end. A decision that meets the ADR gates goes to an ADR, while every other material choice for a multi-session effort gets one stable ID in the per-effort Decision ledger owned by [planning-context](https://aihero.dev/skills-planning-context). Routine implementation choices remain conversational. The artifacts are real files in a real repo, so they can be absent when nothing qualified and they can drift when more than one person is writing them.

## When to reach for it

You invoke this by typing `/grill-with-docs`; the agent will not reach for it on its own.

Reach for it at the start of a change, in a repo, when the plan is still fuzzy and the words for the thing are not settled yet. It is the single-session tool. Which grilling skill you want depends on what is in front of you:

| What you have | Reach for |
| --- | --- |
| You aren't working in a working directory at all | [grill-me](https://aihero.dev/skills-grill-me) |
| A repo, and a change you can settle in one session | `grill-with-docs` |
| An effort too big to hold in one session (a greenfield build, a large feature) | [wayfinder](https://aihero.dev/skills-wayfinder) |
| A repo with no domain docs at all, and no particular feature in mind | `grill-with-docs`, aimed at the repo rather than a change |
| A decision blocked on knowledge in someone else's head | [to-questionnaire](https://aihero.dev/skills-to-questionnaire) |

The wayfinder split comes down to session count: `/grill-with-docs` for single-session planning, `/wayfinder` for multi-session planning.

## Prerequisites

The skill writes into your repo, so you need to be somewhere it is safe to write. Resolved terms go to a `CONTEXT.md` glossary at the root, or to the relevant context's `CONTEXT.md`, if a `CONTEXT-MAP.md` at the root marks the repo as multi-context. Decisions go to `docs/adr/`. Both are created lazily; nothing exists until the first term or decision crystallises, so there is nothing to scaffold up front.

It also needs three other skills present: [grilling](https://aihero.dev/skills-grilling) supplies the interview, [domain-modeling](https://aihero.dev/skills-domain-modeling) owns vocabulary and ADR writing, and [planning-context](https://aihero.dev/skills-planning-context) owns the ledger and checkpoint contract. Installing `grill-with-docs` without those dependencies gets you a skill that does not work.

## The paper trail

Four things can come out of a session, and they are not equal.

| What resolved | Where it lands |
| --- | --- |
| A term: the project's own word for a thing | `CONTEXT.md`, inline, the moment it resolves |
| A decision that is hard to reverse, surprising without context, and a real trade-off | An ADR under `docs/adr/` |
| Another material choice that affects downstream work | The effort's Decision ledger through `planning-context`, with a stable `DEC-NNN` ID |
| A routine implementation choice | The conversation, and nowhere else |

The distinction between the last two rows is the one that catches people out. `CONTEXT.md` is a glossary and is deliberately kept as one: no implementation details, no [spec](https://www.aihero.dev/ai-coding-dictionary/spec), no scratch notes. ADRs are gated on all three conditions at once, while the ledger captures material choices that still need downstream traceability. A session that yields a sharper glossary and no ledger entries is working as designed when nothing material was decided. Hand the same conversation to [to-spec](https://aihero.dev/skills-to-spec) rather than [clearing](https://www.aihero.dev/ai-coding-dictionary/clearing) it when the work crosses sessions.

The glossary is the point. Domain language is the thing this skill is actually building: the project's own words, agreed once, so you, the agent and your colleagues stop paying to re-derive them. It is worth saying that not everyone agrees this buys you agent performance: the sharpest public pushback is that a term and its plain-English expansion get the same result from the [model](https://www.aihero.dev/ai-coding-dictionary/model), and that the vocabulary really compresses communication between the humans who share it. That reading still leaves the glossary valuable; it just moves the value.

## Common questions

**Should I use this or `/wayfinder`?**
Scope decides it. Use this for anything you can settle in one session; use [wayfinder](https://aihero.dev/skills-wayfinder) when the effort is too big to hold in one, and it charts the work as a map of decision [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket) first. Wayfinder is slower and denser, and reaching for it on a well-scoped feature is the common mistake. It does not replace this skill: it can drop into a grilling session for the parts of the map that suit one.

**It ran, but no `CONTEXT.md` and no ADRs appeared.**
Nothing qualifies when no term, ADR, or material Planning decision was resolved. ADRs need all three gates, and a routine choice does not belong in the ledger. If a material choice was confirmed but no `DEC-NNN` appears, check that `planning-context` was loaded and that its ledger was initialized before trusting the session's output.

**It asked everything at once, with no recommendations, and never mentioned `CONTEXT.md`.**
That is the skill failing to load its three dependencies. If [grilling](https://aihero.dev/skills-grilling), [domain-modeling](https://aihero.dev/skills-domain-modeling), or [planning-context](https://aihero.dev/skills-planning-context) is missing, the interview, domain paper trail, or decision IDs can disappear independently. If you suspect it, ask the agent directly which skills it loaded.

**Where did all my other decisions go?**
Material choices now receive stable IDs in the effort ledger through `planning-context`, while routine implementation choices remain in the conversation. [to-spec](https://aihero.dev/skills-to-spec) and [to-tickets](https://aihero.dev/skills-to-tickets) carry the relevant IDs and actionable consequences without copying the ledger's rationale. If the work is not using an active Planning context, the legacy answer still applies: keep the session and feed it straight to `to-spec`.

**Can I point it at an existing repo that has no docs at all?**
Yes. This is the right skill for a codebase with no ADRs, no domain language and no design principles: invoke it and say "help me document my repo". The community pattern pairs it with [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) for building or repairing a `CONTEXT.md`. Expect to steer it: it will read code and ask you about what it finds, and you are the one who says which of the words already in the codebase are the right ones.

**What should I do when the session ends?**
The skill's closing message tends to be open-ended, which is a known rough edge. In the main flow the answer is [to-spec](https://aihero.dev/skills-to-spec), in the same conversation. If the change is small enough to build immediately, go straight to [implement](https://aihero.dev/skills-implement) instead.

**Why is it called that?**
Nobody is happy with the name. There is an open suggestion to rename it `grill-domain-model`, which describes the behaviour more honestly. Nothing has moved on it. If a rename ever lands, the docs page moves with it and the URL changes.

## It's working if

- `CONTEXT.md` changes *during* the session, term by term, rather than appearing in one lump at the end.
- The glossary reads as pure vocabulary (your project's words with tight definitions) and contains no implementation detail or spec-like prose.
- Questions the codebase can answer get answered by reading the codebase, not asked of you.
- You get few or no ADRs, and the ones you get are decisions you would be annoyed to have to re-litigate.
- Every material choice has one `DEC-NNN` ID in the effort ledger, and each round summary names the IDs recorded in that round.
- It challenges a word you used because your existing glossary defines it differently.

## Where it fits

`grill-with-docs` is the head of the main build chain:

```txt
grill-with-docs → intermediate checkpoint → to-spec → to-tickets → final checkpoint → implement → code-review
```

It comes before anything is written down as a spec: it produces the shared understanding, settled vocabulary, and stable decision IDs that [to-spec](https://aihero.dev/skills-to-spec) then synthesises without interviewing you again. Its close neighbours are [grill-me](https://aihero.dev/skills-grill-me), the same interview with no repo and no files, [domain-modeling](https://aihero.dev/skills-domain-modeling), the glossary-and-ADR discipline it drives, and [planning-context](https://aihero.dev/skills-planning-context), the ledger owner it calls for cross-session work. Upstream of it, [wayfinder](https://aihero.dev/skills-wayfinder) charts efforts too large for one session and can hand parts of the map back down to it. When you're unsure which skill or flow fits, [ask-matt](https://aihero.dev/skills-ask-matt) routes you.
