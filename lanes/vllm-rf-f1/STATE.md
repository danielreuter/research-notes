---
id: vllm-rf-f1/state
lane: vllm-rf-f1
kind: state
status: active
created: 2026-09-24T17:32Z
updated: 2026-09-24T18:56Z
---
# vllm-rf-f1: opened-value replay (D1) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 D1, §4 P2; `20260924T1625Z-coordinator-checks-on-check-commit-survey.md`; `survey-check-commit.md` §3.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f1`, branch `lane/vllm-rf-f1` from `72884c8a`.
- **Scope:** the verdict-bearing Commit value check (`oracle_compare` via `committed_reader`) consumes opened, root-verified values only; same for the per-rank TP path; mutate-after-commit negative test (CPU double or pod-marked) plus one real pod run; re-run cheapest dense, MoE, TP2 regression Commit rows via research Tools; commit time before/after.
- **Gate (b) rule (coordinator, after restart):** no failure, error or skip reason outside a1's list in `~/.research/notes/lanes/vllm-rf-a1/baseline.md` (65 failures/errors, 50 skip reasons at `72884c8a`). Pod recipe is in that note.

## Done
- 17:32Z worktree created.
- 18:46Z resumed after the 18:02Z Cursor restart: worktree clean at `72884c8a`, no commits; nothing from the first run survived beyond the worktree.
- 18:56Z mapped compared vs opened positions (below). No code changed yet.

## Compared vs opened positions (at `72884c8a`, paths under `integrations/vllm/verity_vllm/`)

**Opened (root-verified) positions** -- a random sample, not tied to what is compared:
- `harness/commit_delta.py:~2003-2033`: `challenge_positions(rc.run_root, leaves_per_step, args.openings, salt=pair)` -> `com.open(sample)` -> `com.verify(rc, o)`; `row.commit.openings` (a failed opening fails Commit).
- `harness/commit_delta.py:719-742` (`binding_record`): `B.challenge_identities(pop, bmap, rc.run_root, args.openings, salt=b"population/<pair>")` -> open + verify; `openings_population`.
- `openings_after_release` (`commit_delta.py:769+`): deferred positions (retain=none / retain=host+exclude) opened by replay against the run root.

**Compared positions** -- every one reads the collector's retained memory, never an opening:
- `oracle_compare` (`commit_delta.py:2339`, reader `OC.committed_reader(com)`): every binding-map entry except `weights`/`hidden_stream` families and padding entries; bytes `[(eo+lo)*isz, (eo+hi)*isz)` of member `entry_read_name(e)` at `step`, vs the Match oracle.
- `sampled_replay` (`commit_delta.py:2542`, `_rd = OC.committed_reader(com)` at `:2442`): `CommittedStore.words` (`check/sampled_replay.py:656-685`) reads each sampled VU's input and output slices.
- `boundary_linkage` (`commit_delta.py:2515`, same `_rd`): input ids / sampled ids per (step, request).
- `padded_population` (`commit_delta.py:2564`, same `_rd`): padding entries read back == bot.
- TP per rank: `tp/worker.py:1192` `rd = OC.committed_reader(com)` -> `SR.sampled_replay` + `SR.boundary_linkage` on the rank.
- TP, second reader `tp/partial_source.py:58` `_committed(com, step, meta)` (whole meta: `m.host` else `_gpu_blocks[step][0][stream_off:+nbytes]`): used by `partial_source.compare()` (TP-04 C2 vs hook-time taps, `:402`), `compare_match_oracle()` (TP C2 form B vs tp2_match recorder, `:513`), `worker._tp2_attribution` (`:969`, sampled ids vs Match tokens), `worker.tp2_commit_xrank_dump` (`:1268`, cross-rank collective picks), `worker._t6_4_check` (`:1507`, late-read detector).
- Not in scope (other value-ish readers): `check/value_check.py:105` `_committed` (E7 re-execution, `--value-check`), `compiled_value_check.py`.

**`committed_reader` (`check/oracle_compare.py:914-953`)**: finds the meta by name (or `name#ord<k>` for shared modules; a bare name with >1 meta -> None), then slices `com._gpu_blocks[step][0]` at `m.dev_off+lo..hi` (None if a sparse retainer does not hold it), else `m.host[lo:hi]` (padding metas: `dev_off -1`, host view).

**Leaf layout (`acquire/native_host.py`)**, needed to map a byte range to leaves:
- Packed steps (GPU block `_gpu_blocks`, host stream `_streams`, padding): leaf `i` = stream bytes `[i*chunk, min((i+1)*chunk, n))`; member `m` at `[m.stream_off, m.stream_off+m.nbytes)` (GPU: `stream_off == dev_off` after `_commit_step_gpu`, chunk `GPU_CHUNK_BYTES=256`; padding leaves `index >= ps.leaf_base`).
- Per-tensor host steps: leaves `m.first_leaf .. +m.n_leaves`, leaf `k` = `m.host[k*m.chunk : min((k+1)*m.chunk, m.nbytes)]`.
- `com.identity_of(step, i)` gives `byte_lo/byte_hi` (stream coords if packed, tensor coords otherwise). `com.open(list)` slices the retained copy (or a replay source); `com.verify(rc, o)` re-derives the leaf digest (GPU chunk header / padding rule / `pos_leaf`), folds the path, checks `bind_root(...) == step root` and the run root. `verify` is O(#metas + #steps) per leaf (layout digest + run-root fold each call) -- cost matters.

## Plan
- `check/oracle_compare.py`: replace `committed_reader(com)` with an opened reader (same `(step, name, lo, hi) -> bytes | None` signature, same meta selection) that maps the range to covering leaves, opens them with `com.open`, verifies each with `com.verify(rc, o)` against the run root (rank root on TP), caches verified leaf bytes (immutable), and assembles the slice from opened bytes only. A leaf that fails to verify must make the check FAIL by name (not "not retained" -> partial). Delete `committed_reader`.
- Wire it at `commit_delta.py:2339/2442` and `tp/worker.py:1192`; route `partial_source._committed` through opened leaves too.
- Negative test: CPU double committer (host path) that mutates retained bytes after finalize; expect oracle_compare and sampled replay to FAIL. Plus one pod run with a mutate-after-commit fault.
- Measure commit (validate) time before/after on the cheapest dense, MoE, TP2 regression Commit rows.

## Running
- nothing (no pods)

## Next
1. Check `verify` cost and whether a per-step batch is needed; read how `commit_verdict` grades `oracle_compare`/`sampled_replay` results (None vs False).
2. Read `tools/research/README.md`, `integrations/vllm/ops/`, `tests/regression/fixtures.toml` for the regression rows.
3. Implement, CPU tests, then pod.

## Open questions
- none yet

## Found, not fixed
- none yet
