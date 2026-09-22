---
id: r20-proof/a-verifier-2/20260922T1110Z-report-a-verifier-2
campaign: r20-proof
lane: a-verifier-2
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/a_verifier_2.md
---

# a-verifier-2: F1 verdict, the 1.00 s verifier, checker-v2 verification (2026-09-22, ~11:10Z)

Branch `lane/a-verifier-2` off `main` 48897d1.  Pods: vy-sp1 (RTX 4090, GPU prover runs), vy-cpu2 (EPYC 9654, 12 of 32
threads, shared with red-team-v2; load 31-34 during every timing run).  Ledger `ledger/a-verifier-2.jsonl` (4 entries: F1 verdict, verifier timing, e2e row, v2).

## 1. F1: the kernel path is bit-exact on a clean card; the vy-g5 rejection is an environment fault

`note:r20-proof/a-verifier-2/20260922T1054Z-finding-f1-triage` has the full record.  On vy-sp1 with `~/.triton/cache` wiped, `main` 48897d1's
kernel path (`python -m gpu.run prove ... --device cuda`, the configuration of the recorded 4.43 s row) produced proofs
at synth B = 2, B = 64 and B = 512 that are **byte-identical** to the `VERITY_GPU_TORCH_ONLY=1` proofs of the same
inputs and are accepted by both the Python and the Rust verifier (Rust 0.069 / 0.129 / 0.506 s at 16 threads on the
pod's EPYC 7B13); run r20260922-100739-bc57 (B = 512 and the diff), r20260922-100257-911e (B = 2, 64).  The tensor-level
harness `gpu/f1_diff.py` (both paths on the same parent tensors: `build_leaves` level 0, every `combine_level`,
`fold`, `ext_mul`, `logup_round` of all five tables) reports 0 differing entries at B = 64 and B = 2.  The kernels under
suspicion are the same code in c4d472a (the a-gpu row's tree) and `main` (`kernels.py` only gained three unrelated
kernels), so the triage covers them.  **Verdict: hypothesis (b)** -- a stale Triton cache or the vy-g5 environment
(H100 tile selection is the other candidate; not testable from vy-sp1) -- not a latent kernel bug for these sizes on
sm_89.  Two consequences: the a-gpu 4.43 s row still needs re-recording from a committed tree with a proof file the
Rust verifier accepts (B = 4096 does not fit the 4090: a-gpu2 measured 47.9 GB peak); and `main`'s prover (the a-gpu2
merge) is now Rust-verified from a committed tree at B <= 512.

## 2. Sub-second verifier: 3.02 s -> 1.00 s at B = 4096 on 12 threads

Same proof (a-gpu torch path, r20260922-091240-4bf9), same pod, same 12 threads; bit-exact acceptance after every
step (B = 64 / 4096 accepted, 44/44 negatives, 1320/1320 sampled mutations in the final run r20260922-105647-c947;
16485/16485 exhaustive on the a-verifier tree).

| verifier | B = 64, 1T | B = 64, 12T | B = 4096, 1T | B = 4096, 12T | fill CPU s | NTT eval CPU s |
|---|---|---|---|---|---|---|
| a-verifier (main 48897d1; r20260922-093721-1330) | 0.594 | 0.109 | 34.02 | 3.017 | 14.8 | 18.3 |
| a-verifier-2 (r20260922-105647-c947) | 0.222 | 0.077 | 10.29 | **1.000 / 1.027** (2 reps) | 4.5 | 4.9 |

Per stage at 12T, B = 4096: parse 0.035, transcript replay 0.007, functional value 0.116 (5.6x scaling; the `eq`
tables are built serially), Merkle + proximity 0.024, Ligero linear test 0.811 (11.6x scaling of 9.4 CPU-seconds).
Fill breakdown (`VERITY_GKR_PROFILE=1`, CPU s): input claims 0.93, single-column (R16) lookups 1.68 + flush 0.92, ext
lookups 0.79, chain 0.08.

What changed (all in `backends/gkr/verifier/src`):

* **NTT eval 18.3 -> 4.9 CPU s.**  Rows are evaluated 8 at a time in the interleaved layout (`L = 48` lanes per NTT
  point: one twiddle load per 48 Montgomery products), the inverse transform is a permutation-free DIF (bit-reversed
  output), and the forward transforms are **output-pruned** DIT: for each of the three needed cosets, 6 in-L1 stages
  on the bit-reversed coefficients, then each of the ~21 wanted outputs is a 64-term sum (`ntt.rs::dit_pruned`,
  `pruned_twiddles`) -- the twist by the coset generator is folded in as before.  The butterflies run on AVX-512
  (`lanes.rs`: even/odd `vpmuludq` Montgomery product, 16 lanes per register, runtime-detected; `VERITY_GKR_NO_AVX512=1`
  forces the scalar loop, which LLVM autovectorises at 8 x u64) and are bit-exact with the scalar path (unit test on
  random and edge values).  Evaluating directly at the opened points (barycentric / a modular GEMM) was costed and
  rejected: 1.57 M multiply-adds per row versus the NTT path's ~3.7 M lane operations, but a 32 x 32 -> 64 modular
  multiply-add costs ~0.5 instructions per element against ~1.2 for a full butterfly lane, so it comes out even.
