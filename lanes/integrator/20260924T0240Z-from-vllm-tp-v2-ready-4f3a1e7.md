---
id: integrator/20260924T0240Z-from-vllm-tp-v2-ready-4f3a1e7
lane: integrator
kind: handoff
status: open
repo: verity
origin: lane/vllm-tp-v2
---
# vllm-tp-v2 is ready to merge: `4f3a1e75` (supersedes the `8227c75` note)

`origin/lane/vllm-tp-v2` = **`4f3a1e75`**. That is final unless the #70 Commit still running on tp2x finds a defect (bottom). I will append its result here either way.

## Since `8227c751`
- `b0c2e961`: task 1. TP rank Programs on the v2 query: the TP-04 rank-partial policy, `merge_ranks`, and the TP HOOK deleted. `tp_stage.sh` builds with `verity_vllm.query.cli build-global`.
- `e4a8734c`: task 3, cosmetics.
- `3cd4de33`: OLMoE TP rank profile. The all-heads q/k norm keeps the full model's width on a rank, which fixes #70 Match's `FoldError`.
- `4f3a1e75`: a rank Program's mid-module collective sites get the same identities under the runtime-correspondence record and the v1-annotation fallback. Before this, the record collapsed sites, and #70 built 330,020 identities (`aeecf271`) instead of 357,796.

## Merge onto staging `da63c971`: now two hunks, both in `v1_bridge.py`
- Your protocol-loop hunk is unchanged; I used your resolution.
- **New:** the module docstring. Staging adds the literal sentence and `4f3a1e75` adds the collective-site clause to the next bullet. Keep both (resolution below).
- Your recorded resolution no longer matches, because the conflict's preimage changed. I recorded the two-hunk resolution in the shared rr-cache (`~/projects/verity/.git`), so your merge should pick it up.
- My trial merge is **`0633de7d`**: detached, local only, in worktree `/tmp/tpv2trial`, sharing your object store. It includes the keep-list rename `verity_capture.bench.tp2_analyze` → `verity_capture.tp.analyze`.
- rr-cache housekeeping: I deleted 5 entries that my own accidental `git stash pop` created at ~02:09Z (`backends/AGENTS.md`, `accounting.py`, `vector_run.py`, `discrepancy_log.json`, `tools/research/.../cli.py`). None of them were yours.

The docstring resolution:

~~~
  module reads (F-r19-int-20) is not a pass here: such a Value crosses the boundary and is required by definition.  A literal (a Call
  that reads no Value, `module_body.literal_calls`) is the descriptor's: never a boundary Value, never protocol-required.
* WHERE a Value lives: the producing Call's recorded owning module (correspondence), mapped to the implementation's path; a
  collective SITE's at its enclosing module, invocation k (`collective_sites`).
~~~

## Offline results (vyv-v2cpu3, `venv312` without `verity` installed, single process, `-o addopts=`)
- Suites: `verity_capture/commit/tests`, `verity_capture/tp/tests`, `tests/query`, `tests/test_no_by_name_rules.py` (plus `tests/test_no_dead_modules.py` on the trial).
  - Lane `4f3a1e75`: **684 passed, 2 failed, 18 skipped**.
  - Trial `0633de7d`: **692 passed, 2 failed, 18 skipped**.
  - Both failures are the known `test_admit_r19_host_working_set.py` fork / gc-freeze pair (also in your staging baseline).
- Trial, locally: your targeted set (`test_module_body`, `test_literal_operands`, `test_no_dead_modules`) plus my TP tests: **260 passed, 1 skipped**.
- Allowlist: no change since `8227c751`.

## TP manifests: one identity set on every path
| row | v1 | v2, record (pod) | v2, v1 fallback (cpu3) | v2, trial merge |
|---|---|---|---|---|
| #70 OLMoE tp2 (`f17c7641`) | `ede1ad81` (357,796) | `ede1ad81` | `ede1ad81` | `ede1ad81` |
| #75 Qwen3-30B-A3B tp2 (`ea869b3f`) | `8880e805` (277,444) | — | `8880e805` | `8880e805` |

On the trial merge, the components and `op_path_aliases` are byte-equal to the lane's for both rows, so staging's sampler-literals do not move either TP row.

## #70 Commit (task 2), in flight
- Run `r20260924-021402-69d8` on vyv-tp2x, at `4f3a1e75`, from Build `art:962a12b3…` and Match `art:7ecab74a…`.
- Its manifest step: complete, **357,796 identities, digest `ede1ad81`**, `tp_peer_binding_n_unbound 0`, unmodelled `{}`.
- It is in the per-pair finalize steps now. ETA ~03:15Z, then sampled replay.
- I cancelled the earlier Commit `r20260924-012910-784d` (at `3cd4de33`, with the collapsed `aeecf271` manifest). The cancel intent is recorded in its run dir.
