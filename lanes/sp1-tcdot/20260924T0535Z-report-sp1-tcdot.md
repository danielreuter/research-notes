CHECKPOINT 3510b39a7 (10:05Z) [open] HC6 art:b147a31c 5.631s (patch 0010: subnormals on chip, 0.86M cycles); HC7 art:2a4760fb 4.980s (0011 parallel tracegen); HC8 art:0a66c35e 4.258s (ET 2x, 4 chunks) = 4.66x vs stock SP1. verify-night handoff 0954Z. Tuning plateaued; wrapping up.
CHECKPOINT 0742a046 (08:42Z) [open] hill-climb 5 art:174d7b4d (runs art:ff5eaf2a): fork patch 0009 (prover-only local-memory merge, FORK_HEAD_WIT 6096d886), t.total 5.811s, 8 shards, 11.4MB: 3.41x faster than stock SP1's best (19.83s, sp1-table art:fffbf728). verify-night handoff 0841Z (build from the witness fork: vk does not pin the AIR). Next: the 74 software-routed VUs (2.45M of 3.74M cycles).
CHECKPOINT b189a963 (08:24Z) [open] hill-climb 4 art:76c113f4 (runs art:44bded3a): fork patch 0008 (operands from the input stream) + sp1-table k7 merged + two trace chunks, t.total 5.923s, 8 shards, 11.4MB: 3.76x faster than stock SP1's best (22.27s, art:1d6aa0c3). Next: patch 0009 (prover-only local-memory merge), screened 5.6s.
CHECKPOINT d3a5b955 (08:00Z) [open] hill-climb 3 art:a68f2446 (runs art:204f58d0): witness-operands arm (fork patch 0007 cbf66ccd, TC_DOT_BF16 operands as free witness values; coordinator asked 07:45Z), t.total 8.771s, 10 shards, 14.4MB. Building patch 0008 (operands from the input stream, never in memory).
CHECKPOINT 0b0768ed (07:26Z) [open] hill-climb 2 art:255f4f78 (runs art:4afa9f4e): fork patch 0006 (CPU-shard estimate fix + ELEMENT_THRESHOLD 1.25x), t.total 11.485s, 10 shards, 14.9MB, verify 0.61s; emitter now vector_run --variant (merged sp1-table b9b76e75). Next: verify-night addendum, next lever.
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
  - No AIR or verifier change. (Correction, 08:00Z: SP1's vk hash commits to the program, not to the chips. Patch
    0007 changed the TcDotBf16 AIR and the vk hash stayed `0x00b4876f…`, so only the verifier's fork head tells the
    arms apart.)
- **Hill-climb 2, `art:255f4f78…` (runs `art:4afa9f4e…`), source `64014888`, fork `d14b4c62`,
  `--prover-env ELEMENT_THRESHOLD=503316480` (1.25x).**
  - Same ELF and vk as hill-climb 1 (`70d03135…`, `0x00b4876f…`): patch 0006 does not touch the vk.
  - t.total 11.485 s (reps 11.47/13.47/11.38), 10 shards, 14.9 MB, verify 0.61 s, -96.7 after the union bound.
    Warm-up is one full B=4096 proof: the first 5e8-cell shard of a server's life can pay a one-time allocation of
    up to +3 s (screening rep 0: 14.9 s).
  - Rep 1's +2 s came from the CPU side: every pre-GPU step (executor start, splicing, splice serialization) ran
    1.5-1.7x slower, which is host contention, not the prover.
  - Screening, 2 reps each: the estimator fix alone gives 12 shards and 11.47-11.71 s.
  - The emitter is now `vector_run.py --variant` (merged sp1-table `b9b76e75`; `bench.py` writes
    `OUT/variant.json`).
