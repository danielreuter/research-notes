CHECKPOINT none (06:30Z) [open] B=4096 A100 prove 12.2s/17 shards (v1 stmt; 72% of cells = SP1 memory argument for the 25MB private input). Porting to relation-bare/v2 (rebased on sp1-table b5e1ed5f), emitter = vector_run.py sp1-bare via tcdot/bench.py wrapper; next: register result.
CHECKPOINT edf1fb4 (06:05Z) [open] TC_DOT_BF16 chip (fork patches 0004-5, tree 6d55145f) passes prove+negative tests on A100 pod; op-bench batch2048 repro 21,033,942 cycles = orig, 34.75s A100 (4090: 40.59s). Building tcdot host; next: crosscheck/execute/negatives, then B=4096 prove.
CHECKPOINT 0b0768ed (05:25Z) [open] TC_DOT = fp8-E4M3 operands in Ampere BF16 pipeline (K=16/call), not tc-ampere-bf16: cannot prove the A100 BF16 statement as-is. Building fork (v6.4.0+3 patches) + GPU server on A100 pod 4haxoz642k8ho1; next: BF16-operand chip variant.
# sp1-tcdot report (campaign morning-tables)

Lane: `sp1-tcdot`, branch `lane/sp1-tcdot` in `~/projects/verity-main-wt/sp1-tcdot`, base main @ 0b0768ed.
Pod: `vy-tcdot-a100` = `4haxoz642k8ho1` (NVIDIA A100-SXM4-80GB, reference part, 13.6-CPU cgroup, 2 TB host RAM view, $1.39-1.59/h), created 05:27Z.
Budget $12, FINAL 12:00Z.

## Findings before any build (sources read-only)

- **SP1 version.** The fork `~/projects/sp1` branch `tc-dot-precompile` is upstream succinctlabs/sp1 `f66b4bff5`
  ("ci(release): install CUDA setup prerequisite (#2937)", 2026-08-12) = tag **v6.4.0** (workspace version 6.4.0,
  `git describe` v6.4.0), plus three commits: `c31643e8f` reference kernel, `fb4a0a253` syscall/executor/event/guest stub,
  `3510b39a7` AIR chip + RiscvAir registration + cost artifacts + tests (22 files, +2100/-8).
- **What TC_DOT computes.** One 16-element tile step `D = C + A.B` with **fp8 E4M3 operands** (16 bytes A, 16 bytes B)
  and an fp32 accumulator, through the **Ampere BF16 pipeline**: exact products, `G1 = GroupSum({C, P1..P8})`,
  `D = GroupSum({G1, P9..P16})`, 25-bit adder, truncating alignment and normalisation, exponent floor -132.
  K = 16 per call; a length-n dot chains n/16 calls. The fork's own header: "real fp8 tensor cores exist only on Hopper
  (QGMMA) with different constants; this 'fp8 Ampere' contract is the bf16 Ampere pipeline fed with fp8 products."
  So its semantics are **no Verity target**: not `tc-ampere-bf16` (FIRST, BF16 operands), not `fp8-ada-mma`
  (two groups of 16, 14-bit adder, floor -139). Operand contract (witness generation panics outside it): finite
  E4M3 bytes, finite C, no subnormal stage output, no fp32 overflow. Syscall `0x00_01_01_36`,
  `syscall_tc_dot(ab: *const u8 /*32 B*/, c: *mut u64)`.
- **Consequence for the A100 BF16 cell.** TC_DOT as committed cannot prove the Table 2 statement. The pipeline half of
  the chip (GroupSum, shift gadget, normalisation, pack) is exactly FIRST's step (`backends/sp1/common/src/tc.rs`:
  groups [8,8], width 25, floor -132, truncation); what differs is the operand decode (BF16: 8-bit exponent,
  8-bit significand, 16-bit products `<< 9` instead of 4-bit `<< 17`), the exponent range (products down to 2^-252, so
  the -132 floor can clamp with nonzero terms), and FIRST's subnormal stage outputs and saturation, which the fork
  contracts out. Plan: a BF16-operand variant of the chip as an additional patch on the fork (same pipeline gadgets).
- **How the 911k MAC/s number was produced.** RTX 4090 (RunPod `59wds7p5ycje9q`), **forked `sp1-gpu-server`** built from
  `tc-dot-precompile` (`cargo install --path sp1-gpu/crates/server`; the server is generic over chips: CPU `MachineAir`
  trace generation for non-global chips, the zerocheck prover compiles each chip's Rust AIR to bytecode), so the GPU
  path **did prove the chip**. Core proofs, zero-copy layout, n = 16384 per dot, k = 16384 dots per proof: 268M MACs,
  168M cycles, 519 shards, 748 MB proof, prove_s 294.55 s median of 3 (setup ~19 s excluded; verify 33 s):
  `results/gpu-run/gpu_zerocopy_repeats.csv`, commit `edf1fb4`. Core mode only: the recursion vk map was not rebuilt,
  so compressed/Groth16 proofs over TC_DOT programs would fail vk membership.
- **Soundness tests.** `test_tc_dot_negative_soundness` tampers seven witness cells of a real trace (result sign,
  result mantissa bit, stage-2 e_max+1, product nz=0, a product significand bit, a shift selector, the packed exponent)
  and asserts `debug_constraints` rejects each; `test_tc_dot_prove_core` proves and verifies a 3-call program. They
  exercise the chip's constraints, but by targeted tampering, not exhaustively: the claim is "unique witness per
  in-contract input by constraint review + 7 negatives", not a proof. NaN operand bytes are excluded by the witness
  generator, not by the AIR; out-of-contract behaviour of the AIR is unconstrained/unreviewed. The user-mode
  (`TcDotUser`) chip is never exercised end to end.
- CL10 (veritor claim register): the TC_DOT numbers are a `modified` backend, the native-semantics arm; nothing
  unmodified rests on them.

## Log
