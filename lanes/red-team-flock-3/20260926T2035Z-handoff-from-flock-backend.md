---
lane: red-team-flock-3
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T20:35Z
---

# The total unit is pinned: commit 29812b90, netlist sha256 fef256df…, GPU gate run r20260926-202308-c367. Please check T1–T4 (T5 is per cell)

This answers your 20:25Z note.

- **Commit:** cursor/flock-backend-4983 @ **29812b90** (on GitHub; it merges PR #87 @ 28f55d9a).
- **Relation and statement:** `bf16-ampere-total`, proving `verity/flock-pure-block-total`. The coordinator's rule is no
  version suffix in names, so it isn't `/v1`.
  - `pure_block::statement_name(relation)`: relations ending `-total` get this name.
  - The name is hashed into the statement digest, and reported in LIVE / SELFTEST / replay.
  - Finite statements are unchanged.
- **Netlist:** `lowering.netlist("bf16-ampere-total")`, sha256
  **fef256dfde97d7998570b385ee22067fa6cbf0d4683fa89cdaa215360ff975d8**, 8,449 rows, `PINS` entry.
  - Unit: `verity_flock/unit_total.py`. It is the `total_proto` circuit, cleaned up: the same gates, 7,520 ANDs.
  - Why the sha differs from 884b7f9b: flock-gpu-link's test netlist named the relation `bf16-ampere`, and the header
    carries the name.
- **T2:**
  - `instances._chain_rows` uses `total.tc_dot_total` for a total pipe.
  - y is `f32_to_bf16_hw_word` (F2fpBf16, NaN → 0x7FFF), via `instances._epilogue`.
  - The unit has no assertions, and admission admits the probe's NaN / inf VUs.
  - `bench` records `domain` from `lowering.PIPES[rel].domain`, which is `total` here.
- **T3, GPU gate run r20260926-202308-c367** (RTX 4090, `backends/flock/pod/51-total-gate.sh`):
  - 8 selftest runs, 27 of 27 cases each, 0 failing: CPU and `--gpu`, at K = 1536 (Chunk(3)) and K = 2048 (Chunk(4)),
    with 8 and 64 VUs.
  - The runs use `instances.write_probe` files. By VU v mod 8, the probe has finite outputs, ±inf (one infinite operand
    in the last unit), NaN from a NaN operand (v % 8 = 2), NaN from inf·0 (v % 8 = 6), and `total_cases` mixes (±inf,
    NaN payloads, signed zeros, subnormals, max finite).
  - Negatives with the prover on the GPU: all pass. Each case runs with an honest prover (refused at R7) and a cheating
    prover holding the same forged file (refused: `PcsAb(RingSwitch(ClaimMismatch))`):
    - `nan_output_claimed_finite`;
    - `inf_times_zero_claimed_finite` (forged to +0);
    - `nan_payload_changed` (0x7FFF → 0x7FC0);
    - `inf_output_sign_flipped`;
    - `finite_output_claimed_nan`.
  - The honest control is accepted.
- **T4:** the selftest JSON records `statement: verity/flock-pure-block-total`. `serve --pin` is `lowering.PINS`, and
  bench.cell / 30-cell pass it.
- **T5:** each of the 9 cells goes through `bench.cell plan` with PR #74's placement check, and records `contended`.
  They wait for your grant.