- **Where the time goes now (rep 2).**
  - 0 to 2.3 s, GPU idle: CoreExecute setup 0.36 s, the minimal executor 0.33 s at 14.8 MHz, splicing the single CPU
    shard, 0.38 s serializing the 79 MB memory-read log, memory-shard emission (which starts only after all
    splicing), and 0.78 s of CPU tracegen for the first 500M-cell memory shard.
  - GPU busy for 8.7 s on 4.42G cells: 1.78 ns/cell plus about 0.09 s per shard.
  - About 0.35 s of host IPC.
  - This design is close to its floor. What remains is SP1's memory argument for the private operands (3.3G of
    4.4G cells), which no scheduling knob reaches.
  - Larger thresholds would not help: the first memory shard's CPU tracegen grows with it and delays the GPU start
    by about as much as the saved per-shard overhead.
- **verify-night (handoff `20260924T0710Z-handoff-from-verify-night.md`).** `art:90671b80…` is `verified=accepted`
  (verdict `art:4bfc9e7e…`, same_device=false), independently built from `572018a3`. The fork tree reproduced, and so
  did the vk (`0x00347dc9…`). The ELF digest did not (`8f681770…` vs `01dbe1d9…`): the vk hashes only the loaded
  program image, so the difference sits in non-loaded sections, most likely debug-info paths of the fork checkout,
  which `host/build.rs` does not remap. My 06:55Z handoff's "a different ELF means a different vk" was wrong;
  corrected in `lanes/verify-night/20260924T0727Z-handoff-from-sp1-tcdot.md`, which also asks for `art:255f4f78…`.
  Fix for future builds: also remap the fork checkout's canonical path in `host/build.rs` (not done, since it would
  change nothing verified here).
- **Witness-operands arm (decision asked of the coordinator: `lanes/coordinator/20260924T0745Z-handoff-from-sp1-tcdot.md`).**
  - The bare statement is existential in x and W, so SP1's memory argument for the 25 MB of operands adds no
    soundness to it. It is also 76% of the cells.
  - Fork patch 0007 (`sp1-patches/witness-operands/`, `build_fork.sh OPERANDS=witness`, pin `FORK_HEAD_WIT`
    `cbf66ccd`, tree `dc7b3cbd`) makes TC_DOT_BF16's operands free witness values. Both executors read them with
    `mr_slice_unsafe` (no memory event, no page-prot check), and the event carries them as `ab_words`.
  - The chip drops the 8 operand address, memory-read and page-prot columns and the equality between the decode and
    the read words: 1262 to 1166 cells per row.
  - Each limb stays fully determined by its range-checked decode `2^15 s + 2^7 ef + m`. A row therefore proves
    `D = C + A.B` for the operands its decode holds. A proof shows the accumulator chain is reachable from some finite
    BF16 operands, which is exactly relation-bare. It is not sound for a statement that authenticates x and W.
  - The patch reproduces commit and tree under `git am --committer-date-is-author-date`. The executor unit tests, all
    9 chip tests (BF16 prove plus every negative tamper, fp8 unchanged) and cost/complexity consistency pass.
  - The guest and ELF are unchanged. Execution gives the same public values, --flip-y returns false, and 52/52
    negatives are rejected.
  - The arm is separate: the memory arm's pins, patches and backend name are unchanged. `bench.py` takes the arm
    from the host's fork pin and records its operand binding (`fork.operands`, "witness operands" in the backend
    name).
- **Hill-climb 3 (witness arm), `art:a68f2446…` (runs `art:204f58d0…`), source `d3a5b955`, fork `cbf66ccd`,
  ELEMENT_THRESHOLD 503316480.**
  - t.total **8.771 s** (reps 8.92/8.73/8.75), 10 shards, 14.4 MB, -96.7 after the union bound. That is 1.31x faster
    than the memory arm (11.485 s) and 3.4x faster than stock SP1 (29.91 s).
  - A 1.5x threshold crashes the GPU tracegen (`global.rs:127` "invalid configuration argument": Global rows exceed
    a kernel launch limit), so 1.25x is the ceiling.
  - Per shard: 4 memory shards (1.72G cells, the hint init/finalize of the operands, which still sit in memory) take
    2.6 s; 1 CPU shard 0.63 s; 5 precompile shards at 0.48 s each (TcDotBf16 1166 x 84544 plus 3 Global rows per call
    for the accumulator and the syscall); and 2.6 s before the first shard.
  - Next: fork patch 0008, where the executor takes each step's operands from the input stream, so they never enter
    memory (guest and host `stream-operands` feature).
