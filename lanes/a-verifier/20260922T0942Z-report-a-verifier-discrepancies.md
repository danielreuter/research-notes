---
id: r20-proof/a-verifier/20260922T0942Z-report-a-verifier-discrepancies
campaign: r20-proof
lane: a-verifier
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/a_verifier_discrepancies.md
---

# a-verifier: where the independent Rust verifier and the a-gpu Python verifier disagree

Lane `a-verifier` (track A), 2026-09-22.  The verifier is `backends/gkr/verifier/` (`verity-gkr-verify`, no
dependencies: its own BabyBear^6 over X^6 - 31, SHA-256, NTT, `proof.bin` parser, GKR / LogUp / Ligero checks),
written from `backends/gkr/gpu/README.md` + `PROTOCOL.md` and the a-gpu Python source, sharing no code with it.
Every proof below was produced by the a-gpu prover on `vy-g5` (H100) and checked by both verifiers.

## Findings

### F1. The a-gpu Triton-kernel path currently produces proofs that BOTH verifiers reject (prover bug, not a verifier one)

`python -m gpu.run prove /workspace/bb/pos4096 --device cuda` (the configuration of the recorded 4.43 s ledger row,
r20260922-074455-d0b6, tree c4d472a) now yields a proof that the Python verifier rejects with
`LogUp level 0: final check` and the Rust verifier rejects with `LogUp POW level 0: final check`, at B = 2 (synth),
64 and 4096, deterministically (runs r20260922-084329-7c80, -085845-2a26, -090318-2864, -091240-4bf9), and at the
a-gpu lane's own recorded tree c4d472a with its own `PYTHONPATH` (r20260922-091831-ef04, -092229-641b).  With
`VERITY_GPU_TORCH_ONLY=1` (every kernel replaced by its torch reference) the same command produces proofs both
verifiers accept (B = 64: r20260922-090318-2864; B = 4096 x 3 reps: r20260922-091240-4bf9, prover 24.9-27.1 s,
Python verifier 9.7-9.8 s).

The level-0 check is `lambda * q_root == p0 q1 + p1 q0 + lambda q0 q1` at the root of the POW table's fractional-sum
tree, i.e. the committed numerator `sum m_i/(t_i + z) - sum 1/(q_j + z)` is not zero: the kernel path's
multiplicities / leaf build (`_fast_phase1`, `_fast_combine_level`, `_fast_scatter`) disagree with the torch path
for the first table.  Two verifiers written independently reject the proof at the same place, so this is a prover
fault.  The recorded 4.43 s run verified at 07:44Z on the same pod and tree.  Two more facts (r20260922-092229-641b):
the pod's tar-synced working copy `/workspace/verity/backends/gkr/gpu` -- **newer than any commit** (09:20Z, adds
`gkr_packed.py`, `logup_packed.py`, `eq_outer` / `split_limbs` kernels; someone is developing there) -- produces a
B = 64 kernel-path proof the Python verifier accepts (36.9 s with kernel compilation); and `nvidia-smi` shows a
process from another container (pid 3709632) holding 79.3 GB of the H100's 80 GB.  So the committed kernel path
fails on this pod today while an uncommitted newer one passes; whether the committed code has a latent race that the
newer copy fixed, or a Triton cache (`~/.triton/cache`, 223 entries) keyed identically for changed helper kernels is
serving the wrong binary to the old tree, is for the a-gpu lane to settle -- **commit the working copy and re-record**.
**Consequence for the ledger**: the 4.43 s prover row is not reproducible from any commit as of 09:20Z; the
reproducible GPU prover today is the torch path at ~25 s.  The e2e numbers are given for both.

### F2. `proof.bin` did not exist

`gpu/README.md` documented the transcript and the in-memory `Proof` (root, messages, opening) but no serialisation;
the a-gpu lane never wrote a proof to disk (its verifier ran in-process).  This lane added `Proof.to_bytes /
from_bytes` and the README "Proof file" section (self-delimiting little-endian; every count is *checked* against the
statement by the verifier, none is *used* to size anything).  Not a disagreement, but the reason no independent
check existed.

### F3. Statement binding is by the circuit files, not the manifest

The Rust verifier takes the chain columns (`x.c_lo/hi`, `y_lo/hi`, `y32_lo/hi`, `y16`) by *name* from
`circuit.txt` / `epilogue.txt`; the Python `load_instance` takes their indices from `manifest.json["chain"]`.  Both
absorb the same circuit text digest, so a manifest that points at other columns would make Python accept a proof of
a different statement than the one the circuit text describes.  Not exploitable by a prover (the manifest is the
verifier's own input) but a footgun: the manifest's `chain` block should be checked against the names.

### F4. Reported `slots` differ run to run

`gpu.run` reports `slots` (rounds.protocol) 1920 at B = 4096 and 1246 or 1247 at B = 64 for different proofs of the
same statement: Ligero's `open_set` redraws on a duplicate column index, so the count is proof-dependent (expected
excess ~ t^2 / 2n = 1.1).  The Rust verifier's `slots` agrees with Python's for every proof both accepted.  The
depth 438 the latency lane uses does not depend on it.

