# Research

## Install

Native Codex plugin (installs all promoted skills):

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Editable single-skill install:

```bash
npx skills add manoelcalixto/mattpocock-skills --skill=research
```

Select Codex when prompted. Use `npx skills update research` to refresh an editable install.

[Skill source](../../skills/engineering/research/SKILL.md)

## What it does

`research` answers a question by reading the sources that own the answer and leaving a cited Markdown file behind. It works only from **primary sources** — official docs, source code, specs, first-party APIs — never a secondary write-up of them, so what it saves is traceable back to something authoritative rather than a summary of a summary.

## When to reach for it

Type `$research`, or Codex may select it automatically when you request a reusable cited research note or delegate primary-source reading. It should not intercept an ordinary fact question that does not need a repository artifact.

Reach for it when the next step is *finding something out* — how an API behaves, what a spec actually says, whether a claim holds — and you'd rather not stall your own thread doing the reading. For sharpening a plan by interview instead of by reading, use [grilling](../productivity/grilling.md); for exploring what to build with throwaway code, use [prototype](../engineering/prototype.md).

## Delegated legwork

The defining move is that the reading runs in a Codex **subagent** when collaboration is available. It follows each claim back to its primary source and drops a single cited Markdown file into wherever the repo keeps such notes. Without collaboration, the same work runs in the current task and the fallback is disclosed. Research is legwork you delegate, not thinking you outsource — you get back a document to react to, with its sources attached.

## Where it fits

A reach-for-it-anytime standalone that feeds the thinking skills: the file it produces is something to grill, plan, or design against, so it sits upstream of work like [grilling](../productivity/grilling.md) and [to-spec](to-spec.md) rather than in the build chain. For the whole map, see [ask-matt](ask-matt.md).
