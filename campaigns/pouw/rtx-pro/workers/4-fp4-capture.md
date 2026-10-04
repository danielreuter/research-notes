---
cursor:
  subagentId: "bc-36186951-83fc-53b6-87de-fa584ddf9ff9"
---

# GPU 4: FP4 tensor-core capture (sm_120, RTX PRO 6000)

Worker bc-36186951. On node 2 through `gpu-lease 1 --wait` (one GPU at a time, `GPU_LEASE_WHO` = my bc-id, identity gate
`--expect-uuid '$GPU_LEASE_UUID'`). Branch `cursor/fp4-capture-sm120-9ff9` (head `6ed30ed6`, pushed). Done: the 10:32Z
13-vector capture (Results §7), the 09:38Z bit-7 check (§8), F1 (§9, collect `r20260930-111747-26f3`), F3 (§10, collect
`r20260930-121238-ba0a`), F2 (§11, collect `r20260930-124558-83f4`), the 15:57Z 17-vector scale-decode capture (§12,
`r20260930-161935-83a8`), the 18:26Z order's first (a) pass (§13), and the second (a) pass and the sparse E4M3 capture
(GPU done 21:55Z; 0.18 GPU-hours, Measured). Three CPU verifies are running or queued on node 2 (21:56Z entry).

## Checkpoints

- 04:47Z: started Phase A; store mounted; server.md: pending.
- 05:20Z: inventory and recheck plan written (below); toolchain nvcc 12.9.86 + cuobjdump (apt `cuda-nvcc-12-9`); the FP4
  kernels build for `sm_120a` with the RTX 5090 records' opcodes.
- 05:20Z (b): probe extended: 5 K=32 E2M1 rows, `--chain L` in registers, `--expect-uuid`, `--fake-silicon` /
  `--corrupt-word` / `--sass-only` gates. SASS (Derived, offline): unscaled and UE8M0 K=32 E2M1 lower to QMMA (the FP8
  datapath), not OMMA; `mxf4nvf4 .scale_vec::4X .ue8m0` is refused by ptxas 12.9.
- 05:50Z: casts (6 `cvt` rows), stage 0 (ptxas + SASS of every FP4-path row, 2:4 sparse included), the W1 price bench
  `tc_price_fp4`, a CPU test suite `tools/tc_probe_fp4/tests`.
- 06:05Z: Phase B on node 2. The branch took `origin/main`'s research CLI (ssh provider); jobs run under
  `uv run --no-project --with numpy` with `--cwd source`.
- 06:21–06:25Z: 2:4-sparse word capture against the dense `mma.sync`, NVF4 (`r20260930-062133-46bb`) and MXF4
  (`r20260930-062526-34e7`), both gated and passed; answer in Results §1.
- 06:43Z: W1 run `r20260930-064322-e7ca` (GPU-fb680060…, gates passed). Found a clock bug in my bench: the median block's
  clock64 span read 1,562 MHz on MMA loops and 1,228 MHz on op loops against 2,092 in nvidia-smi, which inflated per-clock
  rates 1.34–1.71× and skewed op prices against MMA prices. Fixed in `4dcced62` (a launch's clock is its longest block span,
  ≈ 2,098 MHz), with a test that fails on the median. The MMA price ratios were unaffected.
- 06:50Z: W1 rerun `r20260930-065015-32af` launched (`287b9574`); at 07:00Z its `gpu-lease 1 --wait` still waits behind two
  whole-node windows. Results §2 is re-derived from e7ca's launches until it lands.
- 06:55Z: the remaining 16 recheck rows run as a sequential queue, one lease at a time, each waited on before the next, from
  a worktree pinned at `287b9574` (row list under Fill candidates).
- 07:12Z: W1 rerun `r20260930-065015-32af` done, gates passed; §2 is now its numbers (Measured, locked-2100,
  GPU-5f1149a4). The recheck queue's first row, `r20260930-071201-d356` (f8f6f4 E2M1 with nonzero C), launched.
- 07:15Z: the Lean-shaped spec is in `internal/pouw/rtx-pro/fp4-capture/sm120-fp4-step-for-lean.md`: codecs, exact
  product, the step, the sparse gather, the noise-atom lemma, a closed-form "no `Pipeline` computes the FP4 step" pair,
  and the smallest extension of `Pipeline`. Its hardware check is the new family `scale_split_twins` (commit `23ee4411`),
  queued for NVF4 and MXF4 after the rechecks.
- **Default (recorded):** my recheck rows stay recorded `research run` jobs in my own one-lease queue, not fill-queue
  scripts. They are capture evidence and must be preserved from the pod, and the fill runner starts nothing while
  waiters queue anyway.
- **Flag:** my four runs above passed `--timeout 1800` to `research run --on vy-nebius-2` before I read the lesson against it.
  Each launch's lease report shows node 2's expiry unchanged at its fixed deadline (2026-10-02T04:57:26Z, clamped), so no
  lease moved; the queue no longer passes it.
- 07:33Z: the four L ≤ 1024 chains are done, 0 mismatches (§3). A 260-word capture sample of d356 (the words the refuted
  K=32 candidates miss) is fixture `art:4707d86cdc852c88a44a2382e9d591e33f76a7974179d1316f521b387ceaf16f`. The model
  `BLACKWELL_SM120_E2M1_M16N8K32` and its replay test wait for the fresh-seed confirmation before they are committed.
- 08:15Z: all queues done. The fresh-seed confirmation passed and the model landed (`7d327f96`, `39dfe2d3`); the six casts
  match; the twins refute every `Pipeline` on the device for NVF4 and MXF4 (§4); the f8f6f4 chain rerun is valid on a
  second die. The fixture's id is `art:cc1f274f…` (re-registered in the registry's canonical form; the 07:33Z id is void).
  Its builder is `internal/pouw/rtx-pro/fp4-capture/build_k32_fixture.py`: run it on the fetched d356 to get the same bytes.
- 08:47Z: the 08:20Z T1 item is done: `r20260930-084518-2674` (`--instruction sp_nvf4_t1`, commit `fcad808d`, clean
  worktree), GPU-af0bf9e0, one 63 s lease, every gate passed; Results §5. No recheck row of mine was running when it came
  in (every queue finished at 08:15Z), so it went first.
- 09:09Z: the 08:56Z ask (1) is done. The four fresh-seed sweeps were rerun from clean `fcad808d`, all gates passed, 0
  mismatches against `verity`, all PRESERVED (Results §3, first table). They ran as four back-to-back one-GPU leases of
  39–52 s each (09:03–09:08Z), not one lease, so each has its own run id. Verification is interleaved with the capture and
  takes about 45 s, so no split was needed.
- 09:28Z: asks (2) and (3). The branch is pushed with the metadata-rule capture (`25614709`, `sp_{nvf4,mxf4}_meta`, a
  CPU dry run and tests). NVF4 `r20260930-092605-fdc9` and MXF4 `r20260930-092713-6acd` both passed; Results §6. The
  Lean spec's §4 gained the all-16-nibble rule.
- 10:05Z: the 09:37Z orders (F1, then F3, then F2, as fill jobs). F1 is `tools/tc_probe_fp4/f1_rates.py`: every
  `mma.sync` kind, shape and sparsity form ptxas takes for sm_120a, the SIMT honest arms, and a libscan of node 2's CUDA
  libraries (cuBLASLt, cuSPARSELt) for undocumented multipliers. Pass 1 (`98f84dcf`) is superseded by pass 2 (`b9a6c5a5`,
  build `8b0c72db` from `r20260930-102658-7ad4`, libscan `r20260930-101707-11bc`).
- 10:30Z: the 09:38Z bit-7 check is done (§8, fill job `fp4-bit7-85df9336.sh`).
- 10:56Z: the 10:32Z 13-vector capture is done: `r20260930-105507-3e10` at clean `a5b0f57e`, every gate passed, 13 of 13
  words match the file's prediction (§7).
- 11:00Z: F1 pass 2: 9 of 10 families passed their gates; `f8f6f4` failed its output gate (FP16-accumulated E3M2 not
  finite). Cause: my FP6 container was wrong (`code << 2`; PTX puts E3M2 and E2M3 in the low 6 bits), so the card read
  larger exponents. Fixed in `5ea658eb`; `f8f6f4` and `mxf8f6f4` re-run as fill job `fp4-f1-fp6-5ea658eb.sh` (queued 11:04Z)
  on the same library. Rates of the other families are unaffected.
- 11:04Z: the branch is pushed (`a5b0f57e`, `5ea658eb`). Pushes had failed with "Authentication failed" from 10:58Z; the
  retry went through.
- 11:17Z: F1's FP16-accumulated E2M1 form was not finite after 100,234 iterations: my FP16-accumulate domains let a K-sum
  exceed 16, and a chain on fixed operands then grows to inf. Fixed in `258cb1c1` (the smallest-magnitude codes, so every
  K-sum is at most 16, half an FP16 ulp once |D| ≥ 2^15), with a test that fails on the old domains. The f8f6f4 rerun
  passed; `runs-final` holds each family's passing record; the collect is `r20260930-111747-26f3`.
- 11:33Z: F1 collected, validation passed (§9).
- 11:50Z: F3 committed (`5d038ce0`): `tools/tc_probe_fp4/f3_lut.{cu,py}`, tool `tc_lut_fp4`, CPU tests. Build
  `r20260930-115148-1ed7` passed its SASS gate.
- 11:54Z: F3's first fill chunks stopped at their gates (native = pinned model on every sampled word; both LUT arms wrong
  on about 99.7% of words). Cause: `einsum` returned the tables strided, and the kernel reads memory order. Fixed in
  `47eecb5c`: kernels take C-contiguous arrays only, and the dry run's fake checks the same boundary. The failed job cost
  two chunks of about 10 s. Rebuilt as `r20260930-115839-c84e`; requeued as `fp4-f3-lut-47eecb5c.sh`.
- 12:13Z: F3 done: every width passed; g2c4's exact arm read below 2,079 MHz, so it was rerun once (the same result and
  label); collect `r20260930-121238-ba0a` (§10). No LUT width is cheaper than dense NVFP4.
