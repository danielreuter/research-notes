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
- A custom chip's CPU tracegen sits on its shard's critical path, twice. The prover worker runs
  `generate_dependencies` before the record goes to the GPU. Without an override, the default builds the whole trace
  just to collect byte lookups, and the server then builds it again. Write both as SP1's own chips do (`ShaExtend`):
  - `generate_trace_into`: `par_chunks_mut` over rows, with a throwaway lookup `Vec`;
  - `generate_dependencies`: `par_chunks` of the events into per-thread `HashMap` lookups, then
    `add_byte_lookup_events_from_maps`.

  TcDotBf16 (1173 columns, 84k rows) was sequential. Fork patch 0011 fixed it: its shards reached the GPU 0.5 s sooner,
  and t.total went from 5.63 to 4.98 s (`art:2a4760fb…`).
- Reproducibility: compare `vk_hash`, not the guest ELF's sha256. The vk hashes only the loaded program image, so an
  independent build can differ in debug-info paths and still give the same vk (verify-night `art:4bfc9e7e…` on
  `art:90671b80…`). To make the ELF reproduce too, `--remap-path-prefix` every checkout path that reaches the guest,
  including a path-patched SP1 fork's canonical path. To tell whether two ELFs are the same program, compare the loaded
  sections (.rodata, .eh_frame, .text, .data at the offsets `readelf -S` gives), not the whole file.
- **The vk does not pin the constraint system.** TC_DOT's memory arm and witness arm (patch 0007, a different AIR) share vk
  0x00b4876f… for the same ELF. The memory-arm host rejects witness-arm proofs ("invalid shape of proof"). So a
  verification must name the fork commit it was built at. The `fork_head` that the tcdot host's `info` prints is
  `VERITY_TCDOT_FORK_HEAD` at build time: a label, not proof of what was compiled. (verify-night verdicts on
  `art:174d7b4d…` and `art:a68f2446…`.)
- **Open (verify-night, 2026-09-24 10:20Z):** a fresh CPU build of the 6655716e witness host (97b5b60a, fork tree
  4ca5a6ca, stream-operands) gives vk 0x009f022f… with a guest image identical to the 0x00896ef4 build. The producer
  recorded 0x00896ef4 for `art:0a66c35e…`, and my host rejects those proofs ("global cumulative sum is not zero"). Until
  someone reproduces a result's vk from a fresh build, do not treat it as verified.
- The stock host's `veritor-zk-host verify` exits 0 even when it rejects. Accept a proof only if its JSON line has `ok`,
  `statement_match` and `verdict` true and `unsound` false. (`verity_sp1/host.py` already reads the JSON.)

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
- The GPU proves one shard at a time: `ProverSemaphore::new(1)` in `cuda_worker_builder_with_machine`, and a single
  `CudaShardProver` whose trace buffers are preallocated for one shard. Raising the permit count alone would share
  those buffers.
  - Measured on the A100 at B=4096 bf16 (`art:6e415853…` and its screenings): 1.8-1.9 ns per cell plus about
    0.09-0.15 s fixed per shard.
  - With the TC_DOT chip (`art:0a66c35e…` screenings): 0.22 s at 16-29M cells, 0.44 s at 122M, 0.53-0.57 s at 195M.
    That is about 0.2-0.25 s fixed plus 1.5-2 ns per cell, so fewer, larger precompile shards pay: ELEMENT_THRESHOLD 2x
    beats 1.25x by about 0.5 s.
  - The first large shard of a server's life pays a one-time allocation (up to +3 s at 5e8 cells), so warm up with a
    full-size proof.
- Precompile shards are emitted incrementally. Each CPU shard's prover uploads its deferred events, and the controller
  (`controller/precompiles.rs`) cuts full precompile shards as they accumulate. So a precompile shard waits for the CPU
  shard that issued its calls, then for its own CPU tracegen.
- `MINIMAL_TRACE_CHUNK_THRESHOLD` counts minimal-trace memory values, not cycles. Streamed input words count too:
  0.86M cycles gave 4.8M values. Each chunk gives at least one CPU shard. More chunks with as many
  `SP1_WORKER_NUM_SPLICING_WORKERS` (default 2) trace CPU shards in parallel and start the GPU sooner, despite the
  per-shard fixed cost. On TC_DOT: 4 chunks and 4 splicers beat 2 and 2 by about 0.25 s.
- Before the first GPU work, the server runs these steps in series.
  - At 4.9M cycles and 25 MB input (about 1.7-2.3 s): executor setup 0.36 s, execution, splice serialization (the
    memory-read log, 79 MB), and memory-shard emission (only after all splicing), then the first shard's CPU trace.
  - At 0.86M cycles with 4 chunks (`art:0a66c35e…`, 1.2 s): vk setup 0.09 s; CoreExecute task to "Starting minimal
    executor" 0.39 s; execution 0.31 s (chunks are spliced as they close); the first chunk's tracing re-execution and
    dependencies 0.34 s.
  - The host's prove time exceeds the server's span by about 0.3 s (request and proof transfer).
- `MinimalExecutorRunner::reset` (`crates/core/runner/src/native.rs`) rebuilds the transpiler's shared memory as `new`
  does. So even a working minimal-executor cache would not remove all of that setup.

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

