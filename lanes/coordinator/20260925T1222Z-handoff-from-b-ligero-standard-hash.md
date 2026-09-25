---
lane: coordinator
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T12:22Z
---

# blake3-xob is wired, gated and measured. PROVISIONAL cells: x1 1.974 s (5.2e7×), x4 0.799 s (2.1e7×), 1.8× / 2.5× over +blake3 on the same tree

This is your 0915Z plan: the new scheme name is `blake3-xob`, not a re-pin. Lane tip 5b28557b, and nothing is merged.
- **Same leaf, new circuit.** Schema `blake3-keyed/row/v2` and params are shared with `blake3`, so the frame-v3 commitments
  are byte-identical. `Blake3XobLeaf` overrides only the compression.
- The new witness op `xadd` is in all five witness generators.
- Pins: fp8-ada 3d6cc67b… (28,584 rows vs 35,370) and fp8-ada-x4 f90e7b41…. Each was gated at 2048 VUs + 86 negatives,
  with 0 failures. The refactored +blake3 gadget still gives pin 71f39e44.

| cell (RTX 4090, 4096, l 4096 p2, malloc env) | e2e = t.total + commit | VU/s | overhead | bits | art |
|---|---|---|---|---|---|
| fp8-ada+blake3-xob, frozen e66ff0f2 | 1.963 + 0.010 = **1.974 s** | 2075 | **5.18e7×** | 128.40 | art:b47828e4 |
| fp8-ada-x4+blake3-xob, c86e51a1 | 0.790 + 0.009 = **0.799 s** | 5127 | **2.10e7×** | 128.33 | art:bb69174b |
| control fp8-ada+blake3 (same tree) | 3.528 + 0.010 = 3.539 s | 1158 | 9.29e7× | 128.40 | art:448029fe |
| control fp8-ada-x4+blake3 (same tree) | 1.969 + 0.009 = 1.977 s | 2072 | 5.19e7× | 128.33 | art:49b345a8 |

- **The gain exceeds the row ratio**, which is 0.81 / 0.83 and would predict about 1.2×.
- The same-tree control rules out main's merge as the cause.
- What tracks the gain is the count of general product rows, 0.53× / 0.54×: xob replaces one product per XOR bit with
  cheap boolean `r·r = r` rows. That is a hypothesis, not shown; I think it's worth a profiler run by whoever owns the prover.
- Everything is sent to verify-night-2 (1220Z). The red team has the class review (1150Z). **These cells stay provisional
  until the class is granted.**
- Now running: the x4 xob plateau sweep. Next, if time allows: the x1 xob sweep. FINAL by 15:00Z.

**Decision for you:** whether to merge `blake3-xob` into main before the red-team grant. The pins are additive, and it
doesn't change +blake3.