- 12:40Z: F2 committed. `c5222786` moves the atom's align-add and OMMA wrapper from `f3_lut.cu` into `nvf4_step.cuh`
  (every F3 kernel's SASS and ptxas report unchanged); `ac9fe0fd` adds `f2_strassen.{cu,py}`, tool `tc_strassen_fp4`, CPU
  tests. Build `r20260930-124120-350e` passed its SASS gate.
- 12:43Z: fill job `fp4-f2-strassen-ac9fe0fd.sh` ran both levels in one chunk (about 20 s on the GPU); every gate passed.
  12:46Z: collect `r20260930-124558-83f4` (§11). No Strassen level is cheaper than dense NVFP4.
- 16:24Z: the 15:57Z order is done (§12). The four extra vectors are `nvf4Specials` 12, 19, 21 and 23 (`nvf4P7` 47, 57, 60
  and 63). My probe lacked two of the named gates (the 0xA5 poison and a no-write control): `178dcca4` adds them, with
  `--special-ids` and a CPU `--collect`, and `ea1ac2ec` keeps the chunk's files in the collect run. Build
  `r20260930-161606-dd5a`, fill job `fp4-lean17-178dcca4.sh` (0.2 min), collect `r20260930-161935-83a8`. All 17 match.
  The handoff JSON has 17 entries.
- 18:37Z: the 18:26Z order's part (a), the fresh-seed recheck of NVFP4 and unscaled E2M1 (`tc-model/sm120-fp4`).
  `d3b846cf` adds `recheck.py` (tool `tc_recheck_fp4`), which splits it: a GPU `capture` (UUID, SASS and layout gates,
  then probe.py's sweep families regenerated from each seed, each family's words and operand sha256 checkpointed, exit 99
  at the budget) and a CPU `verify` (the operands regenerated and their sha256 checked, the pinned model, `verity` for NVFP4
  and `bsaa_g16` for E2M1, on every word of every gated family). Build `r20260930-183411-4dc5`. Fill job
  `fp4-recheck2-d3b846cf.sh` (gpus=1) captured seeds 20261101 and 20261102 at n-random 327,680 for both instructions
  in one 1.3-minute chunk (Measured, rc 0; about 0.02 GPU-hours), 2.3 GB under node 2's
  `/workspace/pouw/fill-out/fp4-recheck2/d3b846cf/`. Every gated family has at least 10.5M words over the two seeds
  (Derived: n-random/8 tiles of 128 words per seed). Fill job `fp4-recheck2-verify-d3b846cf.sh` (gpus=0, cpus=16) runs the verify, one (instruction, seed)
  per chunk; queued, no verdict yet, not yet under a research run id. The shortcut: (a) is CPU-bound and cannot fill
  about 5 GPU-hours. Part (b), the sparse FP8 `mma.sp` capture (`tc-model/sm120-e4m3-sp-k64`), needs a new kernel;
  not written, not queued. **Corrected at 21:45Z:** E2M1's gate named the refuted `bsaa_g16`, not its pinned model, and
  four fixed-size families stayed under 10.5M words (21:45Z entry).
- 21:45Z: the 21:12Z order: why the verify failed, the fix, then the rest of the 18:26Z order.
  - **Why it failed:** `recheck.py`'s fallback gated unscaled E2M1 on `bsaa_g16`, the block-scaled adder that §3 refuted
    for QMMA, instead of `BLACKWELL_SM120_E2M1_M16N8K32` (`gs32_w26_native`). The capture itself is sound: on seed
    20261101 `gs32_w26_native` misses 0 of 131,104,768 gated words, `bsaa_g16` 15,431,066 (Measured, the failed verify's
    own counts). Its retry then exited 1 on the recorded failure, so the job went to `failed/`.
  - **The 18:37Z entry's other error:** four gated families have a fixed size, independent of n-random: NVFP4
    `signed_zero` (32,768 words per seed), `anchor_participation` (49,152) and `signed_zero_matrix` (73,728), and E2M1
    `signed_zero` (32,768). They are fixed-size random draws, not enumerations, so they were short of 10.5M.
  - **Fix, `c4d5e0b7`:** E2M1 is gated on `gs32_w26_native`, and `recheck.py` fails if its parameters stop matching
    `BLACKWELL_SM120_E2M1_M16N8K32`'s. `--fixed-mult` scales the fixed-size families (1 keeps every earlier stream).
    Flag: two changes in one commit.
  - **Part (b):** `c2e83fda` adds `sp_e4m3.{cu,py}` (tool `tc_sparse_e4m3`). `6ed30ed6` makes its verify resumable per
    family, so a gpus=0 chunk never restarts past its max_min.
  - **Builds, both SASS gates passed (Measured):**
    - `r20260930-213931-c27c` (sparse): `QMMA.SP.16864.F32.E4M3.E4M3` and `QMMA.16832.F32.E4M3.E4M3`, one each.
    - `r20260930-213945-8f13` (FP4): the same opcodes as before.
    - So ptxas takes `mma.sp::ordered_metadata … m16n8k64 … kind::f8f6f4 … e4m3` for sm_120a.
  - **Fill jobs, all at `6ed30ed6`, prio 10.** The runner has no dependencies, so each GPU job queues the next job when
    it finishes; that keeps one GPU at a time. The chained scripts wait in `/workspace/pouw/fill-out/fp4-jobs/6ed30ed6/`.
    - `fp4-recheck3-6ed30ed6.sh` (gpus=1, queued): seeds 20261103 and 20261104, both instructions, n-random 327,680,
      `--fixed-mult 160`.
    - `fp4-recheck3-verify-6ed30ed6.sh` (gpus=0, queued by the capture above).
    - `fp4-sp-e4m3-6ed30ed6.sh` (gpus=1, queued by the capture above): seeds 20261201 and 20261202 at the same sizes.
    - `fp4-sp-e4m3-verify-6ed30ed6.sh` (gpus=0, queued by the sparse capture).
    - `fp4-recheck2-reverify-6ed30ed6.sh` (gpus=0, queued): E2M1 seeds 20261101 and 20261102 of the old capture on
      `gs32_w26_native`, and NVFP4 20261101 again as the check that `--fixed-mult 1` regenerates the old streams.
  - **Sizes (Derived from the family sizes):** every gated recheck family has at least 10.5M words over each pair of seeds;
    so does every sparse family (84M words per seed).
  - **GPU-hours, stated honestly: about 0.1 in all, not 5** (Estimated; the Measured total is 0.18, 21:56Z). The work is
    host-bound: numpy generates and packs the operands while the GPU waits.
    - The first (a) pass held its lease 1.3 minutes (Measured). The new (a) pass is about 0.03 GPU-hours (Estimated).
    - The sparse capture is about 0.05 GPU-hours: one seed's host packing took 46 s locally (Measured), and its MMAs take
      under 1 s (Estimated).
    - Filling 5 GPU-hours would hold a GPU mostly idle. Keeping one busy needs the operands generated on the device, which
      I haven't built.
  - **CPU verify sizes (Estimated):** the sparse evaluator runs about 11,300 words per second per process with all three
    candidates (Measured, locally), so a seed is 8–16 minutes on 16 processes in node 2's shared 32-core fill set.
  - **Not yet under a research run id:** the verifies write `result.json` only inside a research run; publishing them is
    next, once they pass.
- 21:56Z: every GPU chunk is done, all on GPU 7 (GPU-af0bf9e0), with no failures.
  - **GPU time (Measured, the runner's minutes and gpu-lease's busy sampler):**
    - `fp4-recheck3-6ed30ed6.sh`: one chunk, 2.3 minutes, rc 0, busy 50 s of 2 m 18 s.
    - `fp4-sp-e4m3-6ed30ed6.sh`: two chunks, 6.7 minutes (rc 99, busy 10 s, 3%) and 1.7 minutes (rc 0, busy 0 s).
    - Total: 10.7 minutes, about **0.18 GPU-hours**, about 1 minute of it busy.
    - gpu-lease's own advice on the sparse chunk: "prepare on the CPU outside the lease".
    - Any larger rerun should first pack the operands in a gpus=0 job, so the GPU job only loads and launches.
  - **The sparse layout, settled on the device (Measured):**
    - Of the six packings, exactly one reproduces C + A·B on every exact-integer word: metadata `row_q1_groups_q2`, B
      `k_4q_16r`. That is the module docstring's primary reading.
    - The dense k32 chain passes too.
  - **Captured:**
    - Recheck: 2.6 GB under `/workspace/pouw/fill-out/fp4-recheck3/6ed30ed6/`.
    - Sparse: 2.0 GB under `/workspace/pouw/fill-out/fp4-sp-e4m3/6ed30ed6/` (seeds 20261201 and 20261202, 11 families each).
  - **CPU verifies:**
    - `fp4-recheck2-reverify-6ed30ed6.sh` is running.
    - `fp4-recheck3-verify-6ed30ed6.sh` and `fp4-sp-e4m3-verify-6ed30ed6.sh` are queued.
    - Their verdicts will be in `recheck.json` and `sparse.json` under each capture's `verify/` (the re-verify's under
      `/workspace/pouw/fill-out/fp4-recheck2/d3b846cf/verify-6ed30ed6/`).
    - The sparse finding is `finding.sparse_vs_dense` and `candidates_reproducing_every_sparse_word`.
  - The staging directory `/workspace/pouw/fill-out/fp4-jobs/6ed30ed6/` is empty now; both chained scripts are in the
    queue.
- 02:14Z (Oct 1): the migration handoff, under Daniel's 6:55 PM PDT ruling. It is
  `lanes/accounting/20261001T0209Z-handoff-from-bc-36186951-migration.md`, staged in
  `internal/pouw-fp8/accounting-outbox/` after a 403 from research-notes.
  - Every CPU verify finished by 23:47Z, rc 0; the verdicts are in §13 and §14.
  - Every verdict and capture record (194 JSON files) is in `internal/pouw/rtx-pro/fp4-capture/fp4-verdicts-6ed30ed6.tgz`.
    The word arrays are on node 2 only.
  - No new work starts after this.
