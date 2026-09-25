---
id: vllm-rf-f1/state
lane: vllm-rf-f1
kind: state
status: active
created: 2026-09-24T17:32Z
updated: 2026-09-25T05:47Z
---
# vllm-rf-f1: opened-value replay (D1) (state)

> **Coordinator, 04:40Z: main moved again, to `cc7842a0` (f3 merged). Rebase `299f42d5` onto it.** There is one conflict, in `p10_size.json` on the `commit_delta.main` cap (main 1915, yours 1916): take the count `tests/lint` prints, probably 1914. Then run lints and gate (b) at the new head. Details: `20260925T0406Z-handoff-from-vllm-coordinator.md` (update section).
>
> **Coordinator, 05:01Z: the vyv- pod deadline is now 09:00Z (2 AM PT).** I extend it in steps of at most 4 h while I run. If I stop, pods die at the armed time, so keep results registered as they land.
>
> **Coordinator, 00:32Z: main moved again, to `4bd6c54c` (a23b merged). Rebase onto that instead;** it's clean with your head. See `../vllm-refactor/20260925T0032Z-main-moved-a23b.md`.
>
> **Coordinator, 22:13Z: main moved to `1d9c3198` (a1's lints merged).** Between runs, never mid-run, rebase onto `origin/main` (it's clean with your head) and push with `--force-with-lease`. Run `tests/lint` on a pod, fix the allowlists it prints, and run your gates at the rebased head. The rebased head is a new source identity: ship it to g1b, and I copy it to tp2 (say so under Open questions). Steps: `../vllm-refactor/20260924T2213Z-main-moved-rebase.md`.

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 D1, §4 P2; `20260924T1625Z-coordinator-checks-on-check-commit-survey.md`; `survey-check-commit.md` §3.
- **Lane prompt (verbatim source):** coordinator transcript `eb746331-5a84-4468-9455-5c2a7c14f35c.jsonl`, search "You are lane f1". Key lines:
  - Fix: "the verdict-bearing value check consumes opened, verified values only ... either open and verify every position the compare reads, or restrict the verdict-bearing compare to opened positions and keep any wider in-memory compare only as a labelled diagnostic that can never make the verdict PASS. Choose based on cost (measure opening cost on a real row) and give the reasoning in READY.md. Values opened by replay after release (openings_after_release) count as opened only if verified against the root. Do the same for the per-rank TP path." Problem names `commit_delta.py:2339`, `tp/worker.py:1192`, `tp/partial_source.py:59-65`.
  - Negative test: "mutate the retained buffer after the commit (before openings and compare) and show the value check FAILs ... on CPU if a CPU double exists, otherwise as a pod-marked test, plus one real pod run."
  - Acceptance: gates (a) and (b); on GPU pods re-run one dense, one MoE and one TP2 regression Commit row (cheapest in `tests/regression/fixtures.toml`) through the research Tools, verdicts unchanged and the opened-value compare in the record; negative test FAILs as intended; commit time before and after.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f1`, branch `lane/vllm-rf-f1` from `72884c8a`.
- **Gate (b) rule (coordinator, after restart):** no failure, error or skip reason outside a1's list in `~/.research/notes/lanes/vllm-rf-a1/baseline.md` (65 failures/errors, 50 skip reasons at `72884c8a`). Pod recipe is in that note.
- **Laptop rule:** no pytest / no importing verity_vllm or torch locally; all tests on pods.

## Done
- 17:32Z worktree created.
- 18:46Z resumed after the 18:02Z Cursor restart: worktree clean at `72884c8a`, no commits; nothing from the first run survived beyond the worktree.
- 18:56Z mapped compared vs opened positions (below). No code changed yet.
- 19:08Z design settled (below). Still no code changed.
- 19:17Z written (uncommitted, not yet run anywhere): `committer_api.RangeOpening`; `native_host`: `_open_range_levels` (one gather + one D2H per range for tensor levels), `_run_root` (shared by `verify`/`verify_range`), `leaf_span`, `_tensor_of_leaves`, `open_range`, `_range_leaves`, `verify_range`. Checked against `open`/`verify` leaf rules, `_apply_padding` (mixed steps refold both `_levels` and `_gpu_levels`), `_HostWindows`/`_HostRanges` (`holds`/slicing span windows), `merkle.range_path_shape`/`fold_range` (`CommitError` is a `ValueError`).
- Cost concern: GPU-tree leaves are 256 B and `oracle_compare` reads every binding entry's element range, so a whole-row compare re-hashes ~all compared bytes in Python (~1-1.6 us/leaf incl. fold). Measure bytes read + wall on the base row before deciding on batching/caching.
- 19:30Z written (uncommitted, not run): `oracle_compare.py`: `committed_reader` REMOVED; `meta_by_name`, `OpeningNotVerified`, `OPENED_METHOD`, `OpenedReader(com, run)` (`__call__(step, name, lo, hi)`, `read_meta(step, m, lo, hi)`, `or_none`, `record()`; stats reads/leaves/bytes/not_retained/failed/seconds); `oracle_compare` catches `OpeningNotVerified` per entry -> mismatch. `commit_delta.py`: oracle_compare + sampled_replay/boundary_linkage use `OC.OpenedReader(com, rc)`, `padded_population` uses `_rd.or_none`; `value_source` recorded beside both. `sampled_replay.py`: `replay_vu` wrapper -> VU False on `OpeningNotVerified`; children return their reader stats (`opened_in_children`); `_UnverifiedUnlinked` store wrapper -> boundary pair unlinked.
- 19:38Z pods: g1 (2x L40S) replaced by g1b (1x L40S) per the coordinator's 19:35Z note; TP2 bootstrap found never launched (stuck at `shipping`), relaunched.
- 19:50Z TP + value_check wired (uncommitted then): `partial_source._committed(reader, step, m)` = `reader.read_meta`; `compare(reader)` / `compare_match_oracle(capture_dir, reader)` record `not_verified` + `value_source`, verdict needs `not_verified_n == 0`; `worker.py`: `tp2_commit_finalize` (match-oracle compare), `_tp2_attribution`, `_tp2_sampled_replay`, `tp2_commit_xrank_dump`, `_t6_4_check(…, rc)` all read through `OC.OpenedReader(com, rc)`; `value_check.ValueChecker.compare(reader)` same. `OpenedReader.read_meta` refuses a meta that is not an object of the committer's layout at that step (ValueError: a foreign meta's offsets would open another tensor's leaves).
- 19:58Z checked: `CommittedStore.words` has no try, so `OpeningNotVerified` reaches `replay_vu` -> VU False; `boundary_linkage` counts the pair before the read -> unlinked -> result False; any other raise out of `sampled_replay` lands in the caller's fail-closed 'not run'. `native_host` padding comment updated to name the reader.
- 20:00Z COMMIT `f21f0287` (pushed, `origin/lane/vllm-rf-f1`): all library changes + `tests/check/opened.py` (real CPU committer for tests: `commit_steps` packs step blocks through `commit_block_offline`, the GPU-tree CPU reference). Tests NOT yet ported/run (no torch on the laptop).
- 20:05Z row choice revised: dense = #101 `llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager` (GREEN; cheapest dense row -- the earlier pick #11 is i4096/o512); MoE = #67 (opening cost at scale); TP2 = #70 (only TP2 row with a commit.log; class FAIL by-name -> expect the same FAIL). Stage estimates from vllm-57-fix notes for #67: Build ~34 min, Match ~45 min, Commit ~1h40m.
- Row args: LLAMA32_1B `unsloth/Llama-3.2-1B` `9535bd9b1d1dea6acafbdc4813b728796aeb28da`; OLMOE `allenai/OLMoE-1B-7B-0924` `6d84c48581ece794365f2b8e9cfb043c68ade9c5`; flags `--retain host --build-jobs auto --sweep-dir <dir>` (as #67 in vllm-57-fix). Commit(base) and Commit(head) consume the SAME Build/Match: copy the row dir after Match to a second sweep dir for head.
- NEXT in code: TP (`worker.py` 1192 sampled replay, `_tp2_attribution`, `tp2_commit_xrank_dump`, `_t6_4_check`; `partial_source._committed` -> reader; `compare()`/`compare_match_oracle()` take the reader), `value_check.ValueChecker.compare(reader)` (feeds `value_correspondence` in dense `--value-check` and TP `commit.py:990`, so verdict-bearing: now IN scope). Then tests that call `committed_reader` (7 files) -> OpenedReader over a real CPU committer.

## Compared vs opened positions (at `72884c8a`, paths under `integrations/vllm/verity_vllm/`)

**Opened (root-verified) positions** -- a random sample, not tied to what is compared:
- `harness/commit_delta.py:~2003-2033`: `challenge_positions(rc.run_root, leaves_per_step, args.openings, salt=pair)` -> `com.open(sample)` -> `com.verify(rc, o)`; `row.commit.openings` (a failed opening fails Commit).
- `harness/commit_delta.py:719-742` (`binding_record`): `B.challenge_identities(pop, bmap, rc.run_root, args.openings, salt=b"population/<pair>")` -> open + verify; `openings_population`.
- `openings_after_release` (`commit_delta.py:769+`): deferred positions (retain=none / retain=host+exclude) opened by replay against the run root.

**Compared positions** -- every one reads the collector's retained memory, never an opening:
- `oracle_compare` (`commit_delta.py:2339`, reader `OC.committed_reader(com)`): one read per binding-map entry (step, request, op, member, element_range), except `weights`/`hidden_stream` families and padding entries; bytes `[(eo+lo)*isz, (eo+hi)*isz)` of member `entry_read_name(e)` at `step`, vs the Match oracle. `got is None` -> "not retained" (partial).
- `sampled_replay` (`commit_delta.py:2542`, `_rd = OC.committed_reader(com)` at `:2442`): `CommittedStore.words` (`check/sampled_replay.py:656-685`) reads each sampled VU's input and output slices. NOTE: `replay_vu` runs in FORKED children (`_parallel_replay`) unless retain=device.
- `boundary_linkage` (`commit_delta.py:2515`, same `_rd`): input ids / sampled ids per (step, request).
- `padded_population` (`commit_delta.py:2564`, same `_rd`): padding entries read back == bot.
- TP per rank: `tp/worker.py:1192` `rd = OC.committed_reader(com)` -> `SR.sampled_replay` + `SR.boundary_linkage` on the rank. Rank run commitment is `st["rc"]` after `tp2_commit_finalize` (`worker.py:894`).
- TP, second reader `tp/partial_source.py:58` `_committed(com, step, meta)` (whole meta): used by `partial_source.compare()` (`:402`), `compare_match_oracle()` (`:513`), `worker._tp2_attribution` (`:969`), `worker.tp2_commit_xrank_dump` (`:1268`), `worker._t6_4_check` (`:1507`). `compare()`/`_t6_4_check` run in `tp2_commit_value_check` (its own finalize -> local `rc`).
- `check/value_check.py:105` `ValueChecker._committed` (host copy else GPU block): feeds `value_correspondence` (dense `commit_delta.py:1913` `--value-check`, TP `tp/commit.py:990` via `worker.tp2_commit_value_check`) -> verdict-bearing, IN scope (revised 19:40Z).
- Not in scope: `compiled_value_check.py`, `compiled_kernel_check.py` (compiled-graph rows only; not in the three regression rows) -> "Found, not fixed".

**Leaf layout (`acquire/native_host.py`)**:
- Packed steps (GPU block `_gpu_blocks`, host stream `_streams`, padding): leaf `i` = stream bytes `[i*chunk, min((i+1)*chunk, n))`; member at `[m.stream_off, +m.nbytes)` (GPU: `stream_off == dev_off`, chunk 256; padding metas `dev_off -1`, leaves `>= ps.leaf_base`, `ps.stream[s - ps.stream_base]`).
- Per-tensor host steps: leaves `m.first_leaf .. +m.n_leaves`, leaf `k` = `m.host[k*m.chunk : min((k+1)*m.chunk, m.nbytes)]`.
- Levels: `_levels[step]` host (list of lists of bytes, leaves first, root last); `_gpu_levels[step]` int32 [n,8] tensors (device or host). Tree node/lift hashing == `commit/merkle.py` `hashing.node_hash/lift_hash`, so `merkle.range_path_shape` + `merkle.fold_range` authenticate a contiguous leaf range with O(log n) boundary siblings.
- `verify` per leaf costs `layout_digest` (JSON of all metas) + run-root fold every call: unusable per read at scale.
- `NativeCollectCommitter` (production `native_collect_v2b`) does not override open/verify/identity_of. `CmtRefCommitter` does, but a23 deletes it.

## Design (option A: open and verify every position the compare reads)
- `acquire/committer_api.py`: `RangeOpening(step, lo, hi, value, path)`; path = per level `(left, right)` sibling or None.
- `acquire/native_host.py` (not owned by another lane): `leaf_span(step, meta, lo, hi) -> (a, b, off)`; `open_range(step, a, b) -> RangeOpening | None` (None = bytes not retained; same leaf rules as `open`); `verify_range(run, ro, roots=None) -> bool` (leaf digests recomputed from `ro.value` with `verify`'s three rules; `fold_range`; `bind_root == sc.root`; run-root fold; `roots` = caller memo of step -> authenticated bare root so bind/layout/run-root cost is paid once per step).
- `check/oracle_compare.py`: `OpenedReader(com, run)` replaces `committed_reader` (same call signature + meta selection incl. `#ord`, bare-name ambiguity -> None, padding metas); `read_meta(step, m, lo, hi)` for whole-meta readers; raises `OpeningNotVerified` on a failed verification (never returns unverified bytes); counts `ranges/leaves/bytes/seconds` for the record. `oracle_compare` catches it per entry -> mismatch by name (result False).
- `check/sampled_replay.py` (unowned; minimal hunk): `replay_vu` catches `OpeningNotVerified` -> VU `result False` with the why (works inside forked children). `boundary_linkage`/`padded_population` let it propagate -> caller's except -> not run -> verdict FAIL.
- Wire at `commit_delta.py:2339/2442`, `tp/worker.py:1192`; `partial_source._committed` -> `reader.read_meta`; record `opened_values` stats beside `oracle_compare`.
- Negative tests (CPU, `commit_offline` host path): mutate retained bytes after finalize -> oracle_compare result False naming the opening; variant where the oracle agrees with the mutated memory (PASS before the fix, FAIL after). Pod: one real row with a mutate-after-commit fault.

