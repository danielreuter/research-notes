---
id: vllm-rf-a23/state
lane: vllm-rf-a23
kind: state
status: active
created: 2026-09-24T17:27Z
---
# vllm-rf-a23: dead code, data and paths (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2, §5, §6 (lanes A2, A3); survey `survey-harness-ops-tests-data.md` DEAD, Map 3, Map 4.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-a23`, branch `lane/vllm-rf-a23` from `72884c8a`.
- **Scope:** (1) delete §5.4 "dead now" + CMT-1 (`commit/reference_engine/`, `reference_engine_adapter.py`, `cmt_ref_*` in `harness/commit_delta.py`) + `commit/engine_rs/` + `tools/` and its test; move §5.4 "moved to tests" next to their tests; re-verify every deletion has no caller at 72884c8a. (2) library-read data to package data via `importlib.resources`; one helper for `manifests/` and `workloads/`; remove 8 `sys.path.insert`, 16 `parents[N]`, machine-path defaults, library read of `tests/`; pyproject ships package data.

## Done
- 17:27Z worktree created.
- 17:35-17:50Z re-verified deletion candidates at 72884c8a (analysis only; findings in "Found, not fixed" and READY.md later).
- 17:55Z pod `vyv-rf-a23-veritor-campaign` = RunPod `qcky3qlmvh896c` (cpu3g, 16 vCPU / 64 GB, 80 GB disk, US, ~$0.64/h), created with
  `research pods create --name vyv-rf-a23 --cpu cpu3g --vcpu 16 --disk 80` (launcher `/tmp/rfa23/research.sh` =
  `PYTHONPATH=<wt>/tools/research/src python3.12 -m research`).

- 17:52Z base tree shipped: `git archive 72884c8a | ssh ... tar -x -C /workspace/base` (pod has no rsync; ssh line from `research pods ssh vyv-rf-a23 --print`, wrapper `/tmp/rfa23/ssh.sh`).
- commits (pushed): `b9b23ebf` tools/ + test_relayout_map deleted; `84c691c9` CMT-1 (reference_engine/, adapter, cmt_ref_* in commit_delta) + engine_rs/ + their tests + schemes.py CmtRef/veritor adapters; `446fe8b6` poc_rows, poc_verify_bindings (dist_identity -> observe/engine_profile.py), compiled_fx_kernels (normalise_kernel -> check/kernel_identity.py), batch_candidate, capture_identities_program, rebuild_digest_gate, row_pod_tp2.sh (+ test parts, census roots, keep list, allowlist).

## Running
- pod bootstrap on `qcky3qlmvh896c`: `cd /workspace/base/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap`, log `/workspace/logs/bootstrap.log` (venv `/workspace/venv312`, HF_HOME `/workspace/hf`).

## Next
1. Moves to tests (fa2_prototype/, stream_merkle, synthetic, adversarial, fa2_attn_oracle, b1_authored + serve3_authored, inductor_models).
2. Data/paths (sys.path.insert x8, parents[N] x16, machine paths, package data, commit_delta tests/ read).
3. Pod: base gates (a)+(b) at 72884c8a (a1 baseline not yet written), then lane gates.

## Decisions so far
- SKIPPED as live: `correspondence/resolve_decomp.py` (used by tests/regression/checks/decomp_hashes.py, a census root); `commit/hidden_engine.py` (imported by acquire/native_host, native_collect, leafhash, hidden_gpu, commit/hidden_stream, padding_steps) -- only its dead `_POC` sys.path and fa2_prototype-only helpers go.
- `registry_version()` hashes the source of registry/prims.py + b1.py: editing prims.py (sys.path line) changes that digest; it is export-report provenance only (no Program/manifest digest, no regression check reads it).

## Open questions
- none yet

## Found, not fixed
- none yet
