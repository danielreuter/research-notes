---
id: vllm-rf-f24/ready
lane: vllm-rf-f24
kind: ready
status: draft (gate (a) on the main pod still running)
created: 2026-09-24T22:05Z
---
# vllm-rf-f24 READY: identity and integrity (D5, D6, D7, D10, D11, D13)

- **Branch:** `lane/vllm-rf-f24` (pushed)
- **Head:** `be366f80`
- **Base for gates and diffs:** `72884c8a`
- 6 commits, 26 files, +788 / -462. Nothing under `packages/verity` changed: D10 needed no core change.

## Gate evidence

Environment on every pod (the venv of `integrations/vllm/verity_vllm/ops/pod_bootstrap.sh`, `--cpu` on the CPU pods): Python
3.12.14, torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80.cu129, triton 3.7.1, pytest 9.1.1, pytest-xdist 3.8.0. The head
trees are at `be366f80` (the commit in each tree's `.research-source.json`, printed in every gate `.status`); the base tree is at
`72884c8a`.

| pod | RunPod | used for |
|---|---|---|
| `vyv-rf-f24-veritor-campaign` (`0zb24mk1w6nb4o`) | cpu3g, 16 vCPU / 64 GB | gate (a) T0+T1, gate (b), GM-01 A/B, verdict A/B, D6/D7 probes |
| `vyv-rf-f24-big` | cpu3m, 64 vCPU / 512 GB, terminated | the two T1 `replay_partition` checks of the B=1 rows #11 and #39 |
| `vyv-rf-f24-gpu` | RTX 4090, terminated | the Build A/B (a Build cannot run on a CPU pod, see Found, not fixed) |

Scripts and outputs are in `evidence/` beside this note (`gate_a.sh`, `gate_b.sh` are lane a1's with the log directory moved and,
for gate (a), the key line removed).

### (a) Regression, T0 + T1

From the tree root, with the store and scratch environment of a1's recipe:

~~~
VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression -ra
~~~

- **Main pod** (`gate_a.sh /workspace/head2-reg a_final`, 20:50Z), with
  `--deselect tests/regression/test_regression.py::test_reproduces[T1-replay_partition-r11]` and `...[T1-replay_partition-r39]`:
  **PENDING**.
- **Big pod**, the two deselected checks (`run_big.sh`: `gate_a.sh ... -k "replay_partition and r11"` and `... r39"`, each its own
  process): **#11 1 passed** (843 s, peak RSS 67 GB), **#39 1 passed** (1,364 s, peak RSS 109 GB). They need more than the 64 GB
  pod has.
- **Fixtures and the credential** (`20260924T1942Z-gate-a-credential-route.md`). Every key was minted on the laptop
  (`--permission object-read-only --via local`) and piped into the pod, never echoed. Main pod: `prefetch.sh` fetched all 26
  fixture artifacts (0 failures) and deleted `/root/r2ro.env` at 20:47:22Z. Big pod: its own `--ttl 3h` key, minted 20:55:40Z,
  fetched rows #11 and #39 plus the top-level artifact, deleted 20:56:53Z, before its clean run at 21:14:28Z.
- **Deviation: a key stayed on the main pod's disk during the first hour of `a_final`.** Before the route was published, I
  had piped an earlier key (`--ttl 12h`, written 17:43Z) into `/workspace/r2ro.env` for the lane's first fetches. It was never
  deleted, and `gate_a.sh`'s `key_file_present` check looks only at `/root/r2ro.env`. I found it and deleted it at 21:52:03Z,
  while `a_final` was on row #39. The checks could not have used it: the store reads credentials only from the environment
  variables `store.pod.toml` names, the pod has no `~/.aws`, and the gate process and its children had no `AWS_*` variables
  (`/proc/<pid>/environ` checked). A `--via local` key is a JWT signed with the parent secret, so it can't be revoked; it expires
  about 05:43Z on 2026-09-25 unless the parent key is rotated (the owner's call). **Keyless rerun:** after a sweep of the pod
  found no key file, the checks that ran while the file was there are rerun (rows #4, #11 and #23, and `manifest_digest` of #39):
  T0 as `a_rerun_t0` alongside `a_final` from 21:54:17Z, and T1 as `a_rerun_t1` after `a_final`. **PENDING.**

### (b) Full suite

~~~
OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -n 12 --dist loadfile      # gate_b.sh, as a1's baseline
~~~

At `be366f80`: **56 failed, 11 errors, 296 skipped, 3,550 passed, 6 xfailed** (3,919 tests, 2,405 s). a1's baseline at
`72884c8a` (same command): 54 failed, 11 errors, 297 skipped, 3,536 passed, 6 xfailed (3,904). Test by test (`jdiff.py`,
`evidence/gate_b/`):

- **16 new tests, all pass.** One base test is replaced: `harness/test_hot_commit.py::test_code_identity_hashes_code_not_tests_or_caches`
  pinned the old `CODE_ROOTS` skip lists. Its successor `test_code_identity_is_the_closure_identity_of_the_repository` asserts the
  same things of the closure identity: caches and files outside the closure don't move the key, and an edited file does.
- **2 outcome changes to failed, neither from this branch:** the gc-freeze pair in `harness/test_admit_r19_host_working_set.py`.
  a1's baseline documents it as order-dependent: vLLM's in-process `EngineCore` freezes the GC heap and never unfreezes it, so
  the pair fails whenever an engine ran earlier in the same worker. On this pod it fails the same way at base and head, run
  alone and after `observe/test_execution_label.py`. It also fails in a1's own head run, which has no f24 change.
- 1 outcome change to passed: `observe/test_observer_encoding.py::test_weakref_death_...` (allocator reuse; a1's documented noise).
- **No new skip reason.** Against a1's head run (a1's lints on the base), no outcome changed.

### (c) Acceptance

- **Build T0 rows unchanged except the `construction_version` stamp and FP8 `dtype`** (Build A/B, `evidence/build_ab/`). On the
  RTX 4090 with one venv (the records' vLLM, torch and triton versions), `rebuild_digest_gate` re-derived rows #73 (Qwen3-4B BF16:
  `step`, `request_LP10_T8`) and #74 (Qwen3-4B-FP8: `step`, `request_LP73_T1`) from their recorded `result.json`, with the base
  tree first and then the head tree. Base and head give:
  - the same `program_digest` and `correspondence_digest` for all 4 wrappers, and byte-identical `descriptor.json.gz`,
    `instances.json.gz` and `derive-report.json`;
  - in `result.json`, differences only in `construction_version`, `artifact.identity` (the hash that folds it in), timings,
    and `model_pin.dtype` on #74 only (`bfloat16` -> `fp8`). The build logs and `inputs.json` (the trace of opened files) also
    differ: the tree path, and the number of files opened (for #74 `step`, 208 vs 181 paths outside site-packages and 12,904 vs
    11,506 distinct paths). I kept only the diff of the traces, not the traces themselves, so I can't attribute each path.
- **D6 on every recorded Build** (`evidence/d6`, `cv_evidence.py`): base hashes 14/14 sources as missing (`4a9cdf5b...`, a
  constant of the file names); head hashes all 14 by content. The 180 recorded Builds all carry `ad140226...`, 14/14 missing.
- **D7 on every recorded Build** (`evidence/d7`, `fp8_dtype.py`, each Build's own target and pin through
  `EngineArgs.create_model_config()`): 9 BF16 rows give `bfloat16` (as recorded); the FP8 row gives `fp8` (quantization `fp8`,
  model dtype bf16), where the record says `bfloat16`.
- **Match outputs unchanged (D10)**, GM-01 on row #23, base and head alternated ABAB on the same pod (`evidence/gm`):
  `global_match_global_program.json` byte-identical; `match_decomp.json` differs in 2 timing fields; `global_match.json` differs
  in timings, `impl.source_sha256` (the checker's code identity) and `x09.pipeline.decomp_out` (the run's output path). Verdict
  PASS in all four runs. Wall / CPU (user+sys), s: base 618.8 / 2,409.3, head 693.5 / 2,728.7, base 664.0 / 2,641.6, head
  692.2 / 2,642.8. The second pair is +4.2 % wall at equal CPU (+0.05 %), and the mean wall is +8.0 % (within 10 %). Per-phase CPU
  in the second pair is within 2.5 %. The host was shared (load average about 200), and the same code varied by 17 % in one phase.
- **Verdicts unchanged (D13)** (`evidence/d13`): `verdict.from_record(row).dumps()`, which is the T0 `verdict` check's
  reconstruction and calls the three changed C2 functions (`_replay_seed_of_record`, `_complete_replay_population_gap`,
  `_partial_replay_named_gap`), is byte-identical at base and head for all 10 regression records with a Commit verdict.
  `commit_summary` only lifts the recorded `commit/verdict.json`, so this A/B is the direct evidence. The records carry no codes,
  so this also exercises the decoding of legacy texts.
- **D11:** every program digest in the regression records is a full 64-hex sha256 (a scan of all records), so the stricter
  comparison moves no verdict of record.
- **New identity tests pass** (in gate (b)): `test_hot_commit` (3 new, including the core-edit key test),
  `test_research_tools`, `tp/test_commit_tree_of_record` (2), `test_derive_step_identity` (4).

## What changed

- `c9777273` **D5, one code identity.** `research_tools.CLOSURE` (the Tools' closure) now also lists
  `packages/verity/src/verity/*.py` and `commitments/**`, so it covers every core file (a test walks the tree to check).
  New `research_tools.code_identity(root)` is the canonical sha256 of the closure manifest; it refuses a root that holds no
  integration or no core file. `hot_commit.code_identity` (the hot worker's key) and `tp/commit.tree_of_record` (the TP Commit's
  tree) both use it. Removed `CODE_ROOTS`, `CODE_SKIP_DIRS` and `CODE_SKIP_SUFFIX`; the git-diff tree of record is gone.
- `13acf676` **D6 + D7, Build stamps.** `construction_version` reads its 14 sources from the integration root (the one
  `verity_vllm` is imported from; `root=` for tests) and raises `FileNotFoundError` naming a missing one. `model_pin.dtype` is
  `engine_dtype(cfg.model_config)`: the quantization method when the checkpoint is quantized, else the model dtype.
- `0cdd61e2` **D10, no rebinding.** `batch_decomp.Ops` carries the Program operations (load oracle / derived, projection,
  compare_steps, dag_hashes, live_cone, legs). `Ops.record()` is the record path. `global_match_fast.ops()` is the fast path:
  `FastProg` (a `Prog` whose `_node_functions` supply the memoised `_spec_id` and fast `runs`), `_ProjectionFast`, and the
  memoised compare / hash / cone functions. `global_match.match_ops(fast)` picks one and `_check` / `decompose` take it. The
  `program_compare.COMPACT_ARGS` global became a `compact=` parameter. `install()` / `uninstall()` and every module-attribute
  write are gone, and a test asserts the core functions keep their identity.
- `2a07cd20` **D11, full digests.** `weights_of_record.check` and `stamp_of_record_set` refuse a program digest that is not
  64-hex (the reason says "not full sha256") and compare by set equality. `_eq` and the prefix matches in `stamp_of_record_set`
  are gone.
- `76020a66` **D13, structured reason codes.** New `check/replay_codes.py` (dependency-free) holds the why classes, seed forms and
  the seed-source texts, plus decoders for records written before the codes. `sampled_replay.population` stamps
  `population.not_evaluable_codes` (class, family, domain, tags per reason); `sampled_replay(seed_form=)` stamps
  `sample.seed_form`; `commit_delta` passes the form (a few lines). `commit_verdict` reads the codes. `verdict.py`'s three
  "Match account leg(s) missing" text tests now read `executed_prefix_of_record.facts_of_record` of the faulted requests.
- `be366f80` `tests/by_name_allowlist.json`: the population-gap rule's entry follows its new expression, and the retired
  `CODE_SKIP_SUFFIX` entry is deleted (the ratchet's "delete the entry" message).

## What deliberately didn't change

- Program digests, manifest digests, roots, leaf ids and verdicts (evidence above). The values that do change are all identities
  of code: `construction_version` and `artifact.identity` (D6), the hot worker's key, the TP tree of record, the research
  Tools' closure and cache keys (D5), and GM-01's `impl.source_sha256`.
- Core (`packages/verity`): untouched. The memoisation stays in the integration, passed explicitly (P1).
- Records written before the codes still grade from their texts through `replay_codes`' decoders; every regression row is such
  a record. The fast Match path is still the default.
- `tree_of_record` no longer carries the git / `EXPORT.json` fields. Its only consumer is the TP Commit's `versions.json`
  `tree` block, which nothing reads.

## Rebase notes

- After a23b merges: `construction_version`'s default root should come from a23b's `config.ROOT`. It climbs from
  `verity_vllm.__file__` today, where base climbed from `verity.ir.__file__`.
- a23b deletes `harness/rebuild_digest_gate.py`. Nothing on this branch uses it; I only ran it on a pod for the Build A/B.
- `harness/commit_delta.py` (also edited by f1 and a23b): this branch's hunk is the seed-form lines around the
  `SR.sampled_replay` call.

## Found, not fixed

- `commit_verdict.py:569` and `verdict.py:_replay_of` pick a `components.sampled_replay` by the substring "sampled-exact-replay"
  in its method label (a label, not a message).
- The recorded Builds can't validate a rebuild today. Re-deriving rows #73 and #74 with the base tree (and the head tree) gives
  Program digests different from the records', with the same number of root nodes (14,418 and 32,454 for #73's two wrappers).
  The records were built by pre-relayout code: their `construction_version` lists 25 binding rules (base has 27) and names its
  sources under `verity_capture/experimental/cb_a/`.
- A Build can't run on a CPU pod with the bootstrap's CUDA vLLM wheel, even with a declared TargetProfile: vLLM makes no
  DeviceConfig without a GPU ("Device string must not be empty"). SYNTHESIS §6 validates F2 on "CPU pod: Build T0"; any CUDA GPU
  works, because the profile makes the Program independent of the host.
- Gate (a)'s T1 `replay_partition` on the B=1 rows #11 and #39 peaks at 67 and 109 GB, beyond the 64 GB CPU pod.
- On this pod the gc-freeze pair fails at base even with its file run alone (both tests; a1 saw one).
- Tooling: `research pods create --vcpu` must be a power of 2 (RunPod refuses otherwise; the help text doesn't say).
- Tooling: `gate_a.sh`'s `key_file_present` (from a1's recipe) checks only `/root/r2ro.env`, so a key anywhere else on the pod
  goes unnoticed; that's how the deviation above went unseen for an hour. A sweep for key values before the run would catch it.
