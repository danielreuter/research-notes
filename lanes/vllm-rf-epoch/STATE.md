---
id: vllm-rf-epoch/state
lane: vllm-rf-epoch
kind: state
created: 2026-09-25T17:48Z
updated: 2026-09-26T00:55Z
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

## 20:40Z (decision 2030Z: partial epoch, deadline 03:00Z, budget $130)
- `73a9a90a` epoch item 7: `research_tools.CLOSURE` + `verity/evaluation/**` (the only core package missing; commitments,
  ir, ml, verification, errors.py already in). code_identity 54ed9053… (1191 files) -> e58416b9… (1194). Key-only: the regression's
  `attempt_provenance` is skipped without VERITY_REGRESSION_CANDIDATE, and no other check reads the closure.
- `vyv-rf-epoch-big` (`p7xeovgrfzatpz`, 2x L40S, 233 GB cgroup, $2.18/h) created 20:20Z by the loop: bootstrap `r20260925-202051-bcc1`,
  then #68 on GPU 0 (`r20260925-202204-ecb5`, tree `89cd9d1a`). tp70b is also 233 GB; #70 via tp_stage since 20:30Z.
- The row_pod planner (`telemetry.admission plan`, PAIRS=1), in MiB: #68 commit 191,021 and #67 193,326 fit 222,209 (233 GB).
  #11 commit 229,925 and match 148,512 fit only tp70/h100 (239,372). #39 build 497,248 and commit 609,291 fit no pod.
  Dense rows use uncalibrated phi3 coefficients and overestimate: #4 match is predicted at 125,105 but ran at 80 GB peak. So
  #11/#39 are **not re-baselined** unless a >= 233 GB L40S slot frees early enough: none is free (big #68, tp70 #67, tp70b #70,
  tp75 #75).
- #11 is kept off moe67: the `skip11` run `r20260925-202938-00c9` stops its row_pod.sh when it starts, so rows.sh moves on to #23.

## 21:40Z check
- #4 (moe67): Build PASS (6302 s; Program 262201f9…, manifest 990e2d1f…), Match PASS, **Commit crashed (NOT_RUN)** in
  `native_host.verify` -> `scheme.chunk_header` -> core `vllm_v1.chunk_header`:
  `InvalidArtifact: M must be an integer in [0, 4294967296), got 5036944512`. **Finding, not a re-baseline:** core's u32 check on
  the fa2h header's M (c1's core-routed chunk_header) rejects a layout value that the integration passes above u32. Rows with
  larger steps may hit it too. #4 stays on old expected unless explained.
- #11: skipped on moe67 at 20:59:39Z (skip11). #23 has been running on moe67 since 20:59Z.
- #57 (moe68): Build PASS (6321 s; 9020930a…, manifest 21a77237…), Match FAIL (no fold; #57 is a FAIL-class row); Commit running.
- #73 (h100): Build PASS 10,713 s (345ebaf9…, manifest 69598f76…); Match running. #74 follows (Build ~3 h: borderline for 02:30Z).
- #70 (tp70b, tp_stage): Build PASS 2179 s (r0 508c0f77…, r1 9c2554f1…); Match check pass, fold next.
- #67 (tp70), #68 (big), #75 (tp75): Builds running.
- Pre-PR-#29 recording trees: no `verity_sampled_proofs` workaround needed now. For the final rebaseline on a merged tree, set
  PYTHONPATH+=$TREE/protocols/sampled_proofs on the pod (2055Z/2058Z handoffs).

## 22:08Z (handoff 2145Z: m32 fix coming; hold the Commits)
- #57's Commit also hit the overflow (`M ... got 7953086784`, 563 s). Every B >= 8 row's prefill step is above 2^32 words, so
  every Commit is held: a `holdcommit.sh` run on each pod stops any `row_pod.sh`/`tp_stage.sh ... commit` at start (log
  `$RUN/hold.txt`; `touch /workspace/epoch-release-commits` ends it). Runs `r20260925-220648-{b74c moe67, f596 moe68, e8e7 tp70,
  e634 tp70b, 8419 tp75, 0059 h100, 9104 big}`. Builds and Matches continue, and rows.sh moves to its next row.
- When m32's sha arrives: cherry-pick it (non-epoch) onto lane/vllm-rf-epoch, then re-run Commit only, on each row's own pod, with
  SWEEP_DIR = that row's recording run's sweep. Needed for #4, #57, and every row whose Build+Match PASSes or is a FAIL-class Match.
- Row Commits done so far: #101 PASS (its M is under 2^32).

