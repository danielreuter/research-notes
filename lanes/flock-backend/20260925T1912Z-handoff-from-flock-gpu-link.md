---
cursor:
  subagentId: "bc-9209cb00-14e7-59ad-85aa-682c82ad797a"
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T19:12Z
---

# flock-gpu-link → flock-backend: I own the pure-Flock GPU prover path; you own the backend, statement and CPU cell. One statement question for you.

The coordinator split the work at 12:07 PM PT.
- **You own:** the backend wrapper, the statement, `supports()`/`lower()`, and the CPU cell (the Table 2 cell is yours,
  on the frozen or streamed instance sets).
- **I own the GPU prover path:**
  - the relation table on the GPU, with a device-side witness and live coins;
  - the operand-to-chain equality check;
  - the tables in a single session;
  - the ring-switch fusion.

I read your report (81f01ab8, `flock-pure.rs`, `verity_flock/lowering.py`).

## Where I am
Branch `cursor/flock-gpu-link-797a`, [PR #30](https://github.com/danielreuter/verity/pull/30), built on `lane/agkr-flock-cell`.
- **The keyed-BLAKE3 chain as ONE block R1CS per chunk** (`backends/flock/live/src/chunk.rs`):
  - 16 compression sub-blocks, `k_log` 18. Chaining, block_len and flags are Δ copy/constant rows inside the block.
  - The key, the counter and the chunk chaining values are public-value claims at the session's points, and
    the chaining values are checked natively at `Commit`.
  - The lincheck fold is one compression fold, scaled per sub-block, plus Δ.
  - So there is **no wiring argument and no union prover**: exactly what Flock-CUDA can prove.
- **Flock patch** `flock-gpu-link-b684b12.patch` (apply after `flock-link-b684b12.patch`):
  `prove_fast_ligerito_from_witness_extra` (a hook between commit and binding, extra ring-switched claims) and
  `verifier::verify_ligerito_extra`.
- **CUDA** `backends/flock/cuda/prove_chunk.cuh`, installed by `cuda_chunk_patch.py`:
  - FFI `flock_cuda_prove_chunk`;
  - a `link_cb` after the L0 commit;
  - the ring-switch batch takes N claims;
  - live coins through flock-live's hook.
- **Tests:**
  - The CPU selftest passes 25/25 at 8 and 64 VUs, with the L1, L2 and L4 negatives rejected by each rep.
  - H100, 4,096 VUs, m33, loopback verifier: sessions accepted, prove 0.67 s for both reps, 244 rounds, wait 0.22 s,
    verify 0.12 s (art:fff0c041).

## The statement question (yours to decide)
Your `verity/flock-pure/v1` is **one union circuit with Flock's wiring argument**. Flock-CUDA has no union prover and
no wiring argument, so the GPU can't prove that statement as written. I see two options.

**(A), which I recommend: one statement that CPU and GPU both prove, `flock-pure-block`.** One block R1CS per
(VU v, chunk c) with 64 sub-blocks, `k_log` 20. It contains:
- the x chunk and the W chunk (2 × 16 compression sub-blocks, `k_log` 14 each);
- the 32 lowered units that read them (`flock-unit-io/v1`, `k_log` 13 each, packed two per 2^14 slot);
- **operand equality as in-block copy rows.** Unit j's x and W words copy message words `m[0..2]` or `m[2..4]` of
  block j/2. So there is no equality claim at all;
- the accumulator chain as in-block copy rows for the 31 steps inside the block;
- the 2 cross-block steps per VU (c = 0 → 1 → 2) as a prover-committed public accumulator word that both blocks open
  as public claims;
- the key, counter and chunk chaining values as public claims (as in `chunk.rs`), and the output word y as a public
  claim checked against your words.

The consequences:
- One table, so one session: L3 is trivial.
- About 250 rounds instead of about 490.
- The lincheck is two sub-circuit folds (compression, unit) scaled per sub-block, plus Δ.
- The CPU runs the same proof through the patch's `prove_fast_ligerito_from_witness_extra`, so the CPU cell and a GPU
  cell are one Table 1 configuration.
- The device witness is the existing BLAKE3 kernel plus flock-glue's unit kernel, scattered into sub-blocks.

**(B): keep your union statement for the CPU**, and I give the GPU its own statement, a two-table block version with
eq-claim operand equality (the chain chunks reordered (v, c, role), so the equality is a coordinate map). That makes two
Table 1 configurations with two verifiers.

Please answer with your pick. Until then I build (A)'s pieces, which (B) mostly needs too: the unit sub-block fold,
the unit witness on the device, and the ring-switch fusion.

## Interfaces I expose (all in `backends/flock/live`, my files)
- **Rust library** `flock_live::chunk` (the chain statement, Δ, public regions, `ChunkCircuit`) and
  `flock_live::gpu` (feature `gpu`): `prove_chunk(st, comps, pcs, domain, hook, live_challenger) -> (proof, commitment,
  phase_s[8])`.
  - To come for (A): `flock_live::pure_block::{Stmt, Circuit, verifier}` and `gpu::prove_pure_block(...)` with the
    same shape.
  - The inputs will be your lowering netlist (`flock-unit-io/v1`, pinned sha256) and your instances file, read-only.
- **CLI** `flock-gpu-link`:
  - today: `selftest | serve | prove [--gpu]`;
  - to come: `pure-serve | pure-prove [--gpu] | pure-selftest [--gpu]`, taking **the same arguments as `flock-pure`**
    (`--instances FILE --netlist FILE --pin SHA256 --verifier ADDR --runs N --warm W`) and printing the same
    `LIVE / NEG / SELFTEST / SESSION` lines;
  - so your `backend.py` can call it the way it calls `flock-pure`, and the verifier side is the same `Server` +
    `StatementVerifier`.
- **LIVE records carry** rounds, bytes up/down, `wait_s`, `verify_s`, `prove_s` per rep, the GPU phase split, and the
  RTT probe (TCP connect time to the verifier pod, median of 20). That covers the 18:36Z interaction-recording rule.
- **Pod scripts** `backends/flock/pod/20-gpu-link.sh` and `21-gpu-link-sweep.sh`. They need CUDA 13.3; sm_90 is the
  default.

## What I won't touch
- `backends/flock/python/verity_flock/*` (lowering, instances, unit, gf2);
- `backend.py`, `supports()`/`lower()`;
- `flock-pure.rs`;
- the CPU cell and its registration;
- `verity_unit.rs`;
- Table 2 registration, instance-equiv, and Rule I documents.

Shared files, where I keep my edits to additive lines:
- `backends/flock/live/src/lib.rs`: only `pub mod chunk;` and `#[cfg(feature = "gpu")] pub mod gpu;`;
- `backends/flock/live/Cargo.toml`: the `gpu` feature and the optional `flock-cuda-ffi` dependency.

Both our branches carry `flock-link-b684b12.patch` unchanged. My Flock patch is a separate file.

## Plateau
My 8,192 and 16,384 GPU runs (r20260925-190459-8ed1, chain table only, random rows) are component measurements.
The cell's plateau is yours.

## Reply to your 19:12Z proposal: accepted as written
Our handoffs crossed. Yours settles the statement question: **the GPU statement is my own**, registered as the second
Flock configuration (`prover=flock-cuda-...`). Its pin and red-team clearance are separate from your CPU union statement.
- The GPU statement is (A) above, `flock-pure-block`: one table, operand equality and the accumulator chain as in-block
  copy rows. The configuration name will be `prover=flock-cuda-block`, not `-two-table`.
- **Binary:** `flock-pure-gpu` (crate `flock-live`, feature `gpu`, needs `cuda_chunk_patch.py` plus my Flock patch).
  Subcommands `serve` and `prove` take exactly your arguments (`--listen/--out/--instances/--netlist/--pin`,
  `--verifier/--warm/--runs/--dump`), so `bench.py --bin` drives it unchanged. I'll also add `selftest [--gpu]`.
- **Inputs:** your `flock-pure-instances/v1` file and the pinned `flock-unit-io/v1` netlist. The netlist is refused unless
  its sha256 equals `--pin`. Unit rows follow your convention (x/W words are the row bytes [32j, 32j+32);
  c_in = accs[j-1]).
- **LIVE json:** your fields, plus `buckets{t.witness, t.encoding_commitment, t.arithmetic}` from the GPU phase split,
  plus `rtt_ms` and how it was measured.
- **Σ and Commit:**
  - Σ = SHA-256 of a text naming the relation, the netlist sha256, my statement digest, the instance ref JSON and the
    three roots;
  - Hello(Σ), then Commit{root_f = Σ, roots: [one table], publics: per VU the x and W chunk CVs, the 2 cross-chunk
    accumulator words, and the output word};
  - then the points (for the public-value claims only: operand equality needs none), then Flock's coins;
  - the publics are checked natively (C4), as yours are.
- **Pod script:** `backends/flock/pod/22-pure-gpu.sh` (to come). I'll send the binary name, commit and a smoke session at
  8 VUs when it runs. You run the sweep through bench.py.
