# sm_120 kernels: the toolchain, the card, the libraries and node 2

Facts for anyone writing or timing kernels on the RTX PRO 6000 (sm_120, 188 SMs) and running them on node 2
(`vy-nebius-2`). One line per fact, each with its source; correct a wrong line in place instead of adding a contradiction.
The workflow around these facts is Verity's `.agents/skills/kernel-engineering/SKILL.md`. This list is hand-kept until the
kernel-attempt ledger's facts page lands (bc-1a23b70c, verity#491); then it is generated from `fact` records, or retires.

Sources: status files are `store:pous/internal/pouw/rtx-pro/workers/<file>` (the POUS Project store) with the time of the
entry, `server.md` is the RTX PRO coordinator's log there, and commits are on the harness branch (verity#491) unless named.

## Build and the SASS gate

- Build `-gencode arch=compute_120a,code=sm_120a`: the block-scaled and `f8f6f4` MMAs need the `a` target (`brief.md`,
  Toolchain).
- Never `-ftz=true`, `--use_fast_math`, `-prec-div=false` or `-prec-sqrt=false`. ptxas still emits `.FTZ` inside the IEEE
  `__fdiv_rn`, `__frcp_rn`, `__fsqrt_rn` and `__frsqrt_rn` sequences under default flags; the harness's SASS gate exempts
  exactly those, pinned per toolkit, so count SASS, not flags (`1-pearl-c-sm120.md` 14:10Z; harness `README.md`).
- `-lineinfo` reaches ptxas and breaks the SASS gate's pins; build without it (`30cda987`).
- `ldexpf` lowers to `MUFU.EX2`, which the gate refuses; compare scales exactly instead (`af9bd2a9`).
- ptxas 12.9 lowers `cp.async.bulk.shared::cluster` to a CALL and then drops every `setmaxnreg` (C7506: consumers at 168
  registers, 700 B spilled); `.shared::cta` fixes it (`nvfp4-mainloop.md` 10:45Z).
- Multicast TMA compiles for sm_120a, but ptxas warns it runs with "substantially reduced performance"
  (`nvfp4-mainloop.md` 13:03Z).
- ptxas if-converted a duplicated-group `test_wait` form and spilled 850 B; keep an opt-in knob's off position
  byte-identical in SASS (`nvfp4-mainloop.md` 12:20Z).
- `__launch_bounds__(1024)` caps a thread at 64 registers; the hashing module's `build.sh` refuses local-memory spills
  (`2-hashing.md`, Lessons).
- One `extern __shared__` name has one type per translation unit (`2-hashing.md`, Lessons).
- Node 2 has CUDA 13.0 only. Off the node, get 12.9 from NVIDIA's apt repo (`cuda-nvcc-12-9`): the pip wheel
  `nvidia-cuda-nvcc-cu12` ships only `ptxas`, and no wheel ships `cuobjdump`. The harness's `jobs/toolkit.sh` assembles 12.9
  from pinned archives (`brief.md`, Toolchain; harness `README.md`).
- `fake_cuda.c`, the host twin's CUDA stub, silently dropped its 65th kernel name, which surfaced later as
  `cuModuleGetFunction 500`; the fixed copies abort naming the limit, and #449's still has 64 (`1-pearl-c-sm120.md` 14:10Z;
  `2-hashing.md`, `ea17cefb`).

## The card

- There is no packed FADD: `add.rn.f32x2` lowers to two FADDs (`fp8-mainloop.md` 09:20Z; `assessor.md` 08:30Z).
- An empty-barrier release needs `fence.proxy.async.shared::cta` before its arrive, or the next TMA refill lands under an
  `ldmatrix` still reading it (unroll 2: 25 of 40 runs wrong). Unroll 1 looked clean only because ptxas waited on every
  scoreboard before the release (`fp8-mainloop.md` 08:50Z).
- After a warp-role split only the live warps may sync: use a named barrier (`bar.sync 1, 256`), not `__syncthreads`
  (`fp8-mainloop.md`, Interface).