- **Fork patch 0008 (`sp1-patches/witness-operands/0008`, fork `e3756374`, tree `5f05843c`).** TC_DOT_BF16's
  64 operand bytes per step are the next stdin buffer. The minimal executor pops the buffer and `trace_value`s its 8
  words, and the tracing executor replays them. The chip is unchanged from 0007.
  - The guest and host feature `stream-operands` lays the input out accordingly: a chip VU is 96 step buffers, and a
    VU routed wholly to software is one stock-layout buffer. The host's `info` reports `operands: stream`, and
    `bench.py` refuses a host whose layout does not match the arm.
  - The patch reproduces commit and tree under `git am`. The executor unit tests and all 9 chip tests pass (the BF16
    prove test now feeds its operands through stdin). Execution gives the same statement digest `5e0dd245…`,
    --flip-y returns false, and 52/52 negatives are rejected.
  - Effect: the four memory shards (the hint init/finalize of 25 MB of operands) are gone, and cycles fall from
    4.91M to 4.41M.
- **Where the time went next (1.25x, one trace chunk): 7.3-8.0 s.** The GPU was busy for 3.3 s of 7.0. All 4.4M
  cycles formed one minimal-trace chunk (default 16.7M entries), so one CPU shard's record (2.1 s single-threaded
  replay) gated everything. The precompile shards need its deferred events.
  - `MINIMAL_TRACE_CHUNK_THRESHOLD=2500000` (an SP1 env option; `local_gpu_opts` keeps it) gives two chunks. A
    chunk end closes its shard, so the two CPU shards build their records in parallel on the core workers:
    6.0 s.
  - Four chunks with four splicing workers (6.0 s) and eight (6.4 s) are no better, and three with three
    workers varies (5.6 / 7.0 s).
- **Merged sp1-table `a66c257b` (kernel k7) as `058d5fc8`.** The 74 VUs routed wholly to software run k7, cutting
  cycles from 4.41M to 3.74M (new ELF `525841da…`, vk `0x00896ef4…`, same statement). The merged vector_run passes
  `--layout chunks`, which the tcdot host now accepts (`b189a963`; chunks only). Its first registration attempt
  failed at the negatives on that flag, so no result was produced.
- **Hill-climb 4, `art:76c113f4…` (runs `art:44bded3a…`), source `b189a963`, fork `e3756374`, prover env
  ELEMENT_THRESHOLD 503316480 + MINIMAL_TRACE_CHUNK_THRESHOLD 2500000 (recorded as `prover_options`).**
  - t.total **5.923 s**, 8 shards, 11.4 MB, -97.0 after the union bound; 52/52 negatives; every proof verified.
  - 1.48x faster than hill-climb 3 (8.771 s) and **3.76x** faster than stock SP1's best
    (`art:1d6aa0c3`, k4 + indexed, 22.27 s).
  - Per proof: 1.2 s before the first shard (0.4 s setting up the minimal executor, 0.3 s executing, splicing); a
    1.0 s GPU gap while the two CPU shards build their records; CPU shards 0.8 s; 5 precompile shards 2.3 s.
- **Fork patch 0009 (`sp1-patches/witness-operands/0009`, fork `6096d886`, tree `136b65c4`; prover only).**
  - Each precompile call's event carries a MemoryLocalEvent for its accumulator word. Each became a MemoryLocal row
    and 2 Global rows: 2 of the 3 Global rows per call, and 37% of a precompile shard's cells.
  - A VU's 96 calls touch that word one after another, so inside a shard each call's first access is the previous
    call's last. The calls' own memory interactions already chain, as repeated accesses within a CPU shard do.
  - When the prover builds a TC_DOT_BF16 precompile shard's record, it sorts the local accesses by (address,
    initial timestamp). It folds each access whose initial record equals the running final record into one event
    per run.
  - No chip, executor or verifier change: a wrong merge would unbalance the memory bus, and the proof would not
    verify.
  - Precompile shards shrink from 163.8M to 121.8M cells (Global 253,632 to 86,336 rows). Screened at 5.61 / 5.69 s
    with the same config, against 5.95 / 5.93 s without the patch.
  - The patch reproduces under `git am`. The ELF and vk are unchanged; 52/52 negatives rejected.