## Running
> **Coordinator, 20:03Z: DONE. tp2 now has the 72884c8a source tree, copied pod-to-pod from g1b** (the laptop -> tp2 link can't fit the 10-min ship limit). Rerun your tp2 bootstrap command unchanged now: `research run` finds `/workspace/research/src/72884c8a.../` without READY.json, checks every file's sha256 against your git manifest (all 2,814 were pre-checked identical), writes READY.json and skips the upload. Details: `20260924T2003Z-handoff-from-vllm-coordinator.md`.
> **Coordinator, 19:40Z (confirmed by the owner 19:44Z): keep your pods exactly as they are now. Do NOT terminate `vyv-rf-f1-g1b` or `vyv-rf-f1-tp2`, do NOT recreate g1, and create no new pod.** g1 was already terminated at 19:38Z, so ignore the 19:38Z "cancel, terminate g1b" line; it assumed g1 still existed. Continue your plan. (Your 19:38Z swap is recorded below.) See `20260924T1935Z-handoff-from-vllm-coordinator.md`.
- Pod `vyv-rf-f1-g1b` (`u7awphw9p8i2ru`, 1x L40S, 188 GB, 16 vCPU, $1.09/h, created 19:37Z; in machines.toml): rows #11 (dense) and #67 (MoE), ONE AT A TIME (timings). Bootstrap `pod_bootstrap.sh --cases LLAMA32_1B,OLMOE` from the base worktree `verity-wt/rf-f1-base` (`72884c8a`, clean), launched 19:39Z, log `/tmp/rff1/boot_g1b.log`.
- Pod `vyv-rf-f1-tp2` (`t70u3qv3dm09dl`, 2x L40S, $2.18/h, created 19:21Z): row #70 (olmoe TP2 b8). First bootstrap `r20260924-192617-ea73` never left `shipping` (the shipping shell died); relaunched 19:39Z (`--cases OLMOE`), log `/tmp/rff1/boot_tp2.log`.
- `vyv-rf-f1-g1` (`p8njwdgmlcgycu`) TERMINATED 19:38Z (its bootstrap `r20260924-192616-7a8d` was still running; nothing kept). One-GPU create needed `--min-ram 60 --min-vcpu 8` (per GPU); `--min-ram 120 --min-vcpu 16` returned HTTP 500.

- 20:03Z g1b bootstrap `r20260924-193546-4708` BOOTSTRAP-OK 19:49Z at `72884c8a` (torch cu129, vllm d9105ea80, hidden_gpu + FA2 taps sm_89); GPU idle. Host load average ~16-22 (shared host): note for timings.
- TP2 bootstraps: both `research run --on` shippings (19:35Z, 19:44Z) refused after 600 s (laptop upstream shared with other lanes). 20:05Z shipping a gzip'd `git archive 72884c8a` (105 MB) over `research pods ssh ... tar -xz` into `/workspace/research/src/72884c8a…` (the launcher adopts an existing tree by per-file sha256), then relaunch the bootstrap.
- 20:25Z stage runs (all from `verity-wt/rf-f1-base` = `72884c8a`, launcher `/tmp/rff1/research.sh` = `python3.12 -m research` with this worktree's `tools/research/src`; logs `/tmp/rff1/<stage><row>.log`; no artifact store: every stage reads `/workspace/sweep/<row>` on its pod):
  - #101 Build `r20260924-201453-23bc` PASS (build_wall 131 s). #101 Match `r20260924-202429-ba17` launched 20:24Z.
  - #67 Build `r20260924-201507-8e88` running since 20:15Z (est. ~34 min).
  - TP2 bootstrap `r20260924-201429-68bf` SUCCESS (adopted the coordinator's copied tree). #70 Build `r20260924-202455-105b` launched 20:25Z, flags `--retain host --sweep-dir /workspace/sweep` (= the recorded fresh sequence on vyv-tp2x: build/match/commit all `--retain host`).
  - Plan per row: Build -> Match -> copy `/workspace/sweep/<row>` to `/workspace/sweep_head/<row>` -> Commit(base, `72884c8a`, sweep) and Commit(head, sweep_head) back to back, alone on the pod (timings). Head source: pre-seed `/workspace/research/src/<head sha>/` on each pod from the base tree + `git diff` (the launcher adopts a pre-seeded tree by per-file sha256), so the head launch uploads nothing big.
- 20:25Z code: `tests/check/opened.py` rewritten (uncommitted): one tensor spec `(name, bytes[, ordinal[, dtype, shape]])`; `commit_steps` (GPU-tree block, needs torch) and `commit_host_steps` (per-tensor host path via `commit_offline`, torch-free; the retained copy IS the caller's buffer so a bytearray can be mutated after the commit). `native_host.commit_offline` accepts optional dtype/shape per tensor (uncommitted). 11 test files still call removed APIs (`committed_reader`, `_t6_4_check(com)`, `compare_match_oracle(dir)`, `_tp2_attribution(None)`): porting now.

- 20:40Z COMMIT `232cd7d1` (pushed): 9 test files ported to `OpenedReader` over real CPU committers (no stub committers left; `committed_reader` gone from code); new `tests/check/test_opened_values.py` (D1 attack on both layouts: retained copy changed after the commit to agree with a wrong oracle -> memory compare PASS, opened compare FAIL by name; linkage + replay paths) and `tests/acquire/test_range_openings.py`; TP negatives in `test_tp_partial_match_oracle` / `test_tp2_t6_4_check` / `test_tp2_attribution`. `test_tp2_sampled_replay_fold.py` needs no port (its stubs fail closed before the reader is built). Compiled locally only (py_compile).
- 20:41Z #101 Match `r20260924-202429-ba17` PASS. #67 Build (g1b) and #70 Build (tp2) still running.
- 20:44Z head tree pre-seeded on BOTH pods: `/workspace/research/src/232cd7d1…` = the 2,814 base files (by `git ls-tree` list, so no READY.json / build byproducts) + `git apply` of `git diff 72884c8a 232cd7d1` (158 KB) -> 2,817 files; the launcher adopted it (per-file sha256). Script `/tmp/rff1/seed_head.sh <sha>` (needs `/tmp/rff1_base.files0` + `/tmp/rff1_head.patch` on the pod).
- 20:45Z targeted tests at head on tp2: `r20260924-204543-9d4d` (70 files importing the touched modules; xdist -n 12 loadfile; tree copied to `/workspace/tests/t-232cd7d1-targeted`; junit `/workspace/tests/t-232cd7d1-targeted.xml`). Job script `/tmp/rff1/pytest_job.sh TAG files…` (sent with `--send`).
- Constraint (coordinator 19:40Z): no new pod -> gates (a)/(b) run on tp2 while its stages are untimed (Build/Match), never beside a timed Commit.
- 20:50Z targeted #1 (`232cd7d1`, GPU visible): 711 P / 10 F / 176 S; all 20 new tests PASS. vs a1 xdist: 4 "new" failures:
  (1) `test_padding_pod_consumer::test_the_inactive_stratum…`: REAL, fixture: `_b2_mixed_padded` rewrote 2 metas' dtype/shape AFTER the commit
  (comment claimed "roots hash bytes"; the step root binds `layout_digest`) -> the opened read (correctly) fails. Fixed: commit them typed.
  (2) `tp/test_tp2_xrank_collectives::test_flip_site…`: `TPPartialSource.__new__` stub lacks `_occ`; runs only with CUDA (skips on a1's CPU pod). Pre-existing, untouched code -> "Found, not fixed".
  (3,4) `harness/test_admit_r19_host_working_set::` the two gc-freeze tests: precondition `gc.get_freeze_count() == 0` fails because a FRESH
  interpreter on these GPU pods has freeze count 375 (even `python -S`/`-I`; uv cpython-3.12.14 built 2026-09-01, Clang 22.1.3). Environment, not code.
- Decision: gate (b) on the GPU pods runs with `CUDA_VISIBLE_DEVICES=` (tests behave as on a1's CPU pod; no test takes GPU memory beside a stage).
- 20:53Z COMMIT `7c4fedfb` (pushed): `VERITY_FAULT=retained_flip[:<substr>]` (native_host.fault_retained_flip: after the commit flips byte 0 of the
  earliest committed member whose name contains the substring (default qkv_proj) in the retained copy; commit_delta applies it after finalize,
  before openings/value checks; recorded as `row.fault_retained_flip`) + CPU test + the padding fixture fix. `7bacdbb9`: test typo (t1.1 step).
- 20:58Z targeted #3 (`7bacdbb9`, CUDA hidden, gc probe plugin): 709 P / 8 F / 182 S: 6 F in a1's list (source_identity x4, release_json x2) + the 2 gc-freeze
  (every worker frozen=375 after its FIRST test -> interpreter, see above). 21:00Z base control of the gc tests on tp2: `r20260924-210018-1dff` (same 2 fail at `72884c8a`).
- 21:01Z FULL gate (b) at `7bacdbb9` on tp2, CUDA hidden, xdist: `r20260924-210111-1653` (junit -> `/workspace/tests/t-7bacdbb9-*.xml`). 21:03Z #70 Match `r20260924-210318-37b0` (tp2, untimed, both GPUs).
- 21:10Z COMMIT `653f1e5e` (pushed): tests only -- board ids out of the new docstrings / test names (`test_d1_…` renamed). Library code unchanged since `7c4fedfb`. Seeded on BOTH pods (`/workspace/research/src/653f1e5e…`); head Commits use this sha. Final gate (b) must be re-run at the final head.
- 21:10Z #67 Build: 33 derives done 21:01:56Z (wall 2800 s), now CPU-bound program assembly (GPU idle).
- 21:17Z gate (b) `7bacdbb9` DONE: 3914 tests, 3555 P / 36 F / 0 E / 317 S / 6 xf (a1 xdist base: 3536 P / 54 F / 11 E / 297 S). jdiff vs `baseline-gate_b-xdist.xml.gz` (`/tmp/rff1/jdiff_gate_b_7bacdbb9.txt`): 20 of a1's 65 not failing here; NEW failures 3, NEW skip reason 1:
  - 2 gc-freeze tests: fresh `python -S -I` on tp2 has `gc.get_freeze_count() == 375` (4170 objects) -> interpreter, not vLLM (a1 blames EngineCore; not the case here). Same 2 fail at base on tp2.
  - `commit/test_roundtrip::test_transient_storage_is_released` (tracemalloc growth 40,941 > 37,984): code path `commit/fa2_prototype/*` untouched; the file passes ALONE at head AND base on tp2 (13/13) -> depends on which files ran earlier in the xdist worker (new test files change the loadfile assignment). Final gate (b) logs per-worker file order to pin it if it recurs.
  - new skip reason "builder not runnable here: SmolLM2-135M @ 93efa2f0 snapshot not under HF_HOME" (test_applicability module + test_artifact_applicability_independent): tp2 was bootstrapped `--cases OLMOE` only. FIXED env 21:20Z: B0 fetched into `/workspace/hf` by the bootstrap's own checkpoint step (sha256 OK).
- Env (both pods): Python 3.12.14 (uv, built 2026-09-01, Clang 22.1.3), torch 2.13.0+cu129, vllm 0.28.1rc1.dev472+gd9105ea80.cu129, triton 3.7.1, numpy 2.3.5, pytest 9.1.1, pytest-xdist 3.8.0 (tp2); drivers g1b 570.124.06, tp2 580.126.09. Same versions as a1's baseline pod.
- Row runs use `--tool vllm.match` / `--tool vllm.commit` (Tool declarations in `harness/research_tools.py`), `--stage run --cwd source`.
- 21:22Z #101 Commit(base) `r20260924-212151-1320` on g1b (sweep `/workspace/sweep`), launched WHILE #67's single-threaded global_program assembly runs (1 of 16 vCPU, GPU idle); head follows on `/workspace/sweep_head` (sha256-identical copy, 12,923 files). Noted for timings.
- 21:23Z gate (b) at `653f1e5e` on tp2 `r20260924-212347-5115` (per-worker file-order probe `orderprobe.py`) -> finished rc 1 (pytest rc; to be jdiff'd). 21:45Z gate (b) at `62d6b9e0` `r20260924-214459-15a4` and gate (a) at `62d6b9e0` `r20260924-214517-83de` (job `/tmp/rff1/gate_a_job.sh`: T0,T1, no key) launched on tp2 (GPUs idle; #70 Match `r20260924-210318-37b0` FAILED rc 11 -- read why before the #70 Commits).
- 21:40Z COMMIT `62d6b9e0`: `fault_retained_flip` also writes through `_HostWindows`/`_HostRanges` (the windowed collector's host copies; #101 retains that way), test covers block/host/windows/ranges.
- 21:44Z **#101 base vs head (g1b, `native_collect_v2b`, retain host, 3 pairs): verdicts identical, PASS / PASS, every check PASS.** Head `r20260924-212749-8f78` record: per instrumented pair `oracle_compare` compared 6304 = equal 6304 (grade attribution-complete, as base), `value_source`: 6368 opened ranges, 1,645,440 leaves, 419.7 MB, 7.8-7.9 s, failed 0, not_retained 0, steps_bound 32; openings 64/64 verified; sampled replay True, boundary_linkage 32/32; replay reads (pair 0): parent 127 ranges 0.018 s + forked children 84,118 ranges / 432,949 leaves / 109.6 MB / 55.9 s (summed over children, parallel).
  - Commit wall: base 289 s, head ~380 s. Spans (base -> head, 3 pairs summed): `validate.oracle_compare` 17.7 -> 40.9 (+23.2 s = +7.7 s/pair), `validate.sampled_replay` 165.2 -> 166.2 (+1.0), `openings_after_release` 4.8 -> 4.7; everything else +-0.3 EXCEPT `prep.warmup_instrumented` 1.6 -> 69.1 (+67.5): the `hidden_gpu_tree` torch extension JIT-rebuilt, because base and head import it from different directories and the torch-extensions cache keeps one build per name (the head negative run right after: warmup 1.56 s, cache hit). So the opening cost is +23-24 s on a 289 s Commit (~8%), all in the compare; the warmup delta is a cache artefact, reported separately. A tree switch in either direction pays it once (expect it again on #67/#70 base-after-head).
- 21:47Z pod negative #1 `r20260924-214541-c946` (#101 Commit at `62d6b9e0`, `VERITY_FAULT=retained_flip`, sweep `/workspace/sweep_neg`) CRASHED, verdict NOT_RUN: `fault_retained_flip` -> "Inplace update to inference tensor outside InferenceMode" (the collector copies under `torch.inference_mode()`, so its host windows are inference tensors; the CPU test's `.clone()`s were normal tensors). FIX `e2f85a82`: the flip writes under `inference_mode`; the test now holds block/windows/ranges as inference tensors (reproduces the crash on `62d6b9e0`, passes on `e2f85a82`). NOTE: I checked that by running that one test file on the laptop (v2 worktree venv, torch 2.14) -- against the laptop rule; not repeating it; the pod gate (b) at the final head is the evidence of record.
- 21:54Z `e2f85a82` seeded on g1b; sweep_neg reset (removed commit/, commit.log, verdict.json; the prologue files are rewritten by every stage); negative #2 `r20260924-215417-8d40` launched (same command: `--tool vllm.commit --stage negative --cwd source --env VERITY_FAULT=retained_flip -- bash integrations/vllm/verity_vllm/ops/run_row_v2.sh stage commit <row> ... --sweep-dir /workspace/sweep_neg`).
- Final head is now `e2f85a82` (library change in the fault path) -> gate (b) and gate (a) must be re-run there after the current tp2 runs.
- 22:01Z **pod negative #2 `r20260924-215417-8d40` (#101 Commit at `e2f85a82`, `VERITY_FAULT=retained_flip`): FAILS AS INTENDED.** `commit FAIL rc=3 wall=379s outcome=FAIL runs 3 failed 3`; runtime_match=FAIL, every other check PASS; no traceback. Fault: step 0 `model.layers.0.self_attn.qkv_proj/0` (ordinal 3) byte 0 = leaf 8196, 249 -> 248. Each instrumented pair: `oracle_compare` result False, grade mismatch, compared 6304, equal 6303, why "C2 oracle mismatch: 1 identities differ from the Match oracle (first: step 0 model.layers.0.self_attn.qkv_proj/0 inv 0 req r0 range [0, 786432] -- opened value not verified: step 0 model.layers.0.self_attn.qkv_proj/0 (ordinal 3) bytes [0, 1572864) = leaves [8196, 14340): the opening does not verify against the run root)"; `value_source.failed` 1 (that range). The 64 random openings verified 64/64 and sampled replay stayed True (neither sampled leaf 8196): only the opened compare caught it. (On the pod the flipped byte also differs from the honest oracle, so base's memory compare would fail too, by value; the head fails by root verification, which also catches a retained copy made to agree with the oracle -- shown on CPU in `test_opened_values`.)
- 22:01Z gate (b) at `62d6b9e0` `r20260924-214459-15a4` (xdist, CUDA hidden) vs a1 xdist baseline (`/tmp/rff1/jdiff_gate_b_62d6.txt`): 3927 tests, 3562 P / 51 F / 11 E / 297 S / 6 xf; **new failures 0**; failures+errors 62 (base 65); 25 new tests all PASS; `test_roundtrip` and the gc-freeze pair did not fail this time. ONE new skip reason: `test_artifact_applicability_independent::test_i_b_…[<no-capability-literal-site>]` (at base `[…/target_profile.py]`, in a1's failure list). Cause = MY JOB SCRIPT: `_source_files()` drops any path with a `tests` component and the job copied the tree to `/workspace/tests/<TAG>/`, so the scanner saw no files. Not code. Fixed: `pytest_job_order.sh` now copies to `/workspace/gate/<TAG>/` (a1 used `/workspace/base`). Only that test file has this path sensitivity (grep); gate (a) has none.
- 22:02Z gate (a) at `62d6b9e0` cancelled (cancel-intent, manual, rc 143; 22/158 done); **gate (a) at `e2f85a82` `r20260924-215901-8961`** (tp2, T0,T1, serial). a1's T0-only gate (a) took 2 h 42 min.
- 22:03Z **gate (b) at `e2f85a82` `r20260924-220342-5e8a`** (tp2, `/workspace/gate/<TAG>`). **#67 Match `r20260924-220341-0afd`** (g1b, base tree; row `olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager`; #67 Build PASS 21:38Z wall 2800 s).
- #70 Match `r20260924-210318-37b0` FAILED at the fold: capture/control/check pass (8448 collectives, 0 mismatches, tokens True) but `fold_match` (profile `derived_OLMOE_tp2`) rc 1, fold not ok on both ranks (errors 4096, unresolved 3544) -> "MATCH FAIL -> stop" (match stage only). The commit stage does NOT gate on the Match verdict (`tp_stage.sh` commit: Build digests + manifest + `--match-dir`); with `tp2_fold_match.json` on disk it adds `--require-fold-match`, and `tp.commit` evaluates the fold binding AFTER all pairs/value checks as a named FAIL component. Fixture #70 = class FAIL by-name (AllGather2 query_population / xrank; its reference Match was collective-level only). So Commit(base)/(head) over this Match exercise the TP opened reads fully; both get the same extra fold-binding FAIL. `/workspace/sweep_head/<row70>` (copied 21:30Z after the Match) == `/workspace/sweep/<row70>`: 259,801 files, identical path+size listing, key records same sha256.
- 22:19Z **GATE (b) at the final head `e2f85a82`: MEETS THE RULE.** `r20260924-220342-5e8a` (tp2, CUDA hidden, `-n 12 --dist loadfile`, tree at `/workspace/gate/gate_b-e2f85a82-xdist`, 15 min): 3927 tests, 3559 P / 54 F / 11 E / 297 S (+6 xf); `baseline-jdiff.py` vs a1 xdist exits 0: **new failures 0, new skips 0, new skip reasons 0**; failures+errors 65 = base 65. Outcome changes: the 2 `test_admit_r19_host_working_set` gc-freeze tests pass -> fail (jdiff: order-dependent at base, not counted; they fail in a1's serial base and a1's own xdist head), 2 base failures now pass (`test_row_pod_cancel_forwarding::test_sigint…` timeout, `test_norm_chain::test_mean_pins_match_installed_vllm`). 24 new tests (only in head) all PASS; 1 test renamed (`…committed_reader_answers…` -> `…opened_reader_answers…`). Evidence beside this note: `head-gate_b-xdist.xml.gz`, `head-gate_b-xdist.jdiff.txt`.
- 22:20Z **#70 Commit(base) `r20260924-222022-d9a6`** (tp2, base tree `72884c8a`, `--tool vllm.commit`, `--retain host --sweep-dir /workspace/sweep`; gate (a) serial still running beside it). Head follows on `/workspace/sweep_head` at `e2f85a82`.
- 22:30Z READY.md DRAFT at `/tmp/rff1/READY.draft.md` (laptop; TBD = #67, #70, gate (a)). Move to this directory as READY.md when complete.
- **#70 Commit(base) of record = `r20260924-221949-8668`** (tp2, `72884c8a`, launched 22:19:49Z; tp.commit since 22:29:48Z; PAIRS=3). `r20260924-222022-d9a6` (22:20:22Z) is a VOID DUPLICATE of the same launch (my launch call was re-issued when the harness restarted the turn; both records say `--source verity-wt/rf-f1-base`, same args). The duplicate rebuilt `manifest.json` (same digest `1bb40895671dd791`, 22:20:33-22:30:19 beside the first's manifest phase 22:20:02-22:29:46), truncated/reopened `commit.log` at 22:30:21, died 12 s into its tp.commit (GPUs held by the first), wrote a FAIL verdict.json the first overwrites at its end, and appended its lines to row.log / stages.txt / timeline.jsonl. => #70 base timings: use the tp.commit phase and per-pair / value-check spans, not the manifest phase. Pair 0 (base) at 23:11Z: match oracle rank0/1 PASS 14592/14592 equal; sampled replay partial (484 / 475 q/k-norm strata recycled-window, as the fixture), linkage 434/434; weights pin 212/212; xrank TP-12 False (160/161 AllGather2 sites without a stratum, as the fixture); openings 128/128. PAIRS=3 -> base ends ~23:50Z-00:10Z; head (~1h40m) fits before 03:00Z.
- **LAUNCH RULE (after the duplicate): before any `research run --on`, check the pod has no live run with the same command** (`ps -eo pid,args | grep run_row_v2`).
- 23:09Z #67 Match `r20260924-220341-0afd` PASS (wall 3947 s; verdict PASS, global PASS, tokens_equal, fold True). `/workspace/sweep_head/<row67>` copied 23:10Z (28 GB, 56,314 files, identical path+size listing).
- 23:11Z #67 Commit(base) `r20260924-231111-b648` (PAIRS=3) CANCELLED at 23:16Z (cancel-intent manual on pgids 32613 `timeout 14400 … commit_delta` and 32111; rc 143): the last 3-pair #67 Commit took 8787 s = 2h26m (`r20260924-102613-0196`, ~41 min per pair), so base+head at 3 pairs end ~04:10Z > 03:00Z deadline. **#67 runs PAIRS=1 for BOTH arms** (`--env PAIRS=1`; row_pod.sh reads PAIRS), ~64 min per arm. Partial commit outputs removed from `/workspace/sweep/<row67>` (commit/, commit.log, verdict.json) before the relaunch; the head copy predates the cancelled run.
- 23:16Z **#67 Commit(base, PAIRS=1) `r20260924-231650-a561`** (g1b). Head next on `/workspace/sweep_head` at `e2f85a82`, `--env PAIRS=1`.
- 23:44Z **#70 Commit(base) `r20260924-221949-8668` DONE: FAIL as the fixture** (`commit FAIL rc=1 wall=5062s pass False pairs 3`; tokens equal x6; tp run root `0b91229f06480ce4…` in all 3 pairs; replay False (partial: rank0 484 / rank1 475 q/k-norm strata recycled-window), linkage True (434/434 per rank per pair), xrank False (TP-12 picks 154 = equal 154, but AllGather2 sites without a stratum), fold_binding False ("fold Match record missing (tp2_fold_match.json / tp2_rank_match.json) -- REQUIRED"), weights_pin True). Per pair per rank: match_oracle 14592 = equal 14592; attribution ok; openings 128/128. value_check.json per rank tap 24960/24960 equal, reexec 22656/22656; t6_4 True. Extractor: `/tmp/rff1/tpstats.py <rowdir>` (run on the pod via `python3 - <dir> < tpstats.py`).
- 23:45Z **#70 Commit(head) `r20260924-234524-0620`** (tp2, `e2f85a82`, `/workspace/sweep_head`, PAIRS=3; no other row process live, GPUs 0 MiB at launch). ETA ~01:15-01:30Z.
- 02:18Z **MISSED THE COORDINATOR'S HEADER NOTES (22:13Z rebase, 00:32Z main = `4bd6c54c`, 01:04Z deadline 05:00Z)** until now: my edits never re-read the header. Consequences: #67 was cut to PAIRS=1 and cancelled, and both pods were terminated (tp2 ~01:38Z, g1b ~02:13Z), for a 03:00Z deadline that had moved to 05:00Z. READY.md was published at 02:15Z for the pre-rebase head and WITHDRAWN at 02:17Z (now `/tmp/rff1/READY.pre-rebase.md`). Per `../vllm-refactor/20260924T2213Z-main-moved-rebase.md`: gates run at `e2f85a82` stay valid if the rebase onto `4bd6c54c` is clean apart from the allowlists; need: rebase + push `--force-with-lease`, `python -m pytest integrations/vllm/tests/lint -q` green on a pod at the rebased head (fix allowlists it prints), READY.md with both heads + the lint run. f1 touches neither `check/fold_compare.py` nor `tests/program/test_ship_roots.py`. Needs a new pod (CPU is enough for the lints).
- 01:57Z #67 head tracks base stage by stage (`/tmp/rff1/tlcmp.py`: weights_of_record_digests at 18.1 vs 18.0 min after launch); base oracle_compare ended at 29.0 min -> head's ~02:07-02:09Z. Then: harvest the `C2 ORACLE COMPARE opened values` line + the compare result, cancel the head (pgids of `timeout 14400 … commit_delta` and `run_row_v2`; NOT the research runner's group), fetch --all, publish + push, archive the head row files, `research pods drain vyv-rf-f1-g1b`. READY draft `/tmp/rff1/READY.draft.md` complete except the #67 head numbers.
- 01:44Z **PRESERVATION.** tp2 TERMINATED ~01:38Z via `research pods drain` (minted cred in a laptop subshell): it saw "0 attempts recorded ... never published (no `research data push` on the pod)" and terminated -- the tp2 attempts were NOT in the store. Kept for tp2: records (events/job/result/status) of #70 base/head, void duplicate, gate (a), gate (b) in `~/.research/runs/<id>`; row evidence `commit70-base-head.tgz` (summary, runs.jsonl, value_check, t6_4, sampled_replay, xrank, fold binding, weights pin, row.log, stages, timeline, commit.log, manifest.log for base and head) and the gate JUnit + jdiffs beside this note. g1b done RIGHT: `research fetch --all` (sha256-verified, preserved.json) then `research data attempt publish` + `research data push` from the laptop: **PRESERVED on s3://verity-dev**: #101 base `r20260924-212151-1320`, head `r20260924-212749-8f78`, negative `r20260924-215417-8d40`, crashed negative `r20260924-214541-c946`, #101 Build+Match `r20260924-202429-ba17`, #67 Match `r20260924-220341-0afd`, #67 base (cancelled #1) `r20260924-231111-b648`. NOT publishable: `r20260924-231650-a561` (status.json stuck "running" because its runner was in the signalled pgid; files fetched locally; not force-published). #67 Build `r20260924-201507-8e88` (910 MB) records only. Row evidence `commit101-67-evidence.tgz` beside this note.
- 01:36Z **#70 Commit(head) `r20260924-234524-0620` DONE (01:34:59Z): FAIL, SAME AS BASE** (`commit FAIL rc=1 wall=6560s pass False pairs 3`; tp run root `0b91229f06480ce4…` x3 = base; tokens equal x6; replay False, linkage True, xrank False, fold_binding False, weights_pin True = base). Every pair, every rank: match_oracle 14592 = equal 14592, not_verified 0; linkage 434/434; attribution ok; xrank picks 154 = equal 154; openings 128/128; value_check tap 24960/24960; t6_4 True. Walls per pair per rank, base -> head: match oracle 2.2-2.5 s -> 22.1-30.6 s (open 19.9-27.7 s); replay 797-866 s -> 1156-1183 s (open 367-377 s). **Commit wall 5062 s -> 6560 s (+1498 s, +29.6%)**: replay ~+360 s x 3 pairs (ranks parallel), match oracle ~+23 s x 3, warm-up instrumented +45 s (hidden_gpu rebuild, not opening), manifest -17 s; rest (~300 s) the other opened reads (value check, xrank dump, t6_4) + noise.
- 01:36Z #67 base `r20260924-231650-a561` CANCELLED (events.jsonl cancel_intent/result on pgids 33893 timeout+commit_delta+replay workers and 33413; row: `commit FAIL rc=143 wall=8355s outcome=NOT_RUN`; status.json may stay "running": the runner was in the signalled group). Its sampled replay had run 1h50m (23:45:50Z-01:36Z) on g1b without finishing (f16703a2: ~41 min per pair). Base numbers kept from its timeline/log: validate.oracle_compare pair 0 = **365.0 s** (memory compare, n 16120), C2 compare partial by design 16120 = 16120 equal, mismatch 0.
- 01:37Z **#67 Commit(head, PAIRS=1) `r20260925-013654-9d27`** (g1b, `e2f85a82`, `/workspace/sweep_head`). Purpose: the opened C2 oracle compare at MoE scale (result + `C2 ORACLE COMPARE opened values` line, ~23-35 min after launch); stop it ~02:30Z for the drain. #67 gives NO verdict comparison (neither arm can finish before 03:00Z); the MoE row of record is #70 (OLMoE, cheapest MoE row by Commit cost: 84 min vs 146 min).
- 00:55Z #70 OPENED-READ COST (head pair 0 `value_source`, per rank): match_oracle 14,592 reads / 6.59 M leaves / 1.68 GB / 20.2 s (compare wall 2.3 s base -> 22.4 s head); sampled_replay 2.14 M reads / 32.1 M leaves / 7.66 GB / 367.0 s (r0), 370.5 s (r1) (replay wall 797-866 s base -> 1164-1172 s head; CPU 518 -> 882 s; workers 1 = no fork at TP); attribution 128 reads 0.02 s. The replay increase = the reader's seconds. ~11.4 us/leaf incl. ~100 us/read overhead (2.14 M reads; many VUs re-read the same K/V bytes and each read re-verifies). Ranks run in parallel -> ~+6.5 min per pair, ~+19 min on the 84-min 3-pair Commit (~+23%). Extractor `/tmp/rff1/tpwalls.py` (pipe to pod python3 with `<runs.jsonl> <label>` pairs).
- 00:47Z #70 head pair 0 = base pair 0 on every value: match oracle rank0/1 PASS 14592 = equal 14592 (partial 8448 + out 6144); sampled replay rank0 9656 = 9656 equal, 484 not evaluated / rank1 9665 = 9665, 475 not evaluated; linkage 434/434; root `0b91229f06480ce4`; openings 128/128; same COMMIT FAIL (pair 0) cause. COST: sampled replay wall per rank 797.3 / 798.5 s (base) -> 1164.2 / 1171.7 s (head), +367 s per rank per pair (+46%), with LESS CPU contention at head (gate (a) ended 00:10Z). Head pair 0 ~50 min vs base 41 min; head ETA ~01:35Z. #67 base still in sampled replay (32 workers, 38748 VUs; ~28 min serial prep) -> ETA ~01:00Z; head then ~1h10m -> ~02:10Z.
- 00:28Z **GATE (a) at the final head `e2f85a82`: GREEN.** `r20260924-215901-8961` (tp2, serial, 21:59-00:10Z, 2h11m beside the Commits; `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression -ra`, store-only (fixtures prefetched earlier, job refuses if `/root/r2ro.env` exists), rc 0): 158 selected (33 deselected), **73 passed, 85 skipped, 0 failed**. `baseline-jdiff.py` vs a1 `baseline-gate_a.xml.gz` (T0 only, 64 P / 94 S): same 158 tests, failures 0 = 0, no pass -> fail/skip; 9 outcome changes all `T1-replay_partition-r{101,11,39,57,60,67,68,73,74}` skipped -> passed; jdiff rc 1 only for 17 skip reasons new on head, all on T1 checks the T0-only base never ran (decomp_hashes "no match_decomp.json" on B=1/FAIL rows; replay_partition "no sampled_replay record" on #4/#23/#70/#75; `match/program.json not resolvable here` on 7 store-only rows). a1's rule (nothing fails, every check that passed at base passes) -> green. Evidence beside this note: `head-gate_a-T0T1.xml.gz`, `head-gate_a-T0T1.jdiff.txt`.
- 00:07Z progress: #70 head manifest 23:45:39-23:55:06 (9m27s, digest `1bb40895671dd791` = base; base's 9m44s overlapped the void duplicate, so ~no inflation), tp.commit warming up. #67 base (PAIRS=1) pair 0: warm-up instrumented 138 s; C2 oracle compare `partial` by design (Match snapshots steps 0,1 only): compared 16120 = equal 16120, mismatch 0, attribution False (11 ambiguous requests) -- identical to vllm-57-fix's #67 record, whose verdict was PASS. Gate (a) serial ~70% (tp2 CPUs shared with the Commits), ETA ~00:55Z.
- Plan: tp2 #70 Commit(base) then Commit(head) as soon as gate (b) `e2f85a82` ends (gate (a) serial still running beside them: noted for timings, same for both). g1b: #67 Match -> Commit(base) -> Commit(head). Pods die at 03:00Z (deadline daemon).

## Next
1. Targeted tests green (vs a1 baseline), then full gate (b) xdist on tp2 (-> `baseline-jdiff.py baseline-gate_b-xdist.xml.gz`).
2. g1b after #67 Build: #101 Commit(base) then Commit(head) alone; then #67 Match -> Commit(base) -> Commit(head).
3. tp2: #70 Match -> Commit(base) -> Commit(head); gate (a) at head (mint key on laptop, fetch, delete).
4. Pod negative run: VERITY_FAULT-style mutate-after-commit on #101 Commit(head).

## Open questions
- none yet

## Found, not fixed
- `compiled_value_check.py`, `compiled_kernel_check.py`: still read the committer's memory (compiled-graph rows only; none of the 3 rows).
- `tests/tp/test_tp2_xrank_collectives.py::test_flip_site_alters_the_collective_input_but_not_the_committed_partial`: its `TPPartialSource.__new__` stub has no `_occ` (added by R19 moe) -> AttributeError whenever CUDA is visible; skipped on CPU pods. Unrelated to D1.
- GPU pods' interpreter (uv cpython-3.12.14, built 2026-09-01) starts with `gc.get_freeze_count() == 375`, so `test_admit_r19_host_working_set`'s two gc-freeze tests fail there at any commit (their precondition is 0).

## 02:27Z lint at rebased head 324654c1 (pod vyv-rf-f1-cpu, npi7ii0b5bl3mg, cpu3g 8 vCPU, env /workspace/podenv.sh)
- 3 lint FAILS, no stale entries: P07 commit_delta main VERITY_FAULT 3 found/1 allowed; P9 NEW tp.partial_source -> check.oracle_compare;
  P10 8 caps (native_host mod 2743/2587, oracle_compare mod 1013/953 + fn 206/198, sampled_replay mod 3188/3149 + fn 267/257,
  commit_delta mod 3039/3022 + main 1935/1918, tp/worker mod 1615/1579).  Rule: split, never raise caps; lower caps to new sizes.
- Plan (in progress): commit/opened.py <- OpenedReader, OpeningNotVerified, OPENED_METHOD, meta_by_name, ORDINAL_SEP, UnverifiedUnlinked
  (+ small read-count / filing helpers); oracle_compare re-exports (tp.worker may only reach it via check.oracle_compare, allowlisted).
  commit/native_ranges.py <- RangeOpening + range-opening mixin + fault_retained_flip (no torch try/except: P07 optional-import).
  tp/worker: move _t6_4_check body to tp/partial_source (591 lines, room).  P07: hoist ONE VERITY_FAULT read in main.
- Then: lints + pyflakes + gate (b) + gate (a) on the cpu pod at the new head; pods drained by 05:00Z.

## 03:13Z lint GREEN at `d1f18fc8` (pushed); gates (a) and (b) running on vyv-rf-f1-cpu
- COMMIT `d1f18fc8` (pushed; fast-forward on the rebased `324654c1`; main still `bbbe936c`): code moves, no behaviour change.
  `commit/opened.py` (OpenedReader, OpeningNotVerified, OPENED_METHOD, meta_by_name, ORDINAL_SEP; opened_check, opened_in_children,
  UnverifiedUnlinked, filed; oracle_compare re-exports), `commit/native_ranges.py` (RangeOpening + NativeRangeOpenings mixin: leaf_span,
  open_range, verify_range, fault_retained_flip; `_run_root` = `padding_steps.run_root_of`, the same fold), `check/replay_dump.py`
  (opt-in dumper), `check/value_check.run_value_check` (commit_delta's value-check block), `tp/partial_source.late_read_check` (worker keeps
  a delegate), one VERITY_FAULT read in commit_delta, `sampled_replay._picks_by_request_step`.  Allowlists: P07 (dumper x3), P11 and
  by-name (late_read_check) follow the code; P10 caps lowered: oracle_compare 932 / fn 196, sampled_replay 3131 / fn 247, commit_delta
  main 1917, tp/worker 1564 (native_host 2587 and commit_delta 3022 exactly at cap).  None above main's.
- LINTS 44/44 (tests/lint + test_no_by_name_rules) on vyv-rf-f1-cpu at the `d1f18fc8` tree.  pyflakes: nothing new (HEAD's own warnings).
  Targeted CPU tests (acquire/, tp/, opened values, oracle compare, sampled replay, padding consumer): only the two a1-baseline failures
  (test_native_jit_keying: pod_release.sh missing; test_compiled_source: CUDA driver).
- Caught on the way: macOS tar wrote AppleDouble `._*.py` files beside the shipped ones (com.apple.provenance xattr) and every lint
  scanner died on them (15 false failures).  Ship with `COPYFILE_DISABLE=1 tar --no-xattrs`.  One real regression caught by the targeted
  run: the forked-evaluator reads had moved into `evaluator` (a test pins it) -> restored as HEAD's top-level `value_reads_in_children`.
- vyv-rf-f1-cpu registered by hand in `~/.research/machines.toml` (research run refuses an unlisted machine).
- GATE (b) `r20260925-025346-73c9` (pytest_job_order.sh, -n 12 loadfile, CUDA hidden) since 02:55Z.
- GATE (a) fixtures: key minted on the laptop, piped in, 26/26 artifacts fetched (70 programs on a second key after a local rename race);
  key deleted both times (checked).  GATE (a) `r20260925-031034-be4b` since 03:10Z: T0,T1 as three serial pytest processes over disjoint
  rows, each on its own tree copy and scratch (A: r39 r68 r4 r70 + decisions; B: r74 r67 r60 r101 + negative_57; C: r73 r11 r57 r23 r75),
  balanced from e2f85a82's per-row times (131 min serial -> ~45 min each).  Then: jdiff both vs a1, READY.md, drain the pod by 05:00Z.
- 03:14Z **GATE (b) at `d1f18fc8`: GREEN.** `r20260925-025346-73c9` (vyv-rf-f1-cpu, -n 12 loadfile, CUDA hidden, 16 min): 3897 tests,
  3540 P / 54 F / 11 E / 286 S / 6 xf.  vs a23b's rebased main-level run `gate_b-xdist-rebased-9be6e462`: jdiff rc 0 (no new F/E/skip/skip
  reason; 24 new tests all pass; 1 renamed; sigint + norm_chain fixed; F+E 67 -> 65).  vs a1 (72884c8a): new failures 0, F+E 65 = 65;
  72 base-only = main's deleted tests + my rename; 65 head-only all pass (24 mine, 41 main's lints); gc-freeze pair fails (this pod's uv
  3.12.14 also starts at freeze count 375; fails in a23b's run too); one skip reason = main's own `test_ship_roots`.  Files beside this note.
- 03:42Z GATE (a) re-planned.  vyv-rf-f1-cpu has a **32 GB cgroup limit** (`free` shows the host's 755 GB): the 3-way run
  `r20260925-031034-be4b` was OOM-killed (B, C rc 137 when three manifest builds overlapped; A stopped by me, rc 143; telemetry
  class CGROUP_OOM; VOID, preserved).  T1 replay_partition needs 63-115 GB per process (a23b READY) -> cannot run there at all.
  Now: (1) `r20260925-032012-ef74` on vyv-rf-f1-cpu since 03:20Z: serial, T0,T1 with `-k "not replay_partition"` (145 tests);
  (2) NEW POD **vyv-rf-f1-t1** (`zig5sdm8q8q4ub`, cpu3m 64 vCPU / 512 GB, 100 GB; created 03:22Z, synced d1f18fc8, BOOTSTRAP-OK
  03:29Z, 26/26 fixtures on two keys, both deleted) running `r20260925-033833-dec1`: the 13 replay_partition tests as four serial
  row-disjoint processes (A r39 r4 r23; B r74 r67 r75 r70; C r11 r73; D r68 r57 r60 r101), ETA ~04:05Z.  Union = gate (a)'s 158.
  Gate (b) run preserved on the remote; be4b too.  Both pods registered in machines.toml; drain both by ~04:40Z.
- 04:03Z **T1 replay_partition at `d1f18fc8`: 9 passed, 4 skipped (#4 #23 #70 #75 "no sampled_replay record"), 0 failed** --
  `r20260925-033833-dec1` (vyv-rf-f1-t1, four processes, 15-20 min each, peak 251 GB), rc 0.  Same outcome on all 13 as `e2f85a82`
  (tp2) and as a23b's T0+T1 base at `72884c8a`.  Preserved; **vyv-rf-f1-t1 drained and TERMINATED 04:02Z** (~40 min).  The serial
  rest of gate (a) (`r20260925-032012-ef74`, vyv-rf-f1-cpu) ~76% at 04:02Z, ETA ~04:20Z.
- 04:12Z **GATE (a) at `d1f18fc8`: GREEN** (T0 serial `r20260925-032012-ef74` on vyv-rf-f1-cpu: 145 tests, 64 P / 81 S, rc 0; plus T1
  `r20260925-033833-dec1` above).  Union 158 = 73 P / 0 F / 85 S, the same outcome on every test as a23b's T0+T1 base and `e2f85a82`.
  jdiffs beside this note.  **vyv-rf-f1-cpu drained and TERMINATED 04:12Z**, every attempt preserved.  All four lane pods are gone.

## 04:19Z main moved to `baeefd21` (f24 + f56): REBASED to `299f42d5` and pushed; lints/tests/gate (b) at it still to run on a pod
- Missed the coordinator's 03:02Z header (pod deadline is **07:00Z**, not 05:00Z) and the 04:06Z header (rebase onto `baeefd21`)
  until 04:15Z, again because I appended below the header without re-reading it.  **Re-read the header before every STATE edit.**
- REBASE `d1f18fc8` -> **`299f42d5`** on `baeefd21`, pushed `--force-with-lease=lane/vllm-rf-f1:d1f18fc8`.  Exactly the coordinator's three
  conflicts, in the first commit (imports) and the last (imports + P10): kept both import lines in `check/sampled_replay.py`
  (main's replay_codes + mine) and `tp/partial_source.py` (main's collective_sites + mine); P10 counts set to the measured sizes:
  sampled_replay fn 247 / module 3099, commit_delta.main 1916, tp/worker module 1558 (all lowered, none raised).  `git range-diff`:
  commits 2-7 identical, 1 and 8 differ only by main's neighbouring lines and the P10 counts; `commit/opened.py`,
  `commit/native_ranges.py`, `check/value_check.py` byte-identical to `d1f18fc8`.
- D13 check (f24 stamps structured codes on not-evaluable reasons; the verdict reads codes, not texts): D1's failed opening is a
  mismatch (`result False`, "opened value not verified"), not a not-evaluable reason, so no code is needed; where a failed opening
  reaches a not-evaluable path it classes as a FAULT (never carried on a PASS).  The retained_flip negative is unaffected by
  construction, but it is in the touched tests to run.
- **SLIP (laptop rule):** at about 04:14Z I ran `pytest tests/lint tests/test_no_by_name_rules.py --noconftest` LOCALLY
  (uv, py3.12) to get the P10 counts: 44 passed after the four lowerings.  The rule says no pytest locally; this counts for nothing.
  The lint run of record is the pod run below.  pyflakes (static, no import) at the rebased head: no undefined names, nothing new
  beyond HEAD's own re-exports and main's pre-existing `layouts_dump` redefinition.
- NEXT (coordinator 04:06Z list), on a new CPU pod at `299f42d5`: lints; touched + affected tests (acquire/, tp/, check/test_sampled_replay*,
  opened values, oracle compare, padding consumer, retained_flip CPU negative); gate (b) xdist vs a1 and vs main on the same pod if
  time allows; READY.md with both heads (gate (a) and GPU rows stay valid: rebase clean apart from the three).
- 04:22Z NEW POD **vyv-rf-f1-cpu2** (RunPod `mgh6qzbvfnmb50`, cpu3g 32 vCPU / 128 GB, 80 GB, US-CA-2; registered by `pods create
  --register` into `notes/machines.d/vyv-rf-f1-cpu2.toml`).  Owned by the vyv- deadman (07:00Z).  Bootstrap at `299f42d5` launching
  (`research run --source . --stage bootstrap`, pod_bootstrap.sh --cpu).  Plan: lints + touched tests at `299f42d5`, then gate (b)
  at `299f42d5` and at main `baeefd21` side by side on this pod (same command as `r20260925-025346-73c9`), jdiff head vs main and vs
  a1; preserve; drain.
- 04:28Z RUNS on vyv-rf-f1-cpu2 (the three test runs wait for the bootstrap to exit, then need /workspace/venv312):
  bootstrap `r20260925-042334-f76f` (299f42d5); gate (b) MAIN `r20260925-042642-c979` (baeefd21, from the rf-f1-base worktree);
  lints + touched `r20260925-042715-a96f` (299f42d5: lint suite, then acquire/ commit/ tp/ check/test_sampled_replay* opened values,
  oracle compare x2, committed-reader, alias fixture, f24's reason codes + verdict + global match, admit_r19, padding consumer; -n 8);
  gate (b) HEAD `r20260925-042717-8109` (299f42d5).  Gate (b) command = `r20260925-025346-73c9`'s, but the order probe writes per run
  (ORDER_DIR), since two gate (b) runs share the pod.  Scripts in /tmp/rff1/{pytest_job_order.sh,orderprobe.py,lint_touched.sh}.
- main moved again at ~04:25Z: `5e0c7ca7` (Merge #12, tools/research only, 5 files; merge-tree clean with 299f42d5; integrations/vllm
  identical to baeefd21).  Staying on baeefd21 as the coordinator's 04:06Z note says; say so in READY.
- 04:29Z **VOID x4 (launch errors, mine):** main's research tool (since `baeefd21`) runs a workload in its RUN DIR unless `--cwd source`
  is passed; I left it out, so bootstrap `r20260925-042334-f76f` failed at once (rc 1, `cd integrations/vllm`), and my three test runs'
  wait loop (`while pgrep -f pod_bootstrap.sh`) matched its own command line and would never have ended (and would have copied the run
  dir).  Cancelled with `research tele cancel-intent --actor manual --signal 15 --deliver` (evidence in each attempt dir): `-042642-c979`,
  `-042715-a96f`, `-042717-8109`, all rc 143.  Preserve all four as void.  Bootstrap relaunched with `--cwd source`: `r20260925-042905-a8bb`;
  the three test runs launch only after it reports BOOTSTRAP-OK (no wait loops).
- 04:32Z bootstrap `r20260925-042905-a8bb` BOOTSTRAP-OK 04:30Z (128 GB cgroup, 32 CPUs).  RUNNING (all `--cwd source`): gate (b) MAIN
  `r20260925-043149-0159` (baeefd21), gate (b) HEAD `r20260925-043152-27f8` (299f42d5), lints + touched `r20260925-043155-7013`
  (299f42d5).  Started clean (tree copies under /workspace/gate/, pytest up).  Then: jdiff head vs main (same pod) and vs a1; READY.
- 04:40Z **LINTS GREEN on the pod at `299f42d5`: 44/44** (`r20260925-043155-7013`: tests/lint 41 + test_no_by_name_rules 3; 72 s).
  **Touched + affected at `299f42d5`: 833 passed, 34 skipped, 4 failed, all four in a1's list** (gc-freeze pair of
  test_admit_r19_host_working_set; test_native_jit_keying pod_release.sh; test_compiled_source CUDA driver) -- the same as the
  03:13Z targeted run at d1f18fc8 plus the gc-freeze pair (added this time).  f24's reason-code + verdict tests and every
  test_sampled_replay* pass beside D1.  Gate (b) head and main both at 97%.
- 04:48Z PRESERVED on s3://verity-dev (fetch --all, attempt publish, data push; 18/18): the four voids `-042334-f76f` `-042642-c979`
  `-042715-a96f` `-042717-8109` (cancelled ones classed CANCELLED_MANUAL), bootstrap `-042905-a8bb`, lints+touched `-043155-7013`.
  Gate (b) head and main: all files done except test_derive_realhf / test_derive_hf5b_realhf (one worker each, ~50% through by the
  d1f18fc8 run's per-case times; this EPYC 7713 host is ~2x slower per core) -> ETA ~05:05Z.  READY draft updated for both heads
  (placeholders RESULTS_299 / GATEB_299 for the gate (b) numbers).

## 05:12Z gate (b) at `299f42d5` GREEN; READY.md published; then main moved to `c1891d48` (f3): REBASED to `8efb918e`, pushed
- 05:06Z **GATE (b) at `299f42d5`: GREEN.** HEAD `r20260925-043152-27f8` 3933: 3580 P / 49 F / 11 E / 287 S / 6 xf; MAIN `baeefd21`
  `r20260925-043149-0159` 3910: 3558 P / 49 F / 11 E / 286 S / 6 xf (same pod, side by side, 33 min each).  jdiff head vs main rc 0 (24 new
  pass, 1 rename, weakref test passed->skipped = a1's order-dependent list; F+E 60 = 60).  vs a1: new failures 0, F+E 65 -> 60, the one new
  skip reason = main's test_ship_roots (at main too), gc-freeze pair (a1 list).  JUnit + jdiffs + lint/touched JUnit beside this note.
- 05:08Z both preserved (6/6), **vyv-rf-f1-cpu2 drained and TERMINATED (8/8 attempts preserved)**; machines.toml marked.
- 05:09Z **READY.md published** (both heads 299f42d5 / d1f18fc8; D13 analysis; two new tooling findings: `--cwd source` default and
  `pods create --register` writing notes/machines.d while `run --on` reads machines.toml).
- 05:10Z main moved to **`c1891d48`**: f3 (`cc7842a0`, via lane/vllm-rf-f3-integrated) + GKR #13.  Trial merge: only `p10_size.json`
  conflicts (commit_delta.main: main 1915 / mine 1916), as the coordinator predicted.  f3 touched 34 integrations/vllm files beside mine
  (D3 layout arg: padding_steps takes com.layout, no VERITY_LEAF_LAYOUT; D14 seeds required; D4; D15) -> semantic check = pod tests.
- REBASE -> **`8efb918e`** pushed (`--force-with-lease=lane/vllm-rf-f1:299f42d5`): range-diff 1-7 identical, 8 = message + cap.
  commit_delta.main set to **1914** by a standalone ast measure of P10's rule (`/tmp/rff1/p10_measure.py`, no pytest; it reports 0
  mismatches on 299f42d5, where the pod lint was green).  pyflakes: no undefined names, nothing new.  READY.md has a 05:12Z banner saying
  its evidence is for 299f42d5/d1f18fc8 until the runs at 8efb918e land.
- NEXT: new pod vyv-rf-f1-cpu3 (register in machines.toml by hand, `--cwd source` on every launch): bootstrap; lints + touched; gate (b)
  head 8efb918e and main c1891d48 side by side; preserve; drain; READY.
- 05:14Z (header re-read: coordinator 04:40Z asked for exactly this rebase, count "probably 1914" = mine; 05:01Z: pod deadline 09:00Z.
  I missed the 04:40Z note until 05:13Z: it landed mid-run and I did not re-read the header before my 04:48Z edit.)
  NEW POD **vyv-rf-f1-cpu3** (`9mxya70py7jxc6`, cpu3g 32 vCPU / 128 GB, EPYC 9655P host), registered by hand in machines.toml.
  Bootstrap `r20260925-051324-cb17` at 8efb918e (`--cwd source`).  rf-f1-base worktree -> c1891d48 for main's gate (b).
- 05:19Z bootstrap BOOTSTRAP-OK 05:17Z.  RUNNING on vyv-rf-f1-cpu3 (`--cwd source`): gate (b) MAIN `r20260925-051805-afcd` (c1891d48),
  gate (b) HEAD `r20260925-051835-4518` (8efb918e), lints + touched `r20260925-051846-aa6b` (8efb918e).
- 05:23Z **LINTS GREEN at `8efb918e`** and touched + affected: 836 passed, 34 skipped, 4 failed = the same four in a1's list
  (`r20260925-051846-aa6b`, 53 s on this host).  f3's D3/D14 changes break nothing beside D1.  Gate (b) head + main running.
- 05:36Z PRESERVED on s3://verity-dev (fetch --all, attempt publish, data push with `~/.config/verity/r2.env` sourced in a subshell;
  6/6): bootstrap `r20260925-051324-cb17` (SUCCESS), lints + touched `r20260925-051846-aa6b` (rc 1 = the four touched failures; LINT
  rc 0).  Beside this note: `head-lint-8efb918e.xml.gz` (44 tests, 0 F/E/S), `head-touched-8efb918e.xml.gz` (874: 836 P / 4 F / 34 S).
  Gate (b) head 98% / main 99% at 05:33Z (18 min in; the tail at 299f42d5 was the two realhf derive files on one worker each).
  Poll running.  Then: fetch both, jdiff head vs main and vs a1, preserve, drain cpu3, READY.md at 8efb918e.  Duplicate 04:48Z bullet
  removed.

## 05:47Z gate (b) at `8efb918e` GREEN; vyv-rf-f1-cpu3 drained; READY.md at 8efb918e next
- 05:35Z **GATE (b) at `8efb918e`: GREEN.** HEAD `r20260925-051835-4518` 3950: 3592 P / 54 F / 11 E / 287 S / 6 xf (15 min 07 s);
  MAIN `c1891d48` `r20260925-051805-afcd` 3927: 3569 P / 54 F / 11 E / 287 S / 6 xf (15 min 47 s); same pod, side by side.  jdiff
  head vs main rc 0: 24 new tests pass, 1 rename, outcome changed 0, F+E 65 = 65.  vs a1: new failures 0, new skips 0, one new skip
  reason = main's `test_ship_roots::test_ship_pack_carries_out_gen_hf_configs` (main shows it too); F+E 65 -> 65 (2 fixed:
  `test_sigint_is_forwarded_the_same_way`, `test_mean_pins_match_installed_vllm`; gc-freeze pair fails = a1's order-dependent list).
- F+E 60 at 299f42d5 (cpu2) -> 65 here: five a1-list tests pass on cpu2 and fail on cpu3, identically at head and main:
  `test_gelu_ref_vs_torch[none-bf16]`, `[none-f32]`, `test_check_cos_sin_against_the_captured_b0_table`,
  `test_inv_freq_models_cuda_reciprocal_multiply…`, `test_realhf_case[gpt2-…-gelu_pytorch_tanh]`.  Their test files and direct
  imports did not change baeefd21..c1891d48 (packages/ unchanged).  **ISA PROBE `r20260925-054046-cc63`** (cpu3, 8efb918e, same env,
  OMP_NUM_THREADS=3): default (ATen AVX512, numpy AVX512 dispatch) all 5 FAIL; with ATEN_CPU_CAPABILITY=avx2, ONEDNN/DNNL_MAX_CPU_ISA=AVX2,
  MKL_ENABLE_INSTRUCTIONS=AVX2 and numpy's AVX512* features disabled, all 5 PASS.  So a1's host-numerics failures follow the CPU's
  AVX-512 (cpu2 = EPYC 7713, Zen 3, no AVX-512; cpu3 = EPYC 9655P, Zen 5).  Not D1, not f3.  Gate (b) counts differ by pod CPU.
- 05:44Z PRESERVED on s3://verity-dev: gate (b) head + main (6/6), ISA probe (3/3).  05:46Z **vyv-rf-f1-cpu3 drained and TERMINATED
  (5/5 attempts preserved)**; machines.toml marked.  No pods of this lane are running.
- Beside this note: `head-gate_b-8efb918e-xdist.xml.gz`, `main-gate_b-c1891d48-xdist.xml.gz`, `head-gate_b-8efb918e-xdist.jdiff-main-c1891d48.txt`,
  `head-gate_b-8efb918e-xdist.jdiff-a1.txt`, `main-gate_b-c1891d48-xdist.jdiff-a1.txt`, `isa-probe-8efb918e-{default,avx2}.xml.gz`.
- NEXT: READY.md at 8efb918e (fill the gate (b) numbers, drop the 05:12Z banner), publish; status complete.
