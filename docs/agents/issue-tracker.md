# Issue tracker: GitHub fork

Issues and specs for this repo live in GitHub Issues on `manoelcalixto/mattpocock-skills`. Use the `gh` CLI for all operations.

Every `gh` issue and pull request command must pass `--repo manoelcalixto/mattpocock-skills`. Do not rely on automatic repository inference because this checkout also has the external `mattpocock/skills` upstream remote.

## Conventions

- **Create an issue**: `gh issue create --repo manoelcalixto/mattpocock-skills --title "..." --body "..."`.
- **Read an issue**: `gh issue view <number> --repo manoelcalixto/mattpocock-skills --comments`, also fetching labels.
- **List issues**: `gh issue list --repo manoelcalixto/mattpocock-skills --state open --json number,title,body,labels,comments`.
- **Comment on an issue**: `gh issue comment <number> --repo manoelcalixto/mattpocock-skills --body "..."`.
- **Apply or remove labels**: `gh issue edit <number> --repo manoelcalixto/mattpocock-skills --add-label "..."` or `--remove-label "..."`.
- **Close an issue**: `gh issue close <number> --repo manoelcalixto/mattpocock-skills --comment "..."`.

## Pull requests as a triage surface

**PRs as a request surface: no.**

When changed to `yes`, PRs use the equivalent `gh pr` commands with the same explicit `--repo manoelcalixto/mattpocock-skills` target.

GitHub shares one number space across issues and pull requests. Resolve a bare number with `gh pr view <number> --repo manoelcalixto/mattpocock-skills`, then fall back to `gh issue view <number> --repo manoelcalixto/mattpocock-skills`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in `manoelcalixto/mattpocock-skills`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo manoelcalixto/mattpocock-skills --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with child issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes, Decisions-so-far, and Fog body.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue. Where sub-issues are unavailable, add it to a task list in the map body and put `Part of #<map>` at the top of the child.
- **Blocking**: use GitHub native issue dependencies. Where dependencies are unavailable, use a `Blocked by: #<n>` line.
- **Frontier query**: list open children, then exclude issues with an open blocker or an assignee.
- **Claim**: assign the issue to the driving developer.
- **Resolve**: comment with the answer, close the issue, then append a context pointer to the map.
