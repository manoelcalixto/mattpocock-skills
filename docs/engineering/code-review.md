# Code Review

## Install

Native Codex plugin (installs all promoted skills):

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Editable single-skill install:

```bash
npx skills add manoelcalixto/mattpocock-skills --skill=code-review
```

Select Codex when prompted. Use `npx skills update code-review` to refresh an editable install.

[Skill source](../../skills/engineering/code-review/SKILL.md)

## What it does

`code-review` reviews the diff between `HEAD` and a fixed point you supply — a commit, branch, tag, or merge-base — along two separate axes: **Standards** (does the code follow this repo's documented conventions?) and **Spec** (does it implement what the originating issue or spec asked for?). It runs each axis as an independent pass and reports them side by side. With Codex collaboration available the passes use parallel read-only subagents; otherwise they run sequentially with reduced contextual independence disclosed. It never merges or re-ranks the two sets of findings.

## When to reach for it

Type `$code-review`, or Codex may select it automatically when you ask to review a branch, a PR, work-in-progress changes, or anything "since X".

Reach for this when there is a diff to judge against a known-good point and you want the two questions — *is it built right?* and *is it the right thing?* — answered independently. It runs at the end of the build loop; for actually writing the code test-first, use [tdd](../engineering/tdd.md), and for building a whole spec into code use [implement](../engineering/implement.md), which runs its own `$code-review` pass before committing.

## Prerequisites

The **Spec** axis needs somewhere to find the originating spec — an issue reference in the commit messages, a path you pass in, or a spec under `docs/`/`specs/`. That issue-tracker wiring comes from [setup-matt-pocock-skills](../engineering/setup-matt-pocock-skills.md); without a spec the Spec axis simply skips and says so. The **Standards** axis needs nothing set up — it always carries a built-in Fowler smell baseline even in a repo that documents no conventions.

## Two axes, never merged

The defining idea is the **two axes**. **Standards** asks whether the diff conforms to how this repo writes code — its `CODING_STANDARDS.md` or `CONTRIBUTING.md`, plus a fixed baseline of ~12 Fowler code smells (Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, …). Two rules keep the baseline safe: a documented repo standard always overrides it, and every smell is a judgement call, never a hard violation. **Spec** asks the orthogonal question — does the code do what the issue or spec actually asked, without missing requirements or smuggling in scope creep?

The final report presents the independent passes under separate `## Standards` and `## Spec` headings with a per-axis summary. There is deliberately no single winner across axes.

## It's working if

- It pins and confirms the fixed point first (`git rev-parse`), failing fast on a bad ref or empty diff before either review pass.
- Standards and Spec findings arrive in two distinct blocks, each citing its source — a repo standard or baseline smell for one, a quoted spec line for the other.
- When no spec can be found, the Spec axis reports "no spec available" instead of inventing requirements.

## Where it fits

`code-review` is the review step at the tail of the main build chain:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review
```

Its closest neighbour is [implement](../engineering/implement.md), which drives the build and calls this as its own review pass before committing; upstream, the spec it checks against is produced by [to-spec](../engineering/to-spec.md) and [to-tickets](../engineering/to-tickets.md). When you're unsure which skill or flow fits, [ask-matt](../engineering/ask-matt.md) routes you.
