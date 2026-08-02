# Wayfinder

## Install

Native Codex plugin (installs all promoted skills):

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Editable single-skill install:

```bash
npx skills add manoelcalixto/mattpocock-skills --skill=wayfinder
```

Select Codex when prompted. Use `npx skills update wayfinder` to refresh an editable install.

[Skill source](../../skills/engineering/wayfinder/SKILL.md)

## What it does

`wayfinder` takes an effort too big for one agent session — wrapped in fog, where the way from here to the goal isn't visible yet — and charts it as a **shared map** of **decision tickets** on your issue tracker, then resolves them one at a time until the way is clear. It **plans, it doesn't do**: every ticket resolves a decision — a question to settle, not a slice of a build to execute — and the map is done when nothing is left to decide before someone goes and builds the thing — so it produces decisions, not deliverables.

## When to reach for it

Type `$wayfinder`, or Codex may select it automatically when a huge, foggy effort exceeds one agent session and the implementation path is not yet visible.

Reach for it when an effort is **more than one agent session can hold** and the route to its **destination** is still foggy — you can feel the shape of the work but can't yet write it down as a spec or a plan. For turning an *already-clear* thread into a spec, use [to-spec](../engineering/to-spec.md); for slicing an already-understood plan into buildable tickets, use [to-tickets](../engineering/to-tickets.md). Wayfinder sits upstream of both: it's what you run when there's too much fog to spec directly.

## Prerequisites

The map and its tickets live on the repo's issue tracker, so wayfinder needs the tracker wiring that [setup-matt-pocock-skills](../engineering/setup-matt-pocock-skills.md) lays down — it seeds a "Wayfinding operations" section describing how the map, child tickets, blocking, and frontier queries are expressed for GitHub, GitLab, or local-markdown. Absent that doc, wayfinder defaults to a local-markdown map.

## The map is an index, fog is the frontier

The **map** is a single `wayfinder:map` issue whose tickets are its child issues — one shared URL the whole team can watch. It's an **index, not a store**: each decision lives in exactly one place (its ticket), and the map only gists and links, never restates. A session loads the map at low resolution and zooms into individual tickets on demand.

Beyond the live tickets lies the **fog of war** — decisions you can tell are coming but can't yet pin down. The test for whether something is a ticket or still fog is whether you can *state the question precisely now*, not whether you can answer it. Resolving a ticket clears the fog ahead of it, **graduating** whatever's now specifiable into fresh tickets. The **frontier** is the open, unblocked, unclaimed tickets — the edge of the known — and it's what the tracker's native blocking renders visually, so you see what's takeable without opening the map. Fog only gathers *toward* the **destination**; work past it is ruled **out of scope**, closed, never graduating.

Every ticket is **HITL** (human in the loop — grilling, prototype) or **AFK** (agent alone — research); a HITL ticket only resolves through a live exchange, so the agent never answers its own questions. Research stays a real ticket — a shared blocker downstream decisions hang on — and uses `$research` subagents in parallel when Codex collaboration is available. Each writes a unique artifact in the shared working tree; the sequential fallback is disclosed when collaboration is unavailable.

## It's working if

- Naming the **destination** is the first act — before any ticket exists — because it fixes the scope every ticket is measured against.
- One map is one `wayfinder:map` issue; tickets are its child issues, referred to by **name**, never a bare `#42`.
- A session resolves **at most one ticket** (research tickets excepted), records the answer as a resolution comment, closes the ticket, and appends a one-line pointer to *Decisions so far*.
- If the opening grill surfaces **no fog**, it stops and tells you the journey is small enough to skip the map.

## Where it fits

`wayfinder` is a big-idea **on-ramp**: an effort too large and foggy to spec in one sitting generates a cleared map of decisions, which then merges onto the main build flow. When the fog is pushed back and the way is clear, hand off to [to-spec](../engineering/to-spec.md) to schedule the multi-session build (or, if the effort turned out small, implement directly). It leans on [grilling](../productivity/grilling.md) and [domain-modeling](../engineering/domain-modeling.md) to resolve individual tickets, and on [prototype](../engineering/prototype.md) and [research](../engineering/research.md) for the ticket types that need them. When you're unsure which skill or flow fits, [ask-matt](../engineering/ask-matt.md) routes you.
