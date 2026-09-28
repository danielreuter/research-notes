---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T07:14Z · re: `vllm-epoch-prep/20260928T0725Z-handoff-from-vllm-coordinator-s1d.md`

# S1b gap found: it refuses multi-request manifests, and #57 and #74 are B=8. Fix in progress; S1d = S1b, per your (a)

**The gap.** S1b ([#253](https://github.com/danielreuter/verity/pull/253) @ `5a423c08`) refuses any manifest with more than one request.
- #57 and #74 are both batch-8 rows. Their Commits run against a global manifest (`compose_global`: 8 requests, request-local identities, `engine_steps` compositions). As built, both would exit 3 on the pod.
- My coverage figures (576 / 576 and 41,870 / 41,870) were measured on single-request Programs. They hold per request, but not yet for the packed B=8 step.

**The fix** (S1b's implementer, stacked on `5a423c08`):
- plan per request component;
- at each engine step, split the module's packed arguments by the runtime's request rows, checked against the declared composition and failing closed;
- evaluate each request's rows, and bind them the way B≥2 module outputs are bound;
- acceptance: coverage on #57's and #74's **real global manifests**, rebuilt under S1 from the stored Builds.

It also removes the avoidable part of the ~10 GB per logits step (weight words converted once per Commit, not per step), and measures #57's real per-step host time at B=8. Target: pushed and reviewable by about 09:30Z, inside S1b's 12:30Z window.

**S1d:** per your (a), there's no new source. S1b covers #57 (norm chain plus pre-softcap logits). The pod sizing and the added time go to the epoch-run lane once they're measured on the B=8 path, with your 90-minute stop rule.

**Scope note:** the S1 manifest build and `word.check_query` are unaffected. They already build global manifests per component (S1's `_with_partitions` names every component's partition).
