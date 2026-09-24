---
id: vllm-rf-a23b/state
lane: vllm-rf-a23b
kind: state
status: active
created: 2026-09-24T19:30Z
---
# vllm-rf-a23b: dead code, data and paths (state)

> **Coordinator, 22:13Z: main moved to `1d9c3198` (a1's lints merged).** When your gate (a) finishes, rebase onto `origin/main`. Keep your side of the `check/fold_compare.py` conflict. Run `tests/lint` on your pod, delete the stale allowlist entries, add `"verity_vllm.config": "config"` to `INTERIM_LAYER`, push with `--force-with-lease`, and record both heads in READY.md. Steps: `../vllm-refactor/20260924T2213Z-main-moved-rebase.md`.

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
- 20:23:06Z prefetch done: 26/26 ok, 0 FAIL; `/root/r2ro.env` deleted 20:23:06Z (checked absent 20:24Z); gate (a) `a_lane` started 20:23:06Z (same pid chain 2172 -> exec gate_a.sh).
- 20:22Z `ed81ba7f` (message-only: profile lookup messages stop naming data/hf_configs) pushed after the gates started; gates run at `6da1b430`; re-run the two profile test files at ed81ba7f before READY.
- Checks done on the pod at 6da1b430: new paths resolve (config.ROOT, cos_sin, calibration, W11/W11R/W11C tables, tanh tables, corpus, manifest); `uv build --wheel integrations/vllm` -> `/workspace/a23b/wheel/verity_vllm-0.1.0-py3-none-any.whl` contains all 7 .xz, the .npy, the .jsonl, corpus json, tanh tables (pyproject unchanged: hatchling ships every non-ignored file under verity_vllm/).
- 20:27Z b_lane_x12 at 97% (real-HF tail, as a1's); a_lane running (first 12 = skips; a1's a_base still running on vyv-rf-a1, its baseline.md gate (a) section is still "Pending": compare when it lands). `ed81.patch` (6da1b430..ed81ba7f) shipped to `/workspace/a23b/ed81.patch` for the profile re-run.
- 20:39Z `4e26d864` (pushed): `weights_of_record._default_manifest` used `dirname(__file__)/../..`; now config.CHECKPOINTS then the cwd.
- 20:40Z a_lane (T0 only, 6da1b430) killed by pid (2172, 3343, 3923) after the 20:33Z tiers note. Head tree `/workspace/a23b/head` = cp /workspace/base + `deleted4.txt` rm + `lane4.patch` (`git diff -M --binary --diff-filter=d 72884c8a 4e26d864`); write-tree `a8917dce` = 4e26d864^{tree}, 2791 files; .git moved to `head.git`; copy `head-reg`.
- **20:42:33Z gate (a) T0+T1 at 4e26d864:** `cd /workspace/a23b && setsid nohup nice ./gate_a_t01.sh /workspace/a23b/head-reg a_head_t01` -> pid 4531 (sid 4531); logs `a_head_t01.{log,xml,env,run}`; script copy `gate_a.sh` beside this note. Store already holds every row's fixtures (20:23Z prefetch); no key on the pod.
- **20:43:00Z gate (b) at 4e26d864:** `cd /workspace/a23b && OMP_NUM_THREADS=3 setsid nohup ./gate_b.sh /workspace/a23b/head b_head_x12 -n 12 --dist loadfile` -> gate_b.sh pid 4650 (sid 4650), pytest pid 4659; logs `b_head_x12.{log,xml,env,rss,run}`. b_lane_x12 (6da1b430) left to finish as extra evidence. Compare: `/workspace/venv312/bin/python /workspace/a23b/cmp.py /workspace/a23b/logs/b_head_x12.xml /workspace/a23b/baseline.md`.
- 20:50:27Z b_lane_x12 (6da1b430) done: 52 F, 11 E, 3477 passed, 287 skipped, 6 xfailed (2060 s). a1's jdiff vs base xdist: 0 new skips, 4 new failures:
  (1) `test_source_identity::test_shipped_tree_{takes_its_sha_from_research_source_sha,still_refuses_a_foreign_package}` = MINE (the stub shipped tree lacked `verity_vllm/config.py`, which source_identity now imports) -> fixed in **`748d71c5`** (test stub copies config.py; the file then shows only the 4 base-list no-.git failures);
  (2) the gc-freeze pair in `test_admit_r19_host_working_set` (baseline's order-dependent list): on THIS pod they fail at base too, even with the file alone (`assert 375 == 0`, `assert False`), so host/order, not the lane.
  6 base failures pass here (CPU-host numerics: this pod is AMD EPYC 7702P, no AVX512; a1's differed).
- **20:56:02Z OOM:** cgroup hit 64 GB (my ad-hoc test_execution_label runs beside two gates) and the kernel killed gate (a) a_head_t01 (exit 137). Rule: only gate (a) + ONE gate (b) at a time; no ad-hoc vLLM runs beside them.
- head2 tree at `748d71c5`: `/workspace/a23b/head2` (write-tree `1158eb69` = 748d71c5^{tree}, 2791 files; .git in `head2.git`), copy `head2-reg`.
- **20:57:30Z gate (a) T0+T1 at 748d71c5:** `setsid nohup nice ./gate_a_t01.sh /workspace/a23b/head2-reg a_head2_t01` -> pid 8110; logs `a_head2_t01.{log,xml,env,run}`.
- Next: when b_head_x12 (4e26d864) exits, start gate (b) at 748d71c5: `OMP_NUM_THREADS=3 setsid nohup ./gate_b.sh /workspace/a23b/head2 b_head2_x12 -n 12 --dist loadfile`; then (if time) a same-pod base xdist run for host-numerics classification, only after b_head2 finishes.
- **21:10Z second OOM on vyv-rf-a23 (64 GB): gate (a) T0+T1 alone reached 57 GB on its first T1 check of row #11 and was killed; the OOM also killed sshd, so the pod refused ssh. Terminated 21:15Z (its logs, incl. b_lane_x12.xml, are gone; the results are above).**
  Cause: `tests/regression/checks/replay_partition.py` (T1) loads each B=1 row's whole Program JSON: its docstring says "0.9-1.7 GB compressed and need 120-250 GB of RAM as Python objects: a big pod". **A T0+T1 gate (a) cannot run on a 64 GB cpu3g pod (a1's T0+T1 base will hit the same).**
- **21:17Z new pod `vyv-rf-a23b-big` = RunPod `n2ei0ahhoeu80j`** (cpu3m, 64 vCPU, 512 GB, AMD EPYC 9655 with AVX512, kernel 6.8, 200 GB disk, $3.52/h), created with `research pods create --name vyv-rf-a23b-big --cpu cpu3m --vcpu 64 --disk 200`. ssh: `research pods ssh n2ei0ahhoeu80j --print` (port 21626). (A cpu5m x32 256 GB pod `pt89dyfqpgh8bp` was created first and terminated at once: too small for 250 GB.)
- **Setup on vyv-rf-a23b-big** (ssh wrapper `ssh_big.sh` beside this note; scripts `gate_a.sh` (T0,T1), `gate_b.sh`, `prefetch.sh` beside this note, copies in pod `/workspace/a23b/`, logs `/workspace/a23b/logs/`):
  - 21:19Z `research pods sync n2ei0ahhoeu80j --dest /workspace/head2` (worktree launcher, 180 s): 748d71c5, content = tree `1158eb69` + the two sync stamp files. `/workspace/base` = cp head2 + reverse patch (`git diff -M --binary 748d71c5 72884c8a`), verified tree `7db3f3ba` (2814 files), stamp rewritten to name 72884c8a. Copies: `head2-reg` (gate a), `base-b` (base gate b).
  - 21:25Z `pod_bootstrap.sh --cpu` BOOTSTRAP-OK (from `/workspace/boot`); `pytest-xdist==3.8.0`; `xgrammar` pinned to 0.2.7 -> `uv pip freeze` identical to a1's `baseline-freeze.txt`. Python 3.12.14, Linux 6.8.0-87, glibc 2.35.
  - 21:27Z key minted on the laptop (read-only, expires 00:27Z) piped to `/root/r2ro.env`; `setsid nohup ./prefetch.sh /workspace/head2` (deletes the key at the end and on exit) -> `logs/prefetch.log`.
- **21:29:50Z gate (b) head `b_head2_x12` (748d71c5) and base `b_base_x12` (72884c8a), same pod and flags, concurrently:** `OMP_NUM_THREADS=3 setsid nohup ./gate_b.sh /workspace/{head2,base-b} {b_head2_x12,b_base_x12} -n 12 --dist loadfile` -> gate_b.sh pids 974 (head), 976 (base); pytest 997 (head), 996 (base).
- 21:36:51Z prefetch done: ok=26 fail=0, `/root/r2ro.env` deleted (checked absent 21:37Z; no AWS_* in the environment).
- **21:37:17Z gate (a) T0+T1 at 748d71c5 on vyv-rf-a23b-big:** `cd /workspace/a23b && setsid nohup nice ./gate_a.sh /workspace/head2-reg a_head2_t01` -> pid 5565 (sid 5565); logs `a_head2_t01.{log,xml,env,run}`; scratch `/workspace/a23b/scratch/a_head2_t01`.
- **21:42Z gate (b) done, same pod, same flags:** head `b_head2_x12` (748d71c5): 3833 = 3476 pass / 54 F / 11 E / 286 skip / 6 xf (778 s); base `b_base_x12` (72884c8a): 3904 = 3534 / 56 / 11 / 297 / 6 (762 s).
  a1's `baseline-jdiff.py`: head vs a1's base xdist -> 0 new failures, 0 new skips, 0 new skip reasons, the SAME 65 F/E; 71 tests only in base (all tests of code part 1 deleted); 1 outcome change (observer weakref s -> pass, order-dependent). Head vs same-pod base -> 0 new F, 0 new skips; gc-freeze pair F -> pass (order-dependent). Same-pod base vs a1's base: only the gc-freeze pair differs. XMLs beside this note (`gate_b-xdist-{head-748d71c5,base-72884c8a-samepod}.xml.gz`).
- 21:48Z gate (a): r11 `replay_partition` (T1) passed, peak ~63 GB RSS. Order is per row (r4, r11, r23, r39, ...), 12 checks each. Plan: start a same-pod BASE gate (a) T0+T1 in `/workspace/base-reg` (copied 21:51Z) once head is past r39, so the two heavy loads never overlap: `setsid nohup nice ./gate_a.sh /workspace/base-reg a_base_t01`.
- 22:10Z head gate (a) on r39 `replay_partition` (test 47 of 158), peak 115 GB (VmHWM), still computing. r23's two T1 checks skipped (reasons in the final -ra summary).
- **22:10:30Z same-pod base gate (a) T0+T1 at 72884c8a:** `cd /workspace/a23b && setsid nohup nice ./gate_a.sh /workspace/base-reg a_base_t01` -> pid 6852 (sid 6852); logs `a_base_t01.{log,xml,env,run}`. Peaks (63 GB r11, 115 GB r39) leave room for both runs in 512 GB.
- READY.md drafted with the gate (b) evidence; gate (a) section to fill. Compare gate (a): `python a1/baseline-jdiff.py logs/a_base_t01.xml logs/a_head2_t01.xml` on the pod, and head vs a1's T0 `a1/baseline-gate_a.xml.gz`.
- 22:30Z head gate (a) 82/158, no failure so far; base gate (a) 36/158, no failure. Wheel rebuilt at 748d71c5 on the pod (`/workspace/a23b/wheel/`, 375 files, all package data present).
- 22:53Z head gate (a) 118/158, base 60/158, no failure in either so far.
- Kill by pid only (never pkill -f over ssh).

## Next (updated 20:20Z: 1 and 2 done; 3 running)
1. (done) W11 move (own commit, pushed first): `integrations/vllm/fixtures/W11*` tables read by `fa2_relation.tables_dir()/tables()`, `rms_relation.tables()`, `program/registry/prims.py` MufuTanh -> package data via `importlib.resources`; env overrides and digests untouched (f3 owns them); bytes unchanged. Record `W11 move: <sha>` here.
2. Rest of data/paths (sys.path.insert x8, parents[N] x16, machine paths, other package data, commit_delta tests/ read, manifests/workloads helper, pyproject package data).
3. Gates: (b) a1's gate_b.sh adapted, `OMP_NUM_THREADS=3 ... -n 12 --dist loadfile`; (a) a1's gate_a.sh without the `/root/r2ro.env` file (credential via ssh stdin), prefetch late rows' blobs before expiry as a1 did.
   - **Coordinator, 20:33Z: gate (a) runs tiers T0 and T1** (`VERITY_REGRESSION_TIERS=T0,T1`, per SYNTHESIS §6); a1 is measuring the T0+T1 base. Gate (b) is judged against the base run of the same mode (xdist vs xdist).
   - **Coordinator, 19:47Z: the credential restriction is lifted.** Use the gate (a) recipe in `../vllm-rf-a1/baseline.md`: mint your own read-only key on the laptop (never on the pod) and pipe it into your pod, fetch every row, delete `/root/r2ro.env` right after, then run gate (a) without it. Handoff: `20260924T1942Z-handoff-from-vllm-coordinator.md`.

## Decisions so far
- SKIPPED as live: `correspondence/resolve_decomp.py` (used by tests/regression/checks/decomp_hashes.py, a census root); `commit/hidden_engine.py` (imported by acquire/native_host, native_collect, leafhash, hidden_gpu, commit/hidden_stream, padding_steps) -- only its dead `_POC` sys.path and fa2_prototype-only helpers go.
- `registry_version()` hashes the source of registry/prims.py + b1.py: editing prims.py (sys.path line) changes that digest; it is export-report provenance only (no Program/manifest digest, no regression check reads it).
- Left as is (record content, not code): the `CORE` label in `tests/program/padded_commit_tiny.py` naming `stream_merkle`, and the frozen `why` strings naming `row_pod_tp2.sh` in `tests/regression/expected/*.json` (the live string in `checks/manifest_digest.py` now names `tp_stage.sh`). Both go in READY.md.

## Open questions
- none yet

## Found, not fixed
- none yet
