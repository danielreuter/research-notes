---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T10:08Z
---

# fp8-ada+blake3 4096 frozen cell with a LIVE verifier's own coins (same pod): art:e9932b72…

This follows my 0958Z handoff. The coordinator (0915Z) asked for it only if cheap: "a live verifier with its own coins is
the stronger footnote ... on the 4096 frozen cell".

| Line | bench-result | run_files | VUs | sub-batches | t.total | t.total_live | commit | e2e | VU/s | attempt |
|---|---|---|---|---|---|---|---|---|---|---|
| fp8-ada+blake3 (frozen `e66ff0f2…`) | art:e9932b72b71ed81a6d4a94ea62e36bc3f1db521258c9237744c5c31459ca71ee | art:6a36cde712108a60fe919043996cfdeda11e06a93e583544bd1438b09966742c | 4096 | 49 | 3.585 s | 3.592 s | 0.010 s | 3.596 s | 1139 | r20260925-095340-c456 |

- **Tree 806a2f73; settings as the 0958Z cells**, plus `--verifier tcp://127.0.0.1:7000`.
- **The verifier:** `python -m backends.direct.ligero.live serve` from the same tree, niced, with `--jobs 4 --threads 1
  --target-bits 128` and the pod's ligero-verify e1ed499c….
  - Each recorded rep is one session; the verifier drew the step-0 coins and checked every sub-batch as it arrived.
  - Result: 5 sessions, each ACCEPT 49/49, 2^-128.40.
- **run_files** holds rep 1's dump (proofs/: stmt + proof + system.bin + manifest). It also holds the verifier's records
  under `live/`:
  - index.jsonl and serve.log;
  - each session's hello / session / verdict json and `sub_*.coins`.
- The pod's Rust batch accepts rep 1 49/49 against its own (the live verifier's) coins.
- **Caveat for the footnote:** the verifier ran on the prover's pod. The coins and the process are the verifier's, the
  machine is not. There was no second pod for a hairpin test (kb/live-verifier.md).
- A file re-verification of rep 1 with the fixed reverify (R1 + R2 + R4) applies as for the other cells.
- **Malloc caveat:** this cell was measured before the coordinator's 1003Z malloc-env note (MALLOC_MMAP_MAX_=0 ...).
  Re-measurements with it will come as new results; this one stands as it is.
