---
id: vllm-rf-f24/state
lane: vllm-rf-f24
kind: state
status: active
created: 2026-09-24T17:33Z
---
# vllm-rf-f24: identity and integrity (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D5, D6, D7, D10, D11, D13), §4 (P1, P4, P12); coordinator notes 16:25Z and 16:40Z.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f24`, branch `lane/vllm-rf-f24` from `72884c8a`.
- **Scope:** D5 one code identity (hot worker + TP commit key, reuse `harness/research_tools.py` closure); D6 `construction_version` sources resolved against the integration; D7 Build dtype from the engine; D10 remove core monkeypatch in `check/global_match_fast.py`; D11 full digests in `weights_of_record._eq`; D13 structured reason codes in `check/commit_verdict.py`.
- **Launcher:** `~/.research/bin/research` (coordinator's CLI). ssh wrapper `/tmp/rff24/ssh.sh` (recreate with `research pods ssh 0zb24mk1w6nb4o --print`).

## Done
- 17:33Z worktree created.
- 17:38Z pod `vyv-rf-f24-veritor-campaign` = RunPod `0zb24mk1w6nb4o` (cpu3g, 16 vCPU / 64 GB, 80 GB disk, EUR-IS-1, $0.64/h), created with
  `research pods create --name vyv-rf-f24 --cpu cpu3g --vcpu 16 --disk 80`.
- 17:41Z base tree `git archive 72884c8a` -> pod `/workspace/base`; `pod_bootstrap.sh --cpu` done (venv `/workspace/venv312`).
- 17:52Z GM-01 inputs fetched on the pod (row #23 = `llama32-1b__bf16__l40s__tp1__b64__i1024__o128__mixed__greedy__bi-eager`, the v2-acquisition record
  of lane vllm-v2-gm-scale): Build `art:e2feeb59` -> `/workspace/gm23/build`, Match `art:33632a00` -> `/workspace/gm23/matchrec` (log `/workspace/logs/fetch_gm23.log`).
  Note: the coordinator's "fresh #23 GM-01, 452 s" (run r20260924-084953-66e6, 128-CPU host) used another record of the same row (Build art:ee33269a +
  Match art:d39b5ef8 + instances from the 40 GB row tar art:50076ee1). D10 is judged base-vs-branch on THIS pod over the v2 record (same inputs, same host).

## Running
- pod: gate (b) baseline at 72884c8a: `/workspace/gate_b.sh /workspace/base /workspace/out/base_gate_b` (pytest integrations/vllm/tests, junit in that dir), started 17:43Z, ~53% at 17:57Z.

## Design decisions so far
- D5: `research_tools.CLOSURE` gains `packages/verity/src/verity/*.py` and `.../commitments/**` (the rest of core; the research test asserts the existing
  entries, so they stay); `research_tools.code_identity(root)` = canon sha256 over `VLLM_BUILD.closure_manifest(root)` (the same files, same listing rules
  as the store). `hot_commit.code_identity` and `tp/commit.tree_of_record` call it. Tests: temp repo tree, core edit changes both keys; every core file
  is inside CLOSURE.
- D6: sources resolved against `verity_vllm`'s parent; missing file raises; `root=` parameter for the test.
- D7: `model_pin.dtype` = `cfg.model_config.quantization` when set ("fp8"), else the model dtype name ("bfloat16") -- BF16 rows unchanged.
- Laptop rule slip: at 17:55Z ran one stdlib-only `python3 -c` importing `verity_vllm.harness.research_tools` on the laptop to time the closure
  manifest (0.25 s, 1115 files). No more Python on the laptop.

## Next
1. Implement D5, D6, D7 (edits on laptop), then D10, D11, D13; one commit each; push.
2. Sync branch to pod; gates (a), (b); GM-01 base vs branch (byte-identity + runtime) for D10; Build T0 before/after for D6/D7.

## Open questions
- none yet

## Found, not fixed
- none yet
