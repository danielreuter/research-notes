# SP1 prover (6.4.0 GPU server): measured facts and gotchas

Sources: lane sp1-tcdot report (`lanes/sp1-tcdot/20260924T0535Z-report-sp1-tcdot.md`), `lane/sp1-tcdot` commits, SP1
v6.4.0 source (`f66b4bff5`).

## Custom chips
- Succinct's release `sp1-gpu-server` only knows stock chips. A forked chip needs the server built from the fork. The
  server is generic over chips: CPU `MachineAir` tracegen for non-global chips, and the zerocheck compiles each chip's
  Rust AIR.
- Build the fork's server with `cargo install --locked --path sp1-gpu/crates/server` and `CUDA_ARCHS=80` (A100; 89 =
  4090). Put `/usr/local/cuda/bin` in PATH and set `CUDACXX`, or CMake fails with "Failed to detect a default CUDA
  architecture".
- After a failed configure, delete `target/release/build/sp1-gpu-sys-*`: a stale cache fails with
  "CMAKE_CUDA_ARCHITECTURES must be non-empty".
- Two concurrent builds of fork crates race on the nested `sp1-core-executor-runner` build, and every CUDA proof then
  fails with "Broken pipe". Keep builds sequential (`backends/sp1/tcdot/build_fork.sh`).
- sp1-sdk's cuda client runs `$HOME/.sp1/bin/sp1-gpu-server`. Point HOME at a directory holding a different server to
  keep variants apart. The server's debug log arrives on the host's **stdout**.
- A recursion (compress/Groth16) proof over a new chip fails vk-map membership unless the recursion vk map is rebuilt.
  Such variants are core-proof only.
- Reproducibility: compare `vk_hash`, not the guest ELF's sha256. The vk hashes only the loaded program image, so an
  independent build can differ in debug-info paths and still give the same vk (verify-night `art:4bfc9e7e…` on
  `art:90671b80…`). To make the ELF reproduce too, `--remap-path-prefix` every checkout path that reaches the guest,
  including a path-patched SP1 fork's canonical path.

## Sharding
- `local_gpu_opts()` (`sp1-gpu/crates/prover_components/src/builder.rs`) hard-sets
  `element_threshold = ELEMENT_THRESHOLD` (2^28+2^27 cells) on GPUs over 30 GB and sizes the 4 pinned trace buffers from
  it. The `ELEMENT_THRESHOLD` env has no effect on a stock server. Fork patch 0006 in `lane/sp1-tcdot` (FORK_HEAD
  `d14b4c62`) honours it. The LDE is 4x the area, so above an area of about 5.3e8 it passes 2^31 elements (untested).
- `ShapeChecker::handle_mem_event` (`crates/core/executor/src/vm/shapes.rs`) charges every first access of a
  *deferred* precompile to the issuing CPU shard's estimate (MemoryLocal + 2 Global, about 500 cells per word), but
  those rows land in the precompile shard. Precompile-heavy programs therefore cut CPU shards at about a quarter of
  their real area. Patch 0006 fixes this. `syscall_sent()` is set only for non-retained syscalls (`splicing.rs`
  `execute_ecall`).
- `SHARD_SIZE` does not cut CPU shards in 6.4.0; only the area estimate does.
- The GPU proves one shard at a time (permit). Measured on the A100 at B=4096 bf16 (`art:6e415853…` and its
  screenings): 1.8-1.9 ns per cell plus about 0.09-0.15 s fixed per shard. The first large shard of a server's life
  pays a one-time allocation (up to +3 s at 5e8 cells), so warm up with a full-size proof.
- Before the first GPU work (about 1.7-2.3 s at 4.9M cycles and 25 MB input), the server runs these steps in series:
  executor setup 0.36 s, execution, splice serialization (the memory-read log, 79 MB), and memory-shard emission (only
  after all splicing), then the first shard's CPU trace.

## Memory argument cost
- Each 64-bit word a program touches costs about 4 Global rows (241 columns), plus MemoryLocal, MemoryGlobalInit and
  MemoryGlobalFinalize rows: about 1,040 cells per word. For the relation-bare statement at B=4096 (25 MB private x/W
  hint-read into memory), that is 76% of all cells even with a dot-product precompile (`art:90671b80…`). Packing
  operands densely (4 BF16 per word) is the only lever inside stock SP1.

## Guest-side precompile calls
- A syscall that returns nothing leaves t0 = its own code (`minimal/ecall.rs`: `unwrap_or(code)`) and does not write
  a0/a1. A hot loop can therefore issue back-to-back `ecall; addi a0, a0, stride` in one `asm!` block (2 cycles per
  call, versus about 10 through the non-inlined `extern "C"` stub): `backends/sp1/tcdot/guest/src/main.rs`
  `chip_chain`.

## Emitting results
- Modified SP1 variants use `benchmarks/dot_product/vector_run.py --backend sp1-bare --variant FILE`, with SP1 prover
  options passed as `--prover-env KEY=VALUE` (recorded as `software.prover_options`). `backends/sp1/tcdot/bench.py`
  writes the variant file.
