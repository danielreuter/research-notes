---
id: vllm-rf-epoch/state
lane: vllm-rf-epoch
kind: state
created: 2026-09-25T17:48Z
updated: 2026-09-25T17:48Z
---
# vllm-rf-epoch: C3 identities + the re-baseline epoch (state)

- Agent bc-e66a058f (reused b5patc's VM). Brief `$STORE/internal/lane-briefs/vllm-epoch.md`.
- Branch `lane/vllm-rf-epoch` (pushed), worktree `/workspace-wt/epoch`, from b4c `5494e29f` (= `5c05ff6d` + main `38a8d35d`).
  main has since moved to `f7de4620` (b5patb merged: digest-neutral split; not merged in yet).

## Epoch commits
- `30427930` epoch: Programs cite core `AmpereBF16TcDot16_v2` (cherry-pick of c2b `dedf5313`; subject relabelled `epoch:`).
- `a784d421` epoch: profile id drops `gpu.pod` (now in header notes); `profile-fallback/v1` path raises (C3 / D12 a+b).

## Deferred (larger than S; say so in READY / handoff)
- 2c `sm89-eager` label from probed capability: the κ profile id (`generic.profile_id(role, C, world)`) is fixed at CPU
  profile-build time, before any header is read; capability-derived ids mean selecting derived modules by (role, cc),
  and moving `expected/*.json` + 6 test pins. Not the 12-hex leaf-prefix profile id.
- 3 G1–G8 artifact keys: two namespaces (acceptance `gates.json` and GM-01 `global_match.json checks[].id`), ~30–40 files /
  500–700 touches, no agreed name map (`internal/g1-g8-artifact-keys.md`).
- 4 host `chunk-leaf-v1` label: `padding_steps` picks the padding leaf rule from the same label (`layout.startswith("chunk-leaf-v")`,
  in `padded_binding_map_of_committer` and `padded_map_of_record`), so relabelling host maps needs label and rule split first.
  None of the 13 rows is affected: all commit with `native_collect_v2b` + GPU tree (`row_pod.sh:822`, `tp_stage.sh:258`).

## Running
- `vyv-rf-epoch-moe67` (RunPod `mzp252g5m1qswn`, 1x L40S, 125 GB, 32 vCPU, $1.09/h, driver 580.126.20): bootstrap (B0, OLMOE),
  first `research run` still shipping git history (~17:39Z).
- Pod creation retries (tmux `epoch-create`, `/tmp/ep/retry_create.sh`): moe68, tp70 (2x), tp75 (2x), g1, h100 (SXM).
  L40S stock is low.

## Next
- Rows at `a784d421`: #67 on moe67 first, then the rest as pods appear. Golden re-record (item 5) on a pod.
- `rebaseline.py run/table/write --dry-run/write`.

## Open questions
- (none)

## Found, not fixed
- (none yet)
