---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T06:40Z
---

# IR3 review request: `verity/flock-ir-frame/v2` at c53d9148 (PR #54), the frame-v3 binding for all four templates, the RMSNorms included. IR4 is at b4e05b48, in this tip. The RoPE and SiLU·mul cells are covered: the v1 cells, plus re-runs under v2 in progress with the RMSNorm cells

This replaces the IR3 review of `verity/flock-ir-frame/v1` (ad027ea7). The IR4/IR5 confirmation I asked for at 06:02Z stands: b4e05b48 is an ancestor of this tip, and nothing in `flock-ir-block` / `ir_tail` changed after it, apart from a refactor that moves `cut_map`'s core into `cut_map_of`.

**Why v2 (root decision, option B).**
- flock-gpu-link's mode-1 prover caps a block at 2^22 bits, and that cap stays. v1 put a chunk's whole compression chain and every unit reading it in one block.
- A finer cut can't fix that. For fused N=2048, the 16 warps reading a chunk pair need 16 × 317k useful rows plus 6 × 2^18 rows of hashing, about 6.6M bits against a 4.2M-bit block, whatever the unit size.
- So v2 splits a chunk's compressions into runs, and a block holds only the runs its units read. The cut stays exactly the IR4-pinned one.

**The statement** (`live/src/ir_frame.rs`, header doc; Python `verity_flock/ir_frame.py`):
- **Runs.** A run is `nb` consecutive compressions of one chunk (`chunk_nb` per chunk). The planner takes the largest `nb` (a whole chunk, then halves, and so on) whose unit-and-run components are all one shape and fit 2^22. Run slots are padded to a power of two.

  | template | run | block | k_log |
  | --- | --- | --- | --- |
  | rope | 2 of 2 (whole chunks, as in v1) | 64 units | 20 |
  | silu | 16 of 16 (whole chunks, as in v1) | 256 units | 22 |
  | fused N=2048 | 4 of 16 | 4 warps + 6 runs + 2 empty slots | 22 |
  | Triton N=2048 | 8 of 16 | 1 warp + 2 runs | 22 |

- **Δ** keeps only the chain inside a run (chaining input of compression j ≥ 1 = `out_lo` of j − 1), the constant pins, and the unit leaf wiring (message bits). The key, block_len and flags are no longer Δ constants.
- **Regions.** All are the verifier's values, at two points drawn after the commitment, both reps:
  - `Params`: bits 1024..1152 of every compression: the counter (the chunk's index), block_len 64, and flags (KEYED_HASH, CHUNK_START on a chunk's first block, CHUNK_END and ROOT for a one-chunk row on its last);
  - `CvIn`: every run's chaining input: the x-row key for run 0, otherwise run r − 1's public output value;
  - `Cv`: every run's `out_lo` at its last compression, equal to the prover's public for that run;
  - `Out`;
  - for cut templates, `CutIn` / `CutOut`: each unit's cut input and cut output port groups, taken from the file's cut words.

  So a chunk's runs chain across blocks through their public outputs. The chunk value is its last run's output, folded into the row digest as in v1.
- **Padding.** An empty run slot hashes `nb` zero blocks from the key at counter 0, with KEYED_HASH plus CHUNK_START first and CHUNK_END last. An empty unit slot has zero inputs, so its outputs and cut outputs are the netlist's on zeros. Unit slots are never padded inside a component.
- **Cut words.**
  - The file ends with every instance's cut words, and `public_sha256` (which Σ binds) now covers them.
  - At load, `check_cut_words` evaluates the netlist's pinned tail (IR4) on the words the units produce and requires every other word to match.
  - The CutIn/CutOut claims then bind each unit's cut ports to those words.
  - `cut_map_of` takes the cut structure from the netlist, as `flock-ir-block` does.
- **Claims.** Up to 6 regions × 2 points = 12 extra claims; flock-gpu-link's CUDA accepts 16. The digest adds `chunk_nb`, the cut word count and the region count to the layout it hashes.

**Negatives** (`flock-ir-frame selftest`; the new ones are marked "new"):
- `flags_forged` (new): CHUNK_START dropped from the witness. Both reps reject.
- `chained_run_input_forged` (new): the witness's chaining input of a run with r > 0 forged, and its run re-hashed. Both reps reject. Only files with more than one run per chunk run this case.
- `key_substituted`: now caught by the CvIn claim.
- `row_scalar_forged` (new): refused at load.
- `eps_forged_tail_words` (new): eps × 100, every instance's tail words recomputed. The file is consistent under the forged tail and refused under the pinned one.
- `aggregate_forged_with_its_scalar` (new): the verifier's file has a unit's aggregate changed and its scalar recomputed. It passes load, then both reps reject.
- `cut_input_differs_from_the_cut_word` (new): the prover's unit reads another scalar. Both reps reject.
- The v1 cases, unchanged: the false output claim, the message byte, the unit input, the internal bit, the forged chunk value, coins before y, the reps' witness, the fast profile, replay, and the prover's file.

**Evidence:** `lanes/flock-ir-lowering/evidence/20260926T0635Z-frame-v2-selftests.txt`. All 99 cases pass:

| file | cases |
| --- | --- |
| rope (16 heads) | 14/14 |
| silu (2 rows) | 14/14 |
| silu in runs of 4 (`k_max` 20) | 15/15 |
| fused N=64 (16 rows) | 18/18 |
| fused N=2048 (1 row) | 19/19 |
| Triton N=2048 (1 row) | 19/19 |

**Cells.** Separate verifier pod; each side stages its own files.
- **Under v1** (ad027ea7, plus the open-connection Ping, d3bd9814):
  - RoPE: art:9d899633 (prover r20260926-053944-5195, verifier r20260926-053921-983f);
  - SiLU·mul: art:3173830b (r20260926-054314-9827 / r20260926-054305-d609).
  - Under v2 their block layout is v1's (whole-chunk runs, the same blocks); the statement differs only in the Δ and regions described above.
- **Under v2, running now** on vy-flock-ir-lowering-h100d (prover) / vy-flock-ir-lowering-ver2 (verifier), H100, EUR-IS-3:
  - rmsnorm-fused-cuda on the captured set art:a261c0c2 (r20260926-063305-3f36 / r20260926-063231-f0c1);
  - then rmsnorm-triton (art:9582a734), and RoPE and SiLU·mul again.
  - Their art ids will be in my report's checkpoints.

**Suggested attack points:**
1. The cross-block chain: can a run's CvIn and the previous run's Cv be satisfied with different values? Both read the same public, placed by `run_at`, which is built from the verifier's own block table.
2. Params completeness: every compression's counter, block_len and flags are claimed, including the empty slots.
3. `check_blocks`: every run of every chunk exactly once, and empty slots past the components.
4. Cut words in Σ, and CutIn/CutOut against the pinned tail.
5. The empty-unit dummy cut output.
