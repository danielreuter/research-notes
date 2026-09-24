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

- 20:05Z part 2 commits (pushed): `928813d3` dead sys.path inserts (prims, twins, padding_steps; hidden_gpu keeps its own tree, drops vllm-poc) -- NB it also carries the two `git mv`s below (staged by accident; not rewritten); `ed31d31c` `verity_vllm/config.py` (ROOT/MANIFESTS/WORKLOADS/CHECKPOINTS, `checkpoints_hf_home()`) replaces parents[N] in golden, protected, quarantine_lint, workload, coverage_workloads, dense_generic (+ drops the shadowed data/hf_configs fallback), rmsnorm_fused_sweep, weights_of_record, tp.worker, source_identity; `dfb8cd8b` B0 cos_sin -> `check/tables/B0-divergence-20260907T1604Z/cos_sin_cache.npy` (fold_compare.DEFAULT_COS_SIN), planner calibration -> `harness/planner_calibration.jsonl` (admission_planner.CALIBRATION; commit_delta no longer reads tests/), laptop DEFAULT_RECORD dropped; `24466fdd` HF_HOME default from checkpoints.json (engine_profile.apply_env, beyond_gemm); `6da1b430` test_composition loads MUFU tables via fa2_relation.tables_dir().
- 20:15Z lane tree on pod: `/workspace/a23b/lane` = cp of /workspace/base + `deleted.txt` git rm + `lane2.patch` (`git diff -M --binary --diff-filter=d 72884c8a 6da1b430`); `git write-tree` = `4041b8f8` = 6da1b430^{tree}, 2791 files. Its synthetic .git moved to `/workspace/a23b/lane.git` (baseline ran without .git). Copy `/workspace/a23b/lane-reg` for gate (a). (Laptop->pod tar of the full tree is too slow here and dies with the shell call; ship patches.)

## Running (pod vyv-rf-a23 = qcky3qlmvh896c; scripts `/workspace/a23b/{gate_a,gate_b,prefetch_then_gate_a}.sh`, logs `/workspace/a23b/logs/`)
- 20:16Z gate (b) xdist: `cd /workspace/a23b && OMP_NUM_THREADS=3 setsid nohup ./gate_b.sh /workspace/a23b/lane b_lane_x12 -n 12 --dist loadfile` -> gate_b.sh pid 824 (sid 824), pytest pid 832; logs `b_lane_x12.{log,xml,env,rss}`.
- 20:17Z gate (a): read-only key minted on the laptop (expires 23:17Z) piped to `/root/r2ro.env`; `setsid nohup nice ./prefetch_then_gate_a.sh /workspace/a23b/lane-reg a_lane` pid 2172 (sid 2172): fetches the 26 fixture artifacts (`prefetch.log`), deletes `/root/r2ro.env` (also on exit via trap), then execs `gate_a.sh` (refuses if the key file exists) -> `a_lane.{log,xml,env}`, scratch `/workspace/a23b/scratch/a_lane`. A `FAIL` line in prefetch.log = mint again, fetch that row, delete again.
- Kill by pid only (never pkill -f over ssh).

## Next (updated 20:20Z: 1 and 2 done; 3 running)
1. (done) W11 move (own commit, pushed first): `integrations/vllm/fixtures/W11*` tables read by `fa2_relation.tables_dir()/tables()`, `rms_relation.tables()`, `program/registry/prims.py` MufuTanh -> package data via `importlib.resources`; env overrides and digests untouched (f3 owns them); bytes unchanged. Record `W11 move: <sha>` here.
2. Rest of data/paths (sys.path.insert x8, parents[N] x16, machine paths, other package data, commit_delta tests/ read, manifests/workloads helper, pyproject package data).
3. Gates: (b) a1's gate_b.sh adapted, `OMP_NUM_THREADS=3 ... -n 12 --dist loadfile`; (a) a1's gate_a.sh without the `/root/r2ro.env` file (credential via ssh stdin), prefetch late rows' blobs before expiry as a1 did.
   - **Coordinator, 19:47Z: the credential restriction is lifted.** Use the gate (a) recipe in `../vllm-rf-a1/baseline.md`: mint your own read-only key on the laptop (never on the pod) and pipe it into your pod, fetch every row, delete `/root/r2ro.env` right after, then run gate (a) without it. Handoff: `20260924T1942Z-handoff-from-vllm-coordinator.md`.

## Decisions so far
- SKIPPED as live: `correspondence/resolve_decomp.py` (used by tests/regression/checks/decomp_hashes.py, a census root); `commit/hidden_engine.py` (imported by acquire/native_host, native_collect, leafhash, hidden_gpu, commit/hidden_stream, padding_steps) -- only its dead `_POC` sys.path and fa2_prototype-only helpers go.
- `registry_version()` hashes the source of registry/prims.py + b1.py: editing prims.py (sys.path line) changes that digest; it is export-report provenance only (no Program/manifest digest, no regression check reads it).
- Left as is (record content, not code): the `CORE` label in `tests/program/padded_commit_tiny.py` naming `stream_merkle`, and the frozen `why` strings naming `row_pod_tp2.sh` in `tests/regression/expected/*.json` (the live string in `checks/manifest_digest.py` now names `tp_stage.sh`). Both go in READY.md.

## Open questions
- none yet

## Found, not fixed
- none yet
