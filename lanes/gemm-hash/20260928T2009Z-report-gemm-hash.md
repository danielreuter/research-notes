---
lane: gemm-hash
kind: report
created: 2026-09-28T20:09Z
status: final
---

CHECKPOINT f639cd66 (17:02Z) [final] plan corrected with M0's profile: SHA 54-70% of GEMM session; kernel 1.17x on #101; new row 1b (pinned+overlap+coalesced+device z) 1.18x; all four levers 6.6e6 L40S (3.2x), 5.8e6 H100 NVL (2.6x); $0
CHECKPOINT f639cd66 (16:11Z) [final] plan updated with the measured native kernel: 1.15x on #101 (projected 1.52x; per-compression cost unchanged at 1.15 us); all three levers now 7.1e6 L40S (2.9x), 6.3e6 H100 NVL (2.4x); $0
CHECKPOINT f639cd66 (00:04Z) [final] plan rebaselined on the non-GEMM re-proof: #101 2.16e7x L40S, ~1.5e7x H100 NVL (scaled); native kernel 1.52x/1.42x on #101; tiles 1.96-2.38x; all three 3.5x; $0
CHECKPOINT f639cd66 (22:03Z) [final] plan rebaselined on #327: #101 3.4e7x native L40S (~2.8e7 H100 scaled); SHA 72-84% of GEMM session; native kernel now 1.6x GEMM / 1.24x #101; next: kernel (M0, vs #328), tiles, re-prove non-GEMM on #327; $0
CHECKPOINT f639cd66 (21:11Z) [final] #328 (draft, stacked on #289) @ f639cd66: native SHA-512 witness CPU reference matches eval64 on every row of sha512x3 and hm96 (pinned + carries-every-16) and on staged RoPE / K=256 GEMM; kernel, GPU hour, host bucket are M0's; $0
CHECKPOINT f639cd66 (21:10Z) [open] #328 f639cd66: native SHA-512 witness CPU reference matches eval64 on every row, streamed in row order (4-word ring), rows labelled + pinned per M0's 2042Z handoff (answered 2110Z); CUDA/GPU/host bucket are M0's
CHECKPOINT 0542811c (21:01Z) [open] native SHA-512 witness CPU reference matches eval64 on every row (sha512x3, hm96, carries-every-16; selftest on RoPE + K=256 GEMM): draft #328 stacked on #289; handoff to flock-netlist 2100Z; CUDA/GPU/host bucket are M0's
CHECKPOINT 788bf662 (20:54Z) [open] native SHA-512 witness reference drafted (backends/flock/live/src/sha512_native.rs + selftest case native_sha_matches_eval64) on cursor/native-sha512-witness-1575 off 788bf662; building/testing on CPU
CHECKPOINT ac412eb8 (20:44Z) [open] reopened for the native SHA-512 witness CPU reference (emitter vs eval64) on a branch off #289 788bf662, draft PR; NOT final; no pods
CHECKPOINT ac412eb8 (20:37Z) [final] plan docs/gemm-hash-cost-plan.md: SHA 26-44% of GEMM time post-#289 (host 47-64%); top pick native SHA-512 witness kernel 1.11x on #101 (prover-only); K=8192 2x4 at 2^27 needs carries-every-16 (13 per 2^20); no pods, $0
CHECKPOINT ac412eb8 (20:30Z) [open] measured (CPU): SHA is 26-44% of GEMM session time post-#289 (host bucket 47-64%); no-hash ceiling 1.30x today, 1.07x after tiles; top pick native SHA witness kernel (1.11x); K=8192 2x4 needs only carries-every-16 (13 per 2^20), not <=65,536 rows; writing plan
CHECKPOINT ac412eb8 (20:09Z) [open] started: ranked plan for GEMM in-circuit SHA-512 cost (CPU only, no pods); reading M0 statement, #289 buckets, tile scope; agent bc-abeef3db
# gemm-hash: a ranked plan for GEMM's in-circuit SHA-512 cost

Brief: from the vLLM Project coordinator (agent bc-abeef3db). Analysis plus CPU measurement only: no pods, $0, no code on any branch.
Deliverable: Project store `docs/gemm-hash-cost-plan.md`. Scripts: `internal/gemm-hash-measurements.py` (M0's own circuit builder and layout,
on `main` `ac412eb8`) and `internal/gemm-hash-hostbench.rs`. Inputs: the #289 m = 34 runs' phase buckets (`r20260928-164500-5979` L40S,
`r20260928-164803-8f25` H100 NVL, `r20260928-163419-65fc` L40S `main`), read through a local `research data refresh`.

## Findings
- **Time share.** After #289, SHA-512 is 26–44% of a GEMM session, although it's 83% of the ANDs. The host bucket (the unit's host
  evaluation and staging) is 47–64%. Removing every row hash would be worth at most 1.30× on #101 today, and 1.07× after the K = 2048 tiles,
  because the unit slot (2^21 or 2^23, 56% full) sets bits per coordinate at twice its size.
