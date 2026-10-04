---
cursor:
  subagentId: "bc-0de2d624-783f-5e35-9b57-19c1627bd2f2"
---

# GPU 6: PoUW bench harness (shared) and card characterization

Worker bc-0de2d624. Single owner of the shared PoUW bench harness; both streams' arms plug into it. On node 2 through
`gpu-lease` (whichever GPU a lease gives; every run checks and records its UUID), timed work in `gpu-lease 8 --wait` windows.
Code: `benchmarks/pouw/harness/` on branch `cursor/pouw-harness-sm120-d2f2`, **head `80bff34cc`, on origin** (SASS gate v4
with its numeric pin, panel rules (a) and (b), a library that passes the gate, CUTLASS's tile orders as tuned candidates,
`--screen-only`, and #583's arm interface v0.5: `dump`, the poisoned dump and the no-write control), draft
[PR #491](https://github.com/danielreuter/verity/pull/491). GitHub takes my pushes again. **My own v0.5 (`9182e17d7`,
`508c7b5ea`, `transcript(dir, read)`, `--judge-controls`) is withdrawn**: #583's replaces it (root ruling, server.md
17:17Z), and its store bundle `art:fd3afef5…` is history, not a head to run. Build
`art:3bf425e6bacae3c594f968e4154f321045be01d75ad3d33f31089791bffcdad5` (build run `r20260930-155708-09ed`; on node 2 as
`/workspace/pouw/fill-out/harness/inputs-73339a27/`): `art:46a3756b…`'s kernels plus the tile orders, and the whole library
passes gate v4 (16:05Z). `art:46a3756b9c4a7d2a9a3ae4999d0fedfe0eeebea075b0c071fca4355260f83397` (`485a64660`, run
`r20260930-152632-c20f`, `inputs-485a6466/`) is the same library without them. Untimed check `r20260930-152808-08cb`:
every gate and chain as expected, and the divisors as before (15:35Z).
- **Don't use `art:4e047f88…` (`d6ec4015e`, `38a08255f`)**: it passes the gate, but its derive is 2–3× slower (9–30 µs at
  decode), which would read every decode divisor high.
- **`7f4a67f6b` to `b7b88c95c` with `art:14fff942…` can't run** (15:00Z): the gate refuses that library (built with
  `-lineinfo`, 16 `MUFU.EX2` from `ldexpf`, and `ATOMG.ADD.F32.FTZ` in stream-K). Fixed at `d6ec4015e` (below).
