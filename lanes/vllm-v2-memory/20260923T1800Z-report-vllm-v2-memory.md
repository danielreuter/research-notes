---
lane: vllm-v2-memory
kind: report
created: 2026-09-23T18:00Z
status: open
finding: F-r19-int-25
branch: lane/vllm-v2-memory (pushed; f7de914 on top of main 22e10e0)
pod: vyv-v2cpu2 (755 GB host, 256 GB cgroup, 32 cpu, python 3.12 venv /workspace/venv312)
---

# F-r19-int-25 — v2 `query.cli build` host memory (87 GB #11 / OOM #39) → 3.3 GB / 6.0 GB

Fixed. The v2 engine now runs #11 in **3.3 GB** (was 88.6 GB; v1 72.5 GB) and #39 in **6.0 GB** (was 145.6 GB — OOM at R19's 128 GB cgroup; v1 117.6 GB),
byte-identical `manifest_digest` before/after and against v1, faster wall than either old engine. Ontology and
`verity.verification.query` untouched; only the vLLM integration's *representation* of a Program changed.

## 1. Before/after (pod vyv-v2cpu2, harness B=1 argv, 1 s `/proc` RSS sampler + cgroup `memory.current`)

| row | engine | source sha | peak RSS | wall | manifest_digest | equal |
|---|---|---|---|---|---|---|
| #11 llama32-1b | v1 `required_manifest build` | 22e10e0 | 72.5 GB | 344 s | 26676357…240c | ref |
| #11 | v2 `query.cli build` (before) | 22e10e0 | **88.6 GB** | 461 s | 26676357…240c | = |
| #11 | v2 (after) | 3cbe802 | **3.32 GB** | 233 s | 26676357…240c | = |
| #11 | v2 (after, final) | f7de914 | **3.37 GB** | 278 s † | 26676357…240c | = |
| #39 qwen25-15b | v1 | 22e10e0 | 117.6 GB | 690 s | 844f2c72…90d5 | ref |
| #39 | v2 (before) | 22e10e0 | **145.6 GB** ‡ | 954 s | 844f2c72…90d5 | = |
| #39 | v2 (after) | 3cbe802 | **6.04 GB** | 417 s | 844f2c72…90d5 | = |
| #39 | v2 (after, final) | f7de914 | **6.04 GB** | 472 s † | 844f2c72…90d5 | = |