- **Top pick: a native SHA-512 witness kernel.** It's prover-only, with byte-identical proofs. `t.witness_comp` fits 0.125 s + 1.41 µs per
  compression per rep on the L40S (0.156 s + 1.46 µs on the H100 NVL), which is level-bound. A native kernel would take it to about 10 ms.
  That's 1.11× on #101 on both GPUs, or 1.04–1.05× after tiles.
- **The compression.** It has 57,947 real ANDs, and 81,402 AND rows today. At most 65,536 rows (4 per 2^18) is unreachable: the round
  words alone are 14,336 commit rows. Committing carries every 16 bits gives 74,563 AND rows, and 13 fit a 2^20 slot. That's enough for
  K = 8192's 2×4 tile at 2^27 (2^24 per coordinate), and for an untiled K = 2048 statement in 2^23. It's worth 1.03–1.04× on #101 after tiles.
- **BLAKE3.** 19,594 AND rows per 64-byte block, or 306 per byte against SHA-512's 636. It's a scheme change for Daniel, and it's worth at
  most 1.07× after tiles.
- **The host's hashing since #289.** hm96 costs 6.3 ms of `eval64` plus 2–5 ms of transpose per 64 slots per thread. `main`'s bitwise
  pack took 155–176 ms per group, which is probably most of `main`'s K = 2048 host bucket.

## Handoffs
- Sent: `lanes/flock-netlist/20260928T2035Z-handoff-from-gemm-hash.md`, with the K = 8192 slot density, the native witness kernel proposal
  and the host bucket numbers. It asks M0 whether they take the kernel or gemm-hash writes its CPU reference after #289 merges.
- Received: none.

## FINAL

~~~text
tip: none (no code; analysis and CPU measurement only)          merge-with: none
known-failures: none                                             pod: none; $0
artifacts: none new (reads art:3b7edac2, art:95b9b350, art:27ac34ee run files)
~~~

Next steps are in the plan's "Next": Daniel's call on about one L40S hour for the kernel's byte identity and timing, M0's answer on
who builds the kernel, and the K = 8192 slot going into the tile scope's follow-up once 2^27 is granted.

## Reopened 20:40Z: the native SHA-512 witness's CPU reference (plan row 1)

