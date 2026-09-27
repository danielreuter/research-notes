---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: reverify-fp4 (small cloud lane)

**Launch status:** READY (9:15 AM PT, Sep 25).

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `reverify-fp4`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/reverify-fp4.md`. Write your first checkpoint
> within 10 minutes.

## Why

poseidon-v1's two 5090 NVFP4 B-Ligero results (art:70f275ac, art:6740eb22; Poseidon2 rows, "(alg.)") fail closed in
re-verification. `backends/direct/ligero/reverify.py` `committed_trees` calls `relations.relation('fp4-nvf4')`, which isn't
registered, so it raises "unknown --relation". verify-night-2 found that the result's own binding, roots-match and negative
checks pass (`lanes/coordinator/20260925T1100Z-handoff-from-verify-night-2.md`). Fixing this fills the new-spec Table 2's
5090 · E2M1 · frame-v3 · Poseidon2 rows B-Ligero cell (flagged "(alg.)"), and it unblocks any later fp4 committed cell.

## Build

1. Register `fp4-nvf4` where `reverify.committed_trees` looks relations up, the same way fp8-ada / bf16-hopper are
   registered. Recompute its committed trees (a/b/y bindings, roots, cover) from the manifest's instance set. Per agkr-bound,
   fp4-nvf4 rows are x.bin's 68-byte steps. Use the committer the producer used (see poseidon-v1's report and the frame-v3 /
   core `verity.commitments` code). The recomputed roots must equal the dump's, byte for byte.
2. Tests in `reverify_test.py`: the honest fp4-nvf4 dump passes. Negatives: a flipped instance byte, a remapped VU, a wrong
   `set` block, a missing proof and a statement without a proof must all fail. Existing fp8 / bf16 cases stay green.
3. Re-verify art:70f275ac and art:6740eb22 with the fixed reverify, on a pod, from your branch. If they pass, record
   `verified=accepted --by reverify-fp4` with your commit in the ref. Also re-verify blake3-80gb's four H100 re-runs
   (art:6d067ed3, art:f4dc0501, art:4d43ab87, art:4d151f38): main 8a3aa083 now reads a run_files tree with manifest.json at
   the root, which is what blocked them. Record the same way.
4. **Unblock the first SHA-256 Table 2 cells (rule I).** The red team has labelled art:4aa258ee (fp8-hopper-x4+sha256,
   [0, 32768)) and art:fcd6a623 (bf16-hopper-x4+sha256, [0, 8192)), but the renderer rejects both because their re-packed
   instance sets have no `instance-equiv/v1` artifact. On a pod, run `instance_equiv --relation fp8-hopper-x4 --vus 32768`
   and `instance_equiv --relation bf16-hopper-x4 --vus 8192`, in PR #21's shape: `candidate` exactly the result's
   `workload_fingerprint.instances`, and `frozen` the frozen ref or its synthetic stream over the same range. Register
   each with `research data put --preserve`. Then re-run each document's `--check` from a **fresh** pod and record
   `verified=accepted` only if it reproduces. The renderer requires a verdict by someone other than the result's producer,
   b-ligero-sha256. See `lanes/coordinator/20260925T1255Z`-era x4 BLAKE3 precedents: art:d9b3724d, art:b6f2e1df.
5. A merge-ready handoff to the coordinator: tip, tests, negatives, and the verdict artifacts. Then send red-team-standard-hash-2
   (or the coordinator, if it's FINAL) the list of accepted cells that need `proof_class` labels.

## Limits

- Branch `lane/reverify-fp4` from `origin/main` (8a3aa083 or later). The cheapest CPU pod; `--custody-r2`; no laptop
  fetches. Terminate the pod at the end.
- Don't change any existing relation's recompute. If fp4-nvf4 needs a statement change (not only a registration), stop and
  say so: that would need a red-team review.
- FINAL: 16:00Z hard (9 AM PT) + 3 h = 19:00Z. Budget: $6 (pods).