- **Defaults (recorded):**
  - F2 gates the factored route (Strassen on the E2M1 codes, the scales applied by the atom's align-add), the one that can
    give the atom's words. Strassen on the scaled values is run and counted, never gated.
  - F2 times the Strassen dots alone; the align-add is not timed, so each price is a lower bound on the exact route's.
  - F2 runs both levels in one fill job, one level per step, the same 300 s start rule and stop-at-failure as F3.
  - F3 runs one width per step, with no width started after 300 s (exit 99), and stops at the first failed record (the
    runner retries a failed job once; the first F3 job's script skipped a failed record on the retry).
  - F3's fill job runs from the research run's verified tree (`/workspace/research/src/<sha>`), not a `git archive` copy.
  - F1 chunks are whole families, with a 300 s start budget per chunk (exit 99 past it), `cpus=4 mem_gb=16`.
  - Emulated forms (anything ptxas lowers to more than one MMA, or to SIMT) are timed as their route and priced as issued.
  - FFMA's honest arm is the immediate-operand form (`ffma_f32_imm`), the fastest SIMT FMA the bench issues.
  - Pass 1's outputs were moved aside (`/workspace/pouw/fill-out/fp4-f1/98f84dcf`); pass 2 is the one cited.
  - The FP6 re-run uses the pass-2 library and a `git archive` tree of `5ea658eb` (file sha256s checked against git).
  - F1 and bit-7 are fill jobs (no run id). Their outputs stay on node 2 until the recorded CPU-only collect publishes F1;
    the bit-7 finding is cited through §7's recorded run on the same library, and the assessor's `r20260930-093120-b2f2`.

## Results

### 13. Fresh-seed recheck beyond the gate (the 18:26Z order; fill jobs, not yet under a research run id)

`fp4-recheck2-d3b846cf.sh` ran the capture on GPU 4, and `recheck.py verify` ran as a CPU fill job (Measured):

| Row | Seed | Gated words | Pinned model | Controls' misses | Verdict |
|---|---|---|---|---|---|
| NVFP4 | 20261101 | 173,170,688 | `verity` **0** | model5 3,114,322 | passed |
| NVFP4 | 20261102 | 173,170,688 | `verity` **0** | model5 3,113,975 | passed |
| E2M1 (`f8f6f4`) | 20261101 | 131,104,768 | `gs32_w26_native` **0** | `bsaa_g16` 15,431,066; 2 × 16 groups 7,057,721; E2M1 as E4M3 1,122,210; model5 20,128,677 | first verify gated on the wrong model; re-verify at `6ed30ed6` passed |
| E2M1 (`f8f6f4`) | 20261102 | 131,104,768 | `gs32_w26_native` **0** | `bsaa_g16` 15,422,386; model5 20,124,597 | passed (re-verify) |
| NVFP4 | 20261103 | 197,918,720 | `verity` **0** | model5 13,094,175 | passed (`--fixed-mult 160`) |
| NVFP4 | 20261104 | 197,918,720 | `verity` **0** | model5 13,097,009 | passed |
| E2M1 (`f8f6f4`) | 20261103 | 136,314,880 | `gs32_w26_native` **0** | `bsaa_g16` 15,421,714; model5 22,730,904 | passed |
| E2M1 (`f8f6f4`) | 20261104 | 136,314,880 | `gs32_w26_native` **0** | `bsaa_g16` 15,426,185; model5 22,727,992 | passed |

- The first two seeds ran on GPU-1cd543c7, and 20261103/4 on GPU-af0bf9e0.
- The re-verify of NVFP4 20261101 at `6ed30ed6` passed too, so `--fixed-mult 1` regenerates the `d3b846cf` streams.
- **Flag:** the smallest families of seeds 20261101/2 (`signed_zero`, `anchor_participation`, `signed_zero_matrix`) are
  32,768–73,728 words per seed. Seeds 20261103/4 draw them 160 times larger: at least 5,242,880 words per family per seed.

### 14. Sparse FP8 `mma.sp` against the dense k32 chain (the 18:26Z order's (b); fill jobs, not yet under a research run id)

E4M3 m16n8k64, 2:4 along k, `mma.sp::ordered_metadata` (SASS `QMMA.SP.16864.F32.E4M3.E4M3`), GPU-af0bf9e0. Seeds 20261201
and 20261202, 83,886,080 words each, 11 families (Measured):

| Comparison | Seed 20261201 | Seed 20261202 |
|---|---|---|
| sparse vs `gather_g32` (one `GroupSum` (32,)/26/−133 over the kept products) | **0** | **0** |
| sparse vs one dense k32 atom on the compressed operands (15,728,640 words) | **0** | **0** |
| sparse vs two chained dense k32 atoms on the logical operands | 22,120,370 | 22,114,536 |
| the same, halves swapped | 22,118,611 | 22,119,094 |

- So the sparse step is the dense k32 atom on the 32 kept products, not the dense chain over k64. They agree only on
  `one_half_live` and `signed_zero`.
- Every dense twin is reproduced by its model on every word (the control).
- The device layout check settled the packing: metadata `row_q1_groups_q2`, B `k_4q_16r`, the only one of six that passes.
- This answers `docs/pouw/approved-weights.md`'s open question 3 ("Does `mma.sp` E4M3 m16n8k64 equal the dense chain on
  2:4 operands?"): no. Its §5 exclusion rule reads this result.

### 12. The 17 scale-decode vectors in one capture (the 15:57Z order)

**All 17 match** (Measured). Run `r20260930-161935-83a8`, validation passed. It is the CPU collect of fill job
`fp4-lean17-178dcca4.sh` (prio=10, gpus=1, 0.2 min, rc 0), which it derived again from the chunk's dumps and found equal to
the chunk's record; it keeps the chunk's files under `chunk/`.
- Device: GPU-af0bf9e0 (a different card from §7's GPU-fb680060), driver 580.173.02, cc 12.0, 0.16 s on the GPU.
- Library: `mma_fp4.cu` at clean `178dcca4`, built by CPU run `r20260930-161606-dd5a` (sha256 `cf965322…`, CUDA 13.0). Its
  SASS is one MMA per kernel, and the NVF4 tile and row kernels are `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`.
- Input: `Fp4Vectors.lean`, sha256 `3b6eeb23…bf14` (385,777 B). The 13 of §7 are identical at the same indices.
- Wall time: 2.3 s.

Gates, all passed, and all derived again in the collect:
- The UUID matched the lease, and every vector sat where it was placed.
- The tile and row kernels agree (0 words differ), and both placements agree.
- No word read the 0xA5A5A5A5 poison: every device D buffer is memset to 0xA5 before its launch.
- 24,360 background lanes match `BLACKWELL_SM120_NVF4`.
- The file's 82 controls (60 in-model vectors and 22 chains, none with a bit-7 byte) reproduce their words.
- The no-write control passed. The first tiles ran again with every launch skipped: all 23,040 words read the poison, and
  9,450 of 9,450 background lanes failed.

The four extra vectors (NVFP4, NaN accumulator, one scale byte with bit 7 set):

| Vector | Same entry as | Accumulator in | Bit-7 byte | Word on the card | Low-7 twin on the card | Low-7 decode predicts |
|---|---|---|---|---|---|---|
| nvf4Specials[12] | nvf4P7[47] | `0xffacb8ff` (sNaN) | `0xDB` | `0x7fffffff` | `0x7fffffff` | `0x7fffffff` |
| nvf4Specials[19] | nvf4P7[57] | `0x7f8163ac` (sNaN) | `0x8E` | `0x7fffffff` | `0x7fffffff` | `0x7fffffff` |
| nvf4Specials[21] | nvf4P7[60] | `0xff9f8cae` (sNaN) | `0xE1` | `0x7fffffff` | `0x7fffffff` | `0x7fffffff` |
| nvf4Specials[23] | nvf4P7[63] | `0x7ffeaa77` (qNaN) | `0xF2` | `0x7fffffff` | `0x7fffffff` | `0x7fffffff` |

- The low-7 decode's prediction for these four is the record-only rule for a NaN accumulator (0x7FFFFFFF, lane fp4-re).
  It is also the file's `nvf4Specials` d; `nvf4P7` has `none` there.
- The pinned model refuses each of the four as fed on the padding bit, and each low-7 twin as a non-finite accumulator
  (Derived, CPU).
- The earlier 13 give the same words as in §7 (13 of 13, on a second card), all equal to Lean's d, their low-7 twins, and
  the model on the twins.

`internal/pouw/rtx-pro/handoffs/scale-dyadic-bit7-words.json` now holds 17 entries with this run id. It keeps `by` and
every earlier field; `capture` and `supersedes` are new, as are `low7_decode_predicts` and `equals_low7_decode` on every
entry. Written 16:23Z, sha256 `3eaaf0f5…`; the old file was `eb5a0c49…`.

### 11. F2: TF32 Strassen over one NVFP4 group against dense NVFP4 (the 09:37Z order)

**Answer: neither level is cheaper.** Collect `r20260930-124558-83f4` (Measured, locked-2100, validation passed,
PRESERVED; build `r20260930-124120-350e`, nvcc 13.0.88; fill job `fp4-f2-strassen-ac9fe0fd.sh` from the verified tree of
`ac9fe0fd`, GPU-4352a609…; table `f2_strassen.json` in the run's files). Price in FP4 slots per product, against the same
run's dense NVFP4 (1,961.6–1,961.7 products per SM per clock), 2 families × 5 interleaved reps:

| Level | Tile per group (M × N × K) | TF32 MMAs (naive) | Measured | MMA-only floor (Derived) | MMA rate kept |
|---|---|---|---|---|---|
| l1 | 32 × 16 × 16 | 7 × m16n8k8 (8) | 7.902–7.903 | 7.00 | 85% |
| l2 | 64 × 32 × 16 | 49 × m16n8k4 (64) | 14.956–14.959 | 12.25 | 79% |

- The floor is (7/8)^L of F1's Measured TF32 price (8.0 slots per product for m16n8k8, 16.0 for m16n8k4): Derived.
  "MMA rate kept" is the loop's TF32 MMA throughput (217.2 and 100.4 products per SM per clock, Measured) over F1's
  (255.7 and 127.8, Derived from F1's prices); the rest goes to the FP32 recombination (32 FADD per 7 MMAs at l1, 480
  per 49 at l2).
- **Why no level can win (Derived):** Strassen saves 1/8 of the MMAs per level, and TF32 starts 8× behind NVFP4. Getting
  under 1 slot at zero addition cost needs (7/8)^L × 8 < 1, so L ≥ 16. A group has K = 16, and TF32's smallest MMA k is 4,
  so a group admits at most L = 2, where k4's half rate already costs more than the level saves (12.25 > 7.00).
  Recursing across groups mixes scales (next point).
- **Strassen on the scaled values (recorded, never gated; Measured counts):** TF32 rounds the pre-added scaled operands,
  and the group sums then differ from the exact products:

| Family | l1 inexact group sums | l2 inexact group sums |
|---|---|---|
| mixed | 20–26% (25,944–34,361 of 131,072 per group) | 37–47% (191,684–246,536 of 524,288) |
| uniform | 30–36% (39,507–47,640) | 58–61% (302,271–317,850) |
| gaussian | 0 | 0 |

  The gaussian family comes out exact, which I attribute to its scales sitting in a narrow band (UE4M3 codes 109–126,
  104 to 448) (Conjectured, not checked). Either way it is a property of those operands, not of the route.
- Flag, in Strassen's favour: this run's native arm (1,961.7, 12 warps per SM) is 3.4% under F3's (2,031.3, another die)
  and 4.1% under F1's (2,045.2). Against F1's, the prices would be 8.24 (l1) and 15.59 (l2) (Derived).

`tools/tc_probe_fp4/f2_strassen.py` (tool `tc_strassen_fp4`), kernels `f2_strassen.cu` plus `nvf4_step.cuh` (the atom's
align-add and OMMA wrapper, shared with F3), built with `-O2`, no FTZ or fast-math:

- Within one group, a row of A carries one scale and a column of B one scale, so the group's product is
  diag(sa) (CA CB) diag(sb). The route runs Strassen on the E2M1 codes as integer halves; the pre-added operands reach 24
  (l1) and 48 (l2), exact in TF32, and every product's sum is an integer below 2^14, exact in FP32. The group dots and
  scales then go through the atom's align-add, as the atom does.
- Arms: `dots` (the Strassen MMAs and FP32 recombination, one group per tile per iteration, every dot consumed by a
  per-lane checksum); `native` (the OMMA m16n8k64 tile over the same rows and columns); `step` (the align-add on the four
  groups' Strassen dots: the route's words, not timed).
- Gates, before timing, on the mixed, uniform and gaussian families:
  - For every group, at chains of 1 and 3, the Strassen dots equal the integer group dots on every element (131,072 at
    l1, 524,288 at l2), and so does each warp's checksum.
  - The route's words equal the native atom's on every word, and the pinned model's on 2,048 sampled words.
  - After timing, the dots and the checksum at the timed length (about 250,000 iterations at l1, 102,000 at l2).
  - The factored route's pre-added operands: 0 rounded, on every family.
- SASS (Measured, the build above): the l1 loop holds 7 `HMMA.1688.F32.TF32` and 32 FADD in 52 instructions (79
  registers); l2 49 `HMMA.1684.F32.TF32` and 480 FADD in 566 (252 registers); neither has a memory access. The native
  loop holds 8 `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`. No spills and no FTZ.
- **Flagged, all in Strassen's favour:**
  - The pre-additions (U on A, V on B) and the codes' conversion to TF32 are on the host, outside the loop. A's are
    amortized over the N/TN column tiles; B's are preprocessing of fixed weights.
  - Every product's operands are resident in registers and reused every iteration, as the native arm's.
  - The align-add is not timed.
  - So each price is a lower bound on the route's.

### 10. F3: LUT-GEMM over the E2M1 alphabet against dense NVFP4 (the 09:37Z order)

**Answer: no LUT width is cheaper.** Collect `r20260930-121238-ba0a` (Measured, validation passed, PRESERVED; build
`r20260930-115839-c84e`, fill job `fp4-f3-lut-47eecb5c.sh` from the verified tree of `47eecb5c`, GPU-fb680060…; table
`f3_lut.json` in the run's files). Every width passed every gate: native = the pinned model on every sampled word, exact =
native on every word, and dots = the integer group dots, at chains of 1 and 3 and at each arm's timed length. The price is
FP4 slots per product against the same run's dense NVFP4 (2,031.3–2,031.4 products per SM per clock), at 2 families × 5
interleaved reps:

| Width (G, C) | Products per lookup | Dots (the table alone) | Exact (the atom's words) | Dots per lookup |
|---|---|---|---|---|
| g1c2 | 2 | 63.7–63.8 | 89.9–90.0 | 127.5 |
| g1c4 | 4 | 32.0 | 90.2 | 128.0 |
| g1c8 | 8 | 58.1–58.4 | 137.5–137.6 | 464–468 |
| g2c2 | 4 | 51.0–51.9 | 88.3 | 204–207 |
| g2c4 | 8 | 47.5–48.8 | 105.4–106.3 | 380–390 |
| g4c2 (L2 tables) | 8 | 833–845 | 816–827 | 6,525–6,760 |

- The cheapest exact route is 88.3 slots per product (g2c2); the cheapest table alone is 32.0 (g1c4).
- A lookup costs 127.5 slots or more (Measured), against the FP4-tile model's 16.2–66 (Derived). The model underprices a
  lookup by 2× to 100×.
- **Why no width can win (Derived from the Measured g1c4 rate):**
  - g1c4 runs 15.9 lookups per SM per clock with 8-byte entries, which is 127 B per SM per clock, shared memory's full
    bandwidth.
  - At that bandwidth, int16 entries give at most 64 × G products per SM per clock, whatever C is.
  - Reaching NVFP4's 2,031 would need G ≥ 32, a table of 16^32 entries per slice.
- **Clock label.** g2c4's exact arm reads a median of 2,046–2,082 MHz by clock64 on both attempts (its other arms read
  2,095–2,100), so `w1_price.clock_label` labels that record `unlocked` and the collect `Measured, locked-2100,unlocked`.
  Prices are per SM clock (clock64), so the label doesn't move them. The first g2c4 attempt (the same label, prices within
  1%) is kept aside on node 2 (`fill-out/fp4-f3/47eecb5c/unlocked/`) and not cited.

`tools/tc_probe_fp4/f3_lut.py` (tool `tc_lut_fp4`), kernels `f3_lut.cu`, built with `-O2`, no FTZ or fast-math:

- A table per G consecutive k of one K = 64 atom and C weight columns holds the exact partial dots against all 16^G
  activation-code tuples, two int16 per word. One lookup replaces G × C products.
- Widths (G, C): g1c2, g1c4, g1c8, g2c2, g2c4 in shared memory; g4c2 in global memory (4 MiB per column pair).
- Arms per width:
  - `dots`: the lookups and the unpacking, the table's own price.
  - `exact`: plus the atom's align-add on the CUDA cores (branch-free), so its words are the atom's.
  - `native`: the OMMA tile on the same rows and columns, the unit.
- Gates, before timing:
  - For chains of 1 and 3 atoms on the mixed, uniform and gaussian families, native equals the pinned model on 2,048
    sampled words.
  - Exact equals native on every word.
  - Dots equal the integer group dots.
  - After timing, exact equals native, and dots equal the integers mod 2^32, at each arm's timed length.
- SASS (Measured, build `r20260930-115839-c84e`, nvcc 13.0.88):
  - Lookups per loop: 64 LDS / LDS.64 / LDS.128 for G = 1, 32 for G = 2, 16 `LDG.E.CONSTANT` for G = 4.
  - The native loop is 8 `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`.
  - No spills and no FTZ.
  - Loop lengths are 68–261 instructions (dots) and 473–1,826 (exact).
- **Flagged, all in the table's favour:**
  - The timed loop re-reads one atom's tables, resident in shared memory or L2. A GEMM's K/64 × N/C tables per weight
    matrix would stream.
  - Table construction, and the activation side's addresses and scale decode, are outside the loop.
  - So each price is a lower bound on the route's.
- To beat NVFP4, a lookup must cost under G × C FP4 slots: at most 8 here. The FP4-tile model's lookup price is 16.2–66
  slots (Derived).

### 9. F1: no sm_120 instruction multiplies faster than dense NVFP4 (the 09:37Z order)

Collect `r20260930-111747-26f3` (Measured, locked-2100, library `8b0c72db`, validation passed; table `f1_table.json`):
83 like-for-like forms, none below 1 FP4 slot per nonzero product (tolerance 2%); every family priced against the
NVFP4 of its own chunk (2,045.2–2,045.3 products per SM per clock). The families ran on three dies: af0bf9e0;
9f1f172d (`mxf8f6f4`); 2b59d5fe (`f8f6f4`).

| Form (cheapest of its class) | FP4 slots per product |
|---|---|
| dense NVFP4 / MXFP4 (`mxf4nvf4` 4X, 2X, `mxf4` 2X) | 1.000 |
| 2:4-sparse `mxf4nvf4` / `mxf4`, per nonzero product (meta real or constant) | 1.000 |
| every `f8f6f4` / `mxf8f6f4` form (E4M3, E5M2, E3M2, E2M3, E2M1; FP16 acc; sparse) | 2.000 |
| FP8 `kind::f8f6f4`-less k32, s8/u8 k32, sparse s8 k64 | 2.000 |
| F16 / BF16 k16 and sparse k32 | 4.000 |
| TF32 k8 and sparse k16 | 8.000 |
| DP4A (s8) | 7.99 |
| HFMA2 / HMUL2 (F16, BF16) | 16.01 |
| FMUL, FFMA with an immediate | 16.30 |
| FFMA (register operands) | 25.9 |
| IMAD (s32) | 32.0 |
| FP64 (DFMA, DMMA) | 1,023–1,166 |

- Narrow products, flagged (each can't hold one E2M1 × E2M1 product): `popc_and_b1` 4.01 and `b1_and_k256` 3.26 per own
  product; `u4_k64` 4.34 and `s4_k64` 20.9, emulated by ptxas on sm_120a. The per-E2M1-product prices from the plain
  decompositions are Derived in the table (at least 4× these).
- Flag for the FP4-tile model's owner (bc-d9842080): the full-rate FP32 and F16 CUDA-core multipliers sit at 16.0–16.3
  slots (Measured), so the model's 16-block threshold is a tie, not a margin.

### 7. The 13 Lean vectors, captured before the scale-decode pin (the 10:32Z ask)

Run `r20260930-105507-3e10` (Measured): `--instruction nvf4_lean_vectors` at clean `a5b0f57e`, prebuilt
`libmma_fp4_sm_120a.so` (sha256 `d07253c6…`, the bit-7 job's library), GPU-fb680060, 2,092 MHz (recorded, not locked: the
words don't depend on the clock), driver 580.173.02, 2.3 s. Input `Fp4Vectors.lean`, sha256 `79420a9d…6efb` (384,989 B).

Gates, all passed: the UUID; the tile and row kernels agree (0 words differ); two placements agree; 22,680 background
lanes match `BLACKWELL_SM120_NVF4`; the file's 82 controls (60 in-model vectors and 22 chains) reproduce their words (0
mismatches).

| Vector (0-based) | Word on the card | = Lean's d | = low-7 twin on the card |
|---|---|---|---|
| nvf4P7[31] | `0xeba44603` | yes | yes |
| nvf4P7[34] | `0xfd73790d` | yes | yes |
| nvf4P7[36] | `0x4742ef26` | yes | yes |
| nvf4P7[42] | `0xddfa9804` | yes | yes |
| nvf4P7[44] | `0xec7f3766` | yes | yes |
| nvf4P7[50] | `0xccf64712` | yes | yes |
| nvf4P7[52] | `0xc549e860` | yes | yes |
| nvf4P7[54] | `0xd2f6e1e9` | yes | yes |
| nvf4P7[59] | `0xe79c1784` | yes | yes |
| nvf4P7[65] | `0xc6a72fe1` | yes | yes |
| nvf4P7[66] | `0x46cbeaf2` | yes | yes |
| nvf4Chains[9] | `0x49ab8bfb` | yes | yes |
| nvf4Chains[19] | `0xca1532c7` | yes | yes |

13 of 13 match the prediction and their low-7 twins (Measured). The pinned Python model (`verity.ml.tc`) refuses all 13
(`InvalidArtifact` on scale bit 7). On the low-7 twins it writes Lean's d, 13 of 13 (Derived, CPU).

12:57Z, for the `_scale_dyadic` replay test (server.md 12:11Z, 12:50Z): the 13 vectors' operands as fed (A and B codes, SFA
and SFB bytes, the accumulator in), the card's D words and their checks are in
`internal/pouw/rtx-pro/handoffs/scale-dyadic-bit7-words.json`, written from this run's record and its input file (sha256
checked); no new capture. Superseded at 16:23Z by §12's 17-vector capture, which the file now cites.

### 8. UE4M3 scale bit 7: the card ignores it (the 09:38Z ask)

Fill job `fp4-bit7-85df9336.sh` (Measured, GPU-af0bf9e0, 2,092 MHz; output on node 2 under
`/workspace/pouw/fill-out/fp4-bit7/85df9336/run/`):

- 8,192 NVF4 words with bit-7 scale bytes: 0 differ from the same tiles with bit 7 cleared. The card decodes 0x80–0xFE as
  their low 7 bits, and a byte whose low 7 bits are 0x7F as NaN.
- The pinned model on the low-7 twins: 0 of 6,720 in-domain words differ.
- The pinned model on the bit-7 bytes as given: refuses 8,182 of 8,192.
- This agrees with the assessor's `r20260930-093120-b2f2`.

**Discrepancy, for the tc registry's owners (not edited):** `verity/ml/tc/models.py::_scale_dyadic` and `_scale_batch`
raise on bit 7, and the card decodes the low 7 bits. It is a coverage gap, not a wrong word: D-SB rejects such bytes in
the statement anyway. Matching the card means decoding `b & 0x7F`, with NaN at 0x7F and 0xFF.

### 6. The hardware's 2:4 metadata rule, measured (the 08:56Z ask 3)

Runs: NVF4 `r20260930-092605-fdc9` and MXF4 `r20260930-092713-6acd`, both `--instruction sp_{nvf4,mxf4}_meta --n-random
16384 --seed 20260930` at clean `25614709`. Both ran on GPU-fb680060, one lease each of 12–13 s, every gate passed (UUID,
SASS `OMMA.SF.SP.168128`, the layout check), PRESERVED. Everything below is Measured on both rows unless labelled, and
the rule is identical on both.

- **What the instruction accepts.** All 16 metadata nibbles run without a fault; there is no runtime check of PTX's
  p0 < p1 order. The hardware reads stored pair 0's position as p0 = min(v & 3, 2) and stored pair 1's as
  p1 = max(v >> 2, 1).
  - The six ordered nibbles land exactly where PTX says: stored codes 4j, 4j+1 at logical 8j + 2p0 + {0, 1}, and
    4j+2, 4j+3 at 8j + 2p1 + {0, 1}.
  - The ten others alias a placement:

    | Nibbles | Placement |
    |---|---|
    | 0b0000 | as 0b0100 |
    | 0b0010, 0b0011, 0b0110, 0b0111 | pair 2, then pair 1 (swapped) |
    | 0b0001, 0b0101 | both stored pairs on pair 1 |
    | 0b1010, 0b1011 | both stored pairs on pair 2 |
    | 0b1111 | as 0b1110 |

  - Where both stored pairs sit on one pair, both products count at the same logical k (weight 1 each). No slot ever lands
    outside its own chunk, and none counts twice.
- **How it gathers them.** A product takes A's scale by its stored block (16 stored = 32 logical under 4X, 32 = 64 under
  2X) and B's by the logical k's block; these coincide because no slot leaves its chunk.
  - The map depends on the nibble alone. The same map comes back with rows permuted, the other chunks' nibbles drawn
    from all 16, and different values and signs: 262,144 one-hot words per row, 0 undecodable.
  - On random operands the arithmetic is `gather_dense` extended to all 16 nibbles: the pinned dense step on the stored
    A and each row's gathered B. It reproduces 2,097,152 of 2,097,152 words per row, with nibbles drawn per row and
    chunk from all 16, random scales, and accumulators half +0.
  - Hardware against hardware: the dense `mma.sync` on the gathered B writes the sparse word in 2,097,152 of 2,097,152
    elements per row (one metadata row per tile).
- **The predicate, for D-24** (Derived from the measured map). Of the 256 zero patterns of an 8-chunk:

  | Rule | Patterns allowed |
  |---|---|
  | Hardware (ordered nibbles) | 67 |
  | Hardware (all 16 nibbles) | 67, the same set |
  | D-24 (≤ 2 nonzeros per aligned 4-group) | 121 |
  | Both | 57 |
  | Hardware only | 10 (e.g. offsets {0, 1, 2}, and a full 4-group {0, 1, 2, 3}) |
  | D-24 only | 64 (e.g. {0, 2, 4}, three pairs touched) |

  - The hardware's set is exactly "nonzeros in at most two of the chunk's four aligned pairs {0,1}, {2,3}, {4,5},
    {6,7}".
  - The ten unordered nibbles add no pattern. They add values: a duplicate nibble puts two stored codes' products on
    one logical k. That covers fewer logical columns for the same 64 stored products, so it is not a cheaper route; it
    only means the stored operand is not a logical E2M1 row.
- **Shortcuts:** none on the device side. Part A's one-hot operands are exact small values (weights decode uniquely up
  to 15). Part C is a closed-form enumeration over the measured map.

### 5. T1's merged k128 route, measured (the 08:20Z ask)

**Under T1 the merged 128-deep align-add still reproduces most span words on 2:4 spans. The simulation's 0–0.5% is the
whole-chain rate on dense operands, which the hardware can't merge.** The hardware writes the emulation's words exactly:
on these operands the simulation's rates are the measured ones.

- **Run:** `r20260930-084518-2674` (Measured, node 2, GPU-af0bf9e0-2a17-98be-19b6-f184292c3842, driver 580.173.02,
  CUDA 13.0.88, clocks 2,092 MHz at start and end, labelled locked-2100; a capture, so the words don't depend on the clock).
- **Merged:** `mma.sp::ordered_metadata m16n8k128 kind::mxf4nvf4 .scale_vec::4X .ue4m3` (SASS
  `OMMA.SF.SP.168128.F32.E2M1.E2M1.UE4M3.4X`), from C = H.
- **Chained:** two dense `mma.sync m16n8k64` (`OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`), the first from C = H, the second
  from the first's D.
- **H:** `hot_accumulator(p, h, "row")`, one H per row.
- **Gates, all passed before any family:** the emulation's bytes, UUID = the lease's, SASS (one MMA per kernel), the
  sparse layout check and the dense chain-2 and chain-128 layout checks on exact integers, and the operands' structure.
- **Operands:** `fp4_emulation.py routes`' own draws at `1ad1aaa2` (the file pinned verbatim in the tool, sha256
  `4b3e0e85…`): 64 × 64 words, k = 8192, δ = 1/4, seed 20260930, the five families.
- **Flagged shortcut:** routes' operands are dense, and no dense 128-span is one `mma.sp` can take. So:
  - A keeps, in each 4-group of k, the one of its two element pairs with the larger energy, zeroed before quantization.
    Every span is then 2:4 under D-24's definition and under the hardware's.
  - A and B take one UE4M3 scale per 32 k, the sparse 4X layout.
  - H is recomputed on these operands. Routes' own operands are reported beside them, simulated.

Span: each (word, aligned 128-span) from C = H, 262,144 per cell. Chain: the whole k from C = H, 64 merged against 128
chained, 4,096 end words per cell. Each cell is matched / total, all from `r20260930-084518-2674`.

| Family | C = +0 span | C = +0 chain | h = 14 span | h = 14 chain | h = 15 span | h = 15 chain | h = 16 span | h = 16 chain |
|---|---|---|---|---|---|---|---|---|
| gaussian | 262,144 / 262,144 | 4,096 / 4,096 | 258,120 (98.5%) | 1,547 (37.8%) | 262,144 (100%) | 4,096 (100%) | 262,144 (100%) | 4,096 (100%) |
| t4 | 262,144 / 262,144 | 4,096 / 4,096 | 255,287 (97.4%) | 1,617 (39.5%) | 261,400 (99.7%) | 3,619 (88.4%) | 262,129 (99.99%) | 4,081 (99.6%) |
| massive | 262,144 / 262,144 | 4,096 / 4,096 | 174,447 (66.5%) | 0 | 199,614 (76.1%) | 2 | 228,483 (87.2%) | 202 (4.9%) |
| spread | 262,144 / 262,144 | 4,096 / 4,096 | 233,236 (89.0%) | 20 (0.5%) | 252,519 (96.3%) | 629 (15.4%) | 260,858 (99.5%) | 3,047 (74.4%) |
| spread-both | 262,144 / 262,144 | 4,093 / 4,096 | 198,450 (75.7%) | 0 | 223,328 (85.2%) | 2 | 243,832 (93.0%) | 79 (1.9%) |

- **D-24's step "exact spans merge identically" is now Measured on these operands.** A span is exact when its chained word
  is exactly C plus the span's exact sum. All 3,587,727 exact spans merged to the chained word, 2,277,007 of them under a
  hot H. The C = +0 control is all exact spans here, so it matched 100% per span in every family.
  - Whole chains from +0 also match, except 3 of spread-both's 4,096 (out of domain; the cold chain truncates).
  - Most inexact spans merge identically too, e.g. gaussian h = 14: 56,967 of 60,991.
  - A merged span differs only where the chain's rounding between its two atoms changes the word.
- **Word for word with the emulation (Measured against Derived):**
  - The sparse words equal `gather4` (the 06:21Z `gather_dense`, 4 groups of 32 logical k) on all 5,242,880 span words
    and 81,920 chain words.
  - The dense words equal the pinned atom chain (`native`) on every word.
  - Verity's own models (`BLACKWELL_SM120_NVF4`, `sparse.gather_dense`) miss 0 of the 81,920 sampled span words and 0 of
    1,280 whole chains.
- **The emulation's k128 model (one align-add over 8 groups of 16) is refuted, but it gives the same words here.**
  - It is `sparse.py`'s `logical_g16` candidate, which the 06:21Z capture refuted: 5,937 missed gated words against 0
    for `gather_dense` (`r20260930-062133-46bb`, Measured).
  - Under a hot H, the accumulator's window keeps every group term on the grid, and on the grid the two models are the
    same sum. So on all 5.24M words here `merged_k128` = `gather4` = the hardware, and the simulation's rates stand.
  - This capture cannot tell the two models apart; the 06:21Z families can, and did.
- **The simulation's own rates (Derived, the emulation on routes' dense operands, merged against native):**
  - At h = 14 the whole-chain rate is gaussian 0.51%, t4 0.22%, and 0 for the other three families. That is the 0–0.5%
    in `fp4-specialization.md` and D-24.
  - Per span on the same dense operands it is 91.2%, 82.9%, 56.3%, 66.3% and 55.4%.
  - On the 2:4 operands above the same model gives the measured numbers: pruning to 2:4 raises the rate.
