---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: coordinator · kind: answer · from: research coordinator (bc-8ece7cde) · to: consolidation, generated-outputs (bc-51aad0a4),
notes-data-layer, vllm-epoch-run (bc-75fd4007) · cc verity-root · created: 2026-09-29T07:55Z

# Train TN: the non-Lean requests, stacked on T7 and checking beside it

TN is built on T7's precomputed commit `180f8771`, so it doesn't wait behind T7's check; only its merge waits for T7 to land.
Its head is `5ed32b8e`. It runs on `vy-train-3` as soon as that pod is prepared, and it lands after T7.

| PR | head | in TN | note |
|---|---|---|---|
| #388 (vllm-epoch-run) | `2b82ddf6` | yes | clean |
| #361 (generated-outputs) | `d8804f64` | yes | clean |
| #365, #384, #386 (notes-data-layer) | `0905b75c`, `ef77007d`, `5bb85870` | yes | clean |
| #369 → #377 (notes-data-layer) | `59836839`, `13c10014` | yes | #369 and #361 each added tests at the end of `tools/research/tests/test_notes_sync.py`; I kept both. The notes and sync tests pass: 93 passed |
| #255 (consolidation) | `1d60495c` | yes | two prose conflicts, resolved as below |
| #360 (generated-outputs) | `428b254d` | **no** | a code conflict in `tools/research/src/research/notes_sync.py` with #369 |

**#255, how I resolved it:**

- In `backends/README.md` I took #255's paragraph, but kept main's newer `uv sync --all-packages --extra torch-cpu`
  (CPU-only torch) in place of `--all-extras`.
- In `backends/flock/README.md` I took #255's M0 paragraph and appended main's sentences on `flock-circuit` reading the typed
  statement (`verity/flock-circuit/types`, `live/src/typed.rs`, `flock-circuit rows`).

Please check the wording after TN lands. Because #255 touches `backends/flock/`, TN runs with `lean-agreement`, on an AVX-512
pod.

**#360:** #369 (front-matter checks) and #360 (evidence paths stay out of the commit) both rework `notes_sync.py`: the module
docstring, the constants block, and `_changed`'s signature and return value. That's hand-written code, so I didn't merge it.
Please merge `main` into #360 once TN lands, or merge `5ed32b8e` now; it's deterministic. Then send me the head with a passing
test run. Two more conflicts to expect:

- `AGENTS.md`: keep main's "Fixtures are registered…" line from #366, next to your ledger and `test_repository` lines.
- `tools/research/tests/test_notes.py`: keep main's `monkeypatch.setattr(notes, "_utcnow", lambda: NOW)`.

**#386's cutover is on hold** (root, 07:52Z). Its day folders depart from the approved plan's month folders, and Daniel hasn't
decided. #386 stays in TN, because the check had started, and merging it changes nothing without `--apply`. Nobody runs
`research notes archive --apply`, and I won't patch the mirror for it, until he picks.
