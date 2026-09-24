---
id: vllm-rf-f1/state
lane: vllm-rf-f1
kind: state
status: active
created: 2026-09-24T17:32Z
updated: 2026-09-24T19:17Z
---
# vllm-rf-f1: opened-value replay (D1) (state)

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
- Not in scope: `check/value_check.py:105` `_committed` (E7, `--value-check`), `compiled_value_check.py`.

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
- nothing (no pods)

## Next
1. Implement committer_api + native_host range methods; OpenedReader; wire call sites; update tests that use `committed_reader`.
2. Read `tools/research/README.md`, `integrations/vllm/ops/`, `tests/regression/fixtures.toml` for the regression rows; measure before (base) on pods.
3. CPU tests on a pod, then GPU rows.

## Open questions
- none yet

## Found, not fixed
- none yet
