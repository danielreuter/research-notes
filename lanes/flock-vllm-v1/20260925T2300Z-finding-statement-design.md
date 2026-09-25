---
id: 20260925T2300Z-finding-statement-design
campaign: verity
lane: flock-vllm-v1
kind: finding
status: current
repo: danielreuter/verity
origin: cursor/flock-vllm-v1-4cdd
---

# verity/flock-vllm-block/v1: how vllm-v1's SHA-256 tree and position leaves bind inside the Flock block statement

Code: `backends/flock/live/src/vllm_block.rs` (statement), `src/bin/flock-vllm-v1.rs` (session, verifier, selftest),
`gpu.rs::prove_vllm` + `cuda/prove_chunk.cuh` (mode-1 host witness), `verity_flock/instances.py --scheme vllm-v1`,
`backend.py::FLOCK_VLLM_V1`, `pod/40-vllm-v1.sh`. Branch `cursor/flock-vllm-v1-4cdd` (base flock-backend a6a6e548, which
contains flock-gpu-link 48045063, merged with origin/main 5f8d8789).

## Shape

flock-pure-block v2's fp8 layout (block = VU), with Flock's keyed-BLAKE3 row leaves replaced by vllm-v1 position
leaves `SHA-256("verity/pos-leaf/v0" || u64be(row_bytes) || row)` (PROTOCOL.md §2):

