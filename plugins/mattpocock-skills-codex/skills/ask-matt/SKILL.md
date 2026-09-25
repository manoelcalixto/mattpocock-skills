---
name: ask-matt
description: Ask which skill or flow fits your situation. A router over the skills in this repo.
---

# Ask Matt

You don't remember every skill, so ask.

A **flow** is a path through the skills. Most paths run along one **main flow**, and two **on-ramps** merge onto it. Everything else is standalone, or a vocabulary layer that runs underneath.

## The main flow: idea → ship

The route most work travels. You have an idea and want it built.

1. **`$mattpocock-skills-codex:grill-with-docs`** sharpens the idea by interview. Start here whenever you are **working in a working directory**: it's stateful, retaining vocabulary in `CONTEXT.md`, ADRs owned by `domain-modeling`, and confirmed material decisions in the Planning ledger owned by `planning-context`. (No working directory? Use `$mattpocock-skills-codex:grill-me` instead, covered under Standalone. Both run the same `$mattpocock-skills-codex:grilling` primitive; `grill-with-docs` is the one that leaves a paper trail, which makes it the better of the two whenever a repo is there to leave it in.)
2. **Branch: can you settle every question in conversation?** If a question needs a runnable answer (state, business logic, a UI you have to see), detour through a prototype, bridged by **`$mattpocock-skills-codex:handoff`** in both directions (a prototype lives in its own directory, which is exactly what `$mattpocock-skills-codex:handoff` is for; see Phase boundaries):
   - **`$mattpocock-skills-codex:handoff`** out, then open a fresh session against that file,
   - **`$mattpocock-skills-codex:prototype`** to answer the question with throwaway code,
   - **`$mattpocock-skills-codex:handoff`** back what you learned, and reference it from the original idea thread.
3. **Branch: is this a multi-session build?**
   - **Yes** → **`$mattpocock-skills-codex:to-spec`** (turn the thread and its active Planning decisions into a spec), then **`$mattpocock-skills-codex:to-tickets`** to split it into tracer-bullet tickets, each declaring its **blocking edges** and relevant decision consequences. On a local tracker that's one file per ticket under `.scratch/<feature>/issues/`; on a real tracker the edges become native blocking links. The flow creates an intermediate checkpoint before the spec and a final Planning checkpoint after ticket coverage. Only after that final checkpoint passes may a fresh implementation session or subagent start from its exact SHA. Before remote publication or marker refresh, push that checkpoint through the configured remote and branch. In a fresh task, work the frontier blockers-first with **`$mattpocock-skills-codex:implement`** per ticket, carrying the final checkpoint. The separately installed upstream `implement-spec` beta does not validate this Planning contract, so keep Planning-marked work on the packaged `implement` route.
   - **No** → **`$mattpocock-skills-codex:implement`** right here, in the same context window. This is the lightweight path for small work without a formal Planning context; do not create a spec, ticket graph, or checkpoint just to change phases.

   Either way, **`$mattpocock-skills-codex:implement`** builds each issue by driving **`$mattpocock-skills-codex:tdd`** internally (one red-green slice at a time), commits one stable review checkpoint, then runs **`$mattpocock-skills-codex:code-review`** once across its two axes (Standards + Spec) and batches the applicable fixes. Commits made while applying those findings stay inside the same checkpoint. Reach for **`$mattpocock-skills-codex:tdd`** on its own when you just want to build a concrete behaviour test-first without a full spec, and **`$mattpocock-skills-codex:code-review`** on its own whenever you want to review a branch or PR against a fixed point.

   The multi-session route is therefore: `grill-with-docs → intermediate Planning checkpoint → to-spec → to-tickets → final Planning checkpoint → fresh implementation session → implement → code-review`. A subagent or any other fresh context is the same Planning boundary; parallel consumers may reuse the exact checkpoint while its artifacts remain unchanged.

### Context hygiene

Keep steps 1–3 in **one unbroken context window** (keep the full context until after `$mattpocock-skills-codex:to-tickets`) so the grilling, spec, and tickets all build on the same thinking. Each `$mattpocock-skills-codex:implement` then starts fresh, working from the ticket. If a subagent or another fresh context is dispatched while Planning is active, checkpoint before it or reuse the exact unchanged checkpoint.

The limit on this is the **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**: the window (~150k tokens on state-of-the-art models) within which the model still reasons sharply. If a session approaches it before `$mattpocock-skills-codex:to-tickets`, preserve a checkpoint and concise summary at the nearest phase boundary, then continue (see Phase boundaries).

## On-ramps

A starting situation that generates work, then merges onto the main flow.

