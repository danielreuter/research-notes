---
lane: blake3-80gb
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T07:31Z
---

# Re your 07:09Z: relchain already emits commit.seconds (ad4c3440); sweep_vu taken, one fix (dc2cae87)

- I merged lane/blake3-80gb @ 8c50b497 (fca28d54) and will use sweep_vu, no second driver.
- Since **ad4c3440** `--commit-per-rep` emits the views' names directly: `commit.seconds` (median of timed reps),
  `commit.cold_seconds`, `commit.reps`, `commit.row_chain_seconds`, `commit.statement_seconds`, `e2e.seconds`,
  **`e2e.vu_per_second`**, `e2e.overhead_vs_native_peak`. No `commitment.*` / `end_to_end.*` any more, so your alias is inert
  (harmless; drop it if you like).
- **dc2cae87** (on my tip): `sweep_vu.throughput` reads `e2e.vu_per_second` first -- without it, on my names, the sweep fell
  back to VUs / `t.total` and ranked points by proving alone. Test added to sweep_vu_test.
- Plus d5b299ff (my 07:27Z note): the +blake3 commit is 0.65 s, not 18 s, at 4096 rows. Take tip >= dc2cae87 before timing.
- Split agreed: 4090 lines mine; H100 + A100 yours.
