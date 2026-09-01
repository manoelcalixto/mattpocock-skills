# Domain docs

How the engineering skills consume this repo's domain documentation.

## Before exploring, read these

- `CONTEXT.md` at the repository root.
- Relevant ADRs under `.agents/adr/`.

If an artifact does not exist, proceed silently. `domain-modeling`, reached through `grill-with-docs` and other design skills, creates domain artifacts lazily.

## File structure

This repository uses a single-context layout:

```
/
├── CONTEXT.md
├── .agents/
│   └── adr/
└── skills/
```

## Use the glossary vocabulary

Use domain concepts as defined in `CONTEXT.md`. Do not drift to synonyms that the glossary explicitly avoids.

If a required concept is absent, reconsider whether it belongs to the project language or note the gap for `domain-modeling`.

## Flag ADR conflicts

Surface any conflict with an existing ADR explicitly instead of silently overriding it.