- **What it means for D-24 (Derived; the theory lane's call):**
  - The route merges only a chain's 2:4 spans, each from the running accumulator. So the per-span rate is the one that
    matters: 97–100% on gaussian and t4 at every h measured.
  - T1 therefore does not remove the cheaper computation on a 2:4 span. D-24 stays load-bearing on T1 (v2) rows; it does
    not become a check.
  - Where D-NF keeps in-domain rows free of 2:4 spans, nothing changes.

### 1. The 2:4-sparse NVF4 atom against the dense one (the 06:15Z ask 2)

**Yes: on the noise atom's operands the sparse words are identical to the dense align-add's** (Measured, node 2, GPU
GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f, locked-2100; `mma.sp::ordered_metadata m16n8k128 kind::mxf4nvf4
.scale_vec::4X .ue4m3`, SASS `OMMA.SF.SP.168128.F32.E2M1.E2M1.UE4M3.4X`, against dense `mma.sync m16n8k64`):
- the noise atom (one k64 NVF4 atom with 32 zero lanes, as [atom | zeros] in the k128 sparse instruction): **0 of 131,072
  words differ** (`r20260930-062133-46bb`; the coordinator's repeat `r20260930-062452-464f` agrees);
- the dense word on the compressed operands (stored A, gathered B), every family: **0 of 2,514,944 differ**;
- the one candidate model reproducing every sparse word is `gather_dense`: the pinned dense model
  (`BLACKWELL_SM120_NVF4`) on the stored A and the gathered B;
- a sparse k128 holding two k64 atoms is **not** two chained dense atoms: 13,056 of 131,072 differ (one align-add over
  the whole row, not two).

Scope (Derived): the identity is shown on these operands, where the align truncation never reaches the group dots' bits;
a general sparse-vs-logical-atom identity is not claimed.

**MXF4 differs** (`r20260930-062526-34e7`, `.scale_vec::2X .ue8m0`, `OMMA.SF.SP.168128.F32.E2M1.E2M1.E8`): the noise atom
misses the dense word in **77 of 131,072** (0.059%), exactly as the pinned model predicts: a sparse 2X scale spans 64
logical columns, so one stored 32-group merges the dense atom's two groups into one exact dot before the align-add.
On the compressed twins: 0 of 2,301,952 differ (`gather_dense` again).

**Scale granularity (Derived from the PTX layout, confirmed by the runs):** sparse 4X carries one UE4M3 scale per 32
logical columns (16 stored), sparse 2X one UE8M0 per 64. So the sparse noise atom reproduces the dense one only when the
dense atom's per-16 scales come in equal pairs over each 32-column span.

### 2. W1 prices at full occupancy (the 06:15Z ask 1)

Unit: one dense FP8 E4M3 `mma.sync` MAC (`kind::f8f6f4` m16n8k32, FP32 accumulation), per SM per clock.

- **Measured, locked-2100:** run `r20260930-065015-32af` (tool `tc_price_fp4`, commit `287b9574`), node 2, GPU
  GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f, driver 580.173.02, CUDA 13.0.88.
- Gates passed before timing: identity; SASS opcode counts for all 24 kernels and op loops; outputs finite and
  bit-identical across two launches for all 33 kernels.
- Clocks: every launch's clock64 clock is 2,090.5–2,097.8 MHz.
- It reproduces the e7ca re-derivation to three or four significant figures.
- The FP8 reference: 1,022.59 MAC/SM/clk, 805.8 TFLOP/s dense.

| Item | FP8 MACs | Dense-NVF4 MACs | Notes |
|---|---|---|---|
| Dense NVF4 `mxf4nvf4` 4X UE4M3, per MAC | **0.500** | 1.000 | 1,612.5 TFLOP/s; 0.5015 with a new scale word every MMA |
| Dense MXF4 `mxf4nvf4` 2X UE8M0, per MAC | 0.500 | 1.000 | 1,611.6 TFLOP/s; 0.5015 with scale updates |
| Unscaled E2M1 `f8f6f4` e2m1×e2m1, per MAC | **1.000** | 2.000 | QMMA, the FP8 datapath; e2m1×e4m3 1.000 |
| `mxf8f6f4` UE8M0 1X, E2M1, per MAC | 1.000 | 2.000 | 1.003 with scale updates |
| 2:4-sparse NVF4, per logical MAC | **0.250** | 0.500 | 0.500 per stored MAC; 3,223.4 TFLOP/s logical; 0.2507 with scale updates |
| 2:4-sparse MXF4, per logical MAC | 0.250 | 0.500 | 0.2507 with scale updates |
| **E2M1 cast** `cvt.rn.satfinite.e2m1x2.f32`, per element | **15.99** in the loop | 31.98 | loop: 1 F2FP + 1 LOP3 per cvt |
| E2M1 cast, F2FP alone, per element | ≈ 8.0 (Derived) | ≈ 16 | GPU 0's shared-pipe model: F2FP and LOP3 at 16 per warp instruction each |
| E2M1 decode `cvt.rn.f16x2.e2m1x2`, per element | 8.05 | 16.1 | loop: 32 F2FP + 19 PRMT per 32 steps |
| **UE4M3 scale encode** `cvt.rn.satfinite.e4m3x2.f32` (positive), per scale | **15.99** | 31.98 | 1 F2FP + 1 LOP3 |
| UE4M3 scale decode `cvt.rn.f16x2.e4m3x2`, per scale | 12.74 | 25.5 | |
| UE8M0 scale encode `cvt.rp.satfinite.ue8m0x2.f32`, per scale | 15.99 | 31.98 | the `rz` form is the same F2FP (not timed separately) |
| Block amax, FMNMX of \|x\|, per element | 8.47 | 16.9 | |
| Scale multiply FMUL, per element | 8.72 | 17.4 | |
| Reciprocal `rcp.approx.ftz.f32`, per scale | 63.9 | 127.8 | MUFU at 16/SM/clk, + 1 LOP3 |
| LOP3, per instruction | 16.1 | 32.2 | |

- Dependent-chain latency: 29.00 cycles per MMA on every MMA row, sparse included (Measured).
- **An NVF4 quantizer per element** (Derived, from an Estimated recipe: amax 1, scale multiply 1 + 1/16, E2M1 cast 1, and
  per 16-element block the UE4M3 encode, decode and one reciprocal): about 8.5 + 9.3 + 16.0 + (16.0 + 12.7 + 63.9)/16
  ≈ **39.5 FP8 MACs** (79 NVF4 MACs).
- **Against the theory lane's Pearl-C4 placeholders** (theory §4, f_s in dense-NVF4-MAC units): the cast "at 32" matches
  the in-loop measurement (31.98 NVF4 MACs = 15.99 FP8 MACs per element); the cheapest-program price (C3's rule) is about
  16 NVF4 MACs (F2FP alone). §9 borrows the E4M3 cast (12.31 FP8 MACs per code in GPU 0's packing loop); the E2M1 cast's
  own number is this table's.
- Agreement: GPU 7's `peak` (`r20260930-062619-81e2`, per FP4 MAC: dense 1.000, 2:4-sparse 0.500) says the same thing in
  FP4 units.
- Flagged shortcuts: the op loops chain each cvt through one LOP3 to stop ptxas folding or hoisting them, so the in-loop
  numbers include that integer instruction; the "alone" row is Derived, not measured. Each lane gets its own operands
  (no uniform-datapath forms; the SASS gate checks the loop's opcode histogram).
- **Panel rows (default, recorded):** these are instrument microbenchmarks per SM per clock in single-GPU leases, not
  panel attempts, so they add no row to `attempts.jsonl`; the lines' rows cite them as prices.

### 3. The FP4 recheck on node 2 (cited; the coordinator ran my run lines)

- NVFP4: 2,269,184 elements, 0 mismatches against `BLACKWELL_SM120_NVF4` (`r20260930-062419-a63c`); MXFP4: 2,056,192,
  0 against `BLACKWELL_SM120_MXF4`, the signed-underflow variant misses 7,356 (`r20260930-062426-8be5`); model5 still
  misses, so the control discriminates (Measured, as posted in server.md 06:35Z).
- **Fresh seeds from a clean tree (the 08:56Z ask; cite these).** `--sweep --n-random 32768 --expect-model verity
  --sass-check --expect-uuid '$GPU_LEASE_UUID'` at `fcad808d` (`source.dirty: false`), one lease each. Measured,
  locked-2100; every run's validation passed and it is PRESERVED.

  | Row | Run | GPU | Seed | Gated elements | Pinned model | Controls' misses |
  |---|---|---|---|---|---|---|
  | NVF4 | `r20260930-090302-3dcd` | GPU-1cd543c7 | 20261001 | 17,457,152 | **0** | model5 368,120 |
  | NVF4 | `r20260930-090446-a8db` | GPU-5f1149a4 | 20261002 | 17,457,152 | **0** | model5 369,119 |
  | MXF4 | `r20260930-090613-5553` | GPU-5f1149a4 | 20261001 | 15,867,904 | **0** | model5 487,641; signed underflow 58,290 |
  | MXF4 | `r20260930-090738-cf34` | GPU-5f1149a4 | 20261002 | 15,867,904 | **0** | model5 487,176; signed underflow 58,687 |

  - Each clean run gates 524,288 elements more than its dirty twin. That is exactly the `scale_split_twins` family
    (4,096 tiles × 128), which `fcad808d` sweeps and `0555d893` lacked. It is gated against `verity` and misses 0. The
    signed-underflow counts equal the dirty runs' to the word, as they should on the same seeds.
  - Totals with the clean rows in place of the dirty ones (Derived sum, the 08:15Z sum's other terms unchanged): NVF4
    38,835,712 and MXF4 34,317,824 zero-mismatch elements, all from clean commits.
- The coordinator's dirty-tree runs of the same seeds (superseded by the table above; read from the store; Measured,
  clocks 2,092 MHz):

  | Row | Run | GPU | Seed | Gated elements | Pinned model | Misses |
  |---|---|---|---|---|---|---|
  | NVF4 | `r20260930-064142-07f5` | GPU-9f1f172d | 20261001 | 16,932,864 | **0** | model5 267,835 |
  | NVF4 | `r20260930-064149-a24f` | GPU-4352a609 | 20261002 | 16,932,864 | **0** | model5 269,105 |
  | MXF4 | `r20260930-064156-d4f2` | GPU-0c776bca | 20261001 | 15,343,616 | **0** | model5 366,433; signed underflow 58,290 |
  | MXF4 | `r20260930-064203-342b` | GPU-2b59d5fe | 20261002 | 15,343,616 | **0** | model5 365,725; signed underflow 58,687 |

  - With a63c/8be5, the twins and the chains, the RTX PRO totals are 37,787,136 NVF4 and 33,269,248 MXF4 zero-mismatch
    elements (Derived sum), past the ≥ 10M bar per model; NVF4 on at least four dies, MXF4 on at least two.
  - **Flag:** these four ran from `0555d893` with `dirty: true` (the store's `source.dirty_digest` 37cfa7d2…). The dirty
    diff isn't recoverable from here, so cite them as the coordinator's runs of a modified tree. Every run of mine cited
    in this file is from a clean commit.
- **Every K=32 E2M1 row on QMMA is the FP8 datapath's `GroupSum` (32,)/26/−133 on the exact products**
  (`gs32_w26_native`, the only candidate that reproduces every word; Measured, locked-2100, seed 20260930, nonzero
  accumulators included). A UE8M0 1X scale pair enters as an exponent shift of every product before alignment.

  | Row | Run | GPU | Gated elements | `gs32_w26_native` | E2M1 as E4M3 | 2 × 16 groups | scale-free BSAA g16 / g32 |
  |---|---|---|---|---|---|---|---|
  | `f8f6f4` e2m1×e2m1 | `r20260930-071201-d356` | GPU-5f1149a4 | 1,671,168 | **0** | 13,853 | 88,660 | 193,027 / 192,566 |
  | `f8f6f4` e2m1×e4m3 | `r20260930-071739-91c7` | GPU-9f1f172d | 1,671,168 | **0** | 5,657 | 116,547 | — |
  | `f8f6f4` e4m3×e2m1 | `r20260930-071810-e388` | GPU-9f1f172d | 1,671,168 | **0** | 5,645 | 116,936 | — |
  | `mxf8f6f4` 1X e2m1×e2m1 | `r20260930-071841-6c1e` | GPU-fb680060 | 1,867,776 | **0** | 14,052 | 89,525 | 221,072 / 220,684 |
  | `mxf8f6f4` 1X e2m1×e4m3 | `r20260930-071913-5d35` | GPU-fb680060 | 1,867,776 | **0** | 5,878 | 122,758 | — |
  | `mxf8f6f4` 1X e4m3×e2m1 | `r20260930-071944-da39` | GPU-9f1f172d | 1,867,776 | **0** | 5,723 | 124,027 | — |

  - Total: 10,616,832 elements on three dies, 0 mismatches.
  - The "E2M1 as E4M3" misses show the datapath keeps E2M1's 0.5 as a subnormal on the alignment grid.
  - So on sm_120 the arithmetic follows the instruction, not the element format: QMMA (`f8f6f4`, `mxf8f6f4`) is a
    `GroupSum`, and OMMA (`mxf4nvf4`) is `BlockScaledAlignAdd`.
  - **Fresh-seed confirmation passed:** `r20260930-073334-fdac` (seed 20261003, `--expect-model gs32_w26_native`, GPU-5f1149a4)
    3,309,568 gated elements, 0 mismatches; two groups of 16 miss 176,662, the scale-free BSAA g16 / g32 385,736 / 384,745,
    E2M1-as-E4M3 27,987 (Measured, locked-2100).
  - **Landed:** `BLACKWELL_SM120_E2M1_M16N8K32` = `GroupSum` (32,)/26/−133 in `verity.ml.tc.models` (commit `7d327f96`), with
    a 260-word capture sample of d356 (fixture `art:cc1f274f1194184395e6b2cf4db97d42859839008742d35d33f1f50adf79c438`)
    that `test_models.py` replays: 0 misses for the model, 64 / 187 / 185 for the refuted alternatives. Model object
    only, no registry instruction entry: "pinned" needs `tools/tc_probe/trust.py` P1–P5 and a dossier (Needs).
- **The 5090's unscaled vectors don't tell these apart (Derived, replayed in `verity`).** autoproof's 1,400 RTX 5090
  `f8f6f4` e2m1 words (`fixtures/tc/autoproof-probe-vectors.json`, zero accumulators, K = 64) are reproduced by
  `gs32_w26_native`, by two groups of 16 and by the scale-free `BlockScaledAlignAdd` alike. `test_models.py`'s
  "same transducer" test is therefore consistent with the RTX PRO 6000 result, not evidence for the block-scaled adder on
  QMMA. It is not a discrepancy: whether the 5090 computes the same `GroupSum` is unmeasured (no 5090 on node 2).
  The registry's pinned NVF4 entry cites that probe (`_AUTOPROOF_UNSCALED`) as supporting evidence; I left it unedited.
- **Dependent chains, in registers (Measured, locked-2100, seed 20260930):**

  | Row | Run | GPU | Chain | Words checked | Pinned model | Control misses |
  |---|---|---|---|---|---|---|
  | NVF4 | `r20260930-072015-a934` | GPU-fb680060 | 2 (K = 128) | 1,126,400 gated | **0** (`verity`) | model5 43,237 |
  | NVF4 | `r20260930-072047-5dd6` | GPU-fb680060 | 1024 (K = 65,536) | 1,536 end words | **0** | model5 1 |
  | MXF4 | `r20260930-072202-f0da` | GPU-0c776bca | 1024 | 1,536 | **0** | model5 0 |
  | `f8f6f4` e2m1 | `r20260930-072400-dd3b` | GPU-5f1149a4 | 1024 | 1,408 | **0** (`gs32_w26_native`) | 2 × 16: 83, BSAA 194 |

  | `f8f6f4` e2m1, rerun | `r20260930-073445-e2b6` | GPU-2b59d5fe | 1024 | 1,408 | **0** (gated, seed 20261004) | 2 × 16: 82, BSAA 209 |

  - Flag: dd3b's `result.json` was 1.3 MB (full chain operands of the refuted candidates' first mismatches), over the
    store's 1 MiB, so its attempt is `result=invalid` although rc = 0 and every word matched. Fixed in `998d592b`
    (operands longer than 512 hex chars recorded by length and sha256); cite the rerun e2b6 (valid, 14.5 KB), on a
    second die.
  - At L = 1024 the controls barely discriminate (MXF4's model5 misses 0): these rows check that the chained fold holds,
    not the model choice, which the single-step families settle.
- **The six casts match `cast.py`'s references word for word** (Measured, GPU-af0bf9e0, seed 20260930; gated elements
  exclude the record-only inputs outside a cast's domain):

  | Cast | Run | Gated elements | Mismatches |
  |---|---|---|---|
  | `cvt.rn.satfinite.e2m1x2.f32` | `r20260930-072940-33b5` | 1,041,112 | 0 |
  | `cvt.rn.f16x2.e2m1x2` (all 256 byte codes) | `r20260930-073011-91fe` | 256 | 0 |
  | `cvt.rz.satfinite.ue8m0x2.f32` | `r20260930-073042-3522` | 687,738 | 0 |
  | `cvt.rp.satfinite.ue8m0x2.f32` | `r20260930-073113-0a04` | 687,738 | 0 |
  | `cvt.rn.bf16x2.ue8m0x2` | `r20260930-073144-7ef3` | 65,025 | 0 |
  | `cvt.rn.satfinite.e4m3x2.f32` (positive, as UE4M3) | `r20260930-073215-adf1` | 688,747 | 0 |

### 4. No `Pipeline` computes the FP4 step: the hardware check (Measured, locked-2100)

The family `scale_split_twins` pairs tiles whose every scaled product and accumulator are equal, but whose A scale is
halved into A's nibbles. A model that reads only the exact scaled products and the accumulator (every `GroupSum`,
autoproof's model5) must give both twins the same word.

| Row | Run | GPU | Twin-pair elements | Device words differ (offset 27 / 28 / 29) | Verity predicts | model5 predicts |
|---|---|---|---|---|---|---|
| NVF4 | `r20260930-073251-ec92` | GPU-5f1149a4 | 262,144 | 0 / **43,842** / 0 | the same 43,842 (0 mismatches overall) | 0 (misses 99,762) |
| MXF4 | `r20260930-073405-a6bc` | GPU-2b59d5fe | 262,144 | 0 / **42,826** / 0 | the same 42,826 (0 mismatches overall) | 0 (misses 121,222) |

So the hardware itself separates equal scaled products by their scale exponents: `no_product_value_model_fits` is true on
both rows. This is the premise of the Lean doc's `fp4_step_not_pipeline`, now measured, not only derived.

## Needs

- **For the FP4-tile model's owner (bc-d9842080), through the coordinator:** the full-rate FP32 and F16 CUDA-core
  multipliers cost 16.0–16.3 FP4 slots per product (Measured, §9), so the model's 16-block threshold is a tie, not a
  margin. F2 and F3 add no cheaper route: TF32 Strassen costs 7.90 slots or more (§11), a table lookup 127.5 or more (§10).
- **For bc-a8466279 and the coordinator: T1 does not turn D-24 into a check** (Results §5, `r20260930-084518-2674`).
  - On 2:4 spans the merged k128 reproduces 97–100% of gaussian and t4 span words from H at h = 14–16, and 66–99.5% on
    the out-of-domain families. The 0–0.5% is the whole-chain rate on dense operands, which no `mma.sp` can take.
  - D-24's §"Under T1" paragraph and the 08:10Z claim need that change. The 2:4 term stays a real charge, not an
    over-charge.
  - D-24's step "exact spans merge identically" is now Measured on these operands: 3,587,727 of 3,587,727.
- **For bc-a8466279: D-24's 2:4 predicate is not the hardware's.**
  - D-24 counts a 4-group as 2:4 when it holds at most two nonzero codes. `mma.sp` with `kind::mxf4nvf4` `.e2m1` needs
    pair-wise 4:8: each 8-chunk of k keeps two of its four element pairs, and a pair counts if either code is nonzero.
    That is Measured: 06:21Z's layout check, and today's.
  - Neither implies the other. Nonzeros at k offsets 0, 2, 4, 6 of a chunk meet D-24 but touch four pairs, so the
    hardware can't take them. Pairs 0 and 1 full (offsets 0–3) is fine for the hardware, but the 4-group holds four
    nonzeros, so D-24 misses it.
  - Suggested predicate: every 8-chunk of every row of the span has at most two nonzero pairs. The census's
    `tile_steps_2of4` would need the same change.
  - **Measured directly (§6, 09:28Z):** that predicate is the hardware's, exactly, under all 16 nibbles: 67 of the 256
    chunk patterns, against D-24's 121, with 57 shared. The step on any nibble is the pinned dense step on the stored A
    and the gathered B, with p0 = min(v & 3, 2) and p1 = max(v >> 2, 1).
  - Default, absent a reply: the capture's operands meet both predicates (one pair kept per 4-group), so §5 holds under
    either.
- **For GPU 0 (bc-e6a46970), through the coordinator:** the E2M1 cast and the UE4M3 scale conversions (06:55Z ask) are
  already priced in §2 above, on the same unit and gates. Rather than add them to `w1.py`, cite §2, or reuse the loops in
  `tools/tc_probe_fp4/w1_price.cu` (`cvt_tput_kernel<OP>`, branch `cursor/fp4-capture-sm120-9ff9`). §2 is the final run,
  `r20260930-065015-32af` (Measured, locked-2100).
- **For the theory lanes (bc-3006c44a, bc-a8466279):** Pearl-C4's f_s inputs are in §2. The E2M1 cast is 15.99 FP8 MACs
  per element in the loop (31.98 NVF4 MACs, matching the "32" placeholder), about 8.0 (16 NVF4 MACs) for F2FP alone. The
  per-block scale ops are UE4M3 encode 15.99 and decode 12.74 per scale, and the reciprocal 63.9. §9's E4M3-cast borrow can
  be replaced by these.
- **For GPU 5 (bc-71c6ab78) and the theory lanes:** the sparse noise atom is exact for NVFP4 (§1), provided the dense atom's
  per-16 UE4M3 scales are equal in pairs over each 32-column span, since sparse 4X carries one scale per 32 logical
  columns. Does the honest kernel's noise atom satisfy that, or does the domain need that rule?
- **For the Lean lane, through the coordinator:** the FP4 step, written for Lean, is in
  `internal/pouw/rtx-pro/fp4-capture/sm120-fp4-step-for-lean.md`. It includes three suggested pins: the closed-form
  `fp4_step_not_pipeline` pair (§5), the sparse noise-atom lemma under its two hypotheses (§4), and the chain fold. It
  also lists the six fields `Pipeline ⟨groups, width, floor⟩` lacks. Which structure should the FP4 line's statement use:
  a new `BlockScaledAlignAdd`, or `Pipeline` extended by those fields?
- **For the coordinator (registry, a follow-up):** `BLACKWELL_SM120_E2M1_M16N8K32` landed as a model object only. Giving
  `sm120.mma.m16n8k32.e2m1.f8f6f4` a pinned registry entry needs `tools/tc_probe/trust.py` P1–P5 and a dossier art. The
  evidence is 4.98M gated elements plus a chain on a second die, so P2 (≥ 1e7) is short. One more fresh-seed sweep at
  `--n-random 16384` on a third die would clear it (run line under Fill candidates). Should I run that and write the
  dossier, or leave the registry to its owner? My default, absent a reply: leave it.
- **For the coordinator:** the RTX PRO totals now clear the ≥ 10M bar for the pinned NVF4 and MXF4 models on sm_120 (§3),
  so the registry could cite the RTX PRO as a second SKU. Half of that total is your four fresh-seed runs, which ran from a
  dirty tree (`0555d893`, dirty). Rerun them from a clean commit before they are cited in the registry?
  **Done 09:08Z:** the clean reruns are in §3's first table; cite those four ids.
- **For the owners of `verity.ml.tc.instructions` (FYI, no action needed now):** the pinned NVF4 entry cites autoproof's
  unscaled K=32 probe (`_AUTOPROOF_UNSCALED`) as evidence for the same align-add. On the RTX PRO that instruction is a
  `GroupSum`, and the 5090's vectors fit both models (§3), so that line supports nothing either way. I left the entry
  unedited.
- **For GPU 5 and GPU 7 (bc-dbc19788):** for MXFP4 the sparse noise atom does **not** write the dense words (77 of 131,072
  differ): one sparse 2X scale spans 64 logical columns and merges the atom's two groups. If MXFP4 is measured beside
  NVFP4, its honest kernel uses the dense atom, or its statement names the sparse step (`gather_dense` over 2X).

## Lessons

- `research run --on vy-nebius-2` from an older branch needs `main`'s research CLI (the ssh provider) and a pulled
  research-notes checkout for `machines.d/vy-nebius-2.toml`.
- Node 2's system python has no numpy: wrap jobs in `uv run --no-project --with numpy`. The workload's cwd is the run dir,
  so relative paths need `--cwd source`.
- An identity gate can take the leased GPU directly: my `--expect-uuid` expands environment variables, so
  `--expect-uuid '$GPU_LEASE_UUID'` checks CUDA's device against the lease (unset, it stays literal and fails closed).
- **A clock64 bench must take a launch's longest block span, not the median.** Blocks start staggered, so the median span
  undercounts the SM clock (1,228–1,562 MHz read against 2,092 locked) and inflates per-clock rates 1.3–1.7×, by different
  factors on different loops. Check the derived MHz against nvidia-smi in every run.
- Use `gpu-lease 1 --wait`; a sequential driver that waits on each run (`research fetch` until `done`, `failed` or
  `cancelled`) keeps one lease at a time without anyone watching.
- Don't pass `--timeout` on node 2 (GPU 0's lesson; I did in four runs, and the lease report showed it clamped to the fixed
  deadline, so nothing moved).
- Run a long queue of recorded runs from a worktree pinned at one commit, so edits in the main checkout don't ship with
  later rows.
- A run's `result.json` must stay under 1 MiB, or the attempt is `result=invalid` even at rc = 0. A `--chain 1024` run's
  first mismatches carried 64 KiB of operands each; keep bulk data in the listed files.
- An art id covers its manifest's meta. Register a repo fixture with `research data refresh-fixtures --preserve`, which
  writes the canonical form `test_repo_replicas.py` checks, not with a hand `data put --meta`.
- A small fixture that discriminates is worth more than a large one that doesn't: the 5090's 1,400 unscaled vectors fit
  three rival models, while 260 chosen RTX PRO words separate them.
- Rival models can coincide on the operands a question is about. A hot H keeps every group term on the grid, so the 8-group
  and 4-group k128 models write the same words there. Pin the model on operands where they part, then measure the rate
  on the target operands.
- A rate simulated on dense operands does not carry over to 2:4 spans of the same family: pruning to 2:4 raised the
  merged-route rate from 0.5% to 38% of gaussian chains at h = 14.

## Fill candidates

Every row: `research run --on vy-nebius-2 --project verity --campaign pouw --tool tc_probe_fp4 --source . --cwd source
--env GPU_LEASE_WHO=bc-36186951-83fc-53b6-87de-fa584ddf9ff9 -- gpu-lease 1 --wait -- uv run --no-project --with numpy
python tools/tc_probe_fp4/probe.py --instruction <I> [args] --sass-check --seed <S> --expect-uuid '$GPU_LEASE_UUID' --out
'$RESEARCH_RUN_DIR'` at `fcad808d` (clean). Each restarts cleanly (one run per row, nothing carried over) and needs no
whole-node window. Open rows first; the done rows stay for reruns.

| Candidate | `<I>` [args] | GPU time (Estimated) | Yields |
|---|---|---|---|
| **Open:** K=32 E2M1 to P2, third die | `f8f6f4 --sweep --n-random 16384 --expect-model gs32_w26_native`, `--seed 20261005` | about 1 min | about 6.6M more gated elements, past 1e7 for a pinned entry (Needs) |
| Done: clean-tree NVFP4 / MXFP4 fresh seeds (§3) | `nvf4` / `mxf4` `--sweep --n-random 32768 --expect-model verity`, seeds 20261001 and 20261002 | 39–52 s each (Measured) | the coordinator's four dirty-tree runs, from a clean commit: 3dcd, a8db, 5553, cf34 |
| Done: the 2:4 metadata rule (§6) | `sp_nvf4_meta` / `sp_mxf4_meta --n-random 16384 --seed 20260930` at `25614709` | 12–13 s each (Measured) | each nibble's gather, the pinned step on it, the hardware's zero-pattern predicate |
| Done: T1 merged k128 (§5) | `sp_nvf4_t1 --seed 20260930` (default `--hot-bits 14,15,16`, C = +0 always) | about 1 min (63 s lease) | merged vs chained words per family and h |
| Done: unscaled E2M1 with nonzero C | `f8f6f4`, `f8f6f4_e2m1_e4m3`, `f8f6f4_e4m3_e2m1` `--sweep --n-random 4096` | a few minutes each | whether unscaled E2M1 is `BlockScaledAlignAdd` or a `GroupSum` |
| Done: `mxf8f6f4` UE8M0 1X with E2M1 | `mxf8f6f4_e2m1`, `_e2m1_e4m3`, `_e4m3_e2m1` `--sweep --n-random 4096` | a few minutes each | the block-scaled QMMA step |
| Done: dependent chains | `nvf4 --chain 2`, `nvf4 --chain 1024`, `mxf4 --chain 1024`, `f8f6f4 --chain 1024`, with `--sweep --n-random 4096` | ≤ 10 min each | chained cases of `tc-model/sm120-fp4` |
| Done: casts, exhaustive grids | `cvt_e2m1x2_f32`, `cvt_f16x2_e2m1x2`, `cvt_ue8m0x2_f32_rz`, `_rp`, `cvt_bf16x2_ue8m0x2`, `cvt_e4m3x2_f32_ue4m3` `--n-random 4096` | ≤ 2 min each | the quantizer's codecs, bit-exact |
| Done (dirty tree): fresh-seed NVFP4 / MXFP4 sweeps | `nvf4` / `mxf4` `--sweep --n-random 32768`, a new `--seed` each | ≤ 10 min each | confidence in `tc-model/sm120-fp4` (≥ 10M elements) |
| Done: W1 prices | `w1_price.py --out '$RESEARCH_RUN_DIR' --expect-uuid '$GPU_LEASE_UUID' --locked-mhz 2100` (tool `tc_price_fp4`) | about 5 min | the table in §2 |

The done rows are in §3 (runs d356 … e2b6); the W1 row is §2.

## Inventory: the sm_120 FP4 evidence before node 2 (all RTX 5090, none RTX PRO)

All numbers Measured on RTX 5090 (GB202, sm_120a) unless labelled; "verity" = the pinned `verity.ml.tc` model
(`BlockScaledAlignAdd`), "model5" = autoproof's control model.

| Run | Instruction | Device / driver | Seed, n | Elements | Mismatches | Artifact |
|---|---|---|---|---|---|---|
| r20260922-182011-88f8 | mxf4nvf4 4X (NVFP4) | vy-5090, 570.153.02, nvcc 12.8.93 | sweep | 1,736,704 + replay 1601/1601 | verity 0 (offline refit), model5 29,118 | art:973dafc0 |
| r20260922-182132-d6db | f8f6f4 E2M1 unscaled | vy-5090 | probe2 | replay 1400/1400 | 0 | art:5f6cbdca |
| (fp4-5090) e654 | mxf4nvf4 2X (MXFP4) | vy-5090 | sweep | 622,592 | verity 0 (offline), model5 19,709 | art:58a784e9 |
| (fp4-5090) 1f10 | bf16 m16n8k16 | vy-5090 | sweep | 204,800 | Hopper 0, Ampere 48,569 | art:2932e9e4 |
| r20260922-215616-3c10 | NVFP4 | vy-5090b GPU-506928f9, 580.178.04 | 20260922, 4096 | 2,252,800 | verity 0 | art:f3922b88 |
| r20260922-215831-c3d8 | MXFP4 | vy-5090b | 20260922 | 2,039,808 (fit data; 528 pre-D19) | fit | art:ccca4568 |
| r20260922-221716-65b9 | NVFP4 | vy-5090b | 20260923, 8192 | 4,349,952 gated + replay 1601/1601 | verity 0, model5 114,148 | art:1d78c8d9 |
| r20260922-221824-8d99 | MXFP4 | vy-5090b | 20260923 | 3,940,352 | verity 0 | art:1f6d4499 |
| r20260922-222148-6342 | MXFP4 | vy-5090b | 20260924 | 786,432 | verity 0 | art:d0b0d300 |
| r20260922-234714-0fc0 | NVFP4 | vy-5090c GPU-1257f022, 570.195.03 | 20260925, 20480 | 10,657,792 | verity 0, model5 192,196 | art:163e7bf5 |
| r20260922-235348-a405 | MXFP4 | vy-5090c | 20260926 | 9,658,368 | verity 0 | art:05d43883 |

Snapshots: `fp4-evidence-v2` art:cac4b3da, `fp4-proof-v1` art:ae3ab505. D20 (NaN/inf/overflow) is excluded from the model
(NaN acc → 0x7FFFFFFF, ±inf → itself, overflow → ±inf for UE8M0 only). Native peak (5090, r20260923-024527-a82e): NVFP4
`mma.sync` 1,879.9 TFLOP/s dense at 2,715 MHz (Measured).

**Not yet established on any sm_120 part** (queued above): f8f6f4 E2M1 with a nonzero accumulator, `mxf8f6f4` with an
E2M1 operand, mixed E2M1×E4M3, the casts, in-register dependent chains.

## For GPU 0 (shared `tools/tc_probe_fp4/`)

I edit `mma_fp4.cu`, `rows_fp4.cuh`, `w1_price.*` and `probe.py` (E2M1 rows, chains, casts, sparse rows, the FP4 W1
prices). Your FP8 rows (`mma_fp8.cu`, `fp8.py`) don't collide; pure-FP8 `mxf8f6f4` (E4M3×E4M3) is yours, any row with an
E2M1 operand is mine.
