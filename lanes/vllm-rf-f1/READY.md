---
id: vllm-rf-f1/ready
lane: vllm-rf-f1
kind: ready
status: complete
repo: verity
updated: 2026-09-25T05:09Z
---
# f1 (opened-value replay, D1): READY

## Branch

`origin/lane/vllm-rf-f1` at **`299f42d5`**, on `main` **`baeefd21`** (f24 and f56 merged). Eight commits: the lane's
seven (library, tests, fault hook and padding fixture, test fixes and names, the fault hook on windowed host copies and on
inference tensors), then the lint commit, which moves code so the lints pass. 27 files, +1313 / -497: 10 library files (3
new modules), 13 test files and 4 allowlists. No Markdown added.

Two heads carry the evidence:

- **`d1f18fc8`**, on `main` `bbbe936c`: gates (a) and (b) ran here (Gate evidence).
- **`299f42d5`**: `d1f18fc8` rebased onto `baeefd21`, with exactly the three conflicts named in the coordinator's 04:06Z note.
  Both import conflicts keep both sides: main's `replay_codes` import and mine in `check/sampled_replay.py`, and main's
  `collective_sites` import and mine in `tp/partial_source.py`. The P10 counts are the measured sizes. All four were lowered
  and none raised: `sampled_replay` 247 (function) and 3099 (module), `commit_delta.main` 1916, `tp/worker` 1558. In `git
  range-diff`, commits 2-7 are identical, and commits 1 and 8 differ only by main's neighbouring lines and those counts.
  `commit/opened.py`, `commit/native_ranges.py` and `check/value_check.py` are byte-identical to `d1f18fc8`. At `299f42d5`,
  on a pod: the lints pass (44 of 44), the touched and affected test files fail only on a1's list, and gate (b) is green
  against main `baeefd21` run on the same pod (Gate evidence). By your 04:06Z note, gate (a) and the GPU rows stay valid,
  since the rebase conflicted only in the three named places.

f24's D13 makes the Commit verdict read structured codes on the reasons a value could not be evaluated. It does not
interact with D1. A failed opening is a mismatch (`result False`, "opened value not verified"), not a not-evaluable reason,
so it needs no code. Where a failed opening does reach a not-evaluable path, `why_class` gives it a fault class, and a fault
never counts toward a pass.