- **`8d04bfe5` fails on node 2** (the gate's discovery takes `/dev/zero (deleted)` for a file). The backport
  `art:80d8dc1d25697cfdd1e1ddfe1581dbff20aa7fbff389e8a6aa5f17e2e86a9281` (one commit on `8d04bfe5`; smoke
  `r20260930-142609-e46f`) runs with `art:14fff942…`, which passes that gate (v2) but not v4.
- `0d1d6615` with `art:18a3d82b…` still times decode chains, without the new kernels. **Don't run `e91184bf6` or
  `5b290af35`**: their pins have no numeric run, so the gate exempts nothing and refuses every kernel with a division or
  square root.

## For GPUs 2 and 5 (bc-7442ca43, bc-71c6ab78): `dump`, #583's poisoning (17:50Z; supersedes 17:05Z)

**Use harness `80bff34cc`** (#491 = `e22a2808f` + #583 at `65e700593`, merged as `216143c72`, + one refusal) with build
`art:3bf425e6…` (no native code changed) and `--cutlass-sched nvfp4 mxfp4 fp8-e4m3`. After the lease, `verify.py` alone
judges the transcript and the control (#583's `--tier`, `--publish`, `--push` as GPU 2's pilot uses them). There is no
`bench.py --judge-controls` and no `transcript(dir, read)`: those were my withdrawn v0.5.

**Your arm gives** (arm interface v0.5 as #583 wrote it; `arm.py`'s docstring is the contract):
- **`dump(self, dev, call, shape, out)`** on the arm: writes the transcript file(s) into `out`. It reads the device and
  computes nothing.
- **`call.transcript_buffers`** (`{name: Buffer}`, default `call.outputs`): every buffer the dump reads, including what only
  a setup step writes (Pearl-C4's `root_a`, `seed_a`, `root_b`, `b_scales`; a padded A's buffer). A buffer read and not
  declared escapes the poisoning. **Never an operand**: `80bff34cc` refuses a transcript buffer that overlaps the call's
  operand set before poisoning anything, and records it as the poisoning's error, so the row gets no harness control.
- **Your verifier's `transcript`** under `transcripts/{arm}/{shape}/…`. `verify.py` then judges the control at the same
  path under `negative/`. Name `control` only if your verifier looks somewhere else.
- **Stop dumping from `free()`** or from a flag such as `PEARLC4_NOWRITE_CONTROL`.

**What the harness does** after the timed items, on the hash call of operand set 0 (`bench.poison_dump`): sync, 0xA5 into
every transcript buffer, sync, and a check that every byte is poison; `weight_side` and `launch`, sync; the bytes each
buffer's call wrote (`written`; `wrote_nothing` if none); `dump` into `transcripts/<arm>/<shape>/`; poison again; `dump`
with nothing launched into `negative/<arm>/<shape>/`. `verify.py` then runs a per-shape verifier on both. An accepted
control rejects the row (exit 1); a rejected one's line becomes the row's `negative_control` and `--negative-control`; a
missing one leaves the row without it, which `panel.py append` and the ledger's measured-row check refuse.

**Arms and `dump`** (server.md 17:16Z asks me to list every arm still without it; 17:50Z):

| Arm module | Classes | `dump` on its owner's branch | `dump` elsewhere |
|---|---|---|---|
| `harness/example_arm.py` | `ExampleFp8` | yes, #491 (#583) | |
| `pearl_c4/pearl_c4_arm.py` | `PearlC4Nv`, `PearlC4Mx` | **no**: GPU 5's #580 (`cursor/pearl-c4-f1f2-3084`) is at `0fa9ff70e` | mine, `cursor/pearl-c4-harness-dump-d2f2` at `8e1ece3b6`, one commit on `0fa9ff70e`, for GPU 5 to take |
| `pearl_c_sm120/pearlc_arm.py` | `PearlCSm120`, `PearlCSm120Unpromoted` | **no**: GPU 1's `cursor/pearl-c-sm120-h1-b44b` is at `b6a919292` | `cursor/pearl-c-sm120-h1-commit-9569` at `e0902b4a0` (17:43Z), the pilot's arm |

No other arm module is on #491 or on those branches. When GPU 5 takes `8e1ece3b6` and GPU 1's branch has the pilot's
`dump`, every arm has it, and I'll tell the coordinator.

**Pearl-C4 at `8e1ece3b6`** (GPU 5, bc-71c6ab78): `_Call.transcript_buffers` is `D.WRITTEN["hash"]` (`root_a`, `seed_a`,
`lines_ea`, the A codes and scales, `pa`, `c`, `u`, `y`, `digests`, `leaves`) plus `root_b` and `b_scales`, and with m
padded, the arm's padded `xa`; `xb` and an unpadded `xa` are operands and stay out. The arm's `dump(dev, call, shape, out)`
reads what `R.write_dump` needs (`_Call.write_dump`). The verifier's transcript is `transcripts/{arm}/{shape}/transcript.json`,
so the harness's control is judged without a declared `control`. `transcripts`, `_dumped`, `first_dump` and
`PEARLC4_NOWRITE_CONTROL` are gone; `arm_smoke.py --run-dir` poisons and dumps both itself. CPU: both arms pass
`check_arm`, and `check_verifier` passes. **Checked on the card** (18:00Z): untimed run `r20260930-174056-4c34`
(`gpu-lease 1`, `PearlC4Nv`, cubin `dd01ae5e` from your `r20260930-162438-25e9` ship, both headlines, from
`cursor/pc4-dump-run-d2f2` = `8e1ece3b6` + harness `216143c72`; not for merge). Exit 0 for bench and verify.
- The SASS gate passes the cubin.
- The weight side rewrote all of `root_b` and `b_scales` over the poison, and the call wrote every other buffer. At decode
  the padded `xa` is declared at its real rows (524,288 bytes).
- Both shapes' transcripts ACCEPT, and both `negative/` controls REJECT (the verifier's exit 1 on them is a control's and
  doesn't fail the step). Each row carries its `--negative-control` line, which names the run.
- **Not a panel row** (labelled): untimed on a shared node, and its verifier commit is the run tree's `d52d6fdcd`, not your
  `bca8de21`. Its slowdowns (2.81 prefill, 15.62 decode) are no measurement.

**Limits.** An arm that reads device memory it didn't declare escapes the poisoning; the harness can't see its reads. The
no-write control still catches a stale buffer the verifier checks. Server.md 11:50Z item 3 (vary the inputs per arm)
isn't done.

**`/dev/shm/sem.* (deleted)`.** `b7b88c95c` didn't cover it. It skipped only shared anonymous memory (`/dev/zero`,
`/SYSV…`), so a run whose process maps a multiprocessing semaphore would fail the gate's discovery. It is covered at
`e22a2808f`, and fails closed: a `sem.*` mapping is skipped only if every region is at most one page and holds no ELF or
fatbin; any other deleted mapping still fails.

## Checkpoints

- 04:55–05:56Z (Phase A, CPU): arm interface v0 (05:10Z) and v0.1 (05:56Z); the harness, its CPU tests and the offline SASS
  check; the build preserved as `art:d54534ea…`; `jobs/env.sh`. Returned.
- 06:10Z: Phase B on node 2. Smoke `r20260930-061027-ac20`: GPU 0 = `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`, card check,
  versions. `--gpu lease`, `--server-md` and `--clock-label` added (`279a110b`).
- 06:14Z: characterization, untimed, `r20260930-061232-b66b`.
- 06:21Z, 06:28Z: gates rehearsed untimed, `r20260930-062029-3c4e` (default autotune) and `r20260930-062712-3e5d` (32
  cuBLASLt candidates, 4 finalists, 40 reps): every gate and negative control as expected. cuBLASLt refuses MXFP4; the harness
  now records that and times MXFP4 on CUTLASS instead of failing the run (`7be37429`).
- 06:31Z: **the timed window, `r20260930-062850-de8e`** (`gpu-lease 8 --wait`, 06:28:56–06:31:21Z, 2 min 25 s, timing on
  GPU 0): the baselines at both headlines, then the characterization. Preserved. **Table below.**
- 06:45Z: the arms of GPUs 1 and 5 load and pass the interface check in their own trees with the harness beside them;
  `env.sh` now puts `verity` and `verity_pouw` on `PYTHONPATH` (`940562e2`). How to plug in: below.
- 07:25Z: **the dependent-chain decode method** in the harness (`4e5c3a31`): a device derive of A from the previous call's y
  in every consumer format, its bit-exact numpy twin, chains gated step by step against the twin, a stale-A negative control,
  and each arm's decode split into before, during and after the GEMM, with and without a side stream. Arm interface v0.2.
- 07:35Z: builds on node 2's CPUs with CUDA 12.9.1 assembled from NVIDIA's pinned redistributables (`jobs/toolkit.sh`) and a
  per-object cache (`0e260aae`). Same SASS as `art:d54534ea…` in all 35 kernels.
- 07:45Z: the derive made about a launch (3.8–5.6 µs, from 14–27 µs), because it sits in the divisor too (`0d1d6615`).
  Untimed `r20260930-074502-5cfb`: the derive preflight (63 cases at 3 shapes), every chain gate and the stale-A control
  as expected.
- 07:48Z: **the timed window, `r20260930-074616-9ec9`** (07:46:27–07:48:16Z, 1 min 49 s, timing on GPU 0): both headlines,
  decode as a dependent chain. **The decode divisors are below.**
- 08:33Z: the FP4 search's build (`25529862`, `95247bf3`, `36df5171`; build run `r20260930-083321-6ec9`, `art:14fff942…`).
  It enumerates cuBLASLt's configurations by hand (`native/lt.cu`), loads node 2's cuBLASLt 13.1.1.3 as a second library
  (`libpouw_lt2.so`), and adds 12 CUTLASS sm_120 kernels. 53 kernels, no local-memory spills.
- 08:47Z: untimed search `r20260930-084701-6f87`: every enumerated configuration gated. cuBLASLt's whole NVFP4 space on
  sm_120 is one kernel (below).
- 09:03Z: **the timed window, `r20260930-085331-f280`** (09:01:28–09:02:55Z, 1 min 27 s, timing on GPU 0): both headlines,
  every family, decode as a chain. **NVFP4's prefill divisor moves to 0.78875 ms (−1.9%); nothing else moves.** Table below.
- 09:11Z: the FP4 sweep fill job ran all 21 panel shapes untimed (09:04–09:11Z); outputs preserved as `art:f3f2aefd…`.
- 10:01Z: **the FTZ SASS gate** (server.md 09:34Z; `7e80ee63`, `213a5b5a`), with its fast-math test; every run passes it
  before anything is timed. Arm interface v0.3: `build()` names its binaries.
- 10:17Z: gate v2 (`3481cf09`), two fixes the scan found (below). Node 2 scan `r20260930-101908-ab9a`: 39 binaries, both
  toolsets agree. **No shipped kernel fails** (below); rescanned at the four heads that moved since, 10:38Z: all pass.
- 10:33Z: **panel rule (a)** (server.md 08:50Z; `dcff1b68`): a warm-up to a steady clock, every timed item sized to the same
  device time, NVML sampled during each item, and each panel row carries both sides' per-rep times and SM clocks.
- 10:52Z: **panel rule (b)** (server.md 08:35Z; `8d04bfe5`): arm interface v0.4 names the arm's reference verifier, and
  `verify.py` runs it after the lease in the same run and writes the verifier's commit, accept line and transcript beside
  each panel row. **A measured row now needs harness `8d04bfe5` and, in the arm's `build()`, `binaries` and `verifier`**
  (the lines for GPUs 1 and 5 are under "Panel rules").
- 13:10Z: **SASS gate v3** (`e91184bf6`; server.md 09:58Z, 10:07Z, 10:14Z, 10:21Z, 11:00Z): every `.FTZ` and every FP32
  `MUFU` is flagged, and exempt only inside a whole sequence pinned to the ptxas that built it (below).
- 13:51Z: **gate v4 and its numeric pin** (`5b290af35`): `ieee_pin.cu` and `ieee_pin.py`; operands followed on every
  path; several pinned bodies per subroutine.
- 14:01Z: **the numeric run, `r20260930-135207-db3e`**: both toolkits' pinned builds are exact everywhere, and all three
  negative controls differ. Pinned in `sass_pins.json` (`7f4a67f6b`). Every other lane's shipped sm_120a cubin passes;
  the harness's own library doesn't (15:00Z).
- 14:28Z: **the gate's discovery skipped nothing on node 2** (`b7b88c95c`): a run maps `/dev/zero (deleted)` and
  `/SYSV… (deleted)`, which it read as files and refused, so GPU 1's runs `r20260930-114513-d7e5` and
  `r20260930-122014-33bb` failed. Shared anonymous memory is now skipped. Backport for `8d04bfe5`:
  `art:80d8dc1d…`, smoke `r20260930-142609-e46f` (exit 0; FP8 8192³ at 1.4531 ms, 756.7 TFLOPS, Measured, untimed).
- 15:00Z: **the library passes gate v4** (`af9bd2a9f`, `30cda987d`, `d6ec4015e`; build run `r20260930-145938-d948`,
  `art:4e047f88…`: 26 flagged, all integer-division seeds). It had failed for three reasons:
  - `k_derive` used `ldexpf` (built from `MUFU.EX2`) and FP32 division, whose slow path ptxas specializes to each kernel,
    so no pinned body matches. The NVFP4 scale and codes now round by exact comparisons, not division (below).
  - `build.sh` passed `-lineinfo`, which reaches ptxas, so the args weren't the pinned ones. Removed.
  - CUTLASS stream-K reduces its partial tiles with `RED.ADD.F32.FTZ` (PTX has no non-FTZ f32 atomic). The harness now
    runs stream-K in deterministic mode with a plain read-add-write in place of the atomic. **This changes a baseline;
    flagged.**
- 15:14Z: that build's untimed check `r20260930-150855-d410` failed the derive preflight: the new NVFP4 edge row put a NaN
  in y (`_ulps(0, -1)`), whose bits the device and the twin keep differently. Fixed in `38a08255f`, with a test.
- 15:35Z: **the derive was 2–3× slower on that build** (rerun `r20260930-151357-7641`: 9–11 µs at `m32-n8192-k8192`, 18–30
  µs at the down projections). ptxas had if-converted `scale2`'s FP64 fallback into every element. It is FP32 only now
  (`485a64660`, build `art:46a3756b…`, run `r20260930-152632-c20f`). Untimed check `r20260930-152808-08cb` (Measured,
  `gpu-lease 1`, screening): the derive takes 3.3–5.2 µs at `m32-n8192-k8192`, and the divisors match the 09:03Z table and
  the FP4 sweep within the sweep's noise. The stream-K rows: NVFP4 at `qwen2.5-7b-down-prefill` 0.23426 ms (was 0.23802),
  MXFP4's chains at `qwen2.5-7b-down-decode` 0.05250 (0.05195) and `llama3.1-70b-down-decode` 0.11067 (0.11242). The
  plain read-add-write costs nothing I can see.
- 15:35Z: **FP8's cuBLASLt enumeration queued as GPU fill** (`harness-fp8-enum-485a6466.sh`, prio 10, below).
- 16:05Z: **CUTLASS's tile orders are tuned candidates** (`73339a279`; build `art:3bf425e6…`, run `r20260930-155708-09ed`,
  gate v4 passes: 26 flagged, all int-seed). `--cutlass-sched FAMILY...` adds each 3.x kernel in every order its tile
  scheduler takes: raster along m or n, and max swizzle 2, 4 or 8, less the swizzles CUTLASS lowers onto a smaller one at
  the shape. Each order is gated, then screened with the enumerated configurations. Queued as fill
  (`harness-cutlass-sched-73339a27.sh`, prio 10): MXFP4 and NVFP4 at 32,768³, then 16,384³, FP8 at both, then 8,192³ as
  the control.
- 16:06Z: **MXFP4 at 32,768³: 48.877 ms, from 94.006** (Measured, fill chunk on a busy node, screening only;
  `/workspace/pouw/fill-out/harness/cutlass-sched-73339a27/m32768-n32768-k32768/mxfp4/`). The winner is
  `cutlass3x_mxfp4_256x128x128_coop` with max swizzle 2, at 1,440 TFLOPS. All 72 orders pass the gate, and the negative
  control is rejected. Every swizzle of 2 or more lands within 0.03% of the others; raster barely matters. So the L2
  reading below holds, and **MXFP4's 32,768³ divisor was 1.92× lenient**.
- 16:20Z: **the tile-order job is done** (8 chunks, 42–203 s each, all exit 0, every order gated). Measured, fill on a busy
  node, screening only; each "before" is the same run's best without the orders:

  | Shape | Family | Best with the orders (ms) | Kernel | Before (ms) | Change |
  |---|---|---|---|---|---|
  | 32,768³ | MXFP4 | 48.877 | `cutlass3x_mxfp4_256x128x128_coop_rasterN_sw2` | 94.006 (CUTLASS default order) | **−48.0%** |
  | 32,768³ | NVFP4 | 47.043 | `cutlass3x_nvfp4_256x128x128_coop_rasterN_sw8` | 49.710 (cuBLASLt algo 70) | **−5.4%** |
  | 32,768³ | FP8 | 92.539 | `cutlass3x_fp8_256x128x64_coop_rasterN_sw8` | 92.474 in the tune (cuBLASLt algo 35) | tie |
  | 16,384³ | NVFP4 | 6.0249 | `cutlass3x_nvfp4_256x128x128_coop_rasterN_sw8` | 6.0892 | −1.1% |
  | 16,384³ | MXFP4 | 6.2477 | `cutlass3x_mxfp4_128x128x128_coop_rasterM_sw4` | 6.2582 | −0.2% |
  | 16,384³ | FP8 | 11.2855 | `lt13_fp8-e4m3_0_1_algo35_tile20` (cuBLASLt still wins) | — | 0 |
  | 8,192³ | NVFP4 | 0.7841 | `cutlass3x_nvfp4_256x128x128_coop_sw2` | 0.7917 | −1.0% |
  | 8,192³ | MXFP4 | 0.8097 | `cutlass3x_mxfp4_256x128x128_coop_sw8` | 0.8154 | −0.7% |

  - I had predicted no change at 8,192³. The orders take about 1% off both FP4 families there, so NVFP4's headline
    divisor (0.78875 ms at 09:03Z) is likely about 1% lenient too. A timed window decides.
  - FP8's CUTLASS kernels also run at half rate in the default order at 32,768³ (184.2 ms), but cuBLASLt was already
    FP8's divisor there, so it doesn't move.
- 16:20Z: **FP8's slices are screen-only now.** At decode a slice spent about 6 of its 7 minutes re-tuning the heuristic
  and CUTLASS candidates and timing finalists, which only the shape's final run needs. cuBLASLt 13.1's space at
  `m32-n8192-k8192` is 134,216 configurations (492,875 checked): split-k up to 16 multiplies it. `--screen-only`
  (`af2d27e04`) gates and screens a slice, then stops. At 4,096³ that is 256 configurations in 12 s and 512 in 17 s.
  I withdrew `harness-fp8-enum-485a6466.sh` at a chunk boundary and queued its version b in the same output directory.
  Version b slices screen-only, doesn't halve a preempted slice, adds the tile orders to each final, and runs the
  split-k shapes last (decode and 2,048³).
  - **FP8 at 8,192³ after the whole enumeration** (version a's final, Measured, screening): 1.4416 ms,
    `lt13_fp8-e4m3_0_algo60_tile20_st15` (the 29th of 13.1's 8,940), against 1.4435 in the 15:35Z check. The whole space
    moves the 8,192³ divisor by about 0.1%.
- 16:20Z: **FP4 tile-order sweep queued** (`harness-fp4-sched-af2d27e0.sh`, prio 10): NVFP4 and MXFP4 with
  `--cutlass-sched` at the 18 panel shapes the tile-order job didn't cover, one shape per chunk, decode as a chain.
- 16:42Z: **the gate's discovery skips a deleted POSIX semaphore** (`e22a2808f`, server.md 16:26Z item 2). The mapping
  `/dev/shm/sem.* (deleted)` is skipped only if it is at most one page and holds no ELF or fatbin. `b7b88c95c` didn't
  cover it.
- 16:55Z: my arm interface v0.5, the transcript replay and the no-write control (`9182e17d7`, `508c7b5ea`; server.md
  11:50Z item 1). Withdrawn at 17:24Z for #583's (below).
- 17:03Z: **checked on the card**, run `r20260930-170037-2a99` (a stand-in arm, not a panel row): the replay wrote D over
  the poison, and the verifier rejected the all-0xA5 control. The judge carried the reject line into the row.
- 17:10Z: the coordinator stopped the sequential FP8 enumeration (`harness-fp8-enum-b-af2d27e0.sh`) at its slice
  boundary; bc-df4a6ef1's split workers (`/workspace/pouw/fill-out/harness-split/split.py`) continue it from my finished
  slices (server.md 17:17Z).
- 17:24Z: **#583 adopted into #491** (`216143c72`, a `--no-ff` merge of `65e700593`; root ruling, server.md 17:17Z). My
  v0.5 is withdrawn, never on origin. #583's is stronger: it syncs around the memset, checks every byte is poison, and
  records the bytes written. Card check of the merge `r20260930-172357-070a` (a stand-in arm and verifier on a throwaway
  branch, not a panel row): the transcript accepted, the `negative/` control rejected.
- 17:40Z: **Pearl-C4 on `dump`** (`8e1ece3b6`, above); untimed card check `r20260930-174056-4c34` launched.
- 18:00Z: **`r20260930-174056-4c34` passes** at both headlines: the harness-poisoned transcripts ACCEPT, the `negative/`
  controls REJECT, and the SASS gate passes cubin `dd01ae5e`. Labelled not a panel row (details under "For GPUs 2 and 5").
- 18:18Z: broker: source=broker (server.md PINNED 17:43Z; checksum matched). The first exchange fell back to Cursor's
  token once, and the retry a minute later took the broker's. The VM was reprovisioned again before this, so the helper
  lives in the fresh `/workspace/.git/verity-auth/` and needs installing again after the next reprovision.
- 3:18 PM PDT (22:18Z): **per-die baseline screen queued** (coordinator 3:02 PM PDT; details under "Fill candidates"):
  `harness-perdie-d0-dd23c0c3.sh` … `harness-perdie-d7-dd23c0c3.sh`, one per die (`on=<die>`), about 13 GPU-h in total
  (Estimated). Staging run `r20260930-221814-c80b` checked the build's hashes and passed the SASS gate once, on the CPU.
  All eight had started by 3:24 PM PDT. The first item, NVFP4 at `m32-n8192-k8192` on die 5, finished with exit 0 in 191 s
  (Measured). The script gives a full chunk only to FP8 items whose label contains `decode`, and the decode headline's
  label doesn't. So that shape's FP8 item may be cut short once per die, and it is then retried with the full budget.
  Task (2), the NVFP4 tile orders, had no uncovered shape: the 16:20Z table (9:20 AM PDT) and the 18-shape sweep
  `fp4-sched-af2d27e0` cover all 21 shapes. So the orders are rerun on every die inside these jobs (`--cutlass-sched`).
  The broker was reinstalled after the VM reset (`source=broker`).
- 3:35 PM PDT (22:35Z): **per-die screen trimmed to the two headline shapes** (coordinator 3:32 PM PDT; server.md PINNED
  3:37 PM PDT, compute-accounting YES). Run `r20260930-223456-fd24` swapped each die's script for a copy that differs only
  in `SHAPES=(m32-n8192-k8192 m8192-n8192-k8192)`: d0 and d2–d7 in `running/`, d1 in `queue/`. Each swap was one
  `renameat2(RENAME_EXCHANGE)`, checked against the staged script's sha256 first, so the runner's `shutil.move` never saw a
  missing file. All eight dies had finished their four headline items by then: about 1.2 GPU-h (Measured, the items'
  `wall_s`). What's left is each in-flight chunk's tail on other shapes, at most about 0.9 GPU-h (7 chunks of at most
  7.6 min; Estimated). At its next start each job finds nothing pending and exits 0. About 11 of the planned 13 GPU-h are
  dropped.
- 3:41 PM PDT (22:41Z): **the timed whole-node window, `r20260930-224059-cb8d`**, at #588's head `dd23c0c36`, build
  bab84c16: `research run --no-sampler … gpu-lease 8 --wait --timed --max-min 20 -- timeout 1140`. It runs the per-die items
  again on the lease's first GPU (NVFP4 and FP8 E4M3 at 8,192³ and `m32-n8192-k8192`, `--cutlass-sched`, `--finalists 3
  --reps 20`, FP8 decode with the frozen names), each baseline behind its bit-exact gate. About 10 min (Estimated from the
  per-die walls). **Shortcut, flagged:** it has no arm. A plain GEMM emits no transcript, so there's no verifier line or
  no-write control, and the result is the divisor table, not a measured panel row. Outputs: `divisors/<shape>/<family>/`.
- 5:15 PM PDT (00:15Z): **the divisor window `r20260930-224059-cb8d` has been read.** It ran 3:41–3:44 PM PDT, and all four
  items exited 0. The table is under "Baselines: the divisors". In short: #543's NVFP4 `_o_ew` is the fastest at 8,192³.
  At FP8 8,192³, `verity_fp8_256x128_ew` (1.4148 ms) is the fastest, not `_o_ew` (1.4173). #588's kernels don't run at
  m = 32. There are two gaps at decode: finalists are ranked on independent calls, and the frozen FP8 names were never
  taken. The VM was reset again, so the broker was reinstalled (`source=broker`).
- 6:32 PM PDT (01:32Z): **#491 at `aa4f95db9`**, after the coordinator's 6:12 PM PDT rulings (code and CPU only, no GPU
  time). The VM was reset again; broker reinstalled (`source=broker`).
  - `9db36fe7d`: a configuration `--lt-enumerate-names` names that the run doesn't take stops it with `NamesNotTaken`
    (exit 2, in the JSON), instead of a log line and exit 0. When the cap cut the list, the message names the
    `--lt-enumerate-max` that reaches the names. `parse` refuses a names file that names nothing, or names a family
    `--lt-enumerate` doesn't enumerate.
  - `88ef0927b`: each library's fastest (each cuBLASLt version, CUTLASS, verity on #588) joins the `--finalists` fastest,
    so it is timed interleaved and, at decode, chained. The JSON lists them (`baseline_candidates.<family>.finalists`).
  - `854e8e51c`, `aa4f95db9`: the names rule moved to a README paragraph of its own, so #588 merges #491 without a
    conflict.
  - Tests: 233 passed, 14 skipped (`benchmarks/pouw/tests`, less `test_route_u_shift.py`), up from 230. The three new
    tests fail on `80bff34cc`. #588's head `dd23c0c36` merged with `aa4f95db9` has no conflict, and its tests give 243
    passed, 14 skipped. Ruff's findings in the three files are the base's 26.
- 7:15 PM PDT (02:15Z): **the confirming divisor row is staged, not run; migration handoff written.** This answers
  bc-2aa33ad8's 6:36 PM PDT ask: CPU only, no GPU time, no card check.
  - The ask was overtaken by compute-accounting's order `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`
    (Daniel, 6:55 PM PDT: no work runs in the old Project any more). My handoff is
    `20261001T0209Z-handoff-from-0de2d624-migration`. The notes push got a 403, so it's in the store outbox
    `internal/pouw-fp8/accounting-outbox/`.
  - **Run tree `cursor/divisor-confirm-tree-d2f2` at `036fe6f93`:**
    - Root: #588 + #491 + GPU 1's `a00db59ee`.
    - `runtree/nvfp4/`: `cursor/divisor-confirm-nvfp4-d2f2` at `3535b07fc` (#588 + #491 + #580 `639128c87`), as the same
      git trees.
    - `runtree/divisor_confirm.sh`, in `card` or `timed` mode.
  - **Why two trees:** GPU 1's and #580's `verity_pouw` can't share a process (GPU 1's `pearl_c_work` reads
    `scheme.device`). Merging both breaks 7 Pearl-C4 tests, its replay among them.
  - **CPU checks:** both arms pass `check_arm` and are in domain at both headlines. The NVFP4 tree passes 368 tests (13
    skipped). The FP8 tree's failures are pre-existing or environmental; the handoff lists them.
  - Launch lines and inputs are in the handoff.
- 17:45Z: **`80bff34cc` on #491**: `poison_dump` refuses a transcript buffer that overlaps the call's operands, the one v0.5
  check #583 lacked that nothing downstream catches (a poisoned operand gives a transcript of 0xA5 inputs that the
  verifier can accept, with its control still rejected). v0.5's other extras were already #583's: the reject line in the
  row, and an accepted control rejects it (exit 1; v0.5's exit 5 isn't kept, so verify.py's 0/1/2 contract stays).
  230 tests pass (`benchmarks/pouw/tests`, less `test_route_u_shift.py`, which needs the workspace install).

## The FTZ gate and today's scan (server.md 09:34Z)

**No shipped kernel fails the gate, and no lane builds with `-ftz=true`, `--use_fast_math` or `-use_fast_math`.**
- I built every lane's shipped device code at its branch head, with its own build script's flags and CUDA 12.9.1, and
  gated it.
- Every build uses `-O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a` (#449's and #510's `pearl_c.cubin`:
  `sm_90a`), plus the flags in the table.
- Where the lane's own run shipped a binary, my build is byte-identical to it (noted in the table).

| Lane | Binary | Commit | Other flags | FP32 `.FTZ` found / exempt | sha256 |
|---|---|---|---|---|---|
| GPU 1, `pearl-c-sm120-b44b` | `pearl_c_sm120.cubin` | `3c9e519c` | `-fmad=false` | 16 / 16 | `eb5dd5e3` |
| GPU 1, `pearl-c-sm120-h1-b44b` | `pearl_c_sm120.cubin` | `124585e5` (and `2e9a013d`) | `-fmad=false` | 16 / 16 | `bfd43d77` |
| GPU 2, `pearl-c-sm120-h1-9569` | `pearl_c_sm120.cubin`; `hash_sm120a.cubin` | `bd1c30b2` (and `f2e5a32e`, identical to GPU 1's panel run `r20260930-093140-286c`) | `-fmad=false` | 16 / 16; 0 | `510b4fcb`; `ad044e6e` |
| bc-fb55a759, `mainloop_sm120.cuh` | a unit that instantiates it | `7b417ee7` | `-fmad=false` | 0 | `cf9ae0d9` |
| bc-fb55a759, `mainloop_bench.cu` | `mainloop_bench.cubin` | `e0e84b25` (identical to `r20260930-100116-01f0`'s) | `-fmad=false` | 16 / 16 | `8a4af5c9` |
| GPU 5, `pearl-c-fp4-3084` | `pearl_c4.cubin`, with `pouw_hash.cuh` at `71086532` (sha256 checked) | `1dad25ce` (and `b39f9559`) | `-fmad=false` | 0 | `45ced127` |
| GPU 2 (bc-b139c29c), `pouw-hash-sm120-9569` | `pouw_hash_bench` (and its `check.o`, `bench.o`) | `ceac4f13` (and `cbe4a3a8`) | `--expt-relaxed-constexpr`, no `-fmad` | 0 | `029f4347` |
| #449, `pearl-c-h100-9ada` | `pearl_c.cubin` (`sm_90a`); `hash_sm120a.cubin` | `61d0298d` | `-fmad=false` | 21 / 21; 0 | `407178e0`; `a1e95e5c` |
| #510, `pearl-c-h1-sm120-tune-b0c4` | `pearl_c.cubin` (`sm_90a`); `hash_sm120a.cubin`; `h1_standin.cubin` | `b78c1420` (`h1_standin` identical to `r20260930-092522-d8ad`'s) | `-fmad=false`; `h1_standin`: none | 21 / 21; 0; 0 | `fd882926`; `9f8b6613`; `62f2ee5f` |
| The harness | `libpouw_harness.so`, `libpouw_lt2.so` | build `art:14fff942…` | the build's | 0 | |

- "(and …)" is the head at the 10:00Z scan. Four branches moved by 10:38Z, and I rescanned them at the new heads; the
  flags didn't change.
- The local builds, their logs and every verdict (`*.gate.json`), with the build scripts:
  `art:a248be4a38db96282ae16be07e5095673435fb5a208327f1a0a7dfa309d0af23` (`out/` at the 10:00Z heads, `out2/` at the
  moved ones).
- `libpouw_lt2.so` has no device code. Named explicitly, a binary without device code fails closed, so node 2's run lists
  it as its one failure. A harness run skips it, as it skips every mapped library without device code.

**Node 2**, run `r20260930-101908-ab9a` (commit `3481cf09`, run record
`art:1ce7541fc5dbb939bf380db7ddf1cdc1a832334a2c3949db7cf8ded1e8fe2924`):
- The gate ran over the 39 distinct binaries shipped in node 2's run directories today: once with CUDA 12.9.1's
  `cuobjdump`/`nvdisasm` and once with node 2's 13.0 (V13.0.85).
- Both verdicts agree on all 39. The gate's tests pass with both toolsets (42 each).
- The harness on node 2 resolves the 13.0 tools unless `CUDA_HOME` or `POUW_CUDA_BIN` is set, so this agreement is what a
  run relies on.

**The table above is the 10:00Z scan, at gate v2.** The same builds (`art:a248be4a…`, plus the mainloop bench, #449 and
#510) all pass gate v4 with the shipped pins at `7f4a67f6b`: no offending instruction in any sm_120a cubin. The harness's
own build `art:14fff942…` fails v4, and `art:4e047f88…` passes (15:00Z checkpoint). #449's and
#510's `sm_90a` `pearl_c.cubin` are refused, as every sm_90a cubin is: no sm_90a toolkit is pinned. I haven't rebuilt
branches that moved after 10:38Z. Every run gates what it loads before timing anyway.

**What the gate does** (`benchmarks/pouw/harness/sass_gate.py`, `sass-gate/v4`; your 11:00Z ruling and the three
conditions of server.md 10:07Z, 10:14Z and 10:21Z).
- **Input and disassembly** as in v2: every cubin in the binary (cubin, fatbin, object, executable or shared library),
  through `nvdisasm`, and `cuobjdump -sass` must list the same instructions.
- **What it flags.** Every instruction with `.FTZ` (`FADD`, `FFMA`, `FMUL`, `FSETP`, `FSET`, `FMNMX`, `F2I`, `F2F`,
  `HADD2` and the rest) and every FP32 `MUFU`. PTX with an ftz f32 op is refused as before.
- **What it exempts: only whole sequences, as the pinned ptxas builds them.**
  - A subroutine whose body has one of its toolkit's pinned signatures: the rcp, sqrt and div slow paths,
    `__cuda_sm20_div_u16`, `__cuda_sm20_div_u64` and `__cuda_sm20_rem_s64`. ptxas specializes a body to its call site,
    so one name may have several pinned bodies (13.0 builds `div_u16` two ways).
  - The rcp, sqrt and div fast paths that branch around a call into a pinned body. Division by a constant numerator is
    included, with the constant checked against `FCHK`'s.
  - The integer-division seed: `MUFU.RCP` of `I2F.RP` of an integer.
  - Every value a sequence computes, other than its result, must be read only by the sequence, on every path through
    predicates, calls and returns. A read that another write also reaches passes as a "merge" and is listed: 22 in
    `hash_leaf`, checked by hand.
- **Keyed to the compiler (condition 2).** The cubin's `.note.nv.tkinfo` (ptxas version, build and arguments, `-v`
  aside) must equal an entry of `sass_pins.json`:
  - 12.9.1 (V12.9.86, `36037853_0`) or 13.0.1 (V13.0.88, `36424714_0`);
  - each with `-arch sm_120a -m 64`, with or without `-fmad false`.
  - Any other ptxas or arguments, a cubin without the note (12.9's sm_90a), or an entry without a numeric run: nothing
    is exempt.
- **rsqrt has no entry (condition 3).** 13.0's default `__frsqrt_rn` emits no `.FTZ` (the assessor's
  `r20260930-101332-226b`), so a bare `MUFU.RSQ` is refused. If GPU 1 ships `__frsqrt_rn`, it gets a sequence of its own,
  with its own numeric check.
- **Refused though exact:** `F2I.FTZ.U32.TRUNC` outside a pinned sequence. It truncates a subnormal to 0 with or without
  FTZ, but your rule refuses it; it gets an entry only if a kernel needs one.

**The numeric pin (condition 1): run `r20260930-135207-db3e`** (Measured).
- Source `5b290af35`; the run record is `art:8de038ff5cd72643eb0da824497453ba1fc6feb792d79f0e1a45db9d1eed527c`
  (`ieee-pin.json`). One `gpu-lease 1` (`GPU-fb680060-f371-db1a-73ba-8f2eef43674c`), 93 s wall.
- **What it does.** `ieee_pin.py` builds `ieee_pin.cu` with each pinned toolkit and flag set and with three negative
  controls, then gates every build:
  - each pinned build must pass and cover every sequence and every pinned body;
  - each control must fail;
  - each toolkit's entry must be exactly what its pinned builds pin.
  Then it runs every binary on the leased GPU. Each binary must report that GPU's UUID.
- **The references.** The float checks compare against double arithmetic rounded once, on the card. The host checks
  compare every subnormal input against the host, off the card: under `-ftz=true` the device's own reference flushes
  alike, so only the host checks catch that control. NaNs compare equal whatever their payload; everything else is
  compared bit for bit.
- **Both toolkits, both pinned builds (default and `-fmad=false`): 0 differences anywhere.**

| Check | Inputs | Subnormal inputs | Subnormal outputs |
|---|---|---|---|
| rcp (`__frcp_rn`) | all 2^32 | 16,777,214 | 33,554,430 |
| sqrt (`sqrtf`) | all 2^32 | 16,777,214 | none possible |
| div (`a / b`) | 2^32 pairs, weighted to subnormals | 1,005,716,801 | 213,610,692 |
| 3 / b, and a / b in the same kernel | 2^32 each | 16,777,214; 551,058,482 | 8,388,606; 197,863,028 |
| u16 (looped, and as a call), u32, s32, u32 by 64 uniform divisors | 2^32 each (division by zero skipped) | | |
| u64, s64 | 2^30 each | | |
| host: rcp, sqrt, div, 3 / b | 50,331,646 each (every subnormal input, and every input with a subnormal reciprocal) | 16,777,214 for rcp and sqrt | 33,554,430 for rcp |

- **The controls all differ** (differences, the same on both toolkits):
  - `--use_fast_math`: sqrt 359,384,981, div 731,953,381, and every host check;
  - `-ftz=true`: host rcp 46,137,340 and host sqrt 16,777,214; the on-card checks agree, as they flush alike;
  - `-prec-div=false -prec-sqrt=false`: sqrt 360,813,179, div 845,842,198.
- **13.0 is also checked independently.** The assessor found 13.0's `div.rn`, `rcp.rn` and `sqrt.rn` exact
  (`r20260930-095650-85ec`, `internal/pouw/red-team/fp-model-sm120-scalar.md`). 13.0.1's entry cites it.
- A test ties each entry's numeric record to `ieee_pin.py`'s build lines. A repin that changes a body drops the record,
  and that toolkit exempts nothing until `ieee_pin.py` runs again.

**Caveats, flagged.**
- The 22 merged reads in `hash_leaf` are checked by hand, not by the gate.
- A context-specialized body is trusted for ptxas's preconditions at its call site: 13.0's second `div_u16` body assumes
  a zero-extended dividend.
- Targets of an indirect branch (`BRX`) are assumed not to land inside a fast path.
- A function whose only division has a constant numerator is refused: ptxas builds that case in a way `ieee_pin.cu`
  doesn't pin (it pins the constant beside another division, sharing one slow path).
- FP64 `MUFU` is counted, not gated.
- sm_90a is unpinned.

**Arms must name their binaries (arm interface v0.3).**
- From `213a5b5a` on, `build()` returns `"binaries": [str(path), ...]`: every cubin, fatbin or library its kernels come
  from. A cubin loaded with `cuModuleLoadData` isn't mapped into the process, so the harness can't find it otherwise.
- An arm without the list exits 7 before timing. Today that is GPU 1's `pearlc_arm` and GPU 5's `pearl_c4_arm`.
- The fix is one line in each `build()` record: `"binaries": [str(cubin)]`.
- Nobody is blocked yet: FP8 arms time on `0d1d6615` and FP4 arms on `36df5171`, both before the gate. A measured row
  needs panel rules (a) and (b), and so the harness that has the gate.

## Panel rules (a) and (b)

**(a) is done** (server.md 08:50Z; `dcff1b68`). Per shape:
- **Warm-up.** Before the reps, the same interleaved schedule runs untimed until at least `--warmup-s` (10) seconds of
  device time have passed and a round's median SM clock is within 0.5% of the round before. `--warmup-max-s` (60) bounds
  it, and the shape's `warmup` block says whether it got steady. Its items are kept apart, in `warmup_items`.
- **Equal-duration reps.** Every timed item is sized to the same device time: at least `--item-ms` (40), and at least the
  longest item's natural length. A baseline or an arm gets more calls; a dependent chain gets more replays of its 64-call
  graph. The shape's `sizing` block records each entry's calls, replays and item ms.
- **Clocks.** Every item samples NVML while the GPU runs it (`sensors.during`), beside the before and after samples.
- **The panel row.** Each arm's `panel` block holds `reps`: per side (arm and baseline), every rep's ms per call, item ms
  and SM clock. It also holds `sm_clock_arm` and `sm_clock_base`, comma-separated as `panel.py` takes them, and
  `clock_gap` when the medians are more than 0.5% apart. If any rep has no clock, the block says `sm_clock_missing`
  instead.

**(b) is done** (server.md 08:35Z; `8d04bfe5`): the arm emits the transcript its verifier checks, and the same run runs
the verifier.
- **Arm interface v0.4.** `build()`'s record names the arm's `verifier`, which `bench.py` checks before anything is timed:
  - `transcript`: the file the verifier checks, relative to the run's directory, with `{arm}` and `{shape}`;
  - `commands`: argv lists, run once per shape (`per: "shape"`, the default) or once per run (`per: "run"`), with the
    placeholders `{python}`, `{run_dir}`, `{run_id}`, `{commit}`, `{arm}`, and per shape also `{shape}`, `{transcript}`
    and `{dir}`;
  - `commit`, only if the verifier isn't the run's source commit.
  - The arm writes its transcripts under `ctx["transcripts_dir"]` (the run's `transcripts/`).
- **The verify step** (`verify.py RESULT_JSON`) runs after the lease, in the same `research run`, so no GPU waits on the
  CPU verifier. The run line is in the harness's README.
- **What counts as acceptance.** A transcript is accepted only by an output line that starts with `ACCEPT` and names
  `sha256:<hex>` of the transcript file, as the step hashes the file itself after the commands ran. A `REJECT` line
  naming it rejects it, and so does a failing command of its shape.
- **What it writes.** Each panel row gets `verifier_commit`, `verifier_accept` (verbatim), `transcript`
  (`"<run id>:<path> sha256:<hex>"`) and `panel_args`: every `panel.py append` argument except `--line`, `--version`,
  `--change` and `--description`. The result JSON gets `verification`, with every command's exit code; each command's
  output is kept under `verify/`.
- **Exit codes.** 0 only if every panel row was accepted and every command exited 0; 1 otherwise, each row saying why; 2
  with no run id or commit.
- An arm without a verifier gets no measured row.
- **Checked on CPU, not yet on a real verifier.** The tests use verifiers shaped like both below. That both real
  verifiers print the sha256 of exactly the file the harness hashes (GPU 1's `manifest.json`, GPU 5's `transcript.json`)
  I checked by reading their code.

**What GPUs 1 and 5 add to `build()`'s record** (with `binaries`, v0.3):
- **GPU 1** (`pearlc_arm`, #449's audit through your `verify.py`, which checks the whole run). Both of your arms declare the
  same command, so it runs once:

~~~python
"binaries": [str(cubin)],
"verifier": {"per": "run", "transcript": "transcripts/{arm}/{shape}/manifest.json",
             "commands": [["{python}", str(HERE / "verify.py"), "{run_dir}", "--commit", "{commit}"]]},
~~~

- **GPU 5** (`pearl_c4_arm`, the Pearl-C4 replay). Dump under `ctx["transcripts_dir"]` rather than `PEARLC4_TRANSCRIPTS`,
  or set `PEARLC4_TRANSCRIPTS="$RESEARCH_RUN_DIR/transcripts"` in the run line:

~~~python
R = ["{python}", "-m", "verity_pouw.schemes.pearl_c4_replay"]
"binaries": [str(cubin)],
"verifier": {"transcript": "transcripts/{arm}-{shape}/transcript.json",
             "commands": [R + ["prove", "{dir}", "--run", "{run_id}", "--out", "{transcript}"],
                          R + ["verify", "{transcript}", "--out", "{dir}/verify.json",
                               "--path", "{run_id}:transcripts/{arm}-{shape}/transcript.json", "--commit", "{commit}"]]},
~~~

## Baselines: the divisors

### #588's plain GEMMs in the timed whole-node window (3:41 PM PDT)

Run `r20260930-224059-cb8d` (outputs `art:9ced8dcf…`, `divisors/<shape>/<family>/bench.json`): `gpu-lease 8 --timed`,
3:41–3:44 PM PDT, timed on GPU 0 (`GPU-5f1149a4`), #588's head `dd23c0c36`, build bab84c16, `--cutlass-sched`,
`--finalists 3 --reps 20`. All four items exited 0. Per-call ms, graph method, median (Measured).

- "Timed" means one of the three finalists, interleaved, 20 reps, given with its p10–p90.
- "Tune" means 3 graph reps, before warm-up. A library entry that wasn't a finalist has only a tune time.
- Ratios are Derived, tune against tune, so they compare the same stage.

| Family, shape | #588's plain GEMM | Best cuBLASLt (tune) | Best CUTLASS | Fastest |
|---|---|---|---|---|
| NVFP4, 8,192³ | `verity_nvf4_256x128_o_ew` **0.7245** timed (0.7244–0.7248); tune 0.7272 | 13.1.1 `lt13_nvfp4_0_2_algo70_tile20` 0.8065 (12.9.2 `lt_nvfp4_0_2_algo70_tile20` 0.8129) | `cutlass3x_nvfp4_256x128x128_coop_rasterN_sw8` 0.7861 (tune) | `_o_ew`: 0.925× CUTLASS, 0.902× cuBLASLt. `_ew` is 0.7248 timed, overlapping it |
| FP8 E4M3, 8,192³ | `verity_fp8_256x128_o_ew` **1.4173** timed (1.4164–1.4181); tune 1.4261. `verity_fp8_256x128_ew` **1.4148** timed (1.4141–1.4153) | 13.1.1 `lt13_fp8-e4m3_0_1_algo35_tile20` 1.4531 (12.9.2 `lt_fp8-e4m3_0_0_algo35_tile20` 1.4538) | `cutlass3x_fp8_256x128x64_coop_rasterM` 1.4656 (tune) | `_ew`, 0.17% faster than `_o_ew` (their p10–p90 don't overlap). `_o_ew`: 0.981× cuBLASLt, 0.973× CUTLASS |
| NVFP4, m = 32 decode | none: #588's kernels need m to be a multiple of 256, so they weren't candidates | 12.9.2 `lt_nvfp4_0_1_algo70_tile20` 0.03888 (13.1.1 0.03891) | `cutlass3x_nvfp4_128x32x256_coop_swap`: 0.03015 timed, independent calls; **0.03565** as the dependent chain (derive 0.00515) | CUTLASS: 0.805× cuBLASLt (tune). The 09:03Z chain was 0.03581 |
| FP8 E4M3, m = 32 decode | none, for the same reason | 12.9.2 `lt_fp8-e4m3_0_3_algo35_tile13` 0.0522 (13.1.1 `lt13_fp8-e4m3_0_1_algo35_tile15` 0.0541). Heuristic candidates only (below) | `cutlass3x_fp8_128x32x128_coop_swap_rasterN`: 0.05003 timed, independent; **0.05343** as the chain (derive 0.00327) | CUTLASS on independent calls: 0.980× cuBLASLt (tune). On the chain, not settled (below) |

**Gates.** Every candidate passed its bit-exact gate: NVFP4 8,192³ 152 of 152 (6 verity, 132 CUTLASS, 14 cuBLASLt); FP8
8,192³ 100 of 100 (4, 84, 12); NVFP4 decode 48 of 48 (33 CUTLASS, 15 cuBLASLt); FP8 decode 37 of 37 (21, 16). The gate
runs ternary operands at the exact shape and flag set, and compares 32 sampled rows and 32 sampled columns of D, bit for
bit, against numpy. It found 0 mismatches and 0 unwritten words. Every item's negative controls were rejected:
`flip-output-byte` and `half-k`, plus `chain-stale-a` at decode.

**Clocks.** The SM clock during timing was 2,085–2,092 MHz. During both prefill items' timed reps, `sw_power_cap` was set
in 349 and 352 of 360 sensor samples, and in none during the tune. It applies to all three finalists alike, which at
prefill were all verity kernels. Decode items had no throttle.

**What the run supports.**
- Prefill, NVFP4: yes. #543's `_o_ew` is the fastest plain NVFP4 GEMM here, 7.5% under the best CUTLASS (tune against
  tune), on one die.
- Prefill, FP8: a verity plain kernel as the divisor, yes, 1.9% under cuBLASLt (tune against tune). But the fastest is
  `verity_fp8_256x128_ew` at 1.4148 ms, not `_o_ew` at 1.4173. The divisor is the fastest plain path, so it is `_ew`
  unless the per-die screen shows the order isn't stable.
- Against the coordinator's numbers, 1.4173 ms against cuBLASLt's 1.4546 ms: this run's best cuBLASLt is 1.4531 ms, a
  tune time. Setting it against the timed 1.4173 gives 0.975, which mixes stages and widens the gap from 1.9% to 2.5%.
- Decode: nothing to adopt. #588's kernels don't run at m = 32, so the decode divisors stay the plain libraries'.

**Two gaps at decode** (shortcuts; the per-die screen has the same two):
1. **Finalists are ranked on independent calls.** The decode divisor is the dependent chain, but `--finalists 3` picks by
   independent tune time. At FP8 decode, the three finalists were CUTLASS (0.0511–0.0516 tune), and cuBLASLt's 0.0522 came
   fourth, so it got no chain. At 09:03Z its chain was 0.05270 ms (`r20260930-085331-f280`), under this run's CUTLASS chain
   of 0.05343. This run's FP8 decode divisor may therefore be lenient by about 1.4% (Derived, across runs).
2. **The frozen FP8 decode names weren't used.** The 16 names (`inputs-bab84c16/names/m32-n8192-k8192.txt`) are all
   13.1.1 `algo67` configurations. The enumeration keeps only its first 8,192 per library (`--lt-enumerate-max`, default
   `LT_ENUMERATED_MAX`) of the 134,216 it accepted, and took none of the 16. bench.py logs that and exits 0. So the
   cuBLASLt side there is the heuristic's 16 only. A names file needs `--lt-enumerate-max` of at least the space, and a
   run that takes none of its names should fail rather than log: it's a guard failing open, in my harness (#491).

**What a confirming timed row still needs.** This is one run with no PoUW arm, so it makes no panel row.
- **A verified arm.** A divisor reaches the panel only as the denominator of an arm's measured row. That needs a PoUW arm
  with `dump` and a verifier, timed interleaved with the divisor in the same run, on the same die. Its transcript must be
  ACCEPTed and its no-write control REJECTed (verify.py `--tier 2b`), with both sides' per-rep SM clocks.
- **Libraries timed as finalists.** The best cuBLASLt and CUTLASS entries should be timed interleaved too, not only tuned.
  At prefill, the three finalists were all verity variants. In the tune, the best CUTLASS and cuBLASLt entries ranked 7th
  and 17th of NVFP4's 39 tuned candidates, and cuBLASLt and CUTLASS ranked 4th and 10th of FP8's 31.
- **At decode,** the chain timed for the best of each library, and the FP8 names actually taken.
- **The per-die headline results.** Their winner and ratio on every die, to show the divisors don't depend on the die
  (not yet read).

**The headline divisors** (Measured, GPU 0, locked-2100, one timed window at 09:03Z; details and caveats below):

| Headline | FP8 (`fp8-e4m3`, per-tensor) | FP4 (`nvfp4`) | Method | Run |
|---|---|---|---|---|
| Prefill `m8192-n8192-k8192` | **1.4460 ms** (`lt_fp8-e4m3_0_0_algo35_tile20`, 94.2% of peak) | **0.78875 ms** (`cutlass3x_nvfp4_256x128x128_coop`, 86.4% of peak), divisor possibly lenient, by at most 8.3% | graph of independent calls | `r20260930-085331-f280`. FP8 is within 0.1% of the 06:31Z and 07:48Z windows; NVFP4 was 0.8037 (128×128 tile) |
| Decode `m32-n8192-k8192` | **0.05270 ms** (`lt_fp8-e4m3_0_3_algo35_tile13`) | **0.03581 ms** (`cutlass3x_nvfp4_128x32x256_coop_swap`), divisor possibly lenient | dependent chain, 64 calls | `r20260930-085331-f280`, within 0.2% of `r20260930-074616-9ec9` |

### The FP4 baseline search (09:03Z)

**The result.** No library on this card times NVFP4 near FP8's peak fraction.
- The search's best NVFP4 GEMM at 8,192³ is CUTLASS's 256×128×128 cooperative tile, at 0.78875 ms and 86.4% of the NVFP4
  peak. That is 1.9% faster than the 128×128 tile it replaces, against FP8's 94.2%.
- cuBLASLt 12.9 and 13.1 each have one NVFP4 kernel on sm_120, and neither has any MXFP4 kernel.
- Every block-scaled kind sits 7–11 points under its unscaled neighbour, in both libraries (the evidence is below).
- So FP4 keeps the label "divisor possibly lenient", now bounded. At FP8's 94.2% the NVFP4 divisor would be 0.7232 ms: 8.3%
  under today's, which would raise every FP4 prefill ratio by up to 9.1% (Derived).

**Measured**, run `r20260930-085331-f280` (run record `art:05ca4ebb16572f935f749b5e422fd1e02c2654c862961be7f87ccdd14f575c38`,
`bench.json`).
- GPU 0, `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`, locked-2100, with the node held (09:01:28–09:02:55Z).
- Clocks: SM 2,085 MHz median at prefill and 2,092 at decode. Every prefill family ran at 413–414 W median, with throttle 0x4
  (the software power cap) on 70–75% of its items, so no family got a different clock.
- Harness `36df5171`, build `art:14fff942…`. 40 reps, 32 heuristic candidates per cuBLASLt, 4 finalists per family, and
  `--lt-enumerate nvfp4 mxfp4`.

**What was searched.**
- **cuBLASLt, both versions, enumerated by hand:** 12.9.2.10, and node 2's `/usr/local/cuda` library.
  - That library is **13.1.1.3**, not 13.0: CUDA 13.0's `libcublasLt.so.13` points at it.
  - The enumeration takes every algorithm id, then every tile, stage count, cluster shape, split-k with each reduction
    scheme, swizzle and custom option the caps allow. Each configuration is checked with `cublasLtMatmulAlgoCheck`, then
    gated.
  - Split-k runs 1 to 16 where 128×128 tiles underfill the card (decode), and is 1 elsewhere.
  - **NVFP4** at prefill: 12.9 checked 4 configurations and accepted 3; 13.1 checked 638 and accepted 3. At decode: 46 and
    680 checked, 3 accepted each. Every accepted configuration is algorithm 70, tile 20 (128×128), 37 stages. The one
    configuration per library the heuristic doesn't return tunes no faster (0.8137 and 0.8088 ms).
  - 13.1's algorithm 70 tunes 0.8% faster than 12.9's (0.8072 against 0.8137 ms), and is still 2.6% behind CUTLASS's
    256×128.
  - **MXFP4:** the heuristic fails with status 7 (INVALID_VALUE) in both versions, and none of the 2 and 636 enumerated
    configurations is accepted.
- **CUTLASS v4.8.0's sm_120 block-scaled kernels:**
  - 13 NVFP4 kernels: 128×128×128 cooperative and pingpong; 128×128×256 cooperative and pingpong; 128×256×128 and
    256×128×128 cooperative; 128×128×128 stream-K; the swapped 128×32×256 and 128×64×256, each also as stream-K.
  - 6 MXFP4 kernels.
  - Stream-K zeroes its fixup workspace on every call, inside the timed call, and its gate checks the second call.

**Prefill, `m8192-n8192-k8192`** (graph; % of the card's mma.sync peak for the family's kind: BF16 403.7, E4M3 807.2,
MXF8 806.1, NVFP4 1,614.0, MXFP4 1,612.6, S8 807.5 TFLOPS)

| Family | graph ms | TFLOPS | % of peak | p10–p90 ms | burst ms | Kernel (graph) | Runner-up, graph ms |
|---|---|---|---|---|---|---|---|
| `bf16` | 2.84020 | 387.1 | 95.9% | 2.83896–2.84239 | 2.84941 | `lt13_bf16_0_1_algo21_tile23` | `lt_bf16_0_0_algo21_tile23` 2.84022 |
| **`fp8-e4m3`** | **1.44602** | 760.4 | **94.2%** | 1.44457–1.44906 | 1.46038 | `lt_fp8-e4m3_0_0_algo35_tile20` | `lt13_fp8-e4m3_0_0_algo35_tile20` 1.44663 |
| `mxfp8` | 1.57024 | 700.2 | 86.9% | 1.56828–1.57227 | 1.58073 | `lt13_mxfp8_0_0_algo70_tile20` | `lt_mxfp8_0_0_algo70_tile20` 1.57707 |
| `fp8-blk128` | 1.64014 | 670.4 | 83.0% | 1.63929–1.64120 | 1.64375 | `cutlass3x_fp8_groupwise_128x128x128_coop` | `cutlass3x_fp8_groupwise_64x128x128_pingpong` 1.93555 |
| **`nvfp4`** | **0.78875** | 1,394.0 | **86.4%** | 0.78787–0.79000 | 0.79114 | `cutlass3x_nvfp4_256x128x128_coop` | `cutlass3x_nvfp4_128x128x128_coop` 0.80351 |
| `mxfp4` | 0.81426 | 1,350.3 | 83.7% | 0.81358–0.81570 | 0.81683 | `cutlass3x_mxfp4_256x128x128_coop` | `cutlass3x_mxfp4_128x128x128_coop` 0.81668 |
| `int8` | 1.48695 | 739.4 TOPS | 91.6% | 1.48593–1.48872 | 1.48972 | `cutlass2x_int8_256x128x64_s3` | `cutlass2x_int8_128x256x64_s3` 1.49508 |

- NVFP4's third finalist was cuBLASLt 13.1's algorithm 70, at 0.80916 ms.
- The other NVFP4 kernels, from the tuning sweep (ms, Measured, not interleaved):
  - 128×128 stream-K 0.858, and cuBLASLt's split-k variants with reduction 2 at 0.855–0.856.
  - 128×128×256 pingpong 0.873, 128×128 pingpong 0.882, 128×128×256 cooperative 0.885, 128×256 cooperative 1.157.
- cuBLASLt 13.1 moves `mxfp8` 0.4% (1.5767 to 1.5702 ms) and `bf16` by nothing (0.00%).

**Decode, `m32-n8192-k8192`, dependent chain** (the panel's decode divisor; the method is under "Decode as a dependent
chain" below)

| Family | chain ms | vs 07:48Z | Kernel | Independent graph, same kernel | f alone |
|---|---|---|---|---|---|
| `bf16` | 0.10572 | −0.3% | `lt13_bf16_0_4_algo21_tile20` | 0.10191 | 0.00419 |
| **`fp8-e4m3`** | **0.05270** | +0.2% | `lt_fp8-e4m3_0_3_algo35_tile13` | 0.05164 | 0.00385 |
| `mxfp8` | 0.07517 | +0.1% | `lt_mxfp8_0_0_algo70_tile20` | 0.07274 | 0.00432 |
| `fp8-blk128` | 0.05603 | 0.0% | `cutlass3x_fp8_groupwise_64x128x128_pingpong` | 0.05344 | 0.00385 |
| **`nvfp4`** | **0.03581** | +0.1% | `cutlass3x_nvfp4_128x32x256_coop_swap` | 0.03127 | 0.00561 |
| `mxfp4` | 0.03474 | 0.0% | `cutlass3x_mxfp4_128x64x256_coop_swap` | 0.03087 | 0.00512 |
| `int8` | 0.05479 | −0.4% | `cutlass2x_int8_64x128x128_s3` | 0.05268 | 0.00437 |

At decode, stream-K is slower in the chain: NVFP4's 128×32 stream-K takes 0.04099 ms against 0.03581.

**Why NVFP4 stops at 86%, not 94%** (evidence):
1. **Not the library.** Both cuBLASLt versions offer one NVFP4 kernel, and CUTLASS's best beats it by 2.6% (interleaved).
2. **No longer L2 bandwidth.**
   - Per 128-deep k-step, the 256×128 tile reads 27,648 bytes (A 16,384 plus its UE4M3 scales 2,048; B 8,192 plus 1,024)
     for 8.39 MFLOP. At 1,394 TFLOPS that is 4.59 TB/s from L2, under the measured 5.0–6.0 TB/s (Derived).
   - The 128×128 tile needed 6.0 TB/s at 1,368 TFLOPS, at the ceiling, as does FP8's 128×128 at 760 TFLOPS (5.94 TB/s).
   - The bigger tile cut bytes per FLOP by 25% and bought only 1.9%, so another limit binds.
3. **Block-scaled MMAs lose 7–11 points in every library.**
   - Scaled kinds: MXFP8 86.9% (cuBLASLt 13.1's algorithm 70), NVFP4 86.4%, MXFP4 83.7%, FP8 blockwise 83.0%.
   - Unscaled kinds: FP8 94.2%, BF16 95.9%, INT8 91.6%.
   - MXFP8 runs at FP8's rate on FP8's bytes plus 3% of scales, yet sits 7.3 points under FP8.
   - The scaled mma.sync kinds run at full rate in isolation: 806.1 and 1,614.0 TFLOPS, against 807.2 unscaled (the card
     table below).
   - So the loss is in how the mainloops feed the scaled MMA. My reading, not measured: scale-factor loads and their
     register moves.
   - Caveat: MXFP8's 128×128 tile needs 5.64 TB/s, near the L2 ceiling, so L2 may cost MXFP8 part of its gap.
4. **Not power or clock.** Every prefill family ran at the same 413–414 W median, 2,085 MHz and throttle share.
5. **What's untried, with bounds.**
   - **Stream-K at 256×128:** at most 1.0%. The 2,048 tiles over 188 SMs make 10.89 waves, and a perfect tail gains
     1 − 10.89/11 (Derived).
   - **CUTLASS's tile raster and swizzle:** nothing at 8,192³, where A, B and their scales (72 MiB) fit in L2. They matter
     at 32,768³ (the sweep below).
   - **A block-scaled mainloop of our own that feeds the MMA better than CUTLASS v4.8.0 and cuBLASLt do:** kernel work of
     its own, the only lever left at 8,192³ (up to 8.3%). It is the same work as GPU 5's arm mainloop; bc-fb55a759 writes
     it, as one header for both (09:32Z).
6. The SASS static-mix run `r20260930-085445-609c` was inconclusive, because the loop is rolled. Don't cite it.

**The FP4 panel rows the divisor changes.** I haven't edited them; their owners append re-timed rows. Line numbers are those
of `internal/pouw/panel/attempts.jsonl` at 09:15Z.
- **Measured: attempt 5 prefill** (line 18, 3.1632×, bc-71c6ab78, `r20260930-064339-7ccf`), voided at 08:18Z (line 84).
  - Its arm's 2.546 ms over the new divisor is 3.228× (Derived); its run divided by its own 0.805 ms.
- **Estimated from attempt 5's measured steps** (basis `components`, all over about 0.805 ms):
  - attempt 6 prefill, 2.85 (lines 22, 72, 73; bc-71c6ab78 and bc-a8466279);
  - attempt 13, 2.85 and 2.852 (lines 52 and 63 by bc-2aa33ad8, line 97 by bc-a8466279).
  - Re-priced over 0.78875 ms, they rise by 2.1% (×1.0206) if the arm's time holds (Derived).
- **Candidates off the plots:** attempts 14–17 (lines 75–78, bc-a8466279; renumbered into versions of their own at 08:47Z,
  lines 98–101) reuse attempt 6's figure, so the same factor applies when they are priced.
- **At 16,384³:** line 74 (attempt 6, basis `paper`, bc-a8466279) reuses the 8,192³ estimate.
  - The sweep's NVFP4 divisor there is 6.081 ms (`cutlass3x_nvfp4_256x128x128_coop`, 89.6%). That is 3.4% under the
    7be37429 autotune's 6.294, in untimed screening.
- **Unchanged:**
  - the decode rows (attempt 5 line 20, attempt 6 line 24, attempt 7 line 25): decode's divisor didn't move;
  - the design estimates that don't divide by a timed baseline (attempts 1–4, lines 10–13; attempt 3, line 16; attempts
    8–12, lines 41–45);
  - every FP8 row.

**The sweep at the 21 panel shapes** (screening).
- The run: untimed fill job `harness-fp4-sweep-36df5171.sh`, on whichever GPU the lease gave
  (`GPU-1cd543c7-ad34-75a8-ebfe-863061d1954a`), 20 reps, 09:04–09:11Z. Outputs: `art:f3f2aefd…`, one `bench.json` per shape.
- How to read it:
  - The divisor is the dependent chain at m = 32 and the graph elsewhere.
  - % of peak is the independent graph's TFLOPS over the mxf4nvf4 peak.
  - "vs 7be37429" compares independent graphs with the infra lane's autotune fill run (`autotune-full`, harness `7be37429`).
    It's blank at the headlines, where that run has no output; the timed windows compare them.
- This is screening. The fill runs beside other jobs, and the same kernel differs by up to 2.4% between the two runs, so read
  moves under about 3% as noise.
- The headlines reproduce the timed window on another GPU: NVFP4 0.78868 against 0.78875 ms at prefill, and 0.03578 against
  0.03581 at decode.

| Shape (m, n, k) | NVFP4 divisor ms | Kernel | % of peak | vs 7be37429 | MXFP4 divisor ms | Kernel | % of peak | vs 7be37429 |
|---|---|---|---|---|---|---|---|---|
| `m8192-n8192-k8192` | 0.78868 | `cutlass3x_nvfp4_256x128x128_coop` | 86.4% |  | 0.81436 | `cutlass3x_mxfp4_256x128x128_coop` | 83.7% |  |
| `m32-n8192-k8192` chain | 0.03578 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 8.6% |  | 0.03475 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 8.7% |  |
| `m2048-n2048-k2048` | 0.02497 | `lt_nvfp4_0_2_algo70_tile20` | 42.6% | +0.1% | 0.02470 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 43.1% | +0.1% |
| `m4096-n4096-k4096` | 0.12059 | `cutlass3x_nvfp4_256x128x128_coop` | 70.6% | +0.1% | 0.12407 | `cutlass3x_mxfp4_256x128x128_coop` | 68.7% | −0.9% |
| `m16384-n16384-k16384` | 6.08129 | `cutlass3x_nvfp4_256x128x128_coop` | 89.6% | **−3.4%** | 6.26816 | `cutlass3x_mxfp4_256x128x128_coop` | 87.0% | **−6.5%** |
| `m32768-n32768-k32768` | 49.68613 | `lt_nvfp4_0_algo70_tile20_st37` | 87.7% | −0.1% | 95.09731 | `cutlass3x_mxfp4_256x128x128_coop` | **45.9%** | **−4.3%** |
| `llama3.1-70b-down-decode` (32, 8192, 28672) chain | 0.11407 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 9.2% | −2.4% | 0.11242 | `cutlass3x_mxfp4_128x64x256_coop_swap_streamk` | 9.1% | −1.7% |
| `llama3.1-70b-down-prefill` (2048, 8192, 28672) | 0.72728 | `cutlass3x_nvfp4_256x128x128_coop` | 82.0% | **−3.9%** | 0.75089 | `cutlass3x_mxfp4_256x128x128_coop` | 79.5% | −0.9% |
| `llama3.1-70b-gate_up-decode` (32, 57344, 8192) chain | 0.18953 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 10.1% | −0.9% | 0.17998 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 10.6% | −0.8% |
| `llama3.1-70b-gate_up-prefill` (2048, 57344, 8192) | 1.41163 | `lt_nvfp4_0_2_algo70_tile20` | 84.5% | +0.6% | 1.45225 | `cutlass3x_mxfp4_128x128x128_coop` | 82.2% | +0.6% |
| `llama3.1-70b-o-prefill` (2048, 8192, 8192) | 0.22222 | `cutlass3x_nvfp4_256x128x128_coop` | 76.6% | **−5.4%** | 0.22915 | `cutlass3x_mxfp4_256x128x128_coop` | 74.4% | **−3.4%** |
| `llama3.1-70b-qkv-decode` (32, 10240, 8192) chain | 0.04234 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 8.6% | +0.2% | 0.04093 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 8.8% | +0.1% |
| `llama3.1-70b-qkv-prefill` (2048, 10240, 8192) | 0.26935 | `lt_nvfp4_0_1_algo70_tile20` | 79.0% | +0.1% | 0.27044 | `cutlass3x_mxfp4_128x128x128_coop` | 78.8% | +0.2% |
| `qwen2.5-7b-down-decode` (32, 3584, 18944) chain | 0.05093 | `cutlass3x_nvfp4_128x32x256_coop_swap_streamk` | 6.6% | −2.4% | 0.05195 | `cutlass3x_mxfp4_128x64x256_coop_swap_streamk` | 6.2% | **−11.7%** |
| `qwen2.5-7b-down-prefill` (2048, 3584, 18944) | 0.23802 | `cutlass3x_nvfp4_128x128x128_coop_streamk` | 72.4% | −2.2% | 0.26126 | `cutlass3x_mxfp4_128x128x128_coop` | 66.0% | +0.1% |
| `qwen2.5-7b-gate_up-decode` (32, 37888, 3584) chain | 0.06294 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 9.0% | +0.6% | 0.06067 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 9.4% | −0.7% |
| `qwen2.5-7b-gate_up-prefill` (2048, 37888, 3584) | 0.45170 | `lt_nvfp4_0_algo70_tile20_st37` | 76.3% | +0.3% | 0.46471 | `cutlass3x_mxfp4_256x128x128_coop` | 74.2% | −1.8% |
| `qwen2.5-7b-o-decode` (32, 3584, 3584) chain | 0.01557 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 4.5% | −0.1% | 0.01717 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 3.9% | −0.1% |
| `qwen2.5-7b-o-prefill` (2048, 3584, 3584) | 0.05825 | `lt_nvfp4_0_2_algo70_tile20` | 56.0% | −0.1% | 0.05953 | `cutlass3x_mxfp4_128x128x128_coop` | 54.8% | −0.1% |
| `qwen2.5-7b-qkv-decode` (32, 4608, 3584) chain | 0.01648 | `cutlass3x_nvfp4_128x32x256_coop_swap` | 5.4% | +0.6% | 0.01750 | `cutlass3x_mxfp4_128x64x256_coop_swap` | 4.8% | +0.0% |
| `qwen2.5-7b-qkv-prefill` (2048, 4608, 3584) | 0.07502 | `cutlass3x_nvfp4_256x128x128_coop` | 55.9% | −0.2% | 0.07685 | `cutlass3x_mxfp4_256x128x128_coop` | 54.6% | **−3.1%** |

- The 256×128 tile wins most prefill shapes. cuBLASLt's algorithm 70 still wins NVFP4 at 2,048³, 32,768³, and the Llama
  gate_up and qkv and the Qwen gate_up and o prefills. Stream-K wins where k is long against m × n (Qwen's down projection).
- **At 32,768³ every CUTLASS FP4 kernel runs at about half rate.** NVFP4's CUTLASS kernels take 99.7–105.9 ms and MXFP4's
  94.8–99.6, against cuBLASLt's NVFP4 at 49.7 ms (87.7%).
  - My reading (Derived, not measured): the harness launches CUTLASS with its default tile raster (swizzle 1).
  - So one wave of 188 tiles along one dimension reads 188 panels of the other operand, 2.1–2.3 MiB each with scales.
    That is 400–423 MiB, 3.1–3.3× the L2, so each wave streams its panels from DRAM.
  - That is 0.27–0.29 ms of DRAM against 0.125 ms of MMA per wave: roughly 2× predicted, 2.13× measured.
  - cuBLASLt's split-k −2 configurations (reduction 2) show the same 2.13×.
  - At 16,384³ there are only 128 row tiles, so a wave's panels come to 136–144 MiB, about the L2's size, and they are reused
    over the next columns. At 8,192³ everything fits.
  - So **MXFP4's divisor at 32,768³ is about 2× lenient** (45.9% of peak), because MXFP4 has only CUTLASS. NVFP4 there is
    unaffected, because cuBLASLt wins.
  - The fix is next: tune CUTLASS's swizzle and raster order per kernel, as cuBLASLt's configurations are tuned.
  - **Done at 16:06Z** (checkpoint above): with max swizzle 2, MXFP4's 256×128 takes 48.877 ms (Measured, screening),
    against 94.006 at the default order. NVFP4 wasn't unaffected after all: its 256×128 with the orders takes 47.043 ms,
    5.4% under cuBLASLt. This table's 32,768³ rows are superseded (16:20Z table); a timed window will replace them.

### Decode as a dependent chain: the panel's decode divisor

**Measured**, run `r20260930-074616-9ec9` (run record `art:33de140d65c7f464bc9d6ea47063962ffc452686097fb69aab63cc9f4a5355bf`,
`bench.json`). GPU 0, `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`, locked-2100 (median SM clock 2,092 MHz, no throttle
reason, 154 W median), with the node held (07:46:27–07:48:16Z). Harness `0d1d6615`, build
`art:18a3d82b0a067445b506d12506b24e2be8fc6caac41fd99a9e8525f1c18b5a06` (CUDA 12.9.1's nvcc, cuBLASLt 12.9.2 headers,
CUTLASS v4.8.0). 40 reps, 32 cuBLASLt candidates, 4 finalists per family, as for the table below.

The method (`benchmarks/pouw/harness/chain.py`):
- Each timed call's A is derived on the device from the previous call's y, so no call can start before the one before it
  ends. A chain is 64 calls (the operand sets' weights cycle under it, as in the independent graph), replayed as one CUDA
  graph; the per-call time is the replay over 64.
- **The derive, f.** Row r of A reads row r of y, and column c reads column c mod n. The row is scaled by a power of two so
  its amax lands just under the format's range (the chain's values stay bounded over any length), then converted to the
  GEMM's input format, rounding to nearest even and saturating. The block-scaled formats get real scales: MXFP8 and MXFP4
  by the OCP MX rule per 32, NVFP4 UE4M3(amax/6) per 16. FP8 per-tensor and NVFP4's global scale stay at 1, and so do
  `fp8-blk128`'s A scales (flagged: that family's derive writes E4M3 codes only).
- **f is in both the arm's time and the divisor.** So a slow f would pull every decode ratio toward 1. It costs 3.8–5.6 µs
  per call (below), about a kernel launch with a row reduction, and each chain's own f is reported beside its time.
- **Gates.** Before any timing, the device's f is checked byte for byte against its numpy twin (`derive.py`) for every
  source and consumer format at three shapes, including unaligned buffers, partial warps and FP32 subnormals. Each chain
  is then gated step by step: derive, twin check, launch, the GEMM's own gate. A negative control times nothing: a
  chain whose A is derived from the wrong call's y must fail its gate, and did.

| Family | chain ms (graph) | p10–p90 ms | chain ms (burst) | Kernel (graph) | Runner-up, chain ms | Independent graph, same kernel | f alone | TFLOPS |
|---|---|---|---|---|---|---|---|---|
| `bf16` | 0.10600 | 0.10595–0.10614 | 0.11224 | `lt_bf16_0_1_algo21_tile21` | `cutlass2x_bf16_64x128x64_s3` 0.10682 | 0.10100 | 0.00416 | 40.5 |
| **`fp8-e4m3`** (per-tensor) | **0.05260** | 0.05253–0.05275 | 0.05725 | `lt_fp8-e4m3_0_3_algo35_tile13` | `lt_fp8-e4m3_0_2_algo35_tile15` 0.05263 | 0.05138 | 0.00382 | 81.7 |
| `mxfp8` | 0.07508 | 0.07501–0.07523 | 0.07947 | `lt_mxfp8_0_0_algo70_tile20` | `cutlass3x_mxfp8_128x128x128_coop` 0.07768 | 0.07212 | 0.00428 | 57.2 |
| `fp8-blk128` | 0.05602 | 0.05594–0.05618 | 0.06045 | `cutlass3x_fp8_groupwise_64x128x128_pingpong` | `cutlass3x_fp8_groupwise_128x128x128_coop` 0.07768 | 0.05347 | 0.00382 | 76.7 |
| **`nvfp4`** | **0.03578** | 0.03573–0.03594 | 0.03868 | `cutlass3x_nvfp4_128x32x256_coop_swap` | `cutlass3x_nvfp4_128x64x256_coop_swap` 0.03669 | 0.03107 | 0.00557 | 120.0 |
| `mxfp4` | 0.03474 | 0.03469–0.03494 | 0.03741 | `cutlass3x_mxfp4_128x64x256_coop_swap` | `cutlass3x_mxfp4_128x128x128_coop` 0.05167 | 0.03062 | 0.00509 | 123.6 |
| `int8` | 0.05500 | 0.05495–0.05512 | 0.05858 | `cutlass2x_int8_64x128x128_s3` | `lt_int8_0_0_algo21_tile18` 0.05669 | 0.05279 | 0.00433 | 78.1 TOPS |

How to read it:
- "f alone" is a chain of derives only (ms per call), for the family's input format; TFLOPS = 2mnk / chain time (Derived).
- **The chain costs 1.2 µs over the independent graph for FP8 and 4.7 µs for NVFP4** (Derived), less than f alone (3.8
  and 5.6 µs). My reading, not measured: part of f's launch overlaps the GEMM's tail in the graph.
- **FP8's fastest kernel changes with the method.** In the independent graph it's `cutlass3x_fp8_128x32x128_coop_swap`
  (0.05120 ms); in the chain that kernel takes 0.05380, and cuBLASLt's algorithm 35 is faster.
- **An arm's decode row divides its own chain by this one**, timed in the same run.
  - The report's `chain.arms.<arm>.split` gives, per method: f, before (the arm's work before its GEMM), during (the GEMM
    phase less f), after, and the whole call, serial and with `after` on a side stream (`after_exposed_side_ms`,
    `hidden_by_side_ms`).
  - The shape's `arms.<arm>.panel` block carries `decode_method: "dependent-chain"`, `chain_length` and
    `slowdown_side_stream` for `panel.py append --decode-method dependent-chain`.
  - The example arm (not a PoUW scheme) shows the fields: before 2.2 µs, after 1.9 µs, and the side stream costing 1.0 µs more
    than serial, because its `after` is too short to hide.

### The independent graph (both headlines)

**Measured**, run `r20260930-062850-de8e` (outputs in its run record `art:b75235e986e68c0ab66390943ef7ce65d0c49bac9abf7898d3b7d4c53d38ab72`,
`bench.json`). GPU 0, `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`, **locked-2100**, with the node held. Harness `7be37429`,
build `art:d54534ea…` (cuBLASLt 12.9.2, CUTLASS v4.8.0, CUDA runtime 12.9, driver 580.173.02).

Method: 40 reps. Each rep times every (kernel, method) once, in a seeded random order. The operands are full-entropy, in 8
distinct sets per shape (8.6 GiB at prefill, 2.6 GiB at decode), with a read-only L2 flush before each item. Every kernel
passed the bit-exact gate at its shape before timing.

How to read the table:
- ms is the median ms per call over the 40 reps; TFLOPS = 2mnk / time (Derived).
- **graph** is the headline method; **burst** is beside it.
- Kernel names: `lt_…_algoA_tileT` is cuBLASLt algorithm A with tile id T; `cutlass3x_…` and `cutlass2x_…` are the CUTLASS
  kernels in `native/cutlass_3x.cu` and `native/cutlass_2x.cu`, named by tile and schedule; `_swap` computes Dᵀ = BᵀAᵀ.

**Prefill, `m8192-n8192-k8192`**

| Family | graph ms | TFLOPS | p10–p90 ms | burst ms | Kernel (graph) | Runner-up, graph ms | Share of the mma.sync peak |
|---|---|---|---|---|---|---|---|
| `bf16` | 2.8405 | 387.1 | 2.8377–2.8427 | 2.8461 | `lt_bf16_0_0_algo21_tile23` (algo 21, tile 23, 9 stages) | `cutlass2x_bf16_256x128x32_s3` 2.8426 | 95.9% |
| **`fp8-e4m3`** (per-tensor) | **1.4457** | 760.5 | 1.4428–1.4477 | 1.4568 | `lt_fp8-e4m3_0_0_algo35_tile20` (algo 35, tile 20, 15 stages, swizzle 1) | `cutlass3x_fp8_128x128x64_coop` 1.5171 | 94.2% |
| `fp8-e4m3-rowwise` | none | | | | no plain kernel on sm_120 (below) | | |
| `mxfp8` | 1.5767 | 697.3 | 1.5734–1.5783 | 1.5848 | `lt_mxfp8_0_0_algo70_tile20` (algo 70, tile 20, 36 stages) | `cutlass3x_mxfp8_128x128x128_pingpong` 1.6597 | 86.5% |
| `fp8-blk128` | 1.6402 | 670.3 | 1.6378–1.6422 | 1.6438 | `cutlass3x_fp8_groupwise_128x128x128_coop` | `cutlass3x_fp8_groupwise_64x128x128_pingpong` 1.9349 | 83.0% |
| **`nvfp4`** | **0.8037** | 1368.1 | 0.8026–0.8048 | 0.8075 | `cutlass3x_nvfp4_128x128x128_coop` | `lt_nvfp4_0_0_algo70_tile20` 0.8155 | 84.8% |
| `mxfp4` | 0.8171 | 1345.6 | 0.8150–0.8183 | 0.8208 | `cutlass3x_mxfp4_128x128x128_coop` | `cutlass3x_mxfp4_128x128x128_pingpong` 0.9501 | 83.4% |
| `int8` | 1.4874 | 739.2 TOPS | 1.4856–1.4890 | 1.4901 | `cutlass2x_int8_256x128x64_s3` | `cutlass2x_int8_128x256x64_s3` 1.4951 | 91.5% |

**Decode, `m32-n8192-k8192`** (the graph of independent calls: not the panel's decode divisor, which is the chain above; the
07:48Z window reproduces these within 1.4%, MXFP4 2.5%, all slightly faster)

| Family | graph ms | TFLOPS | p10–p90 ms | burst ms | Kernel (graph) | Runner-up, graph ms | Weight stream (share of DRAM read) |
|---|---|---|---|---|---|---|---|
| `bf16` | 0.1017 | 42.2 | 0.1012–0.1025 | 0.1050 | `lt_bf16_0_1_algo21_tile21` (algo 21, tile 21, split-k 5, reduction 2, 5 MiB workspace) | `cutlass2x_bf16_64x128x64_s3` 0.1026 | 1.32 TB/s (86%) |
| **`fp8-e4m3`** (per-tensor) | **0.0519** | 82.8 | 0.0515–0.0526 | 0.0543 | `cutlass3x_fp8_128x32x128_coop_swap` | `lt_fp8-e4m3_0_2_algo35_tile15` 0.0520 | 1.29 TB/s (84%) |
| `fp8-e4m3-rowwise` | none | | | | no plain kernel on sm_120 | | |
| `mxfp8` | 0.0731 | 58.8 | 0.0724–0.0741 | 0.0781 | `lt_mxfp8_0_0_algo70_tile20` | `cutlass3x_mxfp8_128x128x128_coop` 0.0755 | 0.95 TB/s (62%) |
| `fp8-blk128` | 0.0540 | 79.5 | 0.0534–0.0560 | 0.0562 | `cutlass3x_fp8_groupwise_64x128x128_pingpong` | `cutlass3x_fp8_groupwise_128x128x128_coop` 0.0761 | 1.24 TB/s (81%) |
| **`nvfp4`** | **0.0315** | 136.2 | 0.0311–0.0330 | 0.0336 | `cutlass3x_nvfp4_128x32x256_coop_swap` | `cutlass3x_nvfp4_128x64x256_coop_swap` 0.0328 | 1.20 TB/s (78%) |
| `mxfp4` | 0.0314 | 136.6 | 0.0308–0.0326 | 0.0334 | `cutlass3x_mxfp4_128x64x256_coop_swap` | `cutlass3x_mxfp4_128x128x128_coop` 0.0490 | 1.14 TB/s (74%) |
| `int8` | 0.0534 | 80.4 TOPS | 0.0530–0.0550 | 0.0559 | `cutlass2x_int8_64x128x128_s3` | `lt_int8_0_0_algo21_tile18` 0.0539 | 1.26 TB/s (82%) |

**The headline divisors** (the 09:03Z window's, at the top; this section's tables are the 06:31Z window's).
- **FP8:** `fp8-e4m3` per-tensor, 1.4460 ms at prefill and 0.05270 ms at decode (dependent chain).
  - **The FP8 divisor is per-tensor** (decided 06:50Z). A rowwise GEMM is the per-tensor GEMM plus a per-row and per-column
    scale in the epilogue: rowwise adds only epilogue work, so per-tensor is the honest divisor, and no rowwise kernel is
    built.
  - Nor is there one to time: cuBLASLt 12.9 offers no algorithm for outer-vector scales on sm_120, and CUTLASS v4.8.0 has no
    sm_120 rowwise kernel.
- **FP4:** `nvfp4`, 0.78875 ms at prefill (`cutlass3x_nvfp4_256x128x128_coop`) and 0.03581 ms at decode (dependent
  chain); `mxfp4` beside it. **FP4 ratios stay labelled "divisor possibly lenient"**: the search found nothing within a
  few percent of FP8's peak fraction, and the lenience is at most 8.3% (the FP4 baseline search, above).
- Your own run's ratios divide by the baselines timed in that run, interleaved with your arm. This table says what those
  divisors should be. A run whose divisor is more than about 1% off this table shares the card with something, or its clock
  moved.

**Caveats, flagged.**
- **The FP4 divisors may be beatable: "divisor possibly lenient", by at most 8.3%.** After the search (09:03Z), NVFP4
  reaches 86.4% of its mma.sync peak at prefill and MXFP4 83.7%, against 94.2% for FP8 and 95.9% for BF16 (Derived).
  - A faster plain FP4 GEMM would raise every FP4 ratio, so FP4 ratios over this table are the lenient reading, and the
    panel labels them so.
  - Neither cuBLASLt version has more to offer (enumerated by hand), and CUTLASS's other sm_120 tiles and schedules are
    slower. What's left is a block-scaled mainloop of our own: why, with evidence, in the FP4 baseline search above.
  - **MXFP4 at 32,768³ is about 2× lenient** (45.9% of peak), because CUTLASS runs at its default tile raster there.
- **MXFP8 at decode** has no swapped (skinny-M) CUTLASS kernel built, so it trails FP8 by 43% in the chain. It isn't a
  headline family.
- **Clocks: locked-2100, with the load clock beside it.** The node's owner locks the clocks at 2,100/12,481 MHz, and every
  item's SM and memory clocks are recorded.
  - **At prefill the SM clock is 2,085 MHz under load**, not 2,100: 70% of items carry throttle reason 0x4 (the software
    power cap) at about 415 W median (413 W in both windows, 441–444 W max), against a 600 W limit. That's about 0.3% under
    the idle 2,092.
  - Decode runs at 2,092 MHz with no throttle reason (113 W in the independent graph, 154 W with the chains).
- **Agreement with the untimed rehearsals.** They ran on the shared node and agree within 0.5% at prefill and 2% at decode
  (e.g., FP8 at prefill: 1.4392 and 1.4447 ms against the window's 1.4457; NVFP4: 0.8020 and 0.8032 against 0.8037).

## The card (Measured, same window, GPU 0, locked-2100)

| mma.sync kind | TFLOPS | FLOP/SM/clk (NVML clock 2,092 MHz) |
|---|---|---|
| `bf16` → f32; `f16` → f16 | 403.7; 403.9 | 1,026 |
| `e4m3` → f32; `e4m3` → f16 | 807.2; 807.6 | 2,052 |
| `kind::f8f6f4` e4m3; e2m1 (unscaled FP4 at k32) | 807.7; 806.5 | 2,054; 2,051 |
| `kind::mxf8f6f4` e4m3 with UE8M0 | 806.1 | 2,050 |
| `kind::mxf4nvf4` NVFP4 (UE4M3 per 16); MXFP4 (UE8M0 per 32) | 1,614.0; 1,612.6 | 4,104; 4,100 |
| `s8` → s32 | 807.5 | 2,053 |

- **Rates.** FP8 accumulates into FP32 at the FP16 rate (ratio 0.9995), and FP8 runs at 2.000× BF16.
- **Clock.** The per-clock rates sit 0.2% above powers of two, so the SM clock under the lock is about 2,097 MHz where NVML
  reports 2,092 (Derived).
- **DRAM** (8 GiB buffers): read 1,535 GB/s, copy 1,452 GB/s.
- **L2 read** (zero-filled buffer): 5.7–6.0 TB/s up to 32 MB, 5.0–5.4 TB/s from 48 to 160 MB, 4.5 TB/s at 192 MB, and
  1.8 TB/s from 256 MB (DRAM).
- **Operand entropy** (the same kernel on ternary operands against full-entropy ones, 20 hot calls each): full entropy is
  slower by 0.76% for FP8 (`lt_fp8-e4m3_0_0_algo35_tile20`), 0.24% for NVFP4 and 0.13% for BF16. So timing on full-entropy
  operands, as the harness does, is the strict choice.
- **Held for 30 s:**
  - FP8: 1.4531 ms per call (0.5% over the interleaved median). SM clock 2,077 MHz, up to 468 W, 65 °C, throttle 0x4 in every
    tail sample.
  - NVFP4: 0.8033 ms per call. SM clock 2,085 MHz, up to 421 W, 62 °C, no throttle reason.
- **The earlier untimed run** (`r20260930-061232-b66b`) agrees within 0.3% on every rate.

## Plugging an arm in (GPUs 1 and 5)

Checked on CPU at 06:45Z with the harness at `940562e2` beside each branch:
- `pearl_c4_arm:PearlC4Nv` and `:PearlC4Mx` (`cursor/pearl-c-fp4-3084`, `f9caa50e`) load by `module:Class` under `env.sh`'s
  numpy-only venv.
- So do `pearlc_arm:PearlCSm120` and `:PearlCSm120Unpromoted` (`cursor/pearl-c-sm120-b44b`, `f1874af1`).
- All four pass `check_arm`, are in domain at both headlines, and report `work()`. No module name collides with the
  harness's.
- GPU 1's arm needs `verity_pouw` on the path. `env.sh` provides it from `940562e2` on; an older `env.sh` gives
  `ModuleNotFoundError`.

**Decode rows need the harness at `0d1d6615` or later, with build `art:18a3d82b…` or later** (07:48Z). Only those time
decode as a dependent chain, the only decode method the panel counts; an older build refuses `--decode-method
dependent-chain`, the default.

**From 17:50Z a measured row needs harness `80bff34cc` (#491 with #583) with build `art:3bf425e6…`, and your arm with
`dump` (interface v0.5; under "For GPUs 2 and 5", top).** The rest of this paragraph is from 15:35Z.

**A measured row needs harness `485a64660` or later with build `art:46a3756b…`** (15:35Z). It has panel rules (a) and
(b) and gate v4 with its numeric pin, and your `build()` must name `binaries` and `verifier` (the lines are under "Panel
rules"). In the lines below, check out `485a64660` instead of `36df5171` and fetch
`art:46a3756b9c4a7d2a9a3ae4999d0fedfe0eeebea075b0c071fca4355260f83397` instead of `art:14fff942…`, and add the verify step
(the harness's README has the run line). Heads `7f4a67f6b` to `b7b88c95c` with `art:14fff942…` refuse their own library.
Untimed runs and estimates can stay on the older heads.
- **Your kernels must come from a pinned ptxas:** CUDA 12.9.1's nvcc or node 2's 13.0 (V13.0.88), with
  `-gencode arch=compute_120a,code=sm_120a`, and `-fmad=false` or not.
- The gate reads ptxas's arguments from each cubin. A flag that reaches ptxas (`-Xptxas …`, `-G`, `-ftz`, `-prec-*`),
  or any other toolkit, exempts nothing, so every division and square root in the kernel fails. Every kernel shipped at
  10:38Z qualifies.

**FP4 arms: the 09:03Z divisors come from `36df5171` and `art:14fff942…`** (the lines below use them; for a measured row
swap in `485a64660` and `art:46a3756b…`, which have the same kernels).
- Their in-run NVFP4 prefill divisor includes the 256×128 kernel.
- With `0d1d6615` your run's own divisor is the 128×128 kernel, 1.9% slower, so your prefill ratio would read about 1.9% low.
- Decode is the same in both.
- FP8 arms can stay on `0d1d6615`, because FP8's divisor didn't move.
- Sending `libpouw_lt2.so` is optional. It adds cuBLASLt 13.1, which no headline divisor needs.
- **What your arm needs for the chain:** nothing new if your call's `launch` reads A from the operand set each time and its
  y is `outputs["y"]` (m × n row-major, BF16, the first m rows; say otherwise with a `y_format` attribute). Both of yours
  qualify: the harness derives each call's A into your operand set's A buffer, in your `inputs` format.
- **For the before/during/after split,** give your `Call` a `phases` dict: `before`, `gemm`, `after`, each a function of
  the stream, whose sequence equals `launch`. Without it, the row still counts, and the report says "the arm's calls
  expose no phases".
- **The side stream** runs `after` of call j on a second stream while call j + 1 forms. It needs per-call scratch.
  **GPU 1:** `PearlCSm120` shares its scratch across calls at a shape, so give it per-call scratch before asking for the
  side-stream variant; the serial split works as is.

Run from a tree that holds your branch and the harness. Keep the harness out of your PR:

~~~sh
git fetch origin cursor/pouw-harness-sm120-d2f2
git switch -c run/<you>-harness                     # a throwaway branch or worktree off your head
git checkout 36df5171 -- benchmarks/pouw/harness benchmarks/pouw/tests/test_harness.py
git commit -qm "run: the harness at 36df5171 beside the arm"     # research run --source ships a clean commit
research data fetch art:14fff9420410dec00f7d52c078a5f4da7b84e9812573e5744a53ab524bafde32 --to /tmp/ph-build
cp /cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/rtx-pro/server.md /tmp/server.md   # its GPU table
~~~

Then run `research` from a worktree of `origin/main`, because a branch stacked on #449 carries an older `tools/research`:

~~~sh
R='research run --on vy-nebius-2 --project verity --campaign pouw --source <your run checkout> --cwd source --timeout 1740
   --env GPU_LEASE_WHO=<your bc-id> --send /tmp/ph-build/libpouw_harness.so --send /tmp/ph-build/build.json --send /tmp/server.md
   --send /tmp/ph-build/libpouw_lt2.so'                              # optional: cuBLASLt 13.1 beside 12.9
H='. benchmarks/pouw/harness/jobs/env.sh "$RESEARCH_RUN_DIR/inputs" && "$PY" benchmarks/pouw/harness/bench.py --gpu lease
   --server-md "$RESEARCH_RUN_DIR/inputs/server.md" --clock-label locked-2100 --shapes headline
   --arm-path benchmarks/pouw/pearl_c4 --arm pearl_c4_arm:PearlC4Nv --arm pearl_c4_arm:PearlC4Mx
   --out "$RESEARCH_RUN_DIR/bench.json"'
# GPU 1: --arm-path benchmarks/pouw/pearl_c_sm120 --arm pearlc_arm:PearlCSm120 --arm pearlc_arm:PearlCSm120Unpromoted
$R -- gpu-lease 1 --wait -- bash -c "$H"                          # untimed: gates, negative controls, a first ratio
$R -- gpu-lease 8 --wait -- timeout 1140 bash -c 'export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES%%,*} && '"$H"   # timed
~~~

- **Your kernels.** Your arm's `build()` finds its kernels as on your own runs: ship prebuilt ones with `--send`, or build
  them in the run.
- **Matching this table.** Add `--reps 40 --lt-candidates 32 --finalists 4` to use the same method.
- **Timing.** Time only after an untimed run is clean. My 07:48Z window, with the example arm, took 1 min 49 s for both
  headlines, every family and the decode chains. My 09:03Z window, with the new build and the FP4 enumeration but no arm,
  took 1 min 27 s. Add your arms' calls to that.
- **Exit codes.** 5 means a known-bad variant was accepted; 6 means the consistency gate rejected an arm (`nohash` faster
  than 0.95 × the plain GEMMs its MACs need).
- **Where the report is.** Each shape's `arms.<name>.graph` holds `total_x`, `hash_free_x`, `hashing_x`, the weight side
  and R₁%, and `arms.<name>.panel` holds the fields for `panel.py append`. At decode, the panel block is the chain's
  (`decode_method: "dependent-chain"`), and `chain.arms.<name>` has the split.

**For GPU 5.** Your self-timed plain NVFP4 GEMM at 8,192³ (1.647 ms) is 2.09× the harness's NVFP4 baseline (0.78875 ms,
`cutlass3x_nvfp4_256x128x128_coop`, 09:03Z).
- That kernel is CUTLASS v4.8.0's sm_120 NVFP4 collective (`KernelTmaWarpSpecializedNvf4Sm120`, 256×128×128 tile,
  cooperative), in `native/cutlass_3x.cu`. So the mainloop is the first place to look.
- The card's NVFP4 mma.sync peak is 1,614 TFLOPS (Measured); your 1.6 PFLOPS estimate holds.
- Even CUTLASS's mainloop reaches only 86.4% of it, against FP8's 94.2%, and the search says why (above). A mainloop that
  feeds the scaled MMA better would speed up your arm and the divisor alike.

**For GPU 1.** The FP8 divisor is cuBLASLt algorithm 35 at prefill (1.4460 ms, 94.2% of the FP8 mma.sync peak) and at
decode as a chain (`lt_fp8-e4m3_0_3_algo35_tile13`, 0.05270 ms), both from the 09:03Z window; neither moved.

## Arm interface (v0.5, #583, 17:24Z)

The code is `benchmarks/pouw/harness/arm.py`; this section is its contract. Arms written against v0 keep working through v0.x.

**v0.5 changes (#583, adopted 17:24Z): the poisoned dump.** An arm with `dump(dev, call, shape, dir)` has the harness make
its transcript after timing, from the hash call on operand set 0 with `call.transcript_buffers` (default `outputs`; never
an operand, refused from `80bff34cc`) poisoned with 0xA5, and a no-write control under `negative/` that the verifier must
reject. The verifier may name a `control` path template; with a transcript under `transcripts/{arm}/{shape}/` it needn't.
An arm without `dump` dumps its own and names `control`. The details are under "For GPUs 2 and 5" (top).

**v0.4 changes (10:52Z): the verifier.** `build()`'s record may name the arm's reference `verifier`, and must, for a
measured row (under "Panel rules"). `ctx` also carries `transcripts_dir`.

**v0.3 changes (10:01Z): the SASS gate.** `build()`'s record names its binaries (`"binaries": [path, ...]`), every cubin,
fatbin or library its kernels come from; an arm without them exits 7 before timing (the FTZ gate, above).

**v0.2 changes (07:25Z): the dependent chain.** No change is required of an arm.
- At decode (m = 32) the harness times every arm and baseline as a dependent chain (`--decode-method dependent-chain`, the
  default; `independent` keeps the old graph). It derives each call's A into the operand set's A (and `a_scale`) buffers
  from the previous call's y, so **`Call.launch` must read A from the operand set on every call**, not from a copy made in
  `prepare`.
- **y** is `outputs["y"]` (else `outputs["d"]`): m × n row-major, the first m rows used, BF16 unless the arm sets
  `y_format` (`"bf16"`, `"f32"` or `"int32"`). An arm without either output isn't chained, and the report says why.
- **Optional `Call.phases`:** `{"before", "gemm", "after"}`, each `fn(stream)`, whose sequence is exactly `launch`. With it
  the harness also times the chain with `gemm` alone, with `before` and `gemm`, and with `after` on a side stream (call
  j's `after` overlapping call j + 1's derive and forming; call j + S waits for it before its operand set is reused). The
  side-stream variant needs per-call scratch.
- Each chain is gated step by step: derive, twin check, launch, then the arm's own `gate` on the last call.
The command line has changed since 05:56Z:
- `--gpu lease` takes the one index the lease set, and `--server-md FILE` checks the UUID at that index against the file's
  GPU table (server.md itself works).
- `--clock-label` names clocks the machine fixes; `clocks.timed` summarizes every item's SM and memory clocks.
- A family with no plain kernel is listed in the shape's `no_baseline`.
- `baseline_candidates` gives, per family, what was tried, cuBLASLt's refusals and each candidate's tuning time.

**v0.1 changes (05:56Z).**
- Operands: the timed operand sets are **full-entropy** (random values of the input format, random block scales); the baselines'
  bit-exact gate uses a separate ternary set ({−1, 0, 1}, unit scales), where every precision's output is exact. An arm is gated
  on the first and the last timed set. Operand buffers are read-only for arms.
- `known_bad(dev, shape, operands)`; the two-argument `known_bad(dev, shape)` is still accepted.
- Fill preflight: every fill format's device bytes are checked against `fill.py`'s CPU twin before anything runs, so
  `operands.host()` and an arm's own twin regenerate exactly what is on the device.
- Shape labels are the panel's, `m{m}-n{n}-k{k}`; the headlines are prefill `m8192-n8192-k8192` and decode `m32-n8192-k8192`, and
  each shape's report carries a `panel` block (phase, shape, slowdown, hash_free, baseline, baseline_kernel) for `panel.py append`.
- A run refuses a library its `build.json` doesn't describe.

**Runtime.** One Python process per run: stdlib + numpy, no torch. The harness's native library (`libpouw_harness.so`: device
memory, fill kernels, the L2 flush, events, CUDA graphs, cuBLASLt and CUTLASS baselines) and every arm share the device's
**primary context** (CUDA runtime or driver API, e.g. #449's `run.Dev`/ctypes pattern both work). Device pointers and streams
cross the interface as Python `int`s. Build everything `-gencode arch=compute_120a,code=sm_120a`, nvcc ≥ 12.8.

**What an arm provides** (a class with these members; the harness loads it by `module:Class` from `--arm`; template:
`example_arm.py`, which is plain cuBLASLt FP8, **not a PoUW scheme**):

| Member | What |
|---|---|
| `name: str` | e.g. `pearl-c-sm120-v1`; a new build of it gets a new name or a `build()` record that says so |
| `stream: "fp8" \| "fp4"` | |
| `precision: str` | the baseline family its headline is divided by: `fp8-e4m3` or `nvfp4` (keys in "Baselines" below) |
| `inputs: str` | the operand format the harness generates for it: `f32`, `bf16`, `e4m3`, `e2m1-nv` (E2M1 + UE4M3/16), `e2m1-mx` (E2M1 + UE8M0/32), `int8` |
| `flag_sets: dict[str, frozenset[str]]` | the timed configurations by role. **Required roles:** `hash` (the honest prover, everything it does per call) and `nohash` (the same kernel with every hash and XOF left out: the hash-free control). Extra roles are allowed (e.g. `hash_tile_only`) and are gated and timed like the others |
| `build(ctx) -> dict` | compile or load its kernels; return a record: artifact sha256s, the nvcc command, SASS instruction counts per kernel (e.g. `{"kf": {"QMMA": 64, "HMMA": 0}}`), anything its numbers depend on |
| `domain(shape) -> str \| None` | `None` if the shape is in the arm's domain, else the reason; out-of-domain shapes are reported, not timed |
| `work(shape) -> Work` | per call: `tensor_macs: dict[precision, int]` (tensor-core MACs issued, by precision), `w_ref` and `credited` (Lean's `wrefOf`/`creditOf`, as exact strings, with `unit`), `hashed_bytes: dict[hash, int]` (bytes absorbed per call); per (weight, epoch): `weight_hashed_bytes`; optional `gamma: dict[str, str]` (derived, certificate) |
| `prepare(dev, shape, flags, operands) -> Call` | allocate this operand set's buffers and do nothing timed. `operands` is the harness's `OperandSet` (`index`, `weight_id`, `a`, `b`, `a_scale`, `b_scale` as `Buffer(ptr, nbytes)`, the `seed`, and `host()`, a numpy copy on demand), read-only. A `Call` has: `launch(stream)`, `weight_side(stream)`, `outputs: dict[str, Buffer]`, `free()`. A `prepare` that raises is a failed gate |
| `Call.launch(stream)` | **the timed call**: enqueue one complete per-call prover step on `stream` (forming, the product, clean-up, the noise XOF, every commitment and hashed byte); no host sync, no allocation, no host↔device copy; must be capturable into a CUDA graph (the harness captures it; an uncapturable entry is dropped from `graph` and recorded) |
| `Call.weight_side(stream)` | enqueue the per-(weight, epoch) work for this operand set (B's forming, B̃·F_A, P_B, B's commitments), same rules; a no-op if there is none |
| `gate(dev, call, shape, flags) -> Gate` | run after `call.launch` + a sync: compare the device's outputs with the arm's own reference (CPU twin, or an independent device build) at **this exact shape and flag set**. `Gate(ok, checked, detail)`, where `checked` maps each output name to `"all"` or `"sampled:<what>"`; at least one output must be `"all"` (a root, y's digest). Deterministic |
| `known_bad(dev, shape, operands) -> Call \| None` (optional) | a variant its gate must reject (e.g. a build that corrupts one tile word or skips one tile's hash): the negative control W10 |

**What the harness does with it** (per run, in this order; every failure below stops what it guards and writes no timing for it):

1. **Identity.** Exactly one visible device, `CUDA_VISIBLE_DEVICES` a single index equal to `--gpu` (or, with `--gpu lease`,
   whatever one index the lease set), the device's UUID equal to `--expect-uuid` or to the `--server-md` table's UUID at that
   index, `CUDA_DEVICE_ORDER=PCI_BUS_ID`; NVML addressed by that UUID; the card check (name has "RTX PRO 6000", cc 12.0, 188
   SMs, driver ≥ 575). Versions: driver, CUDA runtime and driver API, cuBLASLt, CUTLASS commit, the machine's nvcc and the
   builder's, numpy, the library's hash and `build.json` (SASS MMA counts per kernel), the arm's `build()` record; the clock
   label. Then the fill preflight.
2. **Negative controls, before any timing** (at the first shape). (a) The harness's known-bad baselines, a GEMM with one output
   byte flipped and a GEMM over half of k, must fail the baseline gate; (b) for each arm: launch, flip one byte in an output the
   arm's gate reports as `"all"`, and its `gate` must reject; relaunch and it must pass; (c) the arm's `known_bad` must be
   rejected. Any accepted known-bad, or a control that crashes, stops the run (exit 5).
3. **Per shape** (m, k, n) in the bench's order: operand sets with distinct weight buffers whose total passes 2× the 128 MB
   L2 (at least 2, at most 512 sets), generated on the device from recorded seeds. **Gates before timing:** for every arm and
   every flag set, `prepare`, `launch`, sync, `gate` on the first and last set; each baseline candidate is gated bit-exactly at
   32×32 sampled output entries against numpy on the ternary set, with D pre-filled with a sentinel. A failed gate records the
   gate and times nothing of that (arm, flags) or baseline at that shape.
4. **Autotune the baselines** at the shape (cuBLASLt's top heuristic algorithms and the CUTLASS sm_120 kernels, each gated,
   then a short timed sweep on the timing sets); the fastest per family (`--finalists`, default 2) enter the interleaved timing,
   and their algorithm ids and configs are recorded. A family cuBLASLt refuses is tuned on CUTLASS alone; one with no kernel
   at all is listed in `no_baseline`.
5. **Timing, everything the same way.** At least 20 reps, all saved. Each rep runs every (entry, method) once in a seeded
   random order (the seed recorded), where entry ∈ {each arm's flag sets, each arm's weight side, each baseline finalist} and
   method ∈ {`burst`: B calls cycling the operand sets between CUDA events; `graph`: the same B calls captured once into a CUDA
   graph and replayed}, B = max(sets, 4). Before each timed item, a **read-only** L2 flush (a sum over 4× L2 of a buffer zeroed
   once). NVML per item: SM and memory clocks, temperature, power, throttle reasons.
6. **Consistency gate (W7), after timing:** at compute-bound shapes (mkn ≥ 2³³), the `nohash` call must take at least
   e · Σ_p (tensor_macs_p / mkn) · (the fastest plain precision-p GEMM), e = 0.95; else the shape's arm row is marked
   `rejected` and the run exits 6. W_ref/mkn is reported beside it.
7. **Report per shape** (both methods; medians, with every rep saved): the baseline per precision (the faster of cuBLASLt and
   CUTLASS, which kernel, TFLOPS); for each arm, over its precision's fastest plain GEMM: `hash_free_x` (nohash), `total_x`
   (hash, everything per call), `hashing_x` (total − hash-free, i.e. hashing and XOF, incremental), the hashing rate
   (bytes/(total − hash-free)); over every other precision's baseline too; the weight side per (weight, epoch) in ms and
   **R₁%**, the reuse count at which it falls under 1% of the baseline call (R ≥ 100 · weight_ms / baseline_ms); W_ref/mkn,
   credited/mkn and γ as the arm states them (Derived). The headline is `total_x` by `graph` at `m8192-n8192-k8192` and
   `m32-n8192-k8192`.

**Baselines (families; `precision` keys).** Each is the faster of cuBLASLt (autotuned over up to 32 heuristic algorithms,
32 MiB workspace) and CUTLASS's sm_120 kernels, GEMM alone on pre-quantized operands, TN layout, BF16 out (int8: int32 out):
`bf16`; `fp8-e4m3` (per-tensor scales); `fp8-e4m3-rowwise` (per-row A, per-column B scales, the per-token quantizer's GEMM);
`mxfp8` (E4M3, UE8M0 per 32); `fp8-blk128` (DeepSeek-style 1×128 / 128×128); `nvfp4` (E2M1, UE4M3 per 16, FP32 global);
`mxfp4` (E2M1, UE8M0 per 32); `int8`. The FP8 headline divides by the faster of `fp8-e4m3` and `fp8-e4m3-rowwise` (decided
06:10Z; on sm_120 that is `fp8-e4m3`, as rowwise has no plain kernel); FP4's by `nvfp4` (MXFP4 beside). An arm may also offer
its adopted quantizer's plain path (`plain_path(dev, shape, operands) -> Call`, optional), reported beside the GEMM-alone
ratio.

**Defaults taken (reversible):** headline over the GEMM alone (the strictest reading); `graph` for the headline, `burst` beside
it; e = 0.95; R₁% relative to the baseline call; full-entropy timing operands (the characterization shows full entropy is the
slower, so the stricter, choice).

## Run lines (node 2)

The build is `art:14fff9420410dec00f7d52c078a5f4da7b84e9812573e5744a53ab524bafde32`, for harness `36df5171`.
- It holds the library, `libpouw_lt2.so`, `build.json`, `sass_mma.tsv` and `res_usage.txt`.
- Key `99d580f350be41b6`: CUDA 12.9.1's nvcc, cuBLASLt 12.9.2.10 headers and CUTLASS v4.8.0, 53 kernels, no local-memory
  spills.
- `libpouw_lt2.so` is `native/lt.cu` alone, built against node 2's cuBLASLt 13.1.1.3
  (`/usr/local/cuda-13.0/targets/x86_64-linux/lib/libcublasLt.so.13.1.1.3`). A run loads it beside the library when it's
  there, and names its configurations `lt13_…`.
- The 07:48Z build `art:18a3d82b…` (`0d1d6615`, key `a56f418696e39f2f`) has neither.

`jobs/env.sh BUILD` makes a venv with NVIDIA's cuBLASLt 12.9.2.10 and runtime 12.9.79 wheels (fine under driver 580 and CUDA
13.0), and puts the tree's `verity` and `verity_pouw` on `PYTHONPATH`.

A build is a CPU job on node 2, with no GPU lease: `jobs/toolkit.sh` assembles CUDA 12.9.1 from NVIDIA's redistributables
(pinned by sha256) under `/workspace/cache/pouw-cuda-12.9.1`, and `build.sh` keeps each object under
`/workspace/pouw/harness/build/objects/` by its own hash. A full build takes about 9 minutes at `JOBS=8`, and one edited
unit about 1. The line is in the harness's README.

From a worktree of `origin/main`, with my branch's clean checkout as the source:

~~~sh
R='research run --on vy-nebius-2 --project verity --campaign pouw --source <harness checkout> --cwd source --timeout 1740
   --env GPU_LEASE_WHO=bc-0de2d624 --env POUW_HARNESS_ENV=/workspace/pouw/harness/env
   --send /tmp/ph-build/libpouw_harness.so --send /tmp/ph-build/libpouw_lt2.so --send /tmp/ph-build/build.json
   --send /tmp/server.md'
E='. benchmarks/pouw/harness/jobs/env.sh "$RESEARCH_RUN_DIR/inputs" && '
G='--gpu lease --server-md "$RESEARCH_RUN_DIR/inputs/server.md" --clock-label locked-2100'
B='"$PY" benchmarks/pouw/harness/bench.py '"$G"' --shapes headline --reps 40 --lt-candidates 32 --finalists 4
   --arm-path benchmarks/pouw/harness --arm example_arm:ExampleFp8 --out "$RESEARCH_RUN_DIR/bench.json"'
C='"$PY" benchmarks/pouw/harness/characterize.py '"$G"' --out "$RESEARCH_RUN_DIR/characterize.json"'
$R -- gpu-lease 1 --wait -- bash -c "$E$B"                                             # untimed rehearsal (about 1 min)
$R --timeout 10800 -- gpu-lease 8 --wait -- timeout 1140 bash -c \
  'export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES%%,*} && '"$E$B"                     # the timed window (about 2 min)
# add ' && '"$C" inside the quotes to characterize in the same window (its two 30 s holds make it over a minute more)
# the 09:03Z FP4 search: B without the --arm-path and --arm flags, plus --lt-enumerate nvfp4 mxfp4
~~~

- **`--lt-enumerate FAMILY…`** enumerates cuBLASLt's configurations by hand for those families only.
- Enumerate only what you're searching: cuBLASLt 13.1's FP8 space at 8,192³ passes 8,192 configurations.
- SIGTERM stops a run and still writes its JSON, with exit code 143.

Never `--lock-mhz` or `characterize.py --sections lock` on node 2: both call `nvidia-smi -lgc`.

## Panel rows

None from me. The baselines are the divisors, not attempts on a line, and the example arm isn't a PoUW scheme.

## Lessons

- **A VM reset wiped `/tmp`, `~/.research`, uv, the CUDA toolkit and the checkout between turns.** Recovery was a fetch, not a
  rebuild, because the build was already in the store (`art:d54534ea…`). Preserve every build as soon as it exists.
- **`gpu-lease` picks the index, so a job can't pass `--gpu N` up front.** Fix: `--gpu lease` reads the one index from
  `CUDA_VISIBLE_DEVICES`, and `--server-md` checks the UUID at that index against server.md's table. The infra lane's
  `GPU_LEASE_UUID` would replace the table lookup.
- **`gpu-lease 8` sets `CUDA_VISIBLE_DEVICES` to all eight.** A one-GPU timed job must narrow it first
  (`export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES%%,*}`), or its identity gate sees eight devices.
- **locked-2100 isn't flat under load.** NVML reads 2,092 MHz idle and 2,085 under 8,192³ GEMMs (about 415 W, throttle 0x4,
  software power cap, against a 600 W limit), and 2,077 in a 30 s FP8 hold (468 W). Record the clocks and throttle reasons
  per item rather than trusting the label.
- **NVML's clock reads about 0.2% low under the lock.** FLOP/SM/clk comes out at 2,052 and 4,104 where the hardware gives
  2,048 and 4,096, so the real clock is about 2,097 MHz. Per-clock rates computed from NVML's reading run 0.2% high.
- **cuBLASLt 12.9.2 on sm_120 has gaps.** Its MXFP4 heuristic query fails with INVALID_VALUE, and FP8 with outer-vector
  (rowwise) scales and FP8 1×128/128×128 get zero algorithms. A harness must treat a refusal as "no candidate from this
  library", not as a failed run (`7be37429`).
- **`research run --on` returns at launch.** `research fetch --all <run>` pulls the outputs and reports `preserved=yes`;
  `research data preserved <run>` is the durability check.
- **Run `research` from a worktree of `origin/main` and pass `--source <branch checkout>`.** A branch's own `tools/research`
  may predate the ssh provider.
- **The machine's nvcc (13.0 on node 2) isn't the builder's (12.9).** `versions()` records both, so a run can't be misread as
  built with 13.0.
- **`env.sh`'s venv holds only numpy and the NVIDIA wheels.** An arm that imports `verity_pouw` needs the tree's sources on
  `PYTHONPATH`; `env.sh` sets that from `940562e2` on.
- **A store file can raise EAGAIN** (`BlockingIOError`) while someone writes it. Copy it and retry rather than reading it in
  place.
- **A dependent chain's derive is in the divisor, so its speed is a fairness question, not a detail.** My first derive took
  14–27 µs per call at decode, 23–40% of the chained call, which would have pulled every decode ratio toward 1. At 8 columns
  per thread with 16-byte accesses it takes 3.8–5.6 µs (`0d1d6615`). Report f beside every chain divisor.
- **A power-of-two multiply is ldexpf, exactly, where the power is a float** (including subnormal powers): both round the
  exact product once. That keeps the device derive bit-identical to numpy's `ldexp` without `ldexpf`'s slow path.
- **The derive's device/twin agreement needs its odd paths on the device too.** The preflight runs three shapes (n not a
  multiple of 8, buffers off 16-byte alignment, partial warps and passes) and rows of FP32 subnormals and near FP32's top.
  A CPU fake device can't reach those paths.
- **Node 2 builds cheaply on its own CPUs.** Pin the builder's toolkit from NVIDIA's redistributables rather than use the
  node's CUDA 13.0, so every build's SASS matches the builds behind earlier numbers: the node-2 build has the same MMA
  counts in all 35 kernels as the earlier one. Cache objects by unit: an edit to `harness.cu` rebuilds in 1 minute, not 9.
- **cuBLASLt's NVFP4 heuristic on sm_120 has one algorithm** (70, tile 20, 37 stages) in split-k variants, so more
  heuristic candidates find nothing. Enumerating by hand confirms it: in 12.9 and 13.1 alike, every accepted NVFP4
  configuration is that kernel, and neither version accepts any MXFP4 configuration.
- **`research fetch` right after a run exits can report `preserved=NO`** while the classifier is still writing its
  files. Fetch again a few seconds later.
- **Node 2's "cuBLASLt 13.0" is 13.1.1.3.** CUDA 13.0's `libcublasLt.so.13` points at it. Record the library's own version,
  as `versions()` does, never the toolkit's.
- **cuBLASLt's search space differs by orders of magnitude between families and versions.**
  - At 8,192³, 13.1 accepts 8,192+ FP8 configurations (the enumeration truncated there), against 638 checked for NVFP4.
  - Enumerating every family made the first search run (`r20260930-084218-64ec`) too slow to finish in its lease, and I
    stopped it. So `--lt-enumerate` takes a family list.
- **A run killed by SIGTERM lost everything,** because nothing wrote the JSON on the way out. `bench.py` now turns SIGTERM
  into a clean stop that writes the JSON and exits 143 (`36df5171`). A fill job's `timeout` or preemption no longer loses
  finished shapes.
- **Editing a script while bash runs it** lets bash read a half-written file (a syntax error mid-run). Never edit a file a
  running command reads.
- **CUTLASS's default tile raster is fine while one wave's panels fit in L2, and costs about 2× when they don't**
  (32,768³). A GEMM's raster order and swizzle are configurations to tune like tile shapes. cuBLASLt's algorithm 70 handles
  it itself; CUTLASS doesn't unless asked.
- **A bigger tile can stop helping before it stops cutting bytes.** NVFP4's 256×128 tile cut L2 bytes per FLOP by 25% and
  bought 1.9%. The block-scaled kinds sit 7–11 points under the unscaled ones in every library, so the next limit is the
  mainloop, not the memory system.

## Fill candidates

All four are untimed and run on one GPU. **Three are already in the fill queue, written by the infra lane (bc-efe47341)**
from this table, in `/workspace/pouw/fill/queue/` on node 2 with outputs under `/workspace/pouw/fill-out/harness/`:
`infra-harness-autotune-<shape>.sh` (one per panel shape), `infra-harness-characterize-gpu<0–7>.sh` and
`infra-harness-hold-600s.sh`. They run harness `7be37429` with the build `art:d54534ea…` (the same SASS as today's). So I
haven't written duplicates.

**The fourth, the FP4 sweep, is done.**
- It ran as `harness-fp4-sweep-36df5171.sh`, 09:04–09:11Z, one shape per chunk (exit 99 until the last), `prio=10`.
- Inputs: `/workspace/pouw/fill-out/harness/inputs-36df5171/`. Outputs: `/workspace/pouw/fill-out/harness/fp4-sweep-36df5171/`,
  preserved as `art:f3f2aefdc897daa72d2daedc88bb4f3d646457b38004cec574c391c54560be11`.
- The results are under the FP4 baseline search, above. They supersede the FP4 rows of the `7be37429` autotune.

| Job | Command after `$E` | GPU-hours (Estimated) | Restartable | Yields |
|---|---|---|---|---|
| **Autotune the baselines at every panel shape** (21 shapes) | `"$PY" benchmarks/pouw/harness/bench.py $G --shapes <one shape> --reps 20 --out "$RESEARCH_RUN_DIR/bench.json"`, one run per shape | about 0.5 in total (32768³ is most of it) | yes, per shape | each shape's winning kernels and ids, so later timed windows time only finalists; the plain side of the 2k–32k frontier and the 7B/70B linears (untimed, shared node) |
| **Characterize every GPU** (8 runs, one per GPU the lease gives) | `"$PY" benchmarks/pouw/harness/characterize.py $G --out "$RESEARCH_RUN_DIR/characterize.json"` | about 0.2 (1.5 min each) | yes, per run | die-to-die spread of mma.sync peaks, DRAM and L2 bandwidth and power-cap behaviour, which says whether GPU 0's baselines transfer to whichever GPU an arm's window times on |
| **Long hold, 10 min per family** (FP8 and NVFP4 in one run) | `"$PY" benchmarks/pouw/harness/characterize.py $G --sections identity hold --sustain-s 600 --out "$RESEARCH_RUN_DIR/characterize.json"` | 0.35 | yes, as a whole run | the steady-state clock and power under the power cap; whether FP8 settles below 2,077 MHz, which bounds how long a timed window may run before its numbers drift |
| **FP4 baseline sweep** (done 09:11Z, `36df5171`: both cuBLASLt versions enumerated, 19 CUTLASS sm_120 FP4 kernels) | `bench.py $G --shapes <one shape> --families nvfp4 mxfp4 --lt-enumerate nvfp4 mxfp4 --reps 20`, one chunk per panel shape | 0.12 (Measured: 7 min on one GPU) | yes, per shape | each panel shape's FP4 divisor with the new kernels (above) |
| **FP8's cuBLASLt enumeration** (queued 15:35Z, `485a64660`, `art:46a3756b…`; from 16:18Z version b, `harness-fp8-enum-b-af2d27e0.sh`: slices `--screen-only`, finals with `--cutlass-sched`, split-k shapes last) | `bench.py $G --shapes <one shape> --families fp8-e4m3 --lt-enumerate fp8-e4m3 --lt-enumerate-range A:B --decode-method independent --reps 20 --finalists 2`, one slice per chunk; then per shape `--lt-enumerate-names` (the 16 fastest by screen time) `--reps 20` as a chain at decode | not known before the first slices; 32768³ is most of it | yes, per slice | FP8's divisor at every panel shape, searched over both cuBLASLt libraries' whole spaces |
| **CUTLASS's tile orders** (queued 16:02Z, `73339a279`, `art:3bf425e6…`) | `bench.py $G --shapes <shape> --families F --cutlass-sched F --reps 20`, one (shape, family) per chunk: MXFP4 and NVFP4 at 32,768³ and 16,384³, FP8 at both, MXFP4 and NVFP4 at 8,192³ | 0.2 (Measured: 8 chunks, 42–203 s; done 16:17Z) | yes, per chunk | the big cubes' CUTLASS divisors with the order tuned (16:20Z table); `/workspace/pouw/fill-out/harness/cutlass-sched-73339a27/<shape>/<family>/` |
| **FP4 tile-order sweep** (queued 16:18Z, `af2d27e04`, `art:3bf425e6…`) | `bench.py $G --shapes <shape> --families nvfp4 mxfp4 --cutlass-sched nvfp4 mxfp4 --reps 20`, one chunk per shape, at the 18 panel shapes the tile-order job didn't cover | about 0.5 (Estimated) | yes, per shape | every FP4 divisor with the order tuned; `/workspace/pouw/fill-out/harness/fp4-sched-af2d27e0/<shape>/` |
| **Per-die baseline screen** (queued 3:18 PM PDT, `dd23c0c36`, build bab84c16; below) | `bench.py --gpu <D> --shapes <shape> --families F --cutlass-sched F [--lt-enumerate fp8-e4m3 --lt-enumerate-names <frozen names>] --finalists 3 --reps 20`, one (shape, family, die) per bench call, 40 per die | planned about 13 (Estimated); trimmed 3:35 PM PDT to the headline shapes: about 1.2 (Measured) plus at most about 0.9 of in-flight chunk tails (Estimated) | yes, per item | per-die evidence for the panel's two divisors: the verity plain kernels against the best CUTLASS and cuBLASLt entries on every die |

**The per-die baseline screen** (queued 3:18 PM PDT; trimmed to the two headline shapes at 3:35 PM PDT, whose items
were all done by then, about 1.2 GPU-h Measured; checkpoints above). It is screening only: a shared node, no arm, not a
panel row. The shape list below is the plan as staged.
- Jobs: `harness-perdie-d<D>-dd23c0c3.sh` for D = 0–7, each `gpus=1 on=<D> max_min=8 prio=10`. It runs bench.py at
  #588's head `dd23c0c36` (which contains #491 `80bff34cc`), with build bab84c16 (`art:01c2f39c…`).
- Each bench call covers one (shape, family, die), 40 items per die: NVFP4 and FP8 E4M3 at the 18 panel shapes, 8,192³
  and 16,384³.
- Candidates: #543's `verity_nvf4_256x128_o_ew` or #570's `verity_fp8_256x128_o_ew`, against cuBLASLt's heuristic
  candidates and CUTLASS in every tile order (`--cutlass-sched`), with `--finalists 3`.
- FP8 also takes the split enumeration's merged names at the 14 shapes that had them at staging. The copies are frozen in
  `inputs-bab84c16/names/` with `SHA256SUMS`, so every die sees the same candidates. The other six (4,096³, 8,192³,
  `qwen2.5-7b-down-decode` and the three Llama-70B decode shapes other than `o`) use the heuristic only.
- Chunks: items run back to back within one chunk of 8 minutes or less, each under `timeout`. The script exits 99 while
  items remain. An item that times out on a shortened budget is retried first in a later chunk; one that times out on
  the full 420 s is marked `.failed`. Any other failure stops that die's job (exit 1).
- The SASS gate ran once, on the CPU, into `inputs-bab84c16/sass-gate-cache/`. Operands are filled on the device, and
  each gate checks sampled rows and columns of D against numpy.
- Outputs: `/workspace/pouw/fill-out/harness/perdie-dd23c0c3/d<D>/<shape>/<family>/` (`bench.json`, `bench.log`, `exit`,
  `wall_s`).

**The FP8 enumeration** is `/workspace/pouw/fill/queue/harness-fp8-enum-485a6466.sh`, outputs under
`/workspace/pouw/fill-out/harness/fp8-enum-485a6466/<shape>/` (`s<A>-<B>/` per slice, then `final/`).
- Each chunk's bench runs under `timeout 420`, so no chunk passes 8 minutes. The first slice is 256 configurations (64 at
  16,384³, 16 at 32,768³). The next is sized from the last one's wall time toward 300 s, at most doubling, and a slice that
  timed out or was killed is retried at half.
- Both libraries (12.9.2.10 and 13.1.1.3) take the same index range. A shape's slices end once the start passes every
  library's accepted count, or a slice takes none. A shape records `inconsistent` if `checked` or `accepted` differ across
  its slices, and `failed` if a slice has no enumeration record.
- Screening only (a shared node, not a quiet window): nothing here goes on the panel. The finals' kernels go to the next
  timed window.

## Next

From 6:12 PM PDT (coordinator's rulings; server.md 6:12 PM PDT):
- **Divisors.** FP8 8,192³ takes `verity_fp8_256x128_ew` (1.4148 ms), and NVFP4 8,192³ takes `_o_ew` (0.7245 ms). The
  panel adopts neither until a confirming timed whole-node row passes. Until then every row keeps today's divisor.
- **The harness fix and the decode gaps** are done in code on #491 `aa4f95db9` (checkpoint 6:32 PM PDT). The FP8 names
  being taken is untested on the card: no GPU time.
- **The confirming row**, for the coordinator to take to compute-accounting:
  - Tree: #588 with #491 `aa4f95db9` merged (bc-6da61042's branch, or a run tree of mine stacked on it), build bab84c16
    (no native change), and a PoUW arm per family with its poisoned dump and verifier. NVFP4: Pearl-C4 `PearlC4Nv`
    (#580, which has `8e1ece3b6`). FP8: GPU 1's `PearlCSm120`.
  - Run: one `gpu-lease 8 --wait --timed --max-min 20` window with two bench calls, because a names file applies at
    every shape. Prefill: both families, `--cutlass-sched`. Decode: also `--lt-enumerate fp8-e4m3 --lt-enumerate-names
    names/m32-n8192-k8192.txt --lt-enumerate-max 140000`. Then `verify.py --tier 2b` on each.
  - It measures each arm's slowdown over the fastest plain GEMM, with every library's best timed as a finalist and, at
    decode, chained. It also gives per-rep SM clocks on both sides, the transcript's ACCEPT and the no-write control's
    REJECT.
- Queue nothing until compute-accounting approves. Tonight's goals of record come first on node 2.

From 3:02 PM PDT (coordinator): **read the per-die screen** at the two headline shapes (all items done). For each shape,
set the verity kernel's time against the best CUTLASS and cuBLASLt entries on every die, and flag any die whose winner or
ratio differs. That answers the two-divisor question before the timed row adopts them.

From 17:16Z (coordinator): #583's poisoning is the one, and every arm moves onto `dump`.
1. **GPU 5 (bc-71c6ab78): take `8e1ece3b6`** from `cursor/pearl-c4-harness-dump-d2f2` (one commit on your #580 head
   `0fa9ff70e`; checked on the card, 18:00Z, above), and run on #491 at `80bff34cc`.
2. **Tell the coordinator when every arm has `dump`** on its owner's branch (table under "For GPUs 2 and 5").
3. **#588 carries my withdrawn v0.5**: `e0fa1f0bb` merges `508c7b5ea` into `cursor/harness-helper-cd3d`. Merged with
   #491's head as it is, it would bring back the second poisoning path (`replay`, `--judge-controls`,
   `transcript(dir, read)`). My suggestion for bc-6da61042: revert that merge (`git revert -m 1 e0fa1f0bb`), then merge
   `80bff34cc`. Its `BenchArm` and step-group commits don't depend on v0.5.
4. **Read the first measured -h1 run of GPU 2 or GPU 5 on #491**: its `poisoning` record and each row's
   `--negative-control`.

The fill below keeps running, without the FP8 enumeration (stopped 17:10Z; split workers continue it).

Before 16:28Z:
1. **Run the verify step on a real verifier** as soon as GPU 1 or GPU 5 has a run with the v0.4 lines (above), or on GPU 1's
   existing transcripts, CPU only.
2. **As fill, in chunks of 8 minutes or less** (exit 99 to continue, `prio=10`):
   - FP8's cuBLASLt space: queued 15:35Z (above). Read its finals, and time the winners in the next window.
   - CUTLASS's tile raster and swizzle: the big cubes are done (16:20Z table), and the other 18 panel shapes are queued
     (`harness-fp4-sched-af2d27e0.sh`). Read those, then time every FP4 winner and the 32,768³ rows in the next window.
     From here on, arms' runs pass `--cutlass-sched nvfp4 mxfp4 fp8-e4m3`, so the divisor includes the orders.
   - FP8's decode spaces (8 split-k shapes, 134,216 configurations each at `m32-n8192-k8192`) come last in version b. Once
     its first decode slices are screen-only, size how long they take; if that is too much fill, ask whether to sample.
   - **Stream-K at 256×128,** at most 1.0% at 8,192³: one more CUTLASS entry, in the next rebuild.
3. Help GPUs 1 and 5 with their first decode rows through the chain, and append their panel rows if they don't.

The block-scaled NVFP4 mainloop isn't mine: bc-fb55a759 writes it after its v1 work, as one header used by both the plain
baseline and Pearl-C4's arm (09:32Z). When it lands, the harness times it as an NVFP4 baseline candidate.

## Needs

None. GitHub takes my pushes again (17:24Z), and #491's head `80bff34cc` is on origin; nobody needs to push it for me.
