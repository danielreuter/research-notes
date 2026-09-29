---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge requests · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T09:20Z

# #395 and #397 (both on #337 `903c60c6`): APPROVED, after #343 in the #337 stack

| PR | Head | What | Checked |
|---|---|---|---|
| #395 | `4fb7c730` | Re-pins the 18 canonical profile fixtures. Each gains exactly one line, `"construction": null`, and the 18 class-A `KNOWN_FAILURES` entries are deleted. No profile id or digest moves | `tests/engine/test_profiles_generic.py`: all pass |
| #397 | `b4c651c1` | #101's records test lists the records tree and fetches the capture log by exact path. It skips by name when the store lists or fetches nothing, and it checks `match_compare.json`'s histogram only where the tree carries it; the refold must still be canonical-equal. Its class-E entry is deleted | `test_fold_sampler_construction.py` passes **with the store reachable** (the refold ran, it didn't skip), and so do the vLLM lints |

**They're independent** (they touch different files). Both go after #343. The lowering lane's `test_registry_one_process` PR goes alongside when its head arrives.

**#348:** the prep lane ran #349's stored-Build test against the live store, and it passes. #348's two heavier stored-Build tests (#75 and #70; #75 was OOM-killed on my 15 GB VM) still need a run on a check pod with 32 GB or more. Please confirm them in #348's train check.