* **Fill 14.8 -> 4.5 CPU s.**  Input claims: `V[col] = rho_l eq(l*, col) + rho_r eq(r*, col)` as 6 x 6 Montgomery
  matrices applied to `eq(c*, u)` in a planar layout (`field.rs::PlanarMats`), one 8-wide product per output lane.
  R16 lookups: the 751 terms per unit are `+-1` coefficients, stored as a CSR of ranks into the unit's 294 touched
  columns; the accumulate is a masked AVX-512 6-lane add/sub into canonical accumulators, and the flush is one
  planar matrix product `(rl eq_hi) x acc` per unit (`verify.rs::flush_single`).  Multi-column lookups: the per-term
  `beta`-combination matrices are precomputed.
* Everything else (transcript, LogUp, GKR, Merkle) is unchanged; peak RSS is still ~100 MB.

Where the time is now and what is left.  Two reps at 1.000 / 1.027 s with the pod at load 33-34 on 32 cores; the
linear test alone would be 0.78 s at perfect scaling, so an idle pod gives ~0.97 s and the target is met only
marginally.  The butterfly path is at the machine's throughput (≈ 9 lane-operations per cycle per core over the
whole eval, i.e. the AVX-512 units are saturated); the remaining levers are algorithmic: (i) skip the multiply-by-one
stage of both transforms (~4% of eval); (ii) thread `eq_table` and `SplitEq::new` in the functional-value stage
(~0.06 s wall at 12T); (iii) the R16 accumulate at 8 ns per query is a dependent-load chain (`eq.lo[x & mask]` then
the CSR terms) -- software prefetch or sorting queries by `x` within a unit would help; (iv) the GPU: rows are
independent and the whole linear test is 9.4 CPU-seconds of BabyBear arithmetic, which is ~50 ms on an H100.

E2E envelope re-rowed (`verifier/e2e.py`, `results_e2e_{agpu2,kernel,torch}.json`; `note:r20-proof/latency/20260922T1111Z-report-latency` section 1 rows +
section 8): with the a-gpu2 1.79 s prover (r20260922-094040-9e76, Python-verified) 2.82 / 3.26 / 7.20 / 24.7 s at
RTT 0 / 1 / 10 / 50 ms, verifier share 36 / 31 / 14 / 4%; with the recorded 4.43 s prover 5.46 s at RTT 0 (was 7.47).

## 3. Checker v2: the Rust verifier verifies `lane/a-gpu-v2`'s proofs

Read-only use of `lane/a-gpu-v2` (its head plus a-verifier's proof serialisation commit b5cba54 cherry-picked in a
scratch branch `scratch/av2-v2test`, never merged) on vy-sp1, run r20260922-103210-9cba.  The Rust verifier gained
(`circuit.rs`, `main.rs`, `verify.rs`):

* `itable` implicit tables (`shift`, `tnorm`) and `R<w>` ranges materialised row by row on access (`TableRows`), with
  the `2^bits x R` / `2^vb x k_rows` row-count checks of `circuit.rs::materialise`; the table union across segments
  (`Statement::tables`, segment 0's tables first, then the epilogue's new ones -- `gpu/prover.py::union_tables`).
* `manifest.json` `"variant": "v2"` selects the v2 statement: `chain.txt` links (`link <in|-> <out> <epi> <init>
  <zero_nonlast>`) with the file's SHA-256 absorbed in the preamble, the per-link constraint counts of PROTOCOL 14.3
  (`Chain::constraints_per_vu`), the init constants in the functional value.
* `read_rows` accepts the v2 synth exporter's u64 rows.

Results (Rust verifier, this laptop, 8 threads): **pos64 (64 VUs of the bench instances) accepted** in 0.37 s, synth2
(2 VUs x 3 steps) accepted in 0.34 s, the kernel-path and torch-path synth2 proofs identical.  Negatives: the 4 chain
cases (`broken_chain`, `false_overflow_flag`, `public_wrong_word`, `saturated_intermediate`) rejected 4/4 (linear
functional value mismatch / `LogUp T_OP level 1 round 0: sum mismatch`); the 52-case `vu-k1536-neg` set: 8 refused at
witness build (off-table keys), the 44 that produce proofs rejected **44/44** (`negatives` subcommand); bit-flip
mutations of the pos64 proof 786/786 rejected (sampled, every message class).  The 30 unit negatives are one-unit,
chainless instances (`gpu.run unit-negatives`): 17 refused by the prover, 13 rejected by the Python verifier; the Rust
verifier has no chainless-statement mode yet, so it has not seen those 13 (open item, small).

## Open items

1. **Re-record the a-gpu B = 4096 row from a committed tree with a Rust-verified proof file** (H100 needed; `main`'s
   prover is verified at B <= 512 on the 4090).  The a-gpu2 1.79 s record (tree 5ad05fb) is Python-verified only.
2. Verifier: 1.00 s is marginal on a shared pod; levers (i)-(iv) above.  Port of the linear test to the GPU is the
   big one.
3. v2: a chainless single-segment statement mode + `unit-negatives --proof-dir` for the 13 unit negatives; verify
   `lane/a-gpu-v2`'s B = 4096 proof when it exists (the v2 circuit has 10 lookup trees -- expect the fill to grow).
4. `fixtures/bench-instances/v1/*.u16` are untracked, so `research run --source .` cannot rebuild the statements on a
   fresh pod; the F1 scripts copy them from an earlier run's directory on vy-sp1.
