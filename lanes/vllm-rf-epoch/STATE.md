---
id: vllm-rf-epoch/state
lane: vllm-rf-epoch
kind: state
created: 2026-09-25T17:48Z
updated: 2026-09-25T20:25Z
---
# vllm-rf-epoch: C3 identities + the re-baseline epoch (state)

- Agent bc-e66a058f (reused b5patc's VM). Brief `$STORE/internal/lane-briefs/vllm-epoch.md`.
- Branch `lane/vllm-rf-epoch` (pushed), worktree `/workspace-wt/epoch`, from b4c `5494e29f` (= `5c05ff6d` + main `38a8d35d`).
  main has since moved to `f7de4620` (b5patb merged: digest-neutral split; not merged in yet).

## Epoch commits
- `30427930` epoch: Programs cite core `AmpereBF16TcDot16_v2` (cherry-pick of c2b `dedf5313`; subject relabelled `epoch:`).
- `a784d421` epoch: profile id drops `gpu.pod` (now in header notes); `profile-fallback/v1` path raises (C3 / D12 a+b).

- `89cd9d1a` item 6 (digest-neutral, not `epoch:`): the host admission's lag = `global_program.workload_target(wl).lag()` via
  `commit.admission_lag` (the `pipeline.workload` import missed; broad except removed) + test in `tests/pipeline/test_admission_commit.py`;
  P10 `main` 1913 -> 1907. No regression check reads `commit/admission_*.json`, no launcher passes `--host-admit`. The declared lag is
  1 under async scheduling (the default), so on the rows it equals the old fallback: it doesn't explain the 12 GiB #67 shortfall.

## Deferred (larger than S; say so in READY / handoff)
- 2c `sm89-eager` label from probed capability: the κ profile id (`generic.profile_id(role, C, world)`) is fixed at CPU
  profile-build time, before any header is read; capability-derived ids mean selecting derived modules by (role, cc),
  and moving `expected/*.json` + 6 test pins. Not the 12-hex leaf-prefix profile id.
- 3 G1–G8 artifact keys: two namespaces (acceptance `gates.json` and GM-01 `global_match.json checks[].id`), ~30–40 files /
  500–700 touches, no agreed name map (`internal/g1-g8-artifact-keys.md`).
- 4 host `chunk-leaf-v1` label: `padding_steps` picks the padding leaf rule from the same label (`layout.startswith("chunk-leaf-v")`,
  in `padded_binding_map_of_committer` and `padded_map_of_record`), so relabelling host maps needs label and rule split first.
  None of the 13 rows is affected: all commit with `native_collect_v2b` + GPU tree (`row_pod.sh:822`, `tp_stage.sh:258`).

## Running (all registered, guard 90, driver 580, created 17:3x–17:49Z)
| pod | RunPod | shape | $/h | bootstrap run | rows planned |
|---|---|---|---|---|---|
| ~~vyv-rf-epoch-g1~~ (terminated) | k9n58r873y9d0s | 1x L40S, 188 GB | 1.09 | r20260925-174831-74aa (B0,LLAMA32_1B,B1,GEMMA2_2B,MISTRAL7B) | #67 (+OLMOE) |
| ~~vyv-rf-epoch-g2~~ (terminated) | qe443tt2vohzix | 1x L40S, 188 GB | 1.09 | (B0,B1,GEMMA2_2B,MISTRAL7B) | #68 (+OLMOE) |
| vyv-rf-epoch-moe67 | mzp252g5m1qswn | 1x L40S, 125 GB | 1.09 | r20260925-173935-1a0c (B0,OLMOE) | #101 #4 #11 #23 (+LLAMA32_1B) |
| vyv-rf-epoch-moe68 | 4ltk4vvdjnoq3o | 1x L40S, 125 GB | 1.09 | r20260925-174653-4b13 (B0,OLMOE) | #39 #57 #60 (+B1,GEMMA2_2B,MISTRAL7B) |
| vyv-rf-epoch-tp70 | m635zk3ooaylcm | 2x L40S, 251 GB | 2.18 | r20260925-174653-5401 (B0,OLMOE) | #70 |
| vyv-rf-epoch-tp75 | 3svupto9cex43o | 2x L40S, 204 GB | 2.18 | r20260925-174831-7d12 (B0,QWEN3_30B_A3B) | #75 |
| vyv-rf-epoch-h100 | tev3epl52xt8gd | H100 80GB HBM3 (SXM) | 3.49 | r20260925-174952-66c1 (B0,QWEN3_4B,QWEN3_4B_FP8) | #73 #74 + golden |
(#67/#68 Commit needs ~180 GB, hence the 188 GB pods; pod names predate that assignment.)

Row runs at `a784d421`, launched 17:54Z (each waits for its pod's bootstrap, adds `BOOT_CASES`, then rows in order):
- g1 `r20260925-175445-95ae` #67 · g2 `r20260925-175445-d7a7` #68 · moe67 `r20260925-175445-2424` #101 #4 #11 #23 then golden ·
  moe68 `r20260925-175445-4e8f` #39 #57 #60 · tp70 `r20260925-175445-cc81` #70 · tp75 `r20260925-175445-fa68` #75
  (GPU_UTIL 0.92, COMMIT_GPU_UTIL 0.80) · h100 `r20260925-175445-08bb` #73 #74.
- 17:52Z runs `r20260925-175229-*` failed at once (unexpanded `$RESEARCH_RUN_DIR` in the launch line); nothing ran.
Row driver: `/tmp/ep/rows.sh` (sent with `--send`): Build+Match, then Commit even on a Match FAIL, PAIRS=1, evidence
`$RESEARCH_RUN_DIR/sweep/<row>/`.

## 18:10Z changes (coordinator handoff 1810Z)
- Memory limits (cgroup): g1/g2 188 GB (= 175 GiB, b1c's #67 OOM point), moe67 125 GB (cgroup **v1**, `memory.limit`, not
  unbounded: the 1,007 GB is the host), moe68 125 GB, tp70 251 GB, tp75 204 GB, h100 251 GB.
- #67 (g1) and #68 (g2) stopped in Build at 18:1xZ; g1 and g2 drained and terminated (bootstrap runs PRESERVED).
- #67 -> tp70 GPU 0 after #70: run `r20260925-181422-250a` (`after.sh`, CUDA_VISIBLE_DEVICES=0), tree `89cd9d1a`.
- #68 -> `vyv-rf-epoch-big` (1x L40S >= 256 GB, or 2x with 300 GB), retrying until 21:00Z (tmux `big68`, `/tmp/ep/big68.sh`,
  log `/tmp/ep/big68.log`); on success bootstrap + #68 run automatically. No big pod yet (no capacity at 18:13Z).
- moe67's live run is `r20260925-175229-a415` (not `...-2424`, which failed on quoting): #101 PASS (build 573313ed, manifest
  ee65240e = c2b's epoch value), now #4.

## 20:25Z check
- `row_pod.sh` has no TP hook: #70 (17:55–19:38Z) and #75 first ran the TP1 path, which is invalid. `rows.sh` now picks `tp_stage.sh`
  for WORLD > 1. #75 relaunched on tp75 `r20260925-201729-6f0c` (tp_stage); #70 goes to the new `vyv-rf-epoch-tp70b` (`wto6vcl88f3aau`,
  2x L40S, 233 GB, $2.18/h; bootstrap `r20260925-201842-c282`, then `rows70-tp70b`).
- #39 Build OOM (rc 137) at 125 GB (moe68). #57 Build running, and its Match advisory would refuse at 119 GiB. #4 Build 2 h, now Match.
  #73 Build 2 h 20 min and going. #67 Build (tp70 GPU 0) since 19:38Z.
- #68: no >= 256 GB pod yet (loop to 21:00Z). Decision asked in `lanes/vllm-coordinator/20260925T2025Z-handoff-from-vllm-rf-epoch.md`.

## Next
- Before the final `write`: merge b4c `9689a1ef` (b4c + a5c; a5 removes `ops/row_pod.sh`) / main; record in READY that the
  recording trees (`a784d421`, `89cd9d1a` for #67/#68) lack a5 and b1 (digest-neutral by their gates). READY: flag `a784d421`'s
  `vllm_adapter.py` hunk under owner review (protected file). vyv- deadline now 00:30Z.
- Rows at `a784d421` once each bootstrap ends. Golden re-record (item 5, `/tmp/ep/golden.sh`) on a pod.
- `rebaseline.py run --record DIR` with `VERITY_REGRESSION_ROWS_ROOT=<run>/sweep` on each recording pod, then table / write.

## Open questions
- (none)

## Found, not fixed
- (none yet)