`main` has since moved to `5e0c7ca7` (Merge #12, five files, all under `tools/research`). It merges cleanly with
`299f42d5` (`git merge-tree`), and `integrations/vllm` is identical at both, so I stayed on `baeefd21` as the 04:06Z note says.

## What changed

Every verdict-bearing value check reads the committed values it compares through `commit/opened.OpenedReader(com, run)`.
Each read opens the leaves holding the requested bytes and verifies them against the run root before returning them.
Nothing compares the committer's retained memory directly any more.

- **Openings** (`commit/native_ranges.py`, a mixin of `acquire/native_host.NativeHostCommitter`): `RangeOpening`;
  `leaf_span`, `open_range` (one gather per range; `None` when the bytes are not retained) and `verify_range` (leaf
  digests recomputed from the opened bytes, folded with the O(log n) boundary siblings to the step root, step root bound
  into the run root; the reader memoizes an authenticated step root, so the bind and run-root cost is paid once per step).
  Same leaf rules as `open`/`verify` on every layout: GPU-tree step block, host stream, per-tensor host, padding steps,
  windowed and ranged host copies. The run root is `padding_steps.run_root_of`, the same fold `verify` uses.
- **Reader** (`commit/opened.py`; `check/oracle_compare` re-exports it): `committed_reader` is removed. `OpenedReader` keeps
  its call signature and meta selection, raises `OpeningNotVerified` naming step, member, ordinal, byte range and leaves
  when an opening does not verify (it never returns unverified bytes), and returns `None` for bytes that are not retained.
  `read_meta` refuses a meta that is not an object of the committer's layout at that step. Its stats go into the record
  as `value_source`: reads, leaves, bytes, seconds, failed (with the failures by name), not_retained, steps_bound.
- **Consumers:**
  - `oracle_compare`: an entry whose opening does not verify is a mismatch by name (result False).
  - `harness/commit_delta.py`: oracle_compare, sampled_replay, boundary_linkage and padded_population read through the
    reader; `value_source` is recorded beside oracle_compare and beside the replay (`opened_values.replay_linkage`).
  - `check/sampled_replay.py`: a VU whose committed read does not verify is a mismatch by name, also in the forked
    replay children, whose reads are summed into `value_reads_in_children`; a boundary pair whose read does not verify
    is unlinked.
  - `check/value_check.py`: `ValueChecker.compare(reader)` (value_correspondence, dense `--value-check` and TP).
  - TP, per rank: `tp/partial_source.py` `_committed` is `reader.read_meta`; `compare(reader)` and
    `compare_match_oracle(capture_dir, reader)` record `not_verified` and `value_source` and pass only with none
    unverified. `tp/worker.py`: the match-oracle compare in `tp2_commit_finalize`, `_tp2_attribution`,
    `_tp2_sampled_replay` and `tp2_commit_xrank_dump` read through `OpenedReader(com, rc)` with the rank's run
    commitment, as does the fused-MoE late-read detector (`partial_source.late_read_check`).
- **Negative-test hook:** `VERITY_FAULT=retained_flip[:<name substring>]` (default `qkv_proj`). After the commit and
  before the openings and value checks, `commit_delta` calls `fault_retained_flip`, which flips the low bit of byte 0 of
  the earliest committed member whose name contains the substring, in the retained copy every read uses. Recorded as
  `row.fault_retained_flip`.
- **Tests:** `tests/check/opened.py` builds real CPU committers (`commit_steps` packs step blocks with
  `commit_block_offline`, the CPU reference of the GPU chunk tree; `commit_host_steps` uses the per-tensor host path).
  New `tests/check/test_opened_values.py` and `tests/acquire/test_range_openings.py`. Nine test files moved from
  `committed_reader` and stub committers to the reader over real CPU committers. TP negatives are in
  `test_tp_partial_match_oracle`, `test_tp2_t6_4_check` and `test_tp2_attribution`. The fixture `_b2_mixed_padded`
  (`test_padding_pod_consumer.py`) rewrote two metas' dtype and shape after the commit; the step root binds the layout,
  so an opened read correctly refused them. It now commits them typed.

## Rebase and lints

The first rebase, onto `bbbe936c`, had no conflicts. (The second, onto `baeefd21`, is described under Branch, and its lint
run is under Gate evidence.) At the head of the first rebase, `tests/lint` failed three rules, all from this lane's code:
P07 (`VERITY_FAULT` read three times in `commit_delta.main`), P09 (`tp.partial_source` importing `check.oracle_compare`)
and P10 (eight size caps over). `d1f18fc8` fixes them by moving code, never by raising a cap:

- `commit/opened.py`: the reader, `OpeningNotVerified`, `OPENED_METHOD`, `meta_by_name`, and the small helpers the checks
  shared (an unverified read as a named mismatch, forked-child read sums, the unverified-unlinked store, record filing).
  `tp.partial_source` now imports from `commit`, which is below it.
- `commit/native_ranges.py`: the range openings and the fault hook, out of `native_host`.
- `check/replay_dump.py` (the opt-in replay word dumper), `check/value_check.run_value_check` (commit_delta's value-check
  block), `tp/partial_source.late_read_check` (the worker keeps a delegate), `sampled_replay._picks_by_request_step`.
- One `VERITY_FAULT` read in `commit_delta`.
- Allowlists: the P07, P11 and by-name entries of moved code follow it; P10 caps are lowered to the new sizes (none is
  above main's).

On `vyv-rf-f1-cpu` at the `d1f18fc8` tree: `tests/lint` and `tests/test_no_by_name_rules.py` pass, 44 of 44. pyflakes
reports nothing that is not already at main. The moves change no behaviour; gates (a) and (b) below ran at `d1f18fc8`.

## Choice: open and verify every compared position

The verdict-bearing compare opens and verifies every position it reads. There is no in-memory compare left and no
diagnostic-only path.

Measured from the head records' `value_source` (per instrumented pair, and per rank on TP2; `e2f85a82`, see acceptance):

| row | check | opened | seconds opening | check wall, base -> head |
|---|---|---|---|---|
| #101 dense | oracle_compare | 6,368 reads, 1.65 M leaves, 419.7 MB | 7.8-7.9 | 5.9 -> 13.6 s |
| #101 dense | sampled replay (32 forked workers) | 84,118 reads, 0.43 M leaves, 109.6 MB | 55.9 CPU, spread over the workers | 55.1 -> 55.4 s |
| #70 TP2 MoE | match oracle | 14,592 reads, 6.59 M leaves, 1.68 GB | 19.9-27.7 | 2.2-2.5 -> 22.1-30.6 s |
| #70 TP2 MoE | sampled replay (1 worker) | 2.14 M reads, 32.1 M leaves, 7.66 GB | 367-377 | 797-866 -> 1156-1183 s |
| #67 MoE | C2 oracle compare (one pair) | 278,604 reads, 36.8 M leaves, 9.35 GB | 196.2 | 365.0 -> 543.4 s |

| row | Commit wall, base -> head |
|---|---|
| #101 dense, 3 pairs | 289 s -> 380 s; about 313 s (+8%) without the one-off extension rebuild |
| #70 TP2 MoE, 3 pairs | 5,062 s -> 6,560 s (+30%) |

- The cost is linear in what is read: about 4.8 us per 256 B leaf on the dense row and 5.3 us on #67's compare, plus
  a per-read overhead that dominates when reads are small and many (about 100 us per read in the TP replay). The dense
  row pays about 8%. #67's compare pays +49% (+178 s on 365 s) for 9.35 GB opened.
- TP2 pays 30%, nearly all in the per-rank sampled replay. It opens 7.66 GB per rank per pair (32.1 M of the rank's
  72.4 M committed leaves) through 2.14 M reads of 3.6 KB on average, so the fixed cost of each read (its boundary
  path and step binding) is more than half of the 367 s. At TP the replay runs in one worker, so none of it overlaps
  with other work. The match oracle adds about 23 s per pair.
- Restricting the verdict to the random openings would shrink what it covers from every compared identity (6,304 per
  pair on #101; 14,592 tensors per rank per pair on #70) to 64-128 sampled leaves per pair. The pod negative shows what
  that loses: the 64 openings (64/64 verified) and the sampled replay (True) both missed the flipped leaf, and only
  the full opened compare failed it.
- A diagnostic memory compare beside it would keep a second path that reads unverified memory, which is what D1
  removes.
- Not done, and the way to take the TP2 cost back without narrowing the verdict: open and verify the replay's reads
  per step in one batch rather than one by one, run the TP replay's evaluators in forked workers as TP1 does, or hash
  the opened leaves on the GPU (the chunk-tree kernel already hashes them).

The +67.5 s in `prep.warmup_instrumented` on the #101 head Commit is not opening cost: the `hidden_gpu_tree` extension
was rebuilt because the base and head trees import it from different directories and torch keeps one build per
extension name. The head negative Commit right after warmed up in 1.56 s.

## Gate evidence

### At the rebased head `299f42d5` (coordinator's 04:06Z list)

These ran on `vyv-rf-f1-cpu2` (RunPod cpu3g, 32 vCPU, 128 GB cgroup limit, AMD EPYC 7713), set up with a1's recipe
(bootstrap `r20260925-042905-a8bb`, BOOTSTRAP-OK). Every run went through `research run --source <worktree> --cwd source`
at a clean committed head.

- **Lints: 44 of 44 pass** (`r20260925-043155-7013`): `tests/lint` 41, `tests/test_no_by_name_rules.py` 3.
- **Touched and affected test files: 833 passed, 34 skipped, 4 failed, all four in a1's list** (same run, `-n 8 --dist
  loadfile`). The files: `acquire/`, `commit/`, `tp/`, every `check/test_sampled_replay*`, `check/test_opened_values`, both
  `check/test_oracle_compare*`, `check/test_committed_reader_shared_module`, `check/test_alias_reference_fixture`, f24's
  `check/test_commit_verdict_reason_codes` and `check/test_verdict`, `check/test_global_match`,
  `harness/test_admit_r19_host_working_set` and `program/test_padding_pod_consumer`. The four failures are the gc-freeze
  pair of `test_admit_r19_host_working_set`, `test_native_jit_keying` (`pod_release.sh` missing) and
  `test_compiled_source` (CUDA driver).
- **Gate (b): green.** `r20260925-043152-27f8` at `299f42d5` and `r20260925-043149-0159` at `main` `baeefd21` ran side by
  side on the same pod, with the command used at `d1f18fc8` (`OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra
  -n 12 --dist loadfile`, `CUDA_VISIBLE_DEVICES=`, each from its own copy of the tree). Each took 33 minutes; this host is
  slower per core than `vyv-rf-f1-cpu`, and `test_derive_realhf` and `test_derive_hf5b_realhf` are the long pole.

| commit | total | passed | failed | error | skipped | xfailed |
|---|---|---|---|---|---|---|
| base `72884c8a` (a1 xdist) | 3904 | 3536 | 54 | 11 | 297 | 6 |
| main `baeefd21` (this pod) | 3910 | 3558 | 49 | 11 | 286 | 6 |
| head `299f42d5` (this pod) | 3933 | 3580 | 49 | 11 | 287 | 6 |

- Against main on the same pod, `baseline-jdiff.py` exits 0: no new failure, error, skip or skip reason. The 24 new tests
  pass, and one test is renamed (`…committed_reader_answers…` to `…opened_reader_answers…`). Failures and errors are 60 at
  both. One outcome changes: `test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation`
  passes at main and is skipped here ("allocator did not reuse the pointer"). a1 lists that test as order-dependent.
- Against a1's baseline: no new failure, and failures and errors drop from 65 to 60. The seven base failures that pass
  here also pass at main on this pod. The two `test_admit_r19_host_working_set` gc-freeze tests fail, as they do in a1's
  list (this pod's interpreter also starts with `gc.get_freeze_count() == 375`). The one new skip reason is main's own
  `test_ship_roots` skip, which main shows on this pod too.

The JUnit files and diffs are beside this note: `head-gate_b-299f42d5-xdist.xml.gz`, `main-gate_b-baeefd21-xdist.xml.gz`,
`head-gate_b-299f42d5-xdist.jdiff-main-baeefd21.txt`, `…jdiff-a1.txt`, `head-lint-299f42d5.xml.gz` and
`head-touched-299f42d5.xml.gz`.

### At `d1f18fc8`

Gates (a) and (b) at `d1f18fc8` ran on `vyv-rf-f1-cpu` (RunPod cpu3g, 8 vCPU, 32 GB cgroup limit), and gate (a)'s T1
`replay_partition` on `vyv-rf-f1-t1` (cpu3m, 64 vCPU, 512 GB). Both pods were set up with a1's recipe: Python 3.12.14 (uv),
torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80, triton 3.7.1, numpy 2.3.5, pytest 9.1.1, pytest-xdist 3.8.0. Every
run went through `research run --source <worktree>` at the clean committed head.

#### (a) regression, tiers T0 and T1

**Green.** At `d1f18fc8`, as two runs that together select gate (a)'s 158 tests (`VERITY_REGRESSION=1
VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression -ra`), store-only: each pod's
fixtures were prefetched with a key minted on the laptop, and the key was deleted before the run (the jobs refuse to start
while `/root/r2ro.env` exists); no rows root or candidate.

- `r20260925-032012-ef74` on `vyv-rf-f1-cpu`, serial, `-k "not replay_partition"`: 145 tests, 64 passed, 81 skipped, exit 0
  (50 min).
- `r20260925-033833-dec1` on `vyv-rf-f1-t1`: the 13 `T1-replay_partition` tests as four serial processes over disjoint rows,
  each with its own tree copy and scratch directory: 9 passed, 4 skipped, exit 0 (15-20 min each, 251 GB peak).

`vyv-rf-f1-cpu` has a 32 GB cgroup limit, although `free` shows the host's 755 GB. A first attempt there with three
processes, `r20260925-031034-be4b`, was OOM-killed (telemetry class `CGROUP_OOM`) and is void. `replay_partition` needs
63-115 GB per process, hence the second pod.

| commit | tiers | selected | passed | failed | skipped |
|---|---|---|---|---|---|
| base `72884c8a` (a1) | T0 | 158 | 64 | 0 | 94 |
| base `72884c8a` (a23b) | T0, T1 | 158 | 73 | 0 | 85 |
| head `e2f85a82` (tp2) | T0, T1 | 158 | 73 | 0 | 85 |
| head `d1f18fc8` | T0, T1 | 158 | 73 | 0 | 85 |

Against a23b's T0+T1 base and against `e2f85a82`, every one of the 158 tests has the same outcome. `baseline-jdiff.py`
exits 1 only for two reworded skip reasons: `manifest_digest` on the TP rows #70 and #75 now names `tp_stage.sh` instead
of `row_pod_tp2.sh` (main's `5cc0506e`; `tests/regression` is identical to main on this branch). Against a1's T0-only
base nothing fails; the changes are the 9 `T1-replay_partition` passes and the T1 skip reasons, as at `e2f85a82`. The
merged JUnit and the diffs are beside this note: `head-gate_a-d1f18fc8-T0T1.xml.gz`, `…jdiff-a23b-base-T0T1.txt`,
`…jdiff-e2f85a82.txt`, `…jdiff-a1.txt`.

#### (b) `python -m pytest integrations/vllm/tests`

**Green.** `r20260925-025346-73c9` at `d1f18fc8`: `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12
--dist loadfile` with `CUDA_VISIBLE_DEVICES=`, from a copy of the tree at `/workspace/gate/gate_b-d1f18fc8-xdist`; 16 min.

| commit | total | passed | failed | error | skipped | xfailed |
|---|---|---|---|---|---|---|
| base `72884c8a` (a1 xdist) | 3904 | 3536 | 54 | 11 | 297 | 6 |
| main-level `9be6e462` (a23b rebased, xdist) | 3874 | 3515 | 56 | 11 | 286 | 6 |
| head `d1f18fc8` | 3897 | 3540 | 54 | 11 | 286 | 6 |

- Against a23b's rebased run (main's `integrations/vllm` tree), `baseline-jdiff.py` exits 0: no new failure, error, skip
  or skip reason. The 24 new tests pass, one test is renamed (`…committed_reader_answers…` to `…opened_reader_answers…`),
  and two base failures pass (`test_row_pod_cancel_forwarding::test_sigint…`, `test_norm_chain::test_mean_pins_match_installed_vllm`).
  Failures and errors: 67 there, 65 here.
- Against a1's baseline: no new failure; failures and errors 65 at both. The 72 base-only tests are main's deleted
  modules plus the rename; the 65 head-only tests all pass (24 of this lane, 41 of main's lints). The two
  `test_admit_r19_host_working_set` gc-freeze tests fail (in a1's list; they fail in a23b's run too, and this pod's
  interpreter also starts with `gc.get_freeze_count() == 375`). One skip reason is new: main's own
  `test_ship_roots::test_ship_pack_carries_out_gen_hf_configs` ("no record_v5/ship.sh or data/hf_configs").

JUnit and both diffs are beside this note: `head-gate_b-d1f18fc8-xdist.xml.gz`, `…jdiff-a23b-rebased.txt`,
`…jdiff-a1.txt`. Before the rebase, both gates were also green at `e2f85a82` on tp2 (`head-gate_a-T0T1.*`,
`head-gate_b-xdist.*`).

### (c) acceptance

The regression Commit rows and the pod negative ran at `e2f85a82`, the lane's head before the first rebase (on
`72884c8a`). The rebased `324654c1` carries the same lane changes onto `bbbe936c`, `d1f18fc8` only moves code, and
`299f42d5` is `d1f18fc8` on `baeefd21`. No row has run at either rebased head: both GPU pods were drained at about
01:40Z, before I read the rebase note (see Open questions).

- **Regression Commit rows, base `72884c8a` vs head `e2f85a82`, same Build and Match** (the row directory copied after
  Match, byte-identical), through `research run --tool vllm.commit`:
  - #101 `llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager` (g1b): base
    `r20260924-212151-1320` PASS, head `r20260924-212749-8f78` PASS, every check PASS at both; oracle_compare 6,304 =
    6,304 equal per pair at both; head `value_source` as in the table, failed 0, not_retained 0.
  - #70 `olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager` (tp2; OLMoE, so the MoE row and the
    TP2 row, and the cheapest MoE row by Commit cost): base `r20260924-221949-8668` and head `r20260924-234524-0620`
    both `commit FAIL rc=1`, 3 pairs, the fixture's class. The component results match: replay False (partial,
    484 / 475 q/k-norm strata not evaluated on rank 0 / rank 1), linkage True, xrank False (AllGather2 sites without a
    stratum), fold_binding False, weights_pin True. Every pair and rank has the same values at both: tp run root
    `0b91229f06480ce4…`, tokens equal, match oracle 14,592 = 14,592 equal (0 not verified at head), sampled replay
    9,656 / 9,665 equal and 0 mismatch, linkage 434/434, attribution ok, xrank picks 154 = 154 equal, openings 128/128,
    value check 24,960 taps equal per rank, t6_4 True. The head records `value_source` on the match oracle, sampled
    replay and attribution. The Match at `72884c8a` fails at the per-rank fold (`derived_OLMOE_tp2`: 4,096 errors and
    3,544 unresolved per rank) after the capture and collective check passed. The Commit stage does not gate on it,
    and both Commits carry the same `fold_binding` FAIL. `r20260924-222022-d9a6` is a void duplicate of the base
    launch (the launch call was re-issued), which ran beside the base's manifest phase and died 12 s into its own
    commit step. The base timings above come from the commit step, which it did not overlap.
  - #67 `olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager` (g1b), reduced to one pair (`PAIRS=1`)
    for both arms, because a 3-pair #67 Commit takes about 2 h 26 min on an idle pod (`r20260924-102613-0196`) and
    both arms would not fit before the pods' then 03:00Z end. Even so, the base's sampled replay ran 1 h 50 min on this
    shared host without finishing, so I stopped it (`r20260924-231650-a561`, cancel intent recorded) to give the head
    time to reach its compare. The head `r20260925-013654-9d27` matched the base stage by stage up to the compare,
    and I stopped it after the compare (cancel intent recorded). Both arms have the same binding map digest
    `4f6b98bedb394ef1`, population 425,312 (digest `1169e03b44caf215`), population openings 81/81 and manifest
    coverage 406,220 with 0 missing. Their C2 oracle compares agree: `partial` by design (the Match snapshots steps 0
    and 1), 16,120 = 16,120 equal, mismatch 0, the same attribution (1,308 pairs, 0 unverified, the same 11 ambiguous
    requests). The head's opened 278,604 reads verify with 0 failed. No #67 verdict comparison exists; #70 is the MoE
    row of record.
- **Negative test:** CPU, `tests/check/test_opened_values.py` (a retained copy changed after the commit to agree with a
  wrong oracle: the memory compare PASSes, the opened compare FAILs naming the member; the same through replay and
  linkage; the fault hook on block, host, windowed and ranged copies held as inference tensors), passing in gate (b) at
  `d1f18fc8`. Pod: `r20260924-215417-8d40`, #101 Commit at `e2f85a82` with `VERITY_FAULT=retained_flip`:
  `commit FAIL rc=3 outcome=FAIL`, runtime_match FAIL and every other check PASS. Each pair: "C2 oracle mismatch: 1
  identities differ from the Match oracle (first: step 0 model.layers.0.self_attn.qkv_proj/0 inv 0 req r0 range [0,
  786432] -- opened value not verified: step 0 model.layers.0.self_attn.qkv_proj/0 (ordinal 3) bytes [0, 1572864) =
  leaves [8196, 14340): the opening does not verify against the run root)". On the pod the flipped byte also differs
  from the honest oracle, so the base's memory compare would fail too, by value; the head fails by root verification,
  which also catches a copy made to agree with the oracle (the CPU tests). The first pod attempt,
  `r20260924-214541-c946` at `62d6b9e0`, crashed in the fault hook (an in-place write to an inference tensor outside
  inference mode); `e2f85a82` fixed the hook, and its CPU test now holds the copies as inference tensors, as the
  collector does.
- **Commit time:** the table above.

Records. Preserved on the store remote (fetched with `research fetch --all`, then `research data attempt publish` and
`research data push` from the laptop): #101 base, head and both negative attempts, the #101 Build+Match
`r20260924-202429-ba17`, the #67 Match `r20260924-220341-0afd`, the first cancelled #67 base
`r20260924-231111-b648`, the #67 head `r20260925-013654-9d27`, and the gate runs at `d1f18fc8` (gate (b)
`r20260925-025346-73c9`; gate (a) `r20260925-032012-ef74` and `r20260925-033833-dec1`; the void
`r20260925-031034-be4b`). tp2 was drained before I found that the drain sees only attempts
already pushed from the pod, so it terminated with its attempts unpushed. For those (the #70 arms, the void
duplicate, both `e2f85a82` gates) the laptop keeps their records in `~/.research/runs/<id>`, and the row evidence
and JUnit files are beside this note: `commit70-base-head.tgz`, `commit101-67-evidence.tgz`,
`commit67-head-partial.tgz`, `head-gate_a-T0T1.*`, `head-gate_b-xdist.*`. `r20260924-231650-a561` (the second #67
base) cannot be published: its runner was in the signalled process group, so its status stayed "running". Its files
are fetched. The runs at `299f42d5` are preserved the same way: the bootstrap `r20260925-042905-a8bb`, the lints and
touched tests `r20260925-043155-7013`, and gate (b) `r20260925-043152-27f8` (head) and `r20260925-043149-0159` (main).
Four void launches are also preserved: `r20260925-042334-f76f`, `r20260925-042642-c979`, `r20260925-042715-a96f` and
`r20260925-042717-8109`. The first failed at once, and I cancelled the other three with `research tele cancel-intent`
(class `CANCELLED_MANUAL`, evidence in each attempt), because I had left out `--cwd source` (Found, not fixed). All five
of the lane's pods are terminated: g1b and tp2 at about 01:40Z, `vyv-rf-f1-t1` at 04:02Z, `vyv-rf-f1-cpu` at 04:12Z and
`vyv-rf-f1-cpu2` at 05:08Z. The last three were drained with every attempt preserved.

Two deviations from the laptop rule. At 21:50Z I ran `tests/check/test_opened_values.py` once on the laptop (the v2
worktree's venv, torch 2.14) to confirm the inference-tensor fix. At about 04:14Z I ran the lint suite on the laptop
(`--noconftest`, Python 3.12) to find the P10 counts after resolving the rebase conflicts. The pod runs above are the
evidence of record for both.

## What deliberately didn't change

- The commitment: committers' layouts, leaf ids, roots, Program and manifest digests are untouched; only the readers
  changed.
- `openings`, `openings_population` and `openings_after_release`. Values opened by replay after release count only
  there, where each is verified against the original run's root and a failure fails the Commit. The value compares
  never read replay values: a released position reads as not retained and is not compared.
- retain=none rows: the compares have no retained bytes to open, as before.
- The compiled-graph checks (below).

## Found, not fixed

- `check/compiled_value_check.py` and `check/compiled_kernel_check.py` still compare the committer's retained memory.
  They run on compiled-graph rows only, none of the three regression rows.
- `tests/tp/test_tp2_xrank_collectives.py::test_flip_site_alters_the_collective_input_but_not_the_committed_partial`:
  its `TPPartialSource.__new__` stub has no `_occ`, so it raises AttributeError whenever CUDA is visible.
- The uv cpython 3.12.14 interpreter on these pods (GPU and CPU alike) starts with `gc.get_freeze_count() == 375`, so
  the two gc-freeze tests of `test_admit_r19_host_working_set` fail there at any commit.
- `tests/program/test_artifact_applicability_independent.py` `_source_files()` drops every path with a `tests`
  component, so run from a tree under a `tests/` directory it scans nothing: the capability-literal tests pass vacuously
  and one case turns into a skip.
- #70's Match at `72884c8a` fails at the per-rank fold Match (above).
- `hidden_gpu_tree`: two source trees on one pod rebuild the extension (about 65 s) at every switch.
- The TP sampled replay runs its evaluators in one worker (`workers 1`), unlike TP1's forked pool, so everything it
  reads is serial. That is where the TP2 opening cost lands.
- `research pods drain` counts only attempts already pushed from the pod. A pod whose attempts are published only to
  its local store reports "0 attempt(s) recorded" and is terminated without `--force`. Once the attempts were pushed,
  the default `--mode head` crashed in `store/preserved.py` (`index.set_replica`: "attempt to write a readonly
  database"); `--mode recorded` drained. (For the two CPU pods at 04:02Z and 04:12Z, `--mode head` worked.)
- On a cpu3g pod, `free` reports the host's memory (755 GB), not the container's 32 GB cgroup limit
  (`/sys/fs/cgroup/memory.max`). Gate (a) with more than one manifest build at a time does not fit.
- The lint scanners read every `*.py` file as UTF-8, so AppleDouble `._*.py` files, which macOS `tar` writes for
  extended attributes unless `COPYFILE_DISABLE=1`, fail every rule at once.
- Since `baeefd21`, `research run --on` runs the workload in its run directory unless `--cwd source` is passed. A
  command written for the old default fails at its first relative path (`cd integrations/vllm`). A launch without it cost
  me four void attempts.
- `research pods create --register` (tool at `baeefd21`) writes the machine to `~/.research/notes/machines.d/<name>.toml`,
  but `research run --on` then refuses the machine because it reads only `~/.research/machines.toml`. I added the entry
  there by hand.

## Open questions

- No Commit row has run at a rebased head. The 22:13Z note asked me to ship the rebased head to g1b for you to copy to
  tp2, but I read that note only after both GPU pods were drained. The rows' evidence is at `e2f85a82`. The rebase onto
  `bbbe936c` was clean, `d1f18fc8` only moves code, and the rebase onto `baeefd21` had only the three conflicts your
  04:06Z note names, so by that note gate (a) and the GPU rows stay valid. If you want a row at the merged head, #101 is
  the cheapest (Commit about 6 min on one L40S after its Build and Match).
- f3 merges next. When it lowers `commit_delta.main` again, its count and this branch's 1916 conflict in `p10_size.json`.
  Take the count `tests/lint` prints at the merged tree.
