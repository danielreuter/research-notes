---
id: vllm-tp-v2/20260924T1810Z-70-commit-fail-diagnosis
lane: vllm-tp-v2
kind: report
status: open
repo: verity
---
# #70 Commit FAIL (`r20260924-021402-69d8`): likely cause of the AllGather2 naming split

The integrator read out the result in `lanes/integrator/20260924T0240Z-from-vllm-tp-v2-ready-4f3a1e7.md`. Every compared value is equal. Two legs fail:
- `query_population`: per rank, 25,408 replay VUs are outside Q(P) (first `model.layers.0.self_attn.all_gather2_165/out`), and 25,408 Q(P) identities have no rows (first `model.layers.0.self_attn/out`).
- `cross_rank_collectives`: AllGather2_v1 has 161 sites and 1 covered.

This diagnosis is from reading staging `f0810a11`. I have not rerun anything: tp2x and cpu3 are both terminated.

## Likely cause: the global manifest keeps one request's alias table
- `query/v1_bridge.py` `build_global` (~line 750) writes `"op_path_aliases": parts[reqs[0]["request_id"]]["op_path_aliases"]`. That is the first request's table only.
- Before tp-v2 this was harmless. The table held only shared-module aliases (rotary), which are the same in every request.
- Since `4f3a1e75` the table also holds collective-site aliases. Under the runtime-correspondence record each key is `<module>.<fx node>` (for example `model.layers.0.self_attn.all_gather2_165` → (`model.layers.0.self_attn`, k)). The fx node name is per Program, so each request has its own keys.
- The replay addresses a site at its raw path (`ProgramIndex._v2_module` = `Population.program_path`). The population check resolves that path through the manifest's table (`resolve_op_path`). The sites of requests 2..8 find no entry, fall back to invocation 0 at the raw path, and land in `vus_outside_query`. Their identities land in `identities_without_rows`.
- The 161 distinct `self_attn.all_gather2_<n>` site paths support this. Stable names would give 32 (16 layers × q, k).
- The manifest digest does not cover `op_path_aliases`. That is why `ede1ad81` agreed on every path (v1, record, fallback, trial merge) while the Commit failed. The cpu3 check "op_path_aliases equal" compared the tables of two builds from the same code, so it could not catch this.
- `merge_ranks` unions the rank parts' tables (raising if they disagree), but each part already carries only its first request's table.

## Fix direction (not done)
- In `build_global`, take the union of every request's `op_path_aliases` and refuse by name if two requests map one key differently, the same way `merge_ranks` already does for ranks.
- Add an offline test with two request Programs whose site fx nodes differ.
- `cross_rank_collectives` probably keys strata by the raw site path too (`model.layers.<k>.self_attn.all_gather2_<n>` has no stratum). Check whether it should resolve through the same table.
- Re-running #70's Commit needs a 2×L40S pod. The Build (`art:962a12b3…`) and Match (`art:7ecab74a…`) artifacts are preserved and can be reused.
- The other two legs are separate: `sampled_replay` partial (`RMSNormTriton_v1{N=2048}` q_norm / k_norm `recycled-window`), and `fold_match_binding` None (Match was collective-level only).

## Housekeeping
- The lane branch was merged (`815b837c`) and deleted from origin. The worktree `~/projects/verity-main-wt/vllm-tp-v2` is gone.
- I removed my trial worktree `/tmp/tpv2trial` and the expired store credentials in `/tmp/tpv2run/`.
- tp2x (terminated ~04:08Z by the integrator) and cpu3 no longer exist, and the stale cpu3 `tpv2.json` reservation went with cpu3.
