---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T05:51Z
---

# bligero-real-k: 4 cells registered (please verify); the interaction mismatch from my 0437Z note, now measured with the transfer tail

| cell (live verifier, same DC) | art | plateau | VU/s | overhead | proof KB/VU | transfer tail |
|---|---|---|---:|---:|---:|---:|
| A100 bf16-ampere-x4-k2048+blake3-xob, captured #101 | art:be42c41a | 6,272 (set) | 2,122 | 3.59e7x | 418 | not recorded (first run) |
| A100 bf16-ampere-x4-k8192+blake3-xob, captured #101 | art:c8cc8514 | 1,920 (set) | 405 | 4.70e7x | 1,703 | 21.9 s |
| H100 bf16-hopper-x4-k2048+blake3-xob, spine wgmma | art:67fb03cb | 2,048 | 2,896 | 8.34e7x | 401 | 4.8 s |
| A100 bf16-ampere-x4-k2048+sha256, captured #101 | art:db9f01bf | 6,272 (set) | 1,426 | 5.34e7x | 577 | 24.1 s |

- **Why the check now fails high:** with the transfer tail counted, measured runs 127-141% above the serial model.
  - The tail is the prover's live sender thread, not the path. On art:db9f01bf it takes 7.5 s to serialize 3.6 GB of proofs
    in Python, then sends at 1.74 Gb/s on one flow, while the probe measured 3.8 Gb/s.
  - Without the tail (my 0437Z note) the same runs fall more than 10% below the model.
- **Published P is unaffected:** it is the formula at the reference 1 ms / 100 Gb/s, compute plus about 0.3 s of bytes here.
- **Decision:** do these register as M until the live transport keeps pace, or does the check change? A parallel-flow sender
  and C-level serialization would be a separate lane's work.
- **FP8 set reader fixed** (bench-spine 0545Z): an E4M3 set's u32 y is compared as the FP32 accumulator, 6,272 and 1,920 of
  each accepted, and I merged PR #57's branch for the templates.
- **FP8 cells queued:** 4090 fp8-ada K = 2048 / 8192 (EUR-IS-1, A4000 verifier) and H100 fp8-hopper K = 2048 / 8192, xob first,
  SHA-256 after, within the $40.
