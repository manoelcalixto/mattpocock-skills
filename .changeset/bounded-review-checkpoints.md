---
"mattpocock-skills": patch
---

Bound automatic code review to one stable checkpoint instead of restarting after every fix commit.

- `implement` now commits a visible checkpoint before review, applies cited findings in one fix batch, and permits at most one eligible follow-up per axis.
- `code-review` pins the exact head SHA, prevents recursive reviewer fan-out, and defines the terminal rule after a follow-up.
- `implement-spec` reviews only the fully integrated PR branch, not each ticket commit, before handing the result to human review.
