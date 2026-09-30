---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# vLLM follow-up epoch: draft plan (Sep 28, about 5:10 PM PT). Nothing launched

**Where the epoch ended** (the epoch lane's final handoff):
- **Written:** #73 only, under rule (a), with its coverage backfill pending #325.
- **Deferred:** the other 12 rows, each keeping its old record.
- **Spent:** $145.07 of $250 (at most $146.51).

## Prerequisites, all on main before GO, in this order

1. **#337 + #338:** the vLLM suite gated in `check`, and the Tools closure over all of `verity/**`. This goes first because it moves Tools identity: no attempt or Build stored before it is reused, and **every row rebuilds**.
2. **The epoch's pending fixes:** #298 and #301 (manifest of record and `query.word_check`, via D3′), #321 (the fold follows the Program's sampler construction) and #325 (the harness coverage check). Then the #73 coverage backfill commit.
3. **The TP2 MoE two-producer fix** (prep lane):
   - the MoE block's `AllReduce2` output modelled as its own member, so `tp_peer_binding.n_unbound` is 0 on #75's and #70's stored Builds (CPU);
   - `build manifest` exits non-zero on `complete False` for a row of record.
   - It gates #70 and #75.
4. **#101's G4 fold-count defect** (prep and lowering lanes): the address map declares 32 more instances than the component (the v2 top-p selects). The fix is shown bijective on try 5's stored Build and records (`art:0e6911da`, `art:55029fe0`) on CPU. It gates #101.
5. **Lift the call-boundaries stop** in the row driver: `call_boundaries` stops a row only if some identity has no attached source (`call_boundary_source` coverage below 100%). With S1b on main, #74 and #57 then run to Commit.
6. **The regression resolver fix:** the harness fetches the row's frozen reference from the store, verified against its sha256 pins. This replaces `side_record.sh`.
7. **The pod-side stops, the lesson of #68:**
   - `stop_after` and each stage deadline run inside the pod job, as `epoch_row.sh` stage markers plus the job's own `--timeout`;
   - the store and `preserved` run before the job exits;
   - custody keys are valid for the job's full timeout plus 1 h;
   - the backstops are the control pod's `research pods guard` for cap and deadline. Nothing the row's outcome depends on runs on a VM.
8. **Conditional rows:**
   - #39 needs #244 (`GemmBias_v1`) on main;
   - #57 needs its host evaluation under about 90 min per Commit (norm-chain and softcap row kernels, a faster exact Gemm, or a `CLAIMS` tap of the pre-softcap `lm_head`);
   - #4 needs the audit of its FAIL-class PASS, whose class change goes to Daniel.

## Rows, the order and the shapes

The estimates use this epoch's measured stages: Builds of 3–4 h; the Match 0.5–1 h; the Commit 1.5–2.5 h without the manifest rebuild (#298), plus about 10 min per pair after the first; the store about 10 min. Every row runs at its record's pair count. There's no time window, only the budget; launch as stock appears.

| Order | Row | Shape | Est. h | Est. $ | Gate |
|---|---|---|---:|---:|---|
| 1 | #74 | 2× H100 secure, ≥ 500 GB | 10.7 | 75 (was 52; at $6.98/h, 52 stopped it in the Match) | prereq 5 |
| 2 | #11 | 2–4× L40S-class, ≥ 512 GB | 9 | 30 | — |
| 3 | #23 | 2× L40S-class, ≥ 512 GB (Commit admission 483 GiB) | 8 | 18 | — |
| 4 | #60 | 2× L40S-class, ≥ 376 GB | 7.5 | 16 | — |
| 5 | #67 | 2× L40/L40S, ≥ 240 GB | 8 | 14 | — |
| 6 | #68 | 2× L40S, ≥ 240 GB (its Build was lost) | 7.5 | 16 | — |
| 7 | #75 | 2× L40S TP2, ≥ 377 GB, `COMMIT_GPU_UTIL=0.70` | 6.5 | 14 | prereq 3 |
| 8 | #70 | 2× L40S TP2 | 5.5 | 12 | prereq 3 |
| 9 | #101 | 1× L40S-class, ≥ 94 GB, 1 pair, raised sampler `max_gates` | 2.5 | 3 | prereq 4 |
| 10 | #4 | 1× L40S, 3 pairs | 5 | 6 | the audit first |
| 11 | #39 | 2–4× L40S-class, ≥ 512 GB | 9 | 30 | #244 |
| 12 | #57 | 2× L40S | 7 | 15 | the host-eval speedup |
| 13 | canary + `known_roots.json` re-pin | 1× L40S | 1 | 2 | after the last row is written |

**Budget:**
- Core rows (1–10 plus the canary): about $183.
- Conditional #39 and #57: about $45.
- Total about $228. With a 15% contingency, **request a $260 cap**, or $210 if #39 and #57 stay deferred.
- After #74's raise to $75: core about $206, total about $251, still within the approved $260.
- The same controls as before: the committed-spend-plus-cap rule, the balance test with the $25 floor, and the `vyv-` guard owned by the vLLM coordinator.

**Also carried:** #325's coverage backfill of #73; the `test_no_dead_modules` `spec.py` fix; and #337's known-failure owners (triaged by the vLLM coordinator).