- **Screens that lost (patch 0009, two chunks).**
  - ELEMENT_THRESHOLD 1.5x (a 5k-call runt plus three 127k-call precompile shards): 6.09 / 5.93 s.
  - 3x (two precompile shards of 165k and 221k calls): 7.2 / 6.8 s. TcDotBf16's trace is CPU-generated in the
    server (no GPU tracegen for the new chip), so big precompile shards stop overlapping with proving.
  - The old 1.5x crash was the Global transpose kernel's grid-y limit (Global rows / 32 <= 65535, i.e. 2.1M rows
    per shard), which only the witness arm's memory shards reached.
  - `SP1_WORKER_USE_FIXED_PK=true` (the pk cache plus the minimal-executor cache) panics in the cached executor's
    child on the second input, so it was dropped.
- **Hill-climb 5, `art:174d7b4d…` (runs `art:ff5eaf2a…`), source `0742a046`, fork `6096d886` (patch 0009), same
  guest, vk and prover env as hill-climb 4.**
  - t.total **5.811 s** (reps 5.72-5.83 s, against 5.84-5.99 s for hill-climb 4), 8 shards, 11.39 MB, -97.0;
    52/52 negatives; verify 0.47 s.
  - **3.41x** faster than stock SP1's best, sp1-table's k7 `art:fffbf728` (19.83 s, 22 shards, 33.5 MB).
  - Rate: 4096 x 1536 MACs / 5.811 s = 1.08M MAC/s (2.17 MFLOP/s). Overhead vs 312 TFLOP/s: 1.44e8x.
  - The screens (5.61 / 5.69 s) were 0.1 s optimistic: the gain over hill-climb 4 is 2%.
  - verify-night handoff `20260924T0841Z` covers hill-climbs 5 and 4 (and 3). The verifier must be built from the
    witness fork, because the vk does not pin the chips' AIR.
- **Harness.** A finished run leaves `/tmp/sp1-cuda-0.sock`. The next client connects to the stale file before its
  new server rebinds and fails with ECONNREFUSED; about every second screen failed this way. `quick.sh` and
  `bench_run.sh` now wait for the last server to exit, then remove the socket.
