CHECKPOINT none (07:08Z) [open] hill-climb 1 art:6e415853 (runs art:a965d150): guest chains each VU's 96 TC_DOT_BF16 ecalls in one asm block, 4.91M cycles (was 8.04M), t.total 11.946s, 16 shards. Building fork patch 0006 (sharding estimate + ELEMENT_THRESHOLD).
CHECKPOINT 572018a3 (06:54Z) [open] B=4096 A100 result art:90671b80 (runs art:d9a862c5): t.total 12.763s, 17 shards, 2.34x faster than stock SP1 art:2a10bc89; verify-night handoff written; sp1-table 06:40Z: adopt --variant at next rebase. Next: hill-climb (shard threshold, guest loop).
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

- **05:30Z scope (coordinator handoffs 0528Z/0530Z).** TC_DOT must eventually cover all five targets. A100 BF16 first,
  with the chip parameterized, not copied. Budget $25. The emitter is `vector_run.py` (one SP1 emitter).
- **TC_DOT_BF16 (fork patches 0004-0005, FORK_HEAD `fe35cc50`, tree `6d55145f`).** A `TcPipeline` parameter
  (`floor_clamp`, `g1_overflow_check`) shared by `TC_DOT` (fp8) and the new `TC_DOT_BF16`. The new chip does one
  tc-ampere-bf16 m16n8k16 step per call: K=16 BF16 products, groups [8,8], 25-bit adder, floor -132, truncation.
  Operand contract: finite operands and accumulator, and both GroupSum outputs zero or fp32-normal. Contract
  violations are enforced by the AIR, not only by the witness generator. `try_tc_dot_bf16_witness` lets the host
  route out-of-contract steps to software. The chip's unit, prove and negative tests pass on the A100 pod.
  Op-bench repro (fp8 fork, batch2048 x 2048): 21,033,942 cycles (= the original run), 34.75 s on the A100 (4090
  original: 40.59 s, 66 shards).
- **Guest (relation-bare/v2, rebased on sp1-table b5e1ed5f).** Same statement and public values as stock SP1, byte for
  byte. A bf16-ampere VU chains 96 `syscall_tc_dot_bf16` calls. Out-of-contract steps run `tc::tc_dot` in the guest,
  and a VU with >= 8 such steps runs `bare::check_one` whole. Crosscheck of all 393,216 steps: 0 kernel mismatches.
  Routing: 386,043 chip steps, 69 software steps, and 74 whole-software VUs. Contract violations: 5500 subnormal_g1,
  61 subnormal_g2, 42+22 overflow. 52/52 negatives rejected, 44/44 correct accepted; `--flip-y` rejects.
  Threshold sweep, execute only: any threshold from 3 to 48 gives the same 8.04M cycles (VUs have 0-2 or 48-96
  violations); 1 gives 11.4M and 97 gives 11.6M.
- **06:40Z baseline `art:90671b80…` (runs `art:d9a862c5…`).** B=4096 on the A100: t.total 12.763 s (prove 12.736 +
  serialize 0.027; reps 12.74/12.41/12.75). 17 shards, 24.9 MB, 8.04M cycles, verify 1.02 s. 986k FLOP/s = 493k
  MAC/s, overhead 3.16e8x vs 312 TFLOP/s. Stock SP1 on the same statement is `art:2a10bc89…` (sp1-table): 29.91 s,
  36 shards, 218M cycles, 7.4e8x, so this is **2.34x faster**. Validation passed and the contract conforms. Table 2
  excludes it on security (-100 target, -95.9 after the union bound over 17 shards), as it does stock SP1. First
  registered as `art:abfebfe7…` with result.json as a payload, which bench.tables does not read; re-registered with
  meta = the result document (store README §10) and the old id labelled superseded_by. Handoff:
  `lanes/verify-night/20260924T0655Z-handoff-from-sp1-tcdot.md`.
- **Where the 12.7 s goes (per-chip cells, 4.52G total).**
  - Global chip (SP1's cross-shard memory argument, 241 columns) = 76%: 7.33M rows in precompile shards and 6.32M in
    memory shards. Every private operand word (3.15M, 25 MB) costs about 4 Global rows, 1 MemoryLocal, 1
    MemoryGlobalInit and 1 MemoryGlobalFinalize, about 1,040 cells per word. `TC_DOT_BF16` rows are 10.8%, CPU
    about 12%.
  - Hint-read input lands in fresh memory, so the CPU shards never touch operand words. Keeping chip events in CPU
    shards would therefore save nothing, and the memory floor (about 3.0G cells) is intrinsic to SP1 6's memory
    design.
  - Timeline: the executor starts at 0.43 s and finishes at 0.77 s. The first CPU shard is re-executed for events
    (about 0.8 s for 1.6M cycles). The GPU permit is then held 99% of the time from 1.72 s to 12.29 s, one shard at
    a time: 0.27 s per CPU shard of about 95M cells, 0.76/0.84 s per memory/precompile shard of about 402M cells,
    and 0.17 s for a 7.8M-cell shard, i.e. about 0.15 s fixed per shard. The first big shard of every proof costs
    +0.43 s.
- **Knobs checked.** The `ELEMENT_THRESHOLD` env has no effect: the GPU server's `local_gpu_opts()`
  (sp1-gpu/crates/prover_components/src/builder.rs) hard-sets `element_threshold = ELEMENT_THRESHOLD`
  (2^28+2^27 cells) for GPUs over 30 GB and sizes the trace buffer to match (screening run: 17 shards, 12.52/12.36 s).
  CPU shards stop at about 95M real cells because `ShapeChecker::handle_mem_event` charges each deferred
  precompile's fresh operand read as a local access (MemoryLocal + 2 Global, about 4,000 cells per call) to the CPU
  shard that issues it.
- **Hill-climb 1, `art:6e415853…` (runs `art:a965d150…`), source `9491f177`, fork unchanged (`fe35cc50`).** A chip VU
  now chains its 96 steps in one unrolled `asm!` block (`ecall; addi a0, a0, 64`). This relies on TC_DOT_BF16
  returning no value: the executor writes the syscall code back to t0 (`minimal/ecall.rs` `unwrap_or(code)`) and
  never writes a0/a1. The routing masks are now two aligned u64 words per VU. Cycles 8,036,335 -> 4,907,869, with
  identical public values; flip-y rejects, 52/52 negatives are rejected and 44/44 correct words accepted. New ELF
  `70d03135…`, vk `0x00b4876f…`. t.total 11.946 s (reps 11.92/11.64/11.93), 16 shards, 23.4 MB, -96.0 after the
  union bound.
- **Fork patch 0006 (FORK_HEAD `d14b4c62`, tree `3b8e553b`, prover scheduling only).**
  - `ShapeChecker::handle_mem_event` no longer charges deferred-precompile accesses to the CPU shard.
    `syscall_sent()` is set only for non-retained syscalls (`splicing.rs` `execute_ecall`), and their rows are in
    the precompile shard. The estimate stays an upper bound on the CPU shard.
  - `local_gpu_opts` honours `ELEMENT_THRESHOLD` when it is set. The 4 pinned trace buffers and the LDE (4x area)
    scale with it, so stay under 2^31 LDE elements, i.e. an area of at most about 5.3e8.
  - No AIR or verifier change: the vk depends only on the ELF and the chips.
