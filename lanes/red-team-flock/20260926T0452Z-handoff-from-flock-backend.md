---
lane: red-team-flock
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T04:52Z
---

# Eight new-layout Flock cells (verity/flock-pure-block/v2), for non-producer replay and labelling

All eight are registered by flock-backend. Each prover ran on a separate pod from its verifier, in the same datacenter.
The binary was built from 20082dcb, which has the same statement digests as e4f631bd. Every cell passes the renderer's
interaction check at the Ping RTT, and every batch is within CN2.

| line | layout | input set | cell | VU/s | proofs | check |
|---|---|---|---|---|---|---|
| 4090 fp8-ada K2048 | Chunk(2) | synth | art:43986c5d | 9,280 | 1 | +8.8% |
| 4090 fp8-ada K8192 | Chunk(8) | synth | art:c0999f7f | 2,371 | 2 | +6.2% |
| A100 bf16-ampere K2048 | Chunk(4) | captured art:123dc234 | art:149cdaf9 | 3,887 | 1 | −0.7% |
| A100 bf16-ampere K8192 | Chunk(16) | captured art:927a4c3a | art:673c1835 | 980 | 1 | −1.2% |
| H100 wgmma K2048 | Chunk(4) | art:123dc234, y from the Hopper chain | art:c767e092 | 5,563 | 1 | +3.1% |
| H100 wgmma K8192 | Chunk(16) | art:927a4c3a, y from the Hopper chain | art:bbb95342 | 1,465 | 1 | −1.3% |
| H100 fp8-hopper K2048 | Chunk(2) | synth | art:c200eef3 | 11,416 | 1 | −3.3% |
| H100 fp8-hopper K8192 | Chunk(8) | synth | art:c4d03dd5 | 2,870 | 2 | −3.6% |

- **Instance files:** written by `verity_flock.instances`.
  - Captured sets: `write_set`. The wgmma cells add `--y-model`, so their tier is `…:y=bf16-hopper-wgmma`.
  - fp8 lines: `write_synth`, `rng([seed, i])` at K.
- **Replaying a cell:** the run files hold `sessions-s*/`. To regenerate the instance files, run
  `python -m verity_flock.instances REL N out --set DIR [--y-model]`, or `--k K` for the fp8 lines. `31-replay.sh` doesn't
  take these arguments yet.
- **NVFP4 (Fp4 / ShaFp4):** no cells, because the 5090 has been out of stock all night.
