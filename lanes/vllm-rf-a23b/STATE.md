---
id: vllm-rf-a23b/state
lane: vllm-rf-a23b
kind: state
status: active
created: 2026-09-24T19:30Z
---
# vllm-rf-a23b: dead code, data and paths (state)

> **a23b succeeds a23 from `c1cf11ef`** (a23's pushed head; a23 silent since 18:02Z). Coordinator: vLLM coordinator, Cursor agent bc-ba6cec03.
> Branch `lane/vllm-rf-a23b`, worktree `/Users/danielreuter/projects/verity-wt/rf-a23b`, base for gates/diffs `72884c8a`.
> Pod `vyv-rf-a23` = RunPod `qcky3qlmvh896c`; my trees/scripts/logs under `/workspace/a23b/`. ssh: `~/.research/bin/research pods ssh vyv-rf-a23 --print`.
> Never touch `~/projects/verity-wt/rf-a23` or branch `lane/vllm-rf-a23`. Deadline: vyv- pods die 2026-09-25T03:00Z; start gate (a) by ~23:00Z.

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2, §5, §6 (lanes A2, A3); survey `survey-harness-ops-tests-data.md` DEAD, Map 3, Map 4.
- **Worktree (a23, not mine):** `/Users/danielreuter/projects/verity-wt/rf-a23`, branch `lane/vllm-rf-a23` from `72884c8a`.
- **Scope:** (1) delete §5.4 "dead now" + CMT-1 (`commit/reference_engine/`, `reference_engine_adapter.py`, `cmt_ref_*` in `harness/commit_delta.py`) + `commit/engine_rs/` + `tools/` and its test; move §5.4 "moved to tests" next to their tests; re-verify every deletion has no caller at 72884c8a. (2) library-read data to package data via `importlib.resources`; one helper for `manifests/` and `workloads/`; remove 8 `sys.path.insert`, 16 `parents[N]`, machine-path defaults, library read of `tests/`; pyproject ships package data.
- **Baseline:** `~/.research/notes/lanes/vllm-rf-a1/baseline.md` (gate (b) at base: 65 F/E, listed by cause; judge as no F/E or skip reason outside that list).

## Done
- 17:27Z worktree created.
- 17:35-17:50Z re-verified deletion candidates at 72884c8a (analysis only; findings in "Found, not fixed" and READY.md later).
- 17:55Z pod `vyv-rf-a23-veritor-campaign` = RunPod `qcky3qlmvh896c` (cpu3g, 16 vCPU / 64 GB, 80 GB disk, US, ~$0.64/h), created with
  `research pods create --name vyv-rf-a23 --cpu cpu3g --vcpu 16 --disk 80` (launcher `/tmp/rfa23/research.sh` =
  `PYTHONPATH=<wt>/tools/research/src python3.12 -m research`).

- 17:52Z base tree shipped: `git archive 72884c8a | ssh ... tar -x -C /workspace/base` (pod has no rsync; ssh line from `research pods ssh vyv-rf-a23 --print`, wrapper `/tmp/rfa23/ssh.sh`). The ship job exited 1 only because its trailing `command -v rsync` failed; the extraction is complete.
- 17:54Z `pod_bootstrap.sh --cpu --out /workspace/bootstrap` BOOTSTRAP-OK (py 3.12, torch cu129 CPU mode, vllm d9105ea80, checkpoint B0; venv `/workspace/venv312`, HF_HOME `/workspace/hf`, log `/workspace/logs/bootstrap.log`).
- 18:00Z synthetic git index in `/workspace/base` (census and source-identity tests need a checkout): bootstrap `__pycache__` removed, marker moved to `/workspace/base.tree`, `git init && git add -A -f && git commit`; tree `7db3f3ba` = 72884c8a's tree, 2814 files. Do the same for the lane tree. Store config copied to pod `/workspace/store.toml` (no secrets).
- commits (pushed): `b9b23ebf` tools/ + test_relayout_map deleted; `84c691c9` CMT-1 (reference_engine/, adapter, cmt_ref_* in commit_delta) + engine_rs/ + their tests + schemes.py CmtRef/veritor adapters; `446fe8b6` poc_rows, poc_verify_bindings (dist_identity -> observe/engine_profile.py), compiled_fx_kernels (normalise_kernel -> check/kernel_identity.py), batch_candidate, capture_identities_program, rebuild_digest_gate, row_pod_tp2.sh (+ test parts, census roots, keep list, allowlist); `c1cf11ef` moves to tests (fa2_prototype/ + fixtures, stream_merkle, synthetic -> tests/commit/; adversarial -> tests/check/; fa2_attn_oracle -> tests/acquire/; b1_authored, serve3_authored, inductor_models -> tests/program/; hidden_engine trimmed to what the committers import).
- 19:30Z a23b started: STATE.md created; worktree clean at `c1cf11ef`.
- **W11 move: `96c12c0b`** (pushed 19:45Z). `fixtures/W11{,R,C}-*/{mufu,tables}/*.xz` -> `verity_vllm/program/numerics/tables/<fixture id>/*.xz` (git mv, sha256 identical); `fa2_relation.tables_dir()`, `rms_relation.tables_dir()`, `prims.MUFU_TANH_TABLE_DIR` default via `importlib.resources.files(__package__)`; env overrides untouched. Tests: `test_composition.py` dropped its dead `VERITY_MUFU_TABLES` setdefault from the old path; `fa2_attn_oracle.py` docstring path.

## Running
- nothing on the pod (checking at 19:30Z).

## Next
1. W11 move (own commit, pushed first): `integrations/vllm/fixtures/W11*` tables read by `fa2_relation.tables_dir()/tables()`, `rms_relation.tables()`, `program/registry/prims.py` MufuTanh -> package data via `importlib.resources`; env overrides and digests untouched (f3 owns them); bytes unchanged. Record `W11 move: <sha>` here.
2. Rest of data/paths (sys.path.insert x8, parents[N] x16, machine paths, other package data, commit_delta tests/ read, manifests/workloads helper, pyproject package data).
3. Gates: (b) a1's gate_b.sh adapted, `OMP_NUM_THREADS=3 ... -n 12 --dist loadfile`; (a) a1's gate_a.sh without the `/root/r2ro.env` file (credential via ssh stdin), prefetch late rows' blobs before expiry as a1 did.

## Decisions so far
- SKIPPED as live: `correspondence/resolve_decomp.py` (used by tests/regression/checks/decomp_hashes.py, a census root); `commit/hidden_engine.py` (imported by acquire/native_host, native_collect, leafhash, hidden_gpu, commit/hidden_stream, padding_steps) -- only its dead `_POC` sys.path and fa2_prototype-only helpers go.
- `registry_version()` hashes the source of registry/prims.py + b1.py: editing prims.py (sys.path line) changes that digest; it is export-report provenance only (no Program/manifest digest, no regression check reads it).
- Left as is (record content, not code): the `CORE` label in `tests/program/padded_commit_tiny.py` naming `stream_merkle`, and the frozen `why` strings naming `row_pod_tp2.sh` in `tests/regression/expected/*.json` (the live string in `checks/manifest_digest.py` now names `tp_stage.sh`). Both go in READY.md.

## Open questions
- none yet

## Found, not fixed
- none yet
