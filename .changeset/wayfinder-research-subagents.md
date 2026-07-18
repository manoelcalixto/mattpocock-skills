---
"mattpocock-skills": minor
---

Wayfinder now burns research tickets down with Codex sidecars instead of leaving them parked for a separately launched session.

Research stays a real ticket type — it's a genuine shared blocker that downstream decisions hang on, and that dependency is exactly what the frontier's blocking edges exist to render. What changes is how it's resolved: because research is AFK, charting doesn't stop and read it. After creating the tickets, the charting session uses the shared `orchestrate-agents` contract to run bounded V1/V2 workers with isolated briefs and unique report paths. Workers never switch branches, commit, mutate the tracker, or edit the map; the root verifies their reports and resolves the tickets once. Research tickets are the one exception to *one ticket per session*.