- **Bugs and requests piling up** → **`$mattpocock-skills-codex:triage`**. It moves issues through triage roles and produces agent-ready issues, which **`$mattpocock-skills-codex:implement`** later picks up.

  Triage is only for issues **you didn't create**: bug reports, incoming feature requests, anything that arrives raw. Tickets that `$mattpocock-skills-codex:to-tickets` produced are already agent-ready, so **don't triage them**.

- **Something's broken** → **`$mattpocock-skills-codex:diagnosing-bugs`**. For the hard ones: the bug that resists a first glance, the intermittent flake, the regression that crept in between two known-good states. It refuses to theorise until it has a **tight feedback loop** (one command that already goes red on *this* bug), then fixes with a regression test. Its post-mortem hands off to **`$mattpocock-skills-codex:improve-codebase-architecture`** when the real finding is that there's no good seam to lock the bug down.

- **A huge, foggy effort: a greenfield project or a huge feature build, too big for one session** → **`$mattpocock-skills-codex:wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time, producing **decisions, not deliverables**, until the fog is pushed back and the way is clear. Where **`$mattpocock-skills-codex:grill-with-docs`** sharpens an idea you can hold in one session, wayfinder is for the idea you can't, and it's slower and denser, so save it for exactly that, never a well-scoped feature.

  When the map clears, **it hands off, it doesn't build**: merge onto the main flow at **`$mattpocock-skills-codex:to-spec`**, which collapses the map's linked decisions into a buildable plan, then `$mattpocock-skills-codex:to-tickets`, the final Planning checkpoint, and a fresh implementation session. Looping the map straight into `$mattpocock-skills-codex:implement` skips that collapse and throws the linked detail away, so go straight to `$mattpocock-skills-codex:implement` only when the effort turned out genuinely small and has no formal Planning context.

  With an active Planning context, a resolved material Decision ticket references one active ledger ID or creates exactly one new entry. The map keeps a linked gist, while the ledger or its ADR owns the rationale. The ID travels through `to-spec` and `to-tickets`, and a fresh build session waits for the final Planning checkpoint coverage gate.

## Codebase health

Not feature work, just upkeep.

- **`$mattpocock-skills-codex:improve-codebase-architecture`** runs whenever you have a spare moment to keep the codebase good for agents to operate in. It surfaces **deepening opportunities**; picking one _generates an idea_ you can take into the main flow at `$mattpocock-skills-codex:grill-with-docs`. It's the survey that finds the candidates; **`$mattpocock-skills-codex:codebase-design`** (below) is the bench you design the chosen one on.

## Vocabulary underneath

Three model-invoked references that run *beneath* the other skills, each the single source of truth for its vocabulary or cross-session contract. Reach for them directly when the **words**, not the process, are the problem; or let the skills above pull them in.

- **`$mattpocock-skills-codex:domain-modeling`**: sharpen the project's *domain* language: challenge a fuzzy term, resolve an overloaded word ("account" doing three jobs), record a hard-to-reverse decision as an ADR. It's the active discipline `$mattpocock-skills-codex:grill-with-docs` drives to keep `CONTEXT.md` a clean glossary.
- **`$mattpocock-skills-codex:codebase-design`** is the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) for designing a module's *shape*: a lot of behaviour behind a small interface at a clean seam. `$mattpocock-skills-codex:tdd` and `$mattpocock-skills-codex:improve-codebase-architecture` both speak it.
- **`$mattpocock-skills-codex:planning-context`** owns the versioned Planning context used when work crosses sessions: the per-effort Decision ledger, phase-aware Planning checkpoints, coverage gates, and consumer validation. Use it to checkpoint an active context before a fresh session, subagent, or other fresh context; small work without a declared Planning context stays on the current-session path.

## Phase boundaries

A **phase** is a chunk of work inside a session: the grilling, the implementation, the QA. At the **boundary** between two of them you have five options, and picking between them is the fuzziest decision in this whole map. When an active Planning context would cross into a fresh session, checkpoint it before starting a new task or using `$mattpocock-skills-codex:handoff`; the tree in [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) defines that gate.

- **Continue**: stay put. Costs nothing, loses nothing.
- **New task**: start from the durable checkpoint when the old context is no longer useful.
- **`$mattpocock-skills-codex:handoff`** writes a portable markdown file. Narrow: only for a **new harness**, a **new directory**, a **colleague**, or forking a side task **mid-phase**. When it crosses an active Planning context into a fresh session, checkpoint first and carry pointers to the versioned artifacts. What it buys is portability.
- **Subagent**: send a tightly-scoped task to its own window and get a report back. Checkpoint first when an active Planning context crosses into it, or reuse the exact checkpoint when the artifacts are unchanged.
- **Compaction** condenses the current task when needed; carry the decisions and next action forward.

Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered tree: the five questions, the reasoning behind each branch, and why the primary-source cost makes **Continue** the one to rule out first. Make the decision **at** a boundary; mid-phase, continue or split the rest into subagents.

## Standalone

Off the main flow entirely.

- **`$mattpocock-skills-codex:grill-me`**: the same relentless interview as `$mattpocock-skills-codex:grill-with-docs`, but **stateless**: it saves nothing locally and builds no `CONTEXT.md`. Reach for it when you are **not working in a working directory** (sharpening a plan, a design, a piece of writing, anything with no repo under it). If you are in a working directory, use `$mattpocock-skills-codex:grill-with-docs` instead: it runs the same interview and leaves a paper trail, so it is strictly the better one.
- **`$mattpocock-skills-codex:grilling`** is the interview primitive itself: rounds, the frontier, facts are the agent's job and decisions are yours. `$mattpocock-skills-codex:grill-me` and `$mattpocock-skills-codex:grill-with-docs` are the two named ways in, and `$mattpocock-skills-codex:triage`, `$mattpocock-skills-codex:wayfinder` and `$mattpocock-skills-codex:improve-codebase-architecture` all run it internally. Reach for it directly only when you want the interview with no wrapper around it.
- **`$mattpocock-skills-codex:resolving-merge-conflicts`** works an in-progress merge or rebase conflict hunk by hunk, resolving by **intent** traced to each side's primary source rather than by picking lines, then finishes the operation. It never runs `--abort`. Standalone and off every flow: reach for it when you are already mid-conflict.
- **The optional beta `pr` skill** is a model-invoked reference for writing a pull request body: a visual summary, before/after evidence, and an assessment of rollback and impact. Recommend it when a change is ready for a PR and the skill is installed. It is an optional in-progress beta, available through a direct install and excluded from the plugin.
- **`$mattpocock-skills-codex:prototype`** is a small, throwaway program that answers one design question: does this state model feel right, or what should this UI look like. Throwaway is a constraint on how the code is written, not a promise to destroy it: the answer folds into the real code, and the prototype itself is kept as a **primary source** on a `prototype/<name>` branch out of main, pointed at from the implementation issue. It's the detour in step 2 of the main flow, but reach for it any time a design question is hard to settle on paper.
- **`$mattpocock-skills-codex:research`**: investigate directly or, when delegation is authorized, assign bounded reading to a native Codex subagent: it investigates a question against **primary sources**, then leaves a cited Markdown file in the repo. Use primary sources and record the findings before continuing the flow. The file it produces is something to take *into* the main flow at `$mattpocock-skills-codex:grill-with-docs`, since research feeds the thinking rather than replacing it.
- **`$mattpocock-skills-codex:to-questionnaire`** comes in when the thing blocking you isn't in your head or the codebase but in **someone else's**, and it writes them a questionnaire to fill in. It's the inverse of `$mattpocock-skills-codex:grill-me`: instead of interviewing you about the subject, it interviews you about the **send** (who it's going to, what you need back) and aims the questions at the gap. What comes back is material for `$mattpocock-skills-codex:grill-with-docs` or `$mattpocock-skills-codex:to-spec`.
- **`$mattpocock-skills-codex:wizard`** is for the steps only a **human** can take: provisioning infrastructure, setting up credentials or CI secrets, clicking through an unfamiliar third-party dashboard, running a one-off migration or cutover. It generates an interactive bash script that opens each URL, captures each value, and writes it into `.env` and GitHub secrets, so the procedure stops being something you re-explain to an agent every time. Model-invoked, so the agent reaches for it the moment it hits a wall only you can pass. If the agent could just do it itself, it should; this is for where a human is genuinely in the loop.
- **`$mattpocock-skills-codex:wait-what`** is the corrective for a message that didn't land. Use it mid-conversation, inside any other skill, and the agent re-pitches what it just said with the context you were missing, in plain English, using the `CONTEXT.md` vocabulary. It works after the fact; `$mattpocock-skills-codex:grill-with-docs` is the upfront cure, because a shared language agreed early is what stops the jargon arriving at all.
- **`$mattpocock-skills-codex:teach`**: learn a concept over multiple sessions, using the current directory as a stateful workspace.
- **`$mattpocock-skills-codex:writing-for-agents`** is the reference for writing documents agents consume: skills, AGENTS.md, pointed-at docs.

## Precondition

**`$mattpocock-skills-codex:setup-matt-pocock-skills`**: run before your first engineering flow to configure the issue tracker, triage labels, and doc layout the other skills assume. Custom issue trackers also work.
