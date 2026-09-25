# Phase boundaries

A **phase** is a chunk of work inside a session: the grilling, the implementation, the QA. The definition is fuzzy on purpose: a phase ends when you think *"ok, we're done with that"*.

The **phase boundary** is the gap between two phases, and it is the only place this decision belongs. Mid-phase there is no decision to make: continue, or split the work that's left into subagents. Compacting mid-phase makes the agent lose the thread.

## Planning context gate

First decide whether the next step starts a fresh session. A Planning context is active when the current map, specification, or ticket declares its `## Planning context` marker, or when a local artifact resolves a Planning checkpoint through its Git trailer. Dispatching a `Subagent` or any other fresh context counts as a fresh session boundary.

When that context is active and the next step is a fresh task or delegated context, follow the installed `mattpocock-skills-codex:planning-context` skill and create the checkpoint before handing off or starting the new context. The checkpoint phase follows the destination:

- **Planning continues**: create an `intermediate` checkpoint, which may leave specification or ticket coverage pending.
- **Implementation starts**: create a `final` checkpoint, after specification and ticket coverage pass.
- **Implementation has finished**: create an `implementation` checkpoint, after verification evidence is complete.

Give the fresh session or subagent the exact full checkpoint SHA, the effort and ledger pointers, and the relevant map, specification, or ticket references. Parallel subagents that consume unchanged Planning artifacts may reuse that exact checkpoint. If a subagent changes Planning artifacts before another fresh context, create the next checkpoint first. A handoff carries pointers instead of copying their contents. The gate does not add a checkpoint to **Continue**, same-session implementation, or small markerless work.

## The five options

| Option       | What it does                                                    |
| ------------ | --------------------------------------------------------------- |
| **Continue** | Stay in the session. No context switch at all.                    |
| **New task** | Start a fresh Codex task from a durable checkpoint.             |
| **`$mattpocock-skills-codex:handoff`** | Write a portable markdown file and seed a session anywhere with it. Checkpoint first when an active Planning context crosses into that session. |
| **Subagent** | Send the task to its own context window and get a report back. Checkpoint first when an active Planning context crosses into it. |
| **Compaction** | Continue this task from its condensed context.                |

## The tree

Work top to bottom at the boundary. Apply the Planning context gate first, then take the first **yes**.

**1. Can you continue in this session?** Two things make the answer yes: the next phase needs this phase as a **primary source**, or you have enough [smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone) left (~150k tokens) for the next phase to fit. Grilling → implementation is the standard yes: the implementation wants the reasoning verbatim, not a summary of it. Continue costs nothing and loses nothing, so rule it out before anything else.

**2. Is the context irrelevant to what comes next?** Is everything in this task (the exploration, the decisions, the dead ends) disposable? If so, start a **new task** using the durable checkpoint and relevant references. If the Planning context is active, the gate above creates its checkpoint first.

The cost of getting this wrong is one-way. Clear a *relevant* context and you lose the **why** behind what you built, and no amount of reading the diff back gets it returned.

**3. Do you need to hand off?** `$mattpocock-skills-codex:handoff` is narrow. You need it only when you are:

- switching to a **different environment**,
- moving to a **new directory** or repo,
- sending the work to a **colleague**,
- or forking a side task you found **mid-phase** without derailing what you're doing.

That list is the whole clause. What `$mattpocock-skills-codex:handoff` buys is **portability**: a file that travels. If nothing is travelling, you don't need it. When an active Planning context travels, the file contains its checkpoint and artifact pointers, not copied planning content.

**4. Is delegation authorized and available?** If the work is tightly scoped and the current instructions permit native Codex subagents, delegate within the current concurrency limits. Otherwise continue directly. The Planning context gate above must already have checkpointed the exact artifacts.

**5. Otherwise, continue in this task.** When the context is condensed, preserve the current objective, checkpoint, decisions, completed work, and next action in the summary.

Compaction is a continuation mechanism, not a reason to discard the task. A summary must preserve the decisions that matter for the next phase.

## Primary and secondary sources

Every move except **Continue** turns a **primary source** into a **secondary source**: the session as it happened, replaced by a summary of it. The trade is always the same shape:

| Source                            | Information | Noise | Room to move |
| --------------------------------- | ----------- | ----- | ------------ |
| Primary (Continue)                | Full        | Lots  | Little       |
| Secondary (compaction, `$mattpocock-skills-codex:handoff`) | Lossy | Less | Lots |

This is why question 1 comes first. You only pay the lossiness when staying costs more than it saves.

## These are judgement calls

The questions are not objective: each has taste in it, and the same boundary can go two ways on two days. The value is in asking them **in order**, at the boundary rather than in the middle of the work.
