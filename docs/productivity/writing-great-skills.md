Quickstart:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Start a new Codex thread and type `$mattpocock-skills:writing-great-skills`.

[Source](https://github.com/manoelcalixto/mattpocock-skills/tree/main/skills/productivity/writing-great-skills)

## What it does

`writing-great-skills` is the reference you write and edit skills against — the shared vocabulary and principles that make a skill predictable.

A skill's job is to wrangle determinism out of a stochastic system, so the goal is not the same *output* every run but the same *process*. **Predictability** is the root virtue, and every design choice is judged against it — not against how clever, complete, or exhaustive the skill reads.

## When to reach for it

Type `$mattpocock-skills:writing-great-skills`, or the agent reaches for it automatically when a task fits.

Reach for it whenever you're authoring a new skill or editing an existing one and want it to behave the same way every time: deciding invocation mode, writing a description, choosing what lives in `SKILL.md` versus a linked file, or diagnosing why a skill misfires.

## Codex-native interaction

A bounded, user-owned choice is a **Decision prompt**. The skill that creates it carries a generated, co-located copy of the repository's canonical `request_user_input` contract, so a standalone installation remains self-contained; validation keeps every copy synchronized. Composed consumers inherit that behavior instead of carrying another copy. This gives interactive skills one consistent native UI, capability fallback, cadence, and timeout policy without turning the contract into another invocable skill.

## Cognitive load

The concept the whole reference turns on is **cognitive load** — and its counterpart, **context load**. Every skill spends one or the other:

- A **model-invoked** skill keeps rich trigger language in its description and omits an invocation policy, so Codex can select it autonomously.
- A **user-invoked** plugin skill sets `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; only a human typing its qualified name, such as `$mattpocock-skills:skill-name`, can reach it. Standalone skills use `$skill-name`.

Both use frontmatter containing only `name` and `description`, plus Codex UI metadata and a default prompt containing the exact installed invocation in `agents/openai.yaml`.

This repository requires every skill to be model-invoked, so its descriptions must earn their context load with clear trigger boundaries and `agents/openai.yaml` must omit the invocation policy. The user-invoked option applies only to other collections whose standards allow it. In those collections, cognitive load becomes the counter-pressure: when user-invoked skills multiply past what you can hold in your head, the cure is a **router skill** that names the others and when to reach for each. Once you're thinking in these two loads, most authoring decisions — split or don't, inline or disclose, model- or user-invoked — become the same trade made in different places.

## The other levers

The rest of the reference is the toolkit for spending those loads well:

- **Leading words** — a compact concept already in the model's pretraining (_tight_, _red_, _tracer bullet_) that the agent thinks with while running the skill. It anchors execution *and* invocation in the fewest tokens; hunt restatements that a single word can retire.
- **Information hierarchy** — the ladder from in-skill step, to in-skill reference, to external reference behind a **context pointer**. **Progressive disclosure** is the move down that ladder so the top stays legible.
- **Pruning** — single source of truth, relevance, and the no-op test applied sentence by sentence, against **sediment** and **sprawl**.
- **Failure modes** — **premature completion**, **duplication**, **sediment**, **sprawl**, **no-op** — to diagnose a skill that isn't behaving.

## Where it fits

This is a reach-for-it-anytime standalone reference — the meta-skill you consult while building the rest of the set, not a step in a chain. Its natural neighbour is any router you maintain, because a router is the direct cure for the cognitive load that user-invoked skills pile up; when you're unsure which skill or flow fits a task, [ask-matt](https://aihero.dev/skills-ask-matt) routes you over the whole set.
