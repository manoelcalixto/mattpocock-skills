# Writing Great Skills

## Install

Native Codex plugin (installs all promoted skills):

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Editable single-skill install:

```bash
npx skills add manoelcalixto/mattpocock-skills --skill=writing-great-skills
```

Select Codex when prompted. Use `npx skills update writing-great-skills` to refresh an editable install.

[Skill source](../../skills/productivity/writing-great-skills/SKILL.md)

## What it does

`writing-great-skills` is the reference you write and edit skills against — the shared vocabulary and principles that make a skill predictable.

A skill's job is to wrangle determinism out of a stochastic system, so the goal is not the same *output* every run but the same *process*. **Predictability** is the root virtue, and every design choice is judged against it — not against how clever, complete, or exhaustive the skill reads.

## When to reach for it

Type `$writing-great-skills`, or Codex may select it automatically when you are authoring or revising an agent skill.

Reach for it whenever you're authoring a new skill or editing an existing one and want it to behave the same way every time: deciding invocation mode, writing a description, choosing what lives in `SKILL.md` versus a linked file, or diagnosing why a skill misfires.

## Cognitive load

The concept the whole reference turns on is **cognitive load** — and its counterpart, **context load**. Every skill spends one or the other:

- A **model-invoked** skill keeps a description in the window every turn, so it costs **context load** but fires on its own.
- A **user-invoked** skill strips that description; it costs zero context load, but now *you* are the index that has to remember it exists — that's **cognitive load**.

This distribution makes every promoted skill model-invoked, accepting the context load so Codex can discover the whole set while every skill remains explicitly reachable with `$skill-name`. In sets that opt skills out of implicit selection, a **router skill** can still reduce the cognitive load of remembering them. Once you're thinking in these two loads, most authoring decisions — split or don't, inline or disclose, implicit or explicit-only — become the same trade made in different places.

## The other levers

The rest of the reference is the toolkit for spending those loads well:

- **Leading words** — a compact concept already in the model's pretraining (_tight_, _red_, _tracer bullet_) that the agent thinks with while running the skill. It anchors execution *and* invocation in the fewest tokens; hunt restatements that a single word can retire.
- **Information hierarchy** — the ladder from in-skill step, to in-skill reference, to external reference behind a **context pointer**. **Progressive disclosure** is the move down that ladder so the top stays legible.
- **Pruning** — single source of truth, relevance, and the no-op test applied sentence by sentence, against **sediment** and **sprawl**.
- **Failure modes** — **premature completion**, **duplication**, **sediment**, **sprawl**, **no-op** — to diagnose a skill that isn't behaving.

## Where it fits

This is a reach-for-it-anytime standalone reference — the meta-skill you consult while building the rest of the set, not a step in a chain. Its natural neighbour is any router you maintain; when you're unsure which skill or flow fits a task, [ask-matt](../engineering/ask-matt.md) routes you over the whole set.
