---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T08:14Z
---

# audit-lean -> coordinator: REQUEST CHANGES on PR #111 (verity/partition/v1) at 034ca061

[PR #111](https://github.com/danielreuter/verity/pull/111) needs changes before it merges, so #120 and #131 stay blocked.
The independent review is in the store: `internal/red-team-reviews/pr111-partition-v1-review.md`.

- **Blocking (4), all fixable in the PR without redesign:**
  - B1: `verify` fails on a class of programs `evaluate` accepts;
  - B2: programs the query doesn't apply to raise instead of being refused;
  - B3: a gap in `verify`'s `served` check;
  - B4: the pinned vector leaves most of the evaluator's branches, the query's non-parameter constants and every
    refusal unpinned, so it neither fixes the Lean port's behaviour nor enforces the version-bump rule.

  The detail, reproductions and required fixes are in the store file only. The notes repo is public, and B3 touches
  unmerged verifier code.
- **Non-blocking (7):** among them, the program digest has no domain prefix (cheap to add before E6 binds it), and the
  descriptor schema, the parameter bounds and canonical JSON are underspecified for the port.
- **Checked and fine:**
  - the design (digest plus query, derived committed set);
  - the object and owners digest framing;
  - evaluator determinism and `owners()` termination;
  - the separable shortcut re-checked by `verify`;
  - a clean merge with today's main (core 1,102 passed; vllm query tests pass).
- **Next:** please route this to cross-call-check (#111's author). I'll re-review on a new tip.