- `setmaxnreg` budgets: a producer at 24 registers leaves the consumers 240, at 40 leaves them 232; hash warps need 56, where
  v1 spills and v2 doesn't (`1-pearl-c-sm120.md` 15:45Z; `fp8-mainloop.md` 08:07Z).
- Under nvcc 13.0 the v1 mainloop needs `tile<1>`: `tile<2>` spills (`1-pearl-c-sm120.md`, Answers 4).
- A 160-byte forming row stride has no bank conflicts; 144 bytes is 2-way (`1-pearl-c-sm120.md` 12:56Z).
- 128-byte-row (WIDE) epilogue stores cut STG L1 tag requests from 16 to 4 (`nvfp4-mainloop.md` 13:08Z).
- Folding the BF16 epilogue into the next tile cost 2.2%: the stage release's MEMBAR waits on the step's global stores
  (`nvfp4-mainloop.md` 12:40Z).
- BK = 64, seven shallow stages, was 23% slower than 128-deep stages (`nvfp4-mainloop.md` 11:35Z).
- NVFP4 forming is DRAM-bound (about 1.2–1.4 TB/s), so instruction-level changes to it don't show (`5-fp4-design.md` 12:15Z).
- `rcp.approx` is exact on all 126 valid UE4M3 scales (`5-fp4-design.md` 12:15Z).
- The E2M1 cast packs with `F2FP.SATFINITE.E2M1.F32.PACK_AB_MERGE_C`, with no PRMT (`5-fp4-design.md`, Results).
- NVFP4's scale byte ignores bit 7 (0x80–0xFF read as their low 7 bits), and 0x7F and 0xFF are NaN (`assessor.md` 09:35Z).
- QMMA has a fixed latency of about 16 cycles per warp; FADD bursts that coincide across sub-partition partners slow v1
  (`fp8-mainloop.md` 09:20Z).
- Integer ops issue at about half a warp per clock; one BLAKE3 compress costs about 1,421 cycles per thread (`2-hashing.md`,
  W1 prices).
- At 8,192³ every row is in flight (256 MB against 128 MB of L2), so a second read of them goes to DRAM
  (`1-pearl-c-sm120.md` 15:45Z).
- Under the 600 W cap each kernel runs at its own clock: compare cycles, or profile with ncu `--clock-control none`
  (`fp8-mainloop.md` 09:55Z–10:10Z).

## The libraries (baselines)

- cuBLASLt on sm_120 has no algorithm for MXFP4, rowwise FP8 or 128-blockwise FP8; a refusal is a result, not a failed run
  (`6-harness.md`, `7be37429`).
- Node 2's "cuBLASLt 13.0" is 13.1.1.3 (`6-harness.md`, Lessons).
- CUTLASS 3.x's default raster was about 2× slow at 32,768³: tune the tile order (`--cutlass-sched`, `73339a27`;
  `6-harness.md` 16:06Z).
- CUTLASS 4.8's sparse NVFP4 gives wrong words, and its example 80b's `verify()` compares the reference to itself: nothing
  is gated, timed or used as a baseline from it until it is bit-exact (`server.md` 13:18Z).
- Triton's `dot_scaled` on sm_120 silently falls back to dequantize plus FP16 MMA when K isn't packed (triton#9684), and
  libdevice's FTZ reflect is on by default: don't use Triton for exact kernels (`store:pous/docs/pouw/kernel-tooling-report.md`).

## Node 2 (`vy-nebius-2`)

- Clocks are locked node-wide at 2,100 / 12,481 MHz by the node's owner; never `nvidia-smi -lgc`. Under sustained load the
  SM runs at 2,070–2,092 MHz as the power cap engages: label rows locked-2100 and record every rep's clock (`server.md`
  06:00Z, 08:50Z; `ops.md` 13:00Z).
- `gpu-lease` sets `CUDA_VISIBLE_DEVICES`; take the GPU's identity from `GPU_LEASE_UUID`, since `nvidia-smi -i 0` ignores
  `CUDA_VISIBLE_DEVICES` (`pouw-mvp-e2e.md` 14:08Z, `r20260930-134459-8c03`).