- **Fork patch 0010: TC_DOT_BF16 constrains subnormal GroupSum outputs (witness arm, fork `0e00bd15`, tree
  `fe0715de`).**
  - Before this, a GroupSum output below the fp32 normal range was outside the chip's contract, so the guest ran the
    step in software, and a VU with 8 or more such steps ran whole in software. That was 74 VUs and 2.45M of 3.74M
    cycles.
  - The reference (`tc::group_sum`) denormalizes: one truncating shift of the aligned sum by k = e_max + 125
    (in [-7, 22]) to exponent -126. The result is zero if nothing survives.
  - The chip reuses its bit-length one-hot for that shift. The new columns (+7, 1166 to 1173 per row) are an is_sub
    flag pinned to e_max + 125 = k, a k = -7 selector, and a nonzero flag checked by a range lookup on the bit count.
    A normal output cannot take this path and a subnormal one cannot take the normal path (range checks on e_out).
    A denormalized D packs with exponent field 0, and a D that truncates to zero packs as +0.
  - The fp8 TC_DOT AIR is unchanged.
  - Tests: 9/9 chip tests pass, including new reference values (2^-130, a chained subnormal accumulator, a negative
    sum that truncates to +0) and the CPU prove test with those tiles. Eight new negative tests tamper with the
    denormalized path, and all are rejected.
  - Routing on the frozen set: 64 of 393,216 steps are left in software (42 G1 and 22 D overflows, one per VU), and
    no VU runs whole in software. Guest cycles fall from 3.74M to 0.86M.
  - The host crosscheck finds 0 kernel mismatches against `tc::tc_dot` over all 393,152 chip steps. The ELF and vk
    are unchanged (again: the vk does not pin the chips' AIR).
- **Hill-climb 6, `art:b147a31c…` (runs `art:ee9b4fdf…`), source `ca647373`, fork `0e00bd15` (patch 0010), step 5's
  prover env (ELEMENT_THRESHOLD 1.25x, MINIMAL_TRACE_CHUNK_THRESHOLD 2.5M).**
  - t.total **5.631 s** (reps 5.60-5.72 s), 8 shards, 11.35 MB, -97.0; 52/52 negatives; verify 0.49 s.
  - 3.52x faster than stock SP1's best (19.83 s). Rate: 1.12M MAC/s (2.23 MFLOP/s). Overhead vs 312 TFLOP/s: 1.40e8x.
  - Only 3% for 4.3x fewer cycles, because the timeline is not bound by the guest. The five TcDotBf16 shards
    (0.44 s each on the GPU) start only 1.2 s after the CPU shards that defer their events.
  - Screen that lost: MINIMAL_TRACE_CHUNK_THRESHOLD 440k (two chunks) gives 12 small CPU shards at about 0.2 s fixed
    cost each, 17 shards in all: 6.05 s. The precompile shards still wait for the CPU shards.
- **Next (patch 0011, prover only).** TcDotBf16's trace is generated sequentially (one of the pod's 128 cores). With
  no `generate_dependencies` override, the default builds the whole trace a second time just to count byte lookups.
  Both passes sit between a precompile shard's events and its GPU proof. The patch follows ShaExtend's pattern:
  `par_chunks_mut` rows, and lookups counted over `par_chunks` of events into per-thread maps. Trace values,
  multiplicities, AIR and verifier are unchanged.
- **Fork patch 0011 (prover only), fork `6655716e`, tree `4ca5a6ca`: TcDotBf16's trace and byte lookups generated in
  parallel (ShaExtend's pattern).**
  - 5/5 chip tests pass, including the CPU prove test, which checks the lookup multiplicities end to end. The host
    checks are unchanged: 0 kernel mismatches, flip-y rejected, 52/52 negatives rejected.
  - The first precompile shard now reaches the GPU at +2.7 s instead of +3.2 s, right behind the CPU shards.
- **Hill-climb 7, `art:2a4760fb…` (runs `art:4b3dc262…`), source `97b5b60a`, fork `6655716e`, step 6's prover env.**
  - t.total **4.980 s** (reps 4.95-4.97 s), 8 shards, 11.35 MB, -97.0; 52/52 negatives; verify 0.49 s.
  - Rate: 1.26M MAC/s (2.53 MFLOP/s). Overhead vs 312 TFLOP/s: 1.24e8x.
- **Screens on 6655716e (reps 0 / 1).** With parallel tracegen, bigger precompile shards now win. A shard costs about
  0.25 s fixed plus 1.5 ns per cell on the GPU. More trace chunks, with as many splicing workers, get the CPU shards'
  records out sooner.
  - ELEMENT_THRESHOLD 1.25x, 2 chunks: 5.01 / 4.90 and 5.05 / 4.88 s (8 shards).
  - 1.5x, 2 chunks: 4.88 / 4.64 s (7 shards).
  - 2x, 2 chunks: 4.45 / 4.35 s (6 shards: 3 precompile shards of at most 135k calls, 8.59 MB).
  - 1.25x, 3 chunks, 3 splicers: 4.76 / 4.62 s (9 shards).
  - 2x, 3 chunks, 3 splicers: 4.21 / 4.26 s (7 shards).
  - **2x, 4 chunks, 4 splicers: 4.22 / 4.12 s (8 shards).**
  - 2.34x (2 precompile shards), 3 chunks: 4.68 / 4.21 s. With 4 chunks: 4.55 / 4.29 s. With 2 chunks: the client
    missed the new server's socket (harness race, not a prover limit).
  - 4.67x (one 393k-call precompile shard), 2 chunks: 6.94 / 5.18 s. Nothing overlaps its tracegen.