### None otherwise

Every proof the Python verifier accepted, the Rust verifier accepted (synth B = 2, B = 64, B = 4096); every proof the
Python verifier rejected, the Rust verifier rejected at the same check (the kernel-path proofs at LogUp POW level 0;
the 44 negatives at `epilogue/assertions phase-2a: round 0 sum mismatch`).

## Results

| B | proof | accepted | negatives rejected | mutations rejected | verify s 1T | verify s 12T | peak RSS | run |
|---|---|---|---|---|---|---|---|---|
| 2 (synth) | 0.43 MB, 723 slots | yes | - | 356/356 (sampled) | 0.04 (laptop) | - | - | r20260922-084329-7c80 |
| 64 | 1.00 MB, 1246 slots | yes | 44/44 (B = 1 each) | 16485/16485 (exhaustive) | 0.594 | 0.109 | 24 MB | r20260922-093721-1330, -092943-2a5a, -092101-c618 |
| 4096 | 33.87 MB, 1920 slots | yes | - | 52/52 (sampled) | 34.0 | 3.00-3.02 | 103 MB | r20260922-093721-1330 |

vy-cpu2 (EPYC 9654, 12 of 32 threads, the b-air-v2 lane running alongside, load ~23; `-C target-cpu=native`).  Python
verifier on the same B = 4096 proof: 9.7-9.8 s (torch on the H100); the Goldilocks Rust verifier row of note:r20-proof/latency/20260922T1111Z-report-latency:
45 s.  Time split at B = 4096 (CPU-seconds, 12T): parse 0.03, transcript replay 0.006, functional value 0.12, Merkle +
proximity 0.03, the Ligero linear test 2.8 s wall = fill of `a` 14.8 + row NTT evaluation 18.3 CPU-s (43417 rows x
(one inverse NTT_4096 + up to three twisted forward NTT_4096)).  A planar/base-field NTT layout was 1.8x slower on
both machines than the interleaved six-lane butterfly; a u64 (instead of u128) extension multiply was slower on the
laptop and not measured on the pod.

Mutation reasons (B = 64 exhaustive): 12548 `ligero: merkle path` (every flip of a transcript-absorbed message or of
`w` / `q` moves the opened set; every root / sibling / column flip breaks a path), 3118 LogUp round or final checks,
95 GKR (`assertions phase-2a/2b`, `depth`), 2 `linear functional value mismatch`, 1 `non-canonical column value`,
the rest at parse (`message count`, `opening`).

## A-GPU end-to-end with this verifier (B = 4096, `prove + verify + 438 x RTT + 33.9 MB / 10 Gb/s`)

| prover | RTT 0 | 1 ms | 10 ms | 50 ms | verifier share (RTT 0) |
|---|---|---|---|---|---|
| recorded kernel path 4.43 s (r20260922-074455-d0b6; not reproducible today, F1) | 7.47 s | 7.91 | 11.85 | 29.37 | 40% |
| reproducible torch path 25.5 s (r20260922-091240-4bf9) | 28.53 s | 28.97 | 32.91 | 50.43 | 11% |
| for comparison, same model: 4.43 s + the Python verifier 7.1 s | 11.6 | 12.0 | 15.9 | 33.5 | 62% |
| for comparison, same model: 4.43 s + the Goldilocks Rust verifier 45 s | 49.5 | 49.9 | 53.8 | 71.4 | 91% |

Envelopes for `benchmarks/latency_compare.py`: `backends/gkr/verifier/results_e2e_{kernel,torch}.json`
(`rounds.sequential_depth` 438, `rounds.protocol` 1920, `verifier.seconds` 3.017).  Verifier `overhead`: 0.736 ms/VU
= 7.5e7 x native; the "hypothetical 1 s verifier" row is not reached (3.0 s; single-thread 34 s).

## Open

* < 1 s at B = 4096 needs ~3x on the linear test: a pruned forward NTT (only ~64 of 4096 outputs per coset are
  used, ~1.7x on 3/4 of the NTT work), AVX-512 lanes for the Montgomery butterflies, and a cheaper `eq` flush in
  the per-unit scatter (400 extension multiplies per unit for R16).  Or run it on the prover's GPU: the linear test
  is 43417 independent rows (embarrassingly parallel); the 1920 transcript slots are sequential but cost 6 ms in total.
* checker v2 (`a-v2`, PROTOCOL.md §14): not started -- the circuit parser and the functional are generic over the
  circuit text, so it is the v2 gate types / query layout that need adding, not the Ligero or transcript side.
* The manifest `chain` block (F3) should be cross-checked against the column names by the Python `load_instance`.