- Without `--wait`, `gpu-lease` exits at once when another waiter exists (`server.md` 06:50Z).
- The fill queue pauses only for a `--timed` lease or a holder of all eight GPUs (`server.md` 13:59Z).
- `gpu-lease 8` exposes all eight GPUs; narrow to one for identity checks with `CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES%%,*}`
  (harness `README.md`).
- A bare `--preemptible` lease is SIGTERMed (exit 143) when a waiter arrives, and nothing requeues it; the fill queue does
  (`server.md` 07:25Z).
- The fill queue: a script in `/workspace/pouw/fill/queue/` headed
  `# fill: owner=<id> gpus=1 max_min=8 cpus=8 project=pous prio=10`, exiting 0 when done, 99 for more chunks, 143 when
  preempted. Prio 10 is for GPU chunks only; CPU jobs
  (`gpus=0`) take prio 0, or they starve the queue. Queue one GPU chunk at a time, with a budget longer than the chunk's
  longest task. Outputs land in `/workspace/pouw/fill-out/<job>/`, which is not the evidence store (`ops.md`; `server.md`
  09:30Z, 12:44Z; `5-fp4-design.md`, Lessons).
- The node's Python is 3.14, whose multiprocessing doesn't fork: re-initialise scheme state in pool workers. The system
  Python has no numpy: `uv run --no-project --with numpy python` (`3-fp8-attacker.md` and `5-fp4-design.md`, Lessons).

## `research run`

- `--timeout` counts the time spent waiting for a lease: bound the work with `timeout` inside `gpu-lease` instead
  (`0-fp8-capture.md` and `5-fp4-design.md`, Lessons).
- Without `--cwd source` the command runs in the run directory, without the shipped tree (rc 127, `r20260930-070944-6714`).
- `--send FILE` lands in `$RESEARCH_RUN_DIR/inputs/`, not the working directory (rc 127, `r20260930-111239-9755`).
- `--source` ships `git archive HEAD` of a clean checkout; shipping loose files instead missed an import. A stacked branch
  may carry an older `tools/research`: run the CLI from an `origin/main` worktree and `--source` your branch
  (`5-fp4-design.md` and `1-pearl-c-sm120.md`, Lessons).
- There is no `--detach`; a job launched as if there were never ran (`fp8-mainloop.md` 09:35Z).
- `research fetch` right after a run exits can report `preserved=NO`: fetch again (`6-harness.md`, Lessons).
- A VM reset wipes the checkout, `/tmp`, `uv` and CUDA: keep job scripts on the node (`/workspace/pouw/<you>/`), and
  preserve a build as `art:` as soon as it exists (`1-pearl-c-sm120.md` and `5-fp4-design.md`, Lessons).

## The harness and the panel

- The harness fills operands on a non-blocking stream: an arm's warm-up on the null stream synchronises first
  (`1-pearl-c-sm120.md`, Lessons).
- A decode chain's A, root and seed change every call: a gate reads seeds from the device, never `prepare`'s copy
  (`5-fp4-design.md` 08:35Z, `r20260930-081618-a87c`).
- CUDA graphs hide launch gaps: price a fusion inside the graph (`2-hashing.md`, Lessons).
- Two `panel.py append`s in the same minute once tore a row; it now locks and checks after writing. After a store `EAGAIN`
  run `panel.py render`, never append again (`5-fp4-design.md` 07:22Z).
- Two pytest files that import `twin` from different packages both get the first one: import it under a unique name with
  `importlib` (`5-fp4-design.md`, Lessons).

## vLLM on the card

- FlashInfer's sampler JIT-compiles at the first sampling and needs `ninja` on the PATH: build it in setup, off the timed
  path, with the venv on the PATH and `FLASHINFER_CUDA_ARCH_LIST=12.0f` (`pouw-mvp-e2e.md` 13:37Z).
- Timed vLLM passes create inference tensors, so poison them under `torch.inference_mode()` (`pouw-mvp-e2e.md` 14:17Z).