† the f7de914 runs shared the 32 cpus with the concurrently running old-v2 #39 job (the small ones are allowed to overlap under the
RAM protocol); the wall difference vs 3cbe802 is contention, not code. ‡ old v2 completes on #39 only because this pod's cgroup is
256 GB; R19's 128 GB cgroup killed it at the 117 GB `json.load` plateau + views.
R19's 87 / 67 GB were `/usr/bin/time -v` maxrss on the 128 GB pod; the 1 s sampler here reads 88.6 / 72.5 (same ordering, ~1.2×
ratio confirmed). Identities 109 219 (#11) / 189 239 (#39), `complete: true`, `program_digest` equal per row across all runs.
Traces: `/workspace/mem/runs/<label>/<label>.trace.jsonl` (+ `.meta.json` with sha/argv/peaks, `.log`, `.meta.digest`); mirrored
into the research store, see §6.

## 2. Census (#11, old v2 22e10e0, `census.py`: phase RSS + `gc.get_objects()` type counts, shallow `getsizeof`)

#11's Program: **747 358 Calls, 341 159 100 operand runs** (reads). Practically all of the reads are the attention rows' `kv`-style
operands (hundreds of runs per Call); the descriptor is small, `instances.json.gz` is 922 MB compressed.

| phase | t | RSS | HWM | what is alive |
|---|---|---|---|---|
| `json.load(instances.json.gz)` | 74 s | 63.8 GB | 72.3 GB | 343.5 M `list` (33.1 GB shallow) + one `int` per run (28 B × 341 M ≈ 9.6 GB) + row dicts |
| `from_instances(doc)` (doc still alive) | 397 s | **88.6 GB** | 88.6 GB | doc + 341 M `ValueRef` (19.1 GB shallow + the ints ≈ 28.7 GB) + 755 k `reads` tuples (2.8 GB) + 747 k `CallView` |
| `del doc` | 424 s | 88.6 GB | 88.6 GB | RSS does not fall: pymalloc arenas fragmented by the interleaved live ValueRefs |
| `Correspondence.of` (v1_annotations source) | 483 s | 88.6 GB | 91.3 GB | +2.7 GB transient: `read_program_dir` → `json.load(descriptor.json.gz)` for `annotations[correspondence]` |
| `boundary_values` | 546 s | 88.6 GB | 91.3 GB | +747 k `CallName`, +dicts/frozensets: ~0.3 GB |
| `shared_instances` / `request_manifest` / serialize | 660 s | 88.6 GB | 91.3 GB | ~0.1 GB |

Top structures by bytes, per unit:
1. decoded JSON run lists `[cid, port]` — 341 M × (72 B list + 28 B int) ≈ **34 GB**, ~100 B/read (also v1's cost: v1 `json.load`s the same document, hence its 72 GB).
2. `ValueRef` NamedTuples — 341 M × 56 B + 28 B int ≈ **28.7 GB**, 84 B/read (v2-only: the materialized `CallView.reads`).
3. `CallView.reads` tuples — 755 k, **2.8 GB** (8 B/read pointer array).
4. `annotations`-bearing descriptor as a Python object during `Correspondence.of` — **2.7 GB transient** (the whole descriptor incl. `definitions` decoded to read one key).
5. everything else (CallView 66 MB, CallName 54 MB, Port/Spec/dicts) < 0.3 GB — the *partition* and *boundary* passes were never the problem; they are proportional to Calls (7.5e5), not to reads (3.4e8).

So the "per-use" cost was ~184 B/read held twice over (doc + views), ×341 M = the whole 88 GB. `Q_module_body_v1` and `BoundaryValues`
themselves were fine; they only ever touch the reads through `boundary_values`'s producer scan.

## 3. What changed (branch `lane/vllm-v2-memory`, 2 commits, +779/−75)

**3cbe802 — columnar streaming `ProgramView`** (`integrations/vllm/verity_vllm/query/program_view.py`, `v1_bridge.py`)
- `from_instances` streams `instances.json.gz` row-by-row (`iter_instance_rows`: chunked gzip text → `raw_decode` per row; never
  `json.load`s the document) into flat columns: `array('q')`/`array('i')` `read_off/read_call/read_port` (+ the param-read columns
  `pread_*`), one interned spec/family/form/name per Call via index arrays. #11's 341 M reads cost 8+4 B each in arrays ≈ 4 GB → the
  observed 3.3 GB peak with the descriptor and correspondence alive. Falls back to the old `json.load` path only if rows are out of
  body order (the fallback still produces identical views; tested).
- `ProgramView.calls` is a lazy `Sequence[CallView]` (`_Calls`), `CallView.reads` a lazy `Sequence[ValueRef]` (`_Reads`): a
  `CallView`/`ValueRef` exists only while a caller iterates it. Both behave as tuples (`len`, index, negative index, slice, `==`,
  `hash`, `+`), so every existing consumer (`module_body`, `boundary_values`, `v1_bridge`, `correspondence`, `cli`, `compare`) is
  unchanged in behaviour. Hand-built tuple views (tests, `frontend`) are untouched; `ProgramView.columns` exposes the columns
  when present.
- `from_descriptor` builds the same columns through `_Builder` (no per-Call intermediate lists).
- `v1_bridge`'s three reads loops use `param_reads(call)` / `reads_any_of(call, producers)` which read the arrays directly
  instead of building 341 M `ValueRef`s to compare their `call` field.
- Type annotations widened (`reads: Sequence[ValueRef]`, `calls: Sequence[CallView]`); no public name removed, `__all__` grew
  by `param_reads`, `reads_any_of`, `iter_instance_rows`.

**f7de914 — streamed descriptor annotation** (`integrations/vllm/verity_vllm/runtime_correspondence.py`)
- `read_program_dir` → `read_descriptor_annotation(path, namespace)`: a small streaming JSON walker (`_Stream`/`_walk`) that
  builds only `annotations[namespace]` and skips (`definitions`, `body`, …) without materializing them. Removes the 2.7 GB (#11)
  transient and makes `Correspondence.of` independent of descriptor size. Number-at-chunk-boundary case handled and tested.

Not changed: `verity.verification.query` (Partition / boundary_values / required_values), any serialized id/schema/digest,
`verity_capture` (v1). No numpy dependency added (stdlib `array`).

## 4. Tests (laptop, venv `verity-wt/v2/.venv`, PYTHONPATH = worktree roots)

- `integrations/vllm/tests/query`: 35 → 47 (+ `test_program_view_columns.py`: streamed vs reference reader on multi-port/dedup/
  out-of-order/chunk-boundary bodies, lazy-sequence tuple semantics; `test_descriptor_annotation_stream.py`: streamed annotation ==
  `json.load` across chunk sizes, gz and plain).
- `integrations/vllm` suite (`tests/ir`, `tests/query`, `verity_capture`): 465 passed.
- `packages/verity` suite: green. `tests/test_no_by_name_rules.py` (allowlist 438, no new by-name rules), `tests/test_repository.py`: green.
- Pod: harness `manifest_digest` equality under ENGINE=v2 on #11 and #39 (the two staged rows) vs v1 and vs old v2, see §1.

## 5. What remains / notes

- `from_instances` still spends most of its wall in `raw_decode` per row (~230 s for #11's 922 MB gz); a C-level row decoder or a
  columnar on-disk format for `instances` would cut that further, but it is now faster than v1.
- v1 (`verity_capture.commit.required_manifest`) still `json.load`s the document (72 / 118 GB). Not in scope (v1 is the baseline
  and is being retired); if wanted, it could reuse `iter_instance_rows`.
- `frontend/liveness.py` builds hand tuples — unaffected, small Programs.
- #60/#73/#74 small-row `tracemalloc` scaling plot: skipped — the #11 census alone attributed >95 % of the bytes to two
  structures with exact per-read costs, so the extrapolation was unnecessary.
- Only #11 and #39 programs are staged on the pod; other rows were not re-checked under v2 (the harness `manifest_digest` check
  with ENGINE=v2 should be run on the next full sweep).

## 6. Artifacts, shas, pod time

- Branch `lane/vllm-v2-memory` @ `f7de914` (pushed; base `origin/main` 22e10e0). Commits: 3cbe802 (columnar ProgramView),
  f7de914 (streamed descriptor annotation).
- Research artifact `art:29f35c157d81e4af551d9fdea3c8f0cad8ff39aeca3078f1d53589651069d68e` (kind run-files/v1, PRESERVED
  2026-09-23T18:14Z, 45 objects): `runs/<label>/{*.trace.jsonl,*.meta.json,*.meta.digest,*.log}` for the 9 runs in §1, `census.json`
  (old v2 #11 phases), `SUMMARY.json` (one row per run), and the tooling `rsstrace.py` (sampler), `run_baseline.sh` (harness argv
  under the sampler, ramlock write/remove), `census.py`/`run_census.sh`. Manifests themselves are not in the artifact (digests are).
- Pod source trees: `/workspace/mem/src/{wt=22e10e0, fix=3cbe802, fix2=f7de914}` (git-archive exports, `SHA` file in each);
  programs `/workspace/mem/programs/{r11,r39}/build_request`.
- Pod wall used by this lane: ≈ 1.6 h (16:40Z–18:14Z), of which ~1 h were the four big baseline/census jobs (72–146 GB, one at a
  time under `/workspace/ramlock/int25-*.json`; all locks removed). Lane wall ≈ 3.5 h incl. static reading and the local suites.