## 22:15Z: m32 fix cherry-picked; Commits released onto the fixed tree
- `ad8050e9` = cherry-pick of m32's `271a0952` (pre-gate fix sha; non-epoch): `scheme.chunk_header` passes `M & 0xFFFFFFFF`
  (+ `test_production_vectors.py`). Digest-neutral per m32. **Every row Commit from now on runs at `ad8050e9`**, over Build+Match
  recorded at `a784d421` (#67 and #68 at `89cd9d1a`).
- Per pod: `commitonly.sh` waits for the pod's recording chain to end, then re-runs Commit only, into the recording run's sweep.
  `holdold.sh ad8050e9` stops any pre-fix-tree Commit (the recording chains' own Commit attempts). Old holdcommit released.
  Runs `r20260925-221340-{f2ea tp70 #67, 4631 big #68, 926f tp70b #70, 4d89 tp75 #75, 6ae1 moe67 #4 #23, cd7f moe68 #57 #60,
  d321 h100 #73}`.
- h100: #74 dropped (Build ~3 h would end after 02:30Z). The rows.sh kill at 22:12Z also killed the recording run's supervisor
  (`r20260925-175445-08bb`), so that run won't publish on its own. #73's row_pod (pid 4223) is still in Match.
- **Custody gap to close before terminating any pod:** Commit re-runs write into the recording runs' sweep dirs, which the
  recording runs' custody has already published (or, for 08bb, never will). Do a custody-copy run of each pod's sweep, then run
  rebaseline on the pod.

## 23:45Z
- Dropped, staying on old expected:
  - **#75**: rank Build of request LP1024_T127 hit `TIMEOUT after 7200s`, and there's no time for a rerun.
  - **#73**: Commit OOM-killed at the 251 GB cgroup (`memory.events oom_kill 1`) after C2 compare. Build PASS `345ebaf9…`,
    Match PASS. Small-file copy of its recording run in `r20260925-234027-23b6` (PRESERVED).
  - **#74** (time), **#11, #39** (memory).
- tp75 and h100 drained and terminated at 23:44Z.
- The first commitonly runs never started: their wait matched the recording runs' `research run` supervisors, which were still
  uploading custody (tp70b: 38 GB since 22:06Z). Relaunched with anchored patterns as `r20260925-233854-{4602 tp70b #70,
  9e59 moe68 #57 #60, 42c8 tp70 #67, 8ece big #68, c7c4 moe67 #4 #23}`. #70 and #57 Commits started at 23:39Z.

## 00:55Z
- Commits: #57 FAIL (local_replay; a FAIL-class row). #60 refused by F-dA-15 (121,309 > 119,209 MiB), re-run with
  VERITY_ADMIT_OVER_BOUND=1 (`r20260926-004846-55a8`). #4, #67, #70 running. #23: Build PASS 10,183 s, but **Match FAIL (NO FOLD)** on a
  GREEN row: a finding. Its Commit runs after #4.
- The old commitonly runs (221340-*) had survived the pgid kill (their bash lived in another process group). moe68's re-ran
  #57/#60 after 9e59: sequential, same tree, #57's final outputs are cd7f's. All old ones were killed at 00:47Z.
- #68 dropped (time); big terminated at 00:53Z. Golden recorded on moe67 (`r20260925-175229-a415/golden/`).
- Rebase runs `r20260926-004934-{9d5e moe67 r4|r23|r101, ec89 moe68 r57|r60, d097 tp70 r67, 20d1 tp70b r70}` (78cb went with big).
- Status handoff: `lanes/vllm-coordinator/20260926T0055Z-handoff-from-vllm-rf-epoch.md`.

## 07:58Z: overnight goal 8 (dropped rows, evidence only, no write; ~$60)
- #23 confirmation on `vyv-rf-epoch-bisect-23` (0hwhyqwzqmmeym, 251 GB): Build PASS 7605 s (2bdeb8e3, manifest e55e5407), Match
  PASS (fold True). Commit running since 06:56Z; stop by 08:55Z ($12 cap). Then #11 starts on the same pod (`r20260926-075108-6123`, after.sh).
- #39: `vyv-rf-epoch-dropped-39` (oqwbnrvq6or9gb, 2x L40S, 377 GB, $2.18/h), rows `r20260926-075241-f3e2` (GPU 0).
- #75: `vyv-rf-epoch-dropped-75` (q50qthz4jqtsjs, 2x L40S, 377 GB), rows `r20260926-075240-af98` (tp_stage, BUILD_TIMEOUT 14400).
- #68: `vyv-rf-epoch-dropped-68b` (se1yqv9bnshs0l, 2x L40S, 377 GB), rows `r20260926-075702-d929` (GPU 0, BOOT_CASES). The first pod
  (dropped-68) came up with only 188 GB and was terminated at once.
- #73: not started: an H100 with more than 251 GB won't fit the ~$60 (4 L40S pods at $8.72/h use it by ~15:00Z). A budget gap unless
  a row ends early.

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
