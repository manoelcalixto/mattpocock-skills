## What it does

`to-spec` turns the conversation you have just had into a **[spec](https://www.aihero.dev/ai-coding-dictionary/spec)** with traceable Planning decision coverage, and publishes it to your issue tracker as a single issue.

It does not interview you. By the time you reach for it the deciding is already done, so it synthesises what is known (from the thread, from the codebase, from your `CONTEXT.md`, ADRs, and active Decision ledger) rather than opening a fresh round of questions. An active ledger is exhaustive: every applicable entry gets one actionable consequence in the spec, while the ledger remains the canonical source for rationale.

## When to reach for it

You invoke this by typing `/to-spec`; the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) won't reach for it on its own.

Reach for it when the build is too big for one agent [session](https://www.aihero.dev/ai-coding-dictionary/session) and has to survive being split across several. That is the whole trigger:

| Where you are | What to run |
| --- | --- |
| You haven't decided anything yet | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) first |
| Decided, and the work fits one [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) | [implement](https://aihero.dev/skills-implement): skip the spec |
| Decided, and the work spans several sessions | `/to-spec`, then [to-tickets](https://aihero.dev/skills-to-tickets) |
| A [wayfinder](https://aihero.dev/skills-wayfinder) map has cleared | `/to-spec #<map_issue>` |

## Prerequisites

`to-spec` publishes the spec as an issue, so [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) must have configured a tracker and the triage-label vocabulary for this repo first. Either kind works: a real tracker like GitHub, or local markdown files under `.scratch/`, which is supported out of the box. A Planning-enabled flow also needs the discovery file and an intermediate checkpoint from [planning-context](https://aihero.dev/skills-planning-context); a legacy source without its marker remains valid without them.

## The spec is a decision record

The spec exists because context windows end. Everything you settled while [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) (the shape of the solution, the choices you argued through, what you deliberately refused) is in one conversation that is about to be cleared. The spec is what survives that.

So it does not validate anything, and it does not decide anything. It captures what was decided, in your project's own vocabulary, so that a fresh session can pick the work up without you re-explaining it. Anything the spec asserts that you never actually said is a defect.

## Seams before prose

Before it writes a word, `to-spec` sketches the **seams** the feature will be tested at, and checks them with you. It prefers seams that already exist to new ones, and takes the highest seam it can: the ideal number across a change is one.

Those agreed seams then travel. [tdd](https://aihero.dev/skills-tdd) works only at pre-agreed seams, and [code-review](https://aihero.dev/skills-code-review) reviews the diff against the spec, so a seam nobody agreed to shows up as a review finding. The binding is indirect: it runs through this document, which is exactly why the seam conversation is worth taking seriously here rather than deferring it to implementation.

## Planning decision coverage

For an active Planning context, the spec carries the checkpoint marker and a short `DEC-NNN: consequence` line for every applicable active ledger entry. It does not copy the entry's decision, context, rationale, or ADR. Entries without a specification obligation receive an explicit not-applicable note so the accounting is complete without manufacturing a consequence. After publication, the specification obligation is marked complete with the issue URL, issue number, or local path as evidence.

A cleared Wayfinder map enters this same path through its Planning context marker. Its Decision ticket IDs are treated like grilled decision IDs, and the map remains a pointer rather than a second source of rationale.

The intermediate checkpoint is the bridge into this step. Before publishing or refreshing a marker for a remote consumer, resolve the configured Git remote and branch, run `git push <configured-remote> HEAD:<configured-branch>`, and verify that the checkpoint is reachable there. The final checkpoint belongs after `to-tickets` has recorded ticket coverage, so the spec marker is refreshed then with the final SHA through the configured tracker target.

## Common questions

**Where did `/to-prd` go?**
It is this skill, renamed in v1.1. "Spec" is now the single through-line term, and the old `to-prd` slug is dead; reinstall under the new name. The pair that replaced the old vocabulary is *spec* and *tickets*: the spec is the destination and the decisions that fix it, the [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket) are the execution steps that get there. If you pivot, delete the unfinished tickets and keep the spec.

**Why does the spec get the `ready-for-agent` label? I don't want an agent implementing off it.**
The label means "no further triage needed": the document is complete enough for an agent to work from. It is an input designation, not a work order. But if you run [AFK](https://www.aihero.dev/ai-coding-dictionary/afk) agents that poll for `ready-for-agent`, that distinction isn't visible to them, and they will happily try to build the whole spec in one run instead of picking up the ticket slices. This is the most-reported rough edge on the skill. Until it changes, exclude the parent spec explicitly in your AFK agent's prompt, or strip the label once `/to-tickets` has run.

**Why not go straight from grilling to `/to-tickets` and skip the spec?**
Often you should; the spec earns its step only on multi-session work. Where it pays is that the tickets are disposable and the spec isn't: each ticket is sized for one fresh context window and gets deleted or closed, while the spec stays as the one place the reasoning behind them lives. On a single-session change that buys you nothing, and you have paid an extra synthesis step where the [model](https://www.aihero.dev/ai-coding-dictionary/model) can drift. Go grilling → `/implement`.

**I just finished a wayfinder map. What do I feed it?**
The main map issue: `/to-spec #<map_issue>`, not the individual decision tickets. [wayfinder](https://aihero.dev/skills-wayfinder) produces decisions rather than deliverables, scattered across a map; `to-spec` is the step that collapses them into one buildable document. Looping the map straight into `/implement` throws that collapse away.

**Is the spec for me to review, or is it just for the agent?**
Mostly for the agent, and it reads that way: complete, dense, reference-heavy. The parts worth your eyes are the seams and the out-of-scope section, because those are the two places a wrong decision is cheapest to catch and most expensive to discover later. Reading the whole thing end to end is a real complaint people have, and there is no summary mode: the honest answer is that if the spec surprises you, the grilling was too shallow, not the spec too long.

**Do I keep the spec frozen once tickets start, or let the agent rewrite it?**
Nothing keeps it in sync, so in practice it is a snapshot of what you knew at that moment, and it goes stale the first time implementation teaches you something. Treat it as throwaway once the work ships. The artifacts meant to outlive it are your `CONTEXT.md` and your ADRs; if something learned during implementation deserves to last, it belongs there, not in an edited spec.

**My work is a refactor or a module boundary, not a feature. Does the template fit?**
Less well, and this is a known limitation. The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants. Lean on the implementation-decisions and testing-decisions sections instead, and let the durable architectural calls land as ADRs via [grill-with-docs](https://aihero.dev/skills-grill-with-docs) rather than trying to make the spec carry them.

**Will it check the tracker for related work, or cite the ADRs it's respecting?**
No to related-work discovery. It reads and respects the ADRs covering the area it touches, and it uses the Planning ledger for coverage, but it does not copy their rationale into the spec. Search the configured tracker yourself first if the area is busy.

**How do I know a decision was not silently dropped?**
With an active Planning context, compare the spec's `DEC-NNN: consequence` lines with the ledger's active entries and obligations. Every applicable specification entry has one line, and the post-publication coverage evidence names the spec. The final gate will still fail if the required ticket coverage is pending.

**Why does every GitHub command need `--repo`?**
The configured issue tracker is authoritative. Copy its fully qualified `owner/repository` target into every `gh` operation, including reads and marker updates, because a checkout can have an upstream remote and `gh`'s inference can publish to the wrong repository.

**Why must I push before publishing a Planning marker?**

The marker contains a commit that the consumer must resolve. Before publication or refresh, use the remote and branch configured by the repository or workflow, verify the checkpoint is reachable there, and stop if no unambiguous target exists. Never invent `origin` or a branch name.

**`/to-tickets` couldn't read my spec: it kept truncating.**
Very large specs can outgrow what a tracker issue will serve back cleanly, and there is no local copy to fall back on. The fix is context hygiene: don't [clear](https://www.aihero.dev/ai-coding-dictionary/clearing) or [compact](https://www.aihero.dev/ai-coding-dictionary/compaction) between `/to-spec` and `/to-tickets`. Run them in the same window and the spec never has to be re-fetched at all.

## It's working if

- It starts writing rather than asking you a fresh round of questions.
- It puts the seams to you before it writes, and proposes as few as it can get away with.
- It comes back in your project's nouns, not generic product-management boilerplate.
- Every decision in it is one you can remember making. Nothing was invented to fill a section.
- With Planning context active, every applicable active ledger ID appears beside one actionable consequence, canonical rationale is not duplicated, and specification coverage has publication evidence.
- The out-of-scope section has real things in it: the things you refused are usually the most useful lines on the page.

## Where it fits

`to-spec` is a step in the main build chain, and only on the multi-session branch of it:

```txt
grill-with-docs → intermediate checkpoint → to-spec → to-tickets → final checkpoint → implement → code-review
```

Its neighbours upstream are [grill-with-docs](https://aihero.dev/skills-grill-with-docs), which records confirmed decisions that this skill synthesises, [planning-context](https://aihero.dev/skills-planning-context), which owns the ledger and intermediate checkpoint, and [wayfinder](https://aihero.dev/skills-wayfinder), whose finished map merges onto the chain right here. Downstream, [to-tickets](https://aihero.dev/skills-to-tickets) cuts the spec into tracer-bullet tickets and closes the final planning gate before [implement](https://aihero.dev/skills-implement) builds. When you're unsure which skill or flow fits, [ask-matt](https://aihero.dev/skills-ask-matt) routes you.
