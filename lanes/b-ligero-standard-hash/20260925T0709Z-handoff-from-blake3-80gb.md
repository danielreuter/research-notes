---
lane: b-ligero-standard-hash
kind: handoff
from: blake3-80gb
---

# blake3-80gb merged your 82453d30 + 071e3ef7; views need commit.seconds + sweep/protocol blocks: I added sweep_vu (8c50b497), take it rather than duplicate

- lane/blake3-80gb @ 8c50b497 = main 00ffe398 + your 82453d30/071e3ef7 + ligero-steps-pin 236020a6 + `backends/direct/ligero/sweep_vu.py`.
- Gap found: `bench.views._protocol` (the preview Table 2) rejects any result without `protocol` {warm, runs, contended} and
  `sweep` {plateau: true} blocks, and reads commitment time from the measurement `commit.seconds` (views.COMMIT), while
  `--commit-per-rep` emits `commitment.seconds`. sweep_vu runs bench-vu at doubling --total-vus (1024 up, stop at < 2 % over two
  doublings or a failed point), then stamps every point with `sweep`, `protocol` and `commit.seconds` / `e2e.seconds` aliases.
  If you'd rather emit `commit.seconds` in relchain directly, tell me and I'll drop the alias; please don't write a second sweep driver.
- Split: I run bf16-hopper+blake3 / fp8-hopper+blake3 on an H100 (pod vy-blake3-80gb) now, then bf16-ampere+blake3 on an A100,
  at l = 16384 p4 where memory allows. You keep the 4090 lines and any harness/gadget changes; I only add measurement tooling.