Asked by the vLLM Project coordinator: an emitter checked bit for bit against M0's `eval64`, CPU only, $0, on this lane's own branch
based on #289's head, as a draft PR. M0 takes the CUDA kernel, the GPU byte-identity hour and the host bucket.
- **PR:** [#328](https://github.com/danielreuter/verity/pull/328), draft, `cursor/native-sha512-witness-1575` @ `0542811c`, based on
  `cursor/flock-gemm-witness-4d6a` @ `788bf662`. It adds `backends/flock/live/src/sha512_native.rs` and the selftest case
  `native_sha_matches_eval64`.
- **It matches.** The plans for the pinned `sha512x3` and `hm96` circuits, and for the carries-every-16 variants, are equal to `eval64`
  on every row: random, all-zero and all-one lanes, and lane by lane against `eval64` + `lanes`.
  - The selftest case passes on staged `rope-head/d64/neox-bf16` (8 instances) and `gemm-coordinate/k256/sm80-mma-bf16` (4 instances,
    4-compression chains), padding instances included. `honest` and `host_units_match_witness` still pass.
  - `check_build.sh` passes.
- **For the kernel:** a streaming emitter keeps 2 tape words behind the newest. On one CPU thread, 64 slots take `eval64` + `lanes`
  9–13 ms and native slot by slot 39–46 ms: bit-slicing wins on a CPU, so this is the device kernel's reference, not a host path.
- **Handoff sent:** `lanes/flock-netlist/20260928T2100Z-handoff-from-gemm-hash.md`, with the split and the plan's interface.
- **Received:** `lanes/gemm-hash/20260928T2042Z-handoff-from-flock-netlist-native-sha512-split.md` (M0). It agrees to the split and asks
  for straight-line `u64` code emitting rows in row order, a row-to-role map derived from the laid-out circuit, a test that fails on a
  row-order change, and tests on random inputs and `Stmt::row_inputs`. All four are met on #328 at `f639cd66`:
  - a `Stream` sink with a 4-word ring (window 2);
  - `Role`, `kind`, `describe` and `census` (`sha512x3`'s census equals the builder's counts);
  - matching by kind as well as values (a folded carry row had taken a commit's place, value-identical);
  - the circuits' and plans' SHA-256 pinned.
- **Sent:** `lanes/flock-netlist/20260928T2110Z-handoff-from-gemm-hash.md`, mapping each ask to #328.

## FINAL (reopened work, 21:15Z)

~~~text
tip: cursor/native-sha512-witness-1575 @ f639cd66 (base cursor/flock-gemm-witness-4d6a@788bf662)   merge-with: #289 (it stacks on it) | PR #328 (draft)
known-failures: none                                             pod: none; $0
artifacts: none new
~~~

The CPU reference matches `eval64` on every row. The CUDA kernel, the GPU byte-identity hour and the host bucket are M0's, per their
20:42Z handoff. Open offer to M0: the plan precomputed into META, or as run-length segments, on #328 if they want it.

## Rebaseline on #327 (22:00Z)

M0's #327 removed the host bucket (L40S m = 34: 3.055 → 1.202 s at K = 2048, 3.956 → 1.401 s at K = 8192; `r20260928-213503-2861`;
`internal/lanes/flock-netlist/20260928T2155Z-handoff-from-backend-sweep-327-host-buckets.md`). The plan (`docs/gemm-hash-cost-plan.md`)
is rebaselined, and the time model is `time 327` in `internal/gemm-hash-measurements.py`.
- **#101:** 3.4 × 10⁷ × native on the L40S; about 2.8 × 10⁷ on the H100 NVL (scaled).
- **SHA-512 share of a GEMM session:** 72–84% on the L40S, 69–82% on the H100 NVL.
- **Native kernel:** 1.60× on GEMM and 1.24× on #101 on the L40S (1.49× and 1.15× on the H100 NVL).
- **Order:** unchanged. The host bucket is done, and re-proving the non-GEMM shapes on #327 (half of #101) takes its place.

## Rebaseline on #101's non-GEMM re-proof (00:00Z Sep 29)

- **Received:** `lanes/gemm-hash/20260928T2355Z-handoff-from-backend-sweep-327-non-gemm.md` (backend-sweep, via verity-root). The top 8
  non-GEMM shapes re-proved on #327 fell 4.9×, and #101 on the L40S is 2.16 × 10⁷ × native (GEMM 80%, 839 carried shapes 5.3%).
- **The plan** (`docs/gemm-hash-cost-plan.md`) and `time 327` (`internal/gemm-hash-measurements.py`) are updated:
  - **#101:** 2.16 × 10⁷ on the L40S; about 1.5 × 10⁷ on the H100 NVL (GEMM from #289's device buckets, non-GEMM × 0.88).
  - **Native kernel:** 1.52× on #101 on the L40S and 1.42× on the H100 NVL. That includes 7.5 × 10³ s from the small shapes, whose rep-0
    SHA witness is 38–42% of their sessions.
  - **Tiles alone:** 1.96–2.38× on the L40S and 1.83× on the H100 NVL. Tiles, the kernel and the denser slot together: 3.5× and 2.8×.
  - **Order:** unchanged. Row 3 is done for the top 8.

## The native kernel, measured (16:10Z Sep 29)

- **From root:** M0's native SHA-512 kernel runs on the L40S at m = 34 (`r20260929-154509-1893`, baseline `r20260929-155406-2df4`,
  identity `r20260929-153234-18cf`). It's byte-identical. The median prove goes from 1.147 to 0.979 s (1.17×) and from 1.339 to 1.175 s
  (1.14×).
- **Why it's short:** the native compression witness fits 0.040 s + 1.15 µs per compression. The level-by-level pass was 0.153 s +
  1.15 µs, so only the level syncs went away.
- **The plan** (`docs/gemm-hash-cost-plan.md`, `time kernel`):
  - **The kernel:** 1.15× on #101 (2.08 → 1.81 × 10⁷), against 1.52× projected. It would be 1.46× at write-bandwidth speed.
  - **All three levers:** 7.1 × 10⁶ on the L40S (2.9×; 8.1 × 10⁶ without reuse) and 6.3 × 10⁶ on the H100 NVL (2.4×). With the
    projected kernel this was 6.2 × 10⁶ and 5.3 × 10⁶.

## Corrected with M0's kernel profile (17:05Z Sep 29)

- **Received:** `lanes/gemm-hash/20260929T1652Z-handoff-from-flock-netlist-native-sha512-profile.md` (M0), with the profile in
  `internal/native-sha512-witness-profile.md`. The native SHA witness runs at 0.48 µs per compression. 87 and 125 ms per rep of the
  window is the host slots' pageable upload (1.0 and 1.7 GB). My two-point fit had charged it to the compressions.
- **The model** (`internal/gemm-hash-measurements.py time`) now adds the window's parts: memsets, host-slot upload, SHA level / native /
  coalesced, and M0's overlapped fixes. It reproduces the measured windows and M0's fix estimates.
- **The plan** (`docs/gemm-hash-cost-plan.md`):
  - **SHA:** 54–70% of a GEMM session, not 72–84%. The units' upload is 12–18%.
  - **The kernel:** 1.17× on #101.
  - **Row 1b (new):** M0's fixes 1–4, 1.18× more.
  - **Tiles alone:** 1.74–2.18×.
  - **All four levers:** 6.6 × 10⁶ on the L40S (3.2×; 7.4 × 10⁶ without reuse) and 5.8 × 10⁶ on the H100 NVL (2.6×).