| region of block v (k_log 21 for 1536-byte rows) | what |
|---|---|
| slots 0..25, 2^15 bits each (Flock's `sha2` circuit, Option F) | the x row's position leaf, one compression per 64-byte message block: ⌈(26 + 1536 + 9)/64⌉ = 25 |
| slots 25..50 | the W column's |
| 2^13 positions 200..248 | the 48 census units (pinned `flock-unit-io/v1` lowering) |
| the rest | forced zero |

50 × 2^15 + 48 × 2^13 = 2,031,616 of 2,097,152 bits: the block is 97 % full (the keyed-BLAKE3 fp8 layout: 56 %).
BF16 rows (3072 B, 96 units) give 49 + 49 slots at k_log 22; the code is shape-generic, only fp8 is built on the GPU
(Flock-CUDA's pure mode caps comp_slots at 256 and k_log at 22 in host-witness mode).

`A = I ⊗ circuit + Δ` (and B). Δ, as XOR toggles of input rows (every SHA-256 `H_in`/`M` row is `A = [s], B = [Z]`):
- **chain**: `H_in` of slot 0 = the SHA-256 IV (constant), `H_in` of slot j ≥ 1 = `H_out` of slot j − 1 (copy). Flock's
  `H_out` includes the feed-forward, so the chain is the FIPS 180-4 iteration and slot 24's `H_out` is the digest.
- **prefix and padding**: message bytes `[0, 26)` of block 0 (the 18-byte tag and `u64be(1536)`) and bytes
  `[26 + 1536, 1600)` (0x80, zeros, `u64be(8 · 1562)`) are constants. So the value length is fixed by the statement,
  not the prover (§9.4), and the leaf rule is fixed (§9.3).
- **offset absorption (§8.1)**: row byte t is message byte 26 + t, i.e. slot ⌊(26 + t)/64⌋, byte o = (26 + t) mod 64,
  SHA-256 word o/4, word bit 8·(3 − o mod 4) + bit (big-endian words). Unit u's x and W input bits `A = B = [that
  message bit]`; units straddle message blocks (odd u), which costs nothing in a per-bit copy.
- **accumulator chain**: unit u's c_in = unit u − 1's c_out, unit 0's forced to +0 (as fp8 v2).
- **constant pin**: every slot's and unit's constant column copies slot 0's, pinned by the lincheck β.

Lincheck fold: eq_inner = eq_hi ⊗ eq_lo, so the 2^21 fold is the 2^15 SHA-256 fold scaled per slot, the 2^13 unit fold
scaled per unit position, plus the Δ scatter (Rust `VllmCircuit`, CUDA `pure_comb_expand` with `sub_log` 15).

## What is public, and where each vllm-v1 hash lives

| hash (PROTOCOL.md §8.1) | where |
|---|---|
| position leaf of each x row / W column (25 compressions) | **in the proof** (every compression, IV / prefix / padding constants in Δ) |
| position leaf of each output word (`y_bytes` LE, 1 block) | verifier-native: the verifier holds the output words (they are the statement's output) |
| node / lift (a, b, y trees) | verifier-native, from the leaf digests (§3 fold: pairs, odd tail lifted, no padding) |
| step root `verity/fa2c/root/v0 ‖ program ‖ ctx ‖ geo ‖ layout ‖ u64be N ‖ tree_root` | verifier-native, over its own domain |

Public regions (each opened at two verifier points drawn after the commitment, both reps): x digest (`H_out` of slot 24,
256 bits), W digest (slot 49), output word (unit 47's c_out). The prover sends the 2 × 32-byte digests of every VU in
`Commit`; the verifier folds them, VU v's as leaf v, and compares each step root with the bound root it holds before it
draws the points. 6 extra ring-switch claims per rep (≤ 16 in Flock-CUDA).

## PROTOCOL.md §9 checklist

1. **Domain.** Each port (a x rows, b W columns, y output words) is a `StepDomain`. program / geo / layout are derived
   from the relation's shape (K, word bits, y bytes), ctx from the verifier's own instance reference (dataset, tier,
   manifest, range, port) — `ligero.vllm_tree`'s derivation, so **a Flock cell and a B-Ligero `+vllm-v1` cell on the same
   line bind the same three roots** (Rust `v1::Domain::of` reproduces B-Ligero's port-domain vectors). The three
   `domain_digest`s and the three bound roots are in Σ (`verity/flock-vllm-block/sigma/v1`), which `Hello` and `Commit`
   (root_F = Σ) carry, so every live coin is drawn after it.
2. **Bound root, never the bare tree root.** The verifier compares `domain.bind(fold(digests))` with its held root.
   Negative `bare_tree_root` (both sides name the bare root): refused at Commit.
3. **Leaf rule.** Fixed by the statement (Δ's prefix constants; statement digest), not by any prover label.
4. **Value length.** `u64be(1536)` and the padding's bit length are circuit constants. Negative
   `value_length_prefix_other` (u64be(1535)): both reps reject.
5. **Positions.** VU v's digest is leaf v of each tree; N = the verifier's range length; tree shape from N. Negative
   `digests_swapped_positions`: refused at Commit.
6. **Thread trees:** none.
7. **One tree per opening.** Leaves of a come only from slot 24 (x), of b only from slot 49 (W); nodes never mix
   trees. Negative `digests_swapped_x_w`: refused at Commit.

## Soundness notes for red-team-flock

- Same PIOP as flock-pure-block v2 (zerocheck, lincheck with the structured fold, sparse ring switch with extra claims,
  Ligerito Fast100 × 2 live reps); only the sub-circuit (SHA-256 instead of BLAKE3), Δ and the region list differ.
  Every Δ row is a copy or a constant, no new PIOP. Region claims: 3 regions × 2 points per rep.
- The per-proof bound the bench reports is flock-pure-block v2's granted 2^-195.44 (union over sub-batches); it needs
  red-team confirmation for this statement (m = 21 + nbl, 6 extra claims).
- SHA-256 collision resistance is the vllm-v1 assumption (decision 57), as for B-Ligero's `+vllm-v1`.

## Negatives (selftest, CPU and GPU, 21 cases)

honest ×2; `root_b_other_than_bound_root`, `coins_before_y` (session); `verifier_domain_other_range`, `bare_tree_root`
(Σ agrees, root check refuses), `prover_names_other_domain` (Σ differs, Hello refused); `digest_forged`,
`digests_swapped_x_w`, `digests_swapped_positions`, `row_forged_own_digest` (a consistent chain over another row: refused
at Commit); `row_forged_honest_digest`, `forged_middle_block`, `value_length_prefix_other`, `wrong_iv`,
`unit_internal_bit_flipped`, `unit_operand_differs_from_message`, `acc_in_differs_from_previous_c_out` (both reps
reject); `reps_with_different_witness`, `fast_profile_proofs`, `cross_session_replay_both_reps`.

## Prover path

The SHA-256 witness is built on the host (Flock's `generate_witness_with_ab_packed_and_lincheck`) with the units, and
the whole packed z, a, b is uploaded (`FlockChunkParams.host_z/a/b`, mode 1); built once per session, both reps prove it.
There is no device SHA-256 witness kernel in Flock-CUDA b684b12: writing one (and a device chain/unit-input kernel, as
flock-gpu-link did for BLAKE3) is the next speedup.
