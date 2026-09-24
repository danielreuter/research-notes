---
id: r21-night2/relmin-private/20260923T1010Z-handoff-coordinator-merge-val-findings
campaign: r21-night2
lane: relmin-private
kind: handoff
status: open
repo: verity (main 78ce73f)
origin: coordinator, from lane merge-val's note ~/.research/notes/lanes/merge-val/20260923T1000Z-report-merge-val.md
---
# Coordinator -> relmin-private: your checkpoint 9a42e39 is MERGED into main (8415ceb), but two things break on the merged tree

1. **All four `privsel/relation_test.py::test_differential_v1_v3[...]` FAIL on main** (4 failed / 165 passed in `pytest backends/direct/ligero`
   on a 4090). `privsel/` is byte-identical to your 9a42e39; what changed under it is `pubsel/relation.py` + `pubsel/hints.py` via relmin-lookup's
   later commits 9a869b3 / **6ef1d3d (fraction-bit-free last group)** / c7d32e0, which main took after you branched from 02c3321.
   merge-val's control on your own 9a42e39: 3 pass, **fp8-ada-v3 fails there too** (pre-existing). Please re-derive the v3 windows on merged
   main (rebase or merge main into lane/relmin-private first) and make the differential green; until then Table 2 will NOT use v3.
2. **`fp8-ada-v3 gate-vu` on the 4090: 25/25 honest accepted, then the negatives phase crashed at its first proof**:
   `privsel/hints.py:223 run -> CUDAGraph.replay: RuntimeError: Offset increment outside graph capture encountered unexpectedly.`
   Same class as the break merge-val fixed in `chain.py` (538801e, merged): a CUDA-graph capture that fails is swallowed by an
   `except Exception: g = False` fallback and leaves torch's default generator in capture state, so the NEXT replay raises. main 78ce73f now
   WARNS on every failed capture (`protocol._capture_failed`; `LIGERO_GRAPH_STRICT=1` re-raises) -- run your gate with `LIGERO_GRAPH_STRICT=1`
   to see the real exception; a device sync (`.tolist()`, `.item()`, `.cpu()`) inside your hint graph body is the likely cause.

Deadline for a mergeable fix: 11:45Z (coordinator sweeps 10:30Z / 11:15Z / 12:00Z; CHECKPOINT line in your note).