## Soundness: SP1 cannot reach 2^-128 by raising its constants (lane sp1-128, 2026-09-24)
- `SP1_TARGET_BITS_OF_SECURITY` (sp1-primitives `fri_params.rs`, 100) sets only the FRI query count:
  `unique_decoding_queries = ceil((T - 16) / -log2(5/8))`, giving 124 at 100, 166 at 128 and 175 at 134. The GPU server takes
  it through `core_fri_config()`, so the prover needs a source build and the verifier the same constant. Do not raise
  the constant itself: it also grows the compose/deferred recursion programs every prover builds at start-up (fixed
  reduce shape), which panic "fixed height is too small". Patch only `core_fri_config`'s query count (core proofs only).
- The other per-shard terms are bounded by the KoalaBear^4 challenge field (|F| = 2^123.95) and by two constants,
  `GKR_GRINDING_BITS` 12 (hypercube `verifier/shard.rs`) and `BATCH_GRINDING_BITS` 5 (slop basefold `verifier.rs`).
  soundcalc, unique-decoding regime, proven bounds; log2 per-shard error:

  | config | query | LogUp-GKR | FRI commit (sum) | batching | zerocheck | jagged reduce | sum |
  |---|---|---|---|---|---|---|---|
  | stock, 124 q | -100.1 | -100.3 | -102.4 | -104.4 | -112.2 | -116.4 | -99.0 |
  | T = 134, 175 q | -134.7 | -100.3 | -102.4 | -104.4 | -112.2 | -116.4 | -99.9 |
  | + GKR grinding 40, batch grinding 29 | -134.7 | -128.3 | -102.4 | -128.4 | -112.2 | -116.4 | -102.4 |

- No conjectured regime helps. The LogUp-GKR, zerocheck and reduce terms are Schwartz-Zippel terms, and the commit and
  batching errors are at least about n/|F| in any regime.
- **SP1 cannot reach 2^-128 without protocol changes:** grinding in every FRI commit round (about 25 bits at round 1),
  in zerocheck (about 16) and in the jagged reduction (about 12), or a larger extension field. 40 bits of GKR grinding alone
  is 2^40 hashes per shard.
- The SP1 envelopes before 2026-09-24 book SP1's constant (-100 per shard), about 1 bit optimistic against the additive
  -99.0. Those records are left as they are (coordinator); new envelopes carry the additive figure.
- Reproduce: soundcalc @2af5e7d (github.com/ethereum/soundcalc, 2 MB), then
  `PYTHONPATH=. uv run --no-project --with toml python ~/.research/notes/lanes/sp1-128/evidence/soundcalc_sp1.py`.
  Output: `lanes/sp1-128/evidence/soundcalc_sp1.out`. The config is SP1's own `gen_soundcalc_toml` output with v6.1.0
  machine sizes; the 6.6.0 constants it reads are identical.
- Building the GPU server from source (v6.6.0) needs Go >= 1.24 for `sp1-recursion-gnark-ffi` (apt's golang-go fails
  with "invalid go version '1.24.0'"). `backends/sp1/sec128/build.sh` installs it. `sp1-gpu-sys` needs CMake >= 3.24 (images ship 3.22).
- A `[patch.crates-io]` path crate changes the guest ELF (its panic paths are not under the remapped cargo home) and so
  the vk. Patch the crate in place in a copied `CARGO_HOME` instead; `host/build.rs` remaps that to `/cargo`, so the
  guest stays byte-identical (`sec128/build.sh`).
- sp1-sdk's cuda client compares `sp1-gpu-server --version` with the *linked* `sp1_primitives::SP1_CRATE_VERSION`. On a
  mismatch it stops every server and downloads the release binary over `$HOME/.sp1/bin/sp1-gpu-server`, so a patched
  primitives crate must keep its version. Check the server's sha256 after each run (`sec128/run.sh` does).
- A source-built sp1-gpu-server 6.6.0 needs ~1.03-1.6 s to listen on the A100 pod. sp1-cuda 6.4.0's client tries the
  socket only 10 x 100 ms, so bare-prove panics "Could not connect to `sp1-gpu-server` socket". `sec128/build.sh` raises the
  retry count in the copied cargo home (host-side only).
- Measured cost of 175 core queries (A100 BF16, art:e8c7c331 vs stock art:7233a6a3): t.total 21.05 s vs 18.52 s (+14%);
  proof 45.8 MB vs 33.5 MB (+37%); verify 2.03 s vs 1.40 s. Security stays -95.5 union-bounded (22 shards), so the result
  appears only in D2.

## Emitting results
- Modified SP1 variants use `benchmarks/dot_product/vector_run.py --backend sp1-bare --variant FILE`, with SP1 prover
  options passed as `--prover-env KEY=VALUE` (recorded as `software.prover_options`). `backends/sp1/tcdot/bench.py`
  writes the variant file.

## Building on a fresh pod (merge-postwave, 2026-09-24)
- `sp1up --version v6.4.0` installs `cargo-prove` first and the `succinct` guest toolchain (a 311 MB tarball, ~10 min on a
  cpu3c pod) after it. So `cargo prove --version` succeeding does not mean the toolchain is ready. A host `cargo check` /
  `build` started in that window fails in build.rs with "override toolchain 'succinct' is not installed". Wait for
  `rustup toolchain list | grep succinct`.
- `veritor-zk-common` tests read repo-root `fixtures/` (bench-instances/v1 negatives, typed-obligation-v0). A
  `git archive HEAD backends/sp1` alone gives 4 NotFound failures.
- `backends/sp1/tcdot/build_fork.sh OPERANDS=witness SKIP_SERVER=1` on a CPU pod reproduces the witness-arm fork (HEAD
  6655716e, tree == FORK_TREE_WIT). `cargo check --release -p verity-tcdot-host --features stream-operands` then takes 8m52s
  on 16 vCPU (r20260924-171410-4069).
