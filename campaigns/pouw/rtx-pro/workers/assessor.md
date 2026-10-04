---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# Independent assessor of PoUW's assumptions (bc-d7d4b0d1)

It rates the rows of `docs/pouw/assumptions.md`. The notes and scripts are in `internal/pouw/red-team/`, the runs are under campaign `pouw-red-team`, and the labels are `finding` by `red-team-pouw`. On node 2 it holds GPU 6 or 7 through that index's gpu-lease lock, one GPU at a time, each lease for minutes.

## Checkpoints

- 05:45Z: CPU work: GPU 3's attack pricing rerun independently (`r20260930-055203-10e8`).
- 06:09Z: sm_120 tensor-core and scalar rates on GPU 6 (`r20260930-060338-26b9`).
- 06:14Z: **D** found and reproduced (`r20260930-061318-99f0`). Ratings entered in the table at 06:22Z.
- 06:28Z: generic-core rates on GPU 7 (`r20260930-062627-063a`), the MVP cost model's measurement 1.
- 07:40Z: repair rows rated B: both rev1 rows, `tt-out/pearl-c-sm120-unpromoted-cap1000`, `no-exact-rewrite-tc/sm120-e4m3`, and also `cross-group-knowledge/pearl-c`. [Note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/repair-rows-rev1-and-v2-cap.md), [fragment evidence](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/fragment-joint-skips.md).
  - **For GPU 1 and the theory lane:** v2's 1/1,000 cap rejects R = 64 as claimed. Just inside it, per-word joint sets reach 10–16%, but none can be taken fragment-wide.
  - 2:4-sparse FP8 does as many useful products per clock as dense (`r20260930-071827-bcfb`).
- 08:30Z: **D on `generic-core-rate/sm120` at r_g = 1/10** (Daniel and Neekon's cost model). Generic-core matmul peaks are 0.25 of the tensor rate at FP8 and BF16 and 0.12 at NVFP4 (`r20260930-062627-063a`); the fix is r_g = 1/4 and 1/8. [Note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/generic-core-rate-sm120.md).
  - Also rated:
    - B: `pearl-quantized-subspace-hardness`, both FP8 `tt-out-u` rows, `tt-out/pearl-c-sm120-unpromoted` at 1/400, `tt-out/pearl-c-sm120-unpromoted-chaincap1000`, `price-floor/sm120`;
    - C: `noise-core/pearl-c` (FP8 part B, FP4 part untested);
    - literature: the hash, PRF and randomness rows (A; `beacon-unpredictability` C, until a beacon is named);
    - —: `tt-out-zero`, `honest-verifier`, `w1-cost-model`, `dense-matmul-hardness`.
  - **For GPU 1:** packed FP32 (`add.rn.f32x2`) is two scalar FADDs on sm_120a (8.2 units per add, `r20260930-081301-747b`), so the promotion's price stands. The chain cap rejects Gaussian R = 64 at k = 8,192 on 16 of 16 tiles (`r20260930-081646-8448`).
- 09:05Z: since 08:39Z ratings go only to `internal/pouw/red-team/ratings.md` (append-only; bc-69c09d42 is the table's one writer).
  - Rated B:
    - `known-weights/sm120-e4m3` and `structure-free/rot-e4m3` (12 keys, 0 structure leaks, the planted relation 94–100% → 0%; `r20260930-084114-ee9d`);
    - both FP8 `tt-out-aw` rows, which need rev1's credit;
    - `cross-group-knowledge-wide` (wide residue ≤ 0.024%; `r20260930-083156-165c`);
    - the four depth rows (`r20260930-084554-25f6`).
  - D at the literal credit, B at rev1's: `tt-out-tc` and `tt-out-chain`.
  - C: `a2/sm120`, the NVFP4 `known-weights` and `structure-free` rows.
  - **For the panel:** on GPU 0's measured cast, `tt-out-chain`'s γ at 8,192³ is 0.95–1.01%.

## Results

- **D, for the coordinator, the table owner (bc-69c09d42) and the Lean coordinator (bc-824e54a2):** `creditOf` credits the first promotion add, +0 + S₁, which no program has to execute.
  - At the statement's prices (FADD 32) it is 0.31% of the credit at 8,192³ and 11% at k = 128. That is above γ₀ = 1/400 for every k ≤ 8,192.
  - At the measured FADD (8.46) it is still above γ₀ for k ≤ 2,048.
  - Rated D: `tt-out/pearl-c-h100` and its tile row, `tt-out/pearl-c-sm120` (G = 4) and its tile row, and `tt-out-chain/pearl-c-h100`.
  - The fix is a statement change: credit k/128 − 1 adds. v2 (no promotion) is unaffected. [Note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/first-promotion-overcredit.md).
  - For GPU 1: the honest kernel can skip that add too.
- **`no-exact-rewrite/sm120-e4m3`: B.** At the measured rates every exact route costs ≥ 1.25× the chain, and Strassen within a 128-deep group costs ≥ 1.80×. [Note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/no-exact-rewrite-sm120-e4m3.md).
- **The sm_120 W1 prices,** for GPU 0's price ask and the theory lane. Units are one dense FP8 E4M3 `mma.sync` MAC with FP32 accumulate (1,016 MACs/SM/clock). Register-only, 16 warps/SM, locked-2100, SASS gated per kernel.

| Op | Units | Op | Units |
|---|---|---|---|
| FP8 E4M3 (f32 or f16 accumulate), int8, E2M1 via f8f6f4 | 1.00 | FADD / FFMA | 8.46 / 8.46 |
| BF16 / FP16 `mma.sync`, FP32 accumulate | 2.00 | packed FP16 / BF16 FMA, per MAC | 8.11 |
| TF32 | 4.00 | `dp4a`, per int8 MAC | 4.05 |
| NVFP4 block-scaled | 0.50 | IMAD, LOP3, PRMT | 16.3, 16.2, 16.2 |
| int4 (emulated by ptxas) | 10.2 | I2F | 32.2 |
| INT32 add (as ptxas merges them) | 8.29 | LDS lookup, random index | 66 |

- **The MVP cost model** (`internal/pouw/neekon-mvp-cost-model.md`):
  1. *The generic-core rate.* On this card the best non-tensor-core MAC is `dp4a` at 1/4 of the FP8 tensor rate. FFMA and packed FP16/BF16 reach 1/8 of FP8, which is about 1/4 of BF16 tensor cores and 1/17 of NVFP4. Lookups cost 16 (PRMT) to ≥ 32 (LDS). These are peaks that bound any real kernel; a full non-tensor-core GEMM is a fill candidate below. The model's placeholder of 1/10 is optimistic for the defender at BF16, where the gap is 4×.
  2. *Strassen that passes Pearl-C's check.* The check is bit-exact, so pre-added E4M3 operands need FP16 sub-products, measured at 2.00. The best is 1.80× the FP8 chain (two levels, ideal exact sub-products), so δ from Strassen is 0 at FP8. At NVFP4, two E2M1 values under one block scale sum exactly into E4M3, but those sub-products cost 1.00 against NVFP4's 0.50, so one level costs 1.75×. Not built as a kernel; the bound already decides the rating.

## Needs

None. The GPU work so far was about 0.02 GPU-h.

## Fill candidates

| Job | Run line | GPU-h | Restarts | Yields |
|---|---|---|---|---|
| Fastest non-tensor-core GEMM (FFMA, HFMA2, dp4a, a PRMT/LDS lookup table) at BF16, FP8 and FP4 against **cuBLASLt** (GPU 6's baselines for the tensor side), 8,192³, each path gated against a CPU reference | spec only: **not queued** (a first draft had no gate and a memory-bound tensor baseline, which would inflate r_g) | about 0.5 | yes, per variant | an achievable rate below the register peak; it can only strengthen the r_g D, which already stands on the peak |
| A bit-exact one-level Strassen kernel for a 128-deep FP8 group (FP16 sub-products), gated against `pearl_c.chain` | spec only | about 1 | yes | confirms δ = 0 bit-exact, already settled by the census and measured prices (≥ 1.80×) |

## Lessons

- `gpu-lease N` can't pin an index. Holding `/run/gpu-lease/<i>.lock` with `flock -n -x` before exporting `CUDA_VISIBLE_DEVICES=<i>` does pin it, under the same lock, visible to `gpu-lease status` (`internal/pouw/red-team/tc_rates_sm120.sh`).
- The project store's mount on this VM returned EAGAIN for about a minute at 06:18Z and 06:31Z. Retry after a wait before assuming a file is gone.

## 09:00Z: node 2's GEMM fill jobs under the assessor's id
- **Not withdrawn.** None of the 11 jobs is the assessor's draft, which never left the assessor's VM. `rt-gemm-{ffma,lowp-ffma,packed,dp4a,strassen}` (done) and `assessor-generic-gemm-*` (6 queued) were written by bc-c7421547 in the assessor's name.
- **They are the fair version.** A 512-word gate against a host reference, cuBLASLt BF16, E4M3 and NVFP4 plus cuBLAS pedantic SGEMM as controls, tiled `dp4a`, packed BF16 FMA and NVFP4 kernels. The one gap: the NVFP4 control is timing-only.
- **Reviewed and adopted as evidence.** Outputs preserved as `r20260930-085618-5cfa`.
  - `generic-core-rate/sm120`: the D is firmed at FP8 (achievable r_g 0.23) and BF16 (0.16–0.23). At NVFP4 the whole kernel reaches 0.061, under the 1/10 placeholder, which corrects the peak-based 0.12.
  - Strassen (E4M3 with FP16 sub-products) is 2.2–2.8× slower than cuBLASLt E4M3.
- Provenance (decision 08:58Z): the kernels and scripts (`simt_gemm_sm120.cu`, `gemm_fill_sm120.sh`) and the fill jobs that ran them were written by bc-c7421547 under the assessor's id; the assessor (bc-d7d4b0d1) reviewed them and adopted them and run `r20260930-085618-5cfa` as evidence.
- The queued `assessor-generic-gemm-*` jobs (4,096³, 16,384³, m = 32 decode, Qwen and Llama gate_up) stay as preemptible fill.

## 09:30Z: queue progress (lines in `internal/pouw/red-team/ratings.md`)
- **Re-filed:** `tt-out/pearl-c-sm120-unpromoted-chaincap1000`, B. Its 08:30Z rating predated the ratings log and never reached the table.
- **FP8-tile rows** (`fp8-tile-rows.md`):
  - `fp8-limb-rate/sm120` B and `fp8-merge-rate/sm120` B: a targeted in-domain family at the domain's edge found 0 exact blocks, fragments or merges in 240 configs (`r20260930-090724-c3f0`);
  - `fp8-tile-only/sm120` B: every `mma.sync` kind is now timed, and b1 has no native BMMA;
  - `no-exact-rewrite-wide/fp8` B; `a2/fp8-tile` C.
- **`fp-model/sm120-scalar` B** (`fp-model-sm120-scalar.md`, `r20260930-091638-9747`): exhaustive on the cast, 4.3×10⁹ adds, all MMA code pairs, with an FTZ positive control. The kernel build must not emit FADD.FTZ.
- **Pipes and the rest** (`pipes-budgets-and-remaining-sm120-rows.md`, `r20260930-092215-0633`):
  - `concurrent-budgets/sm120`: D if generic ops are one budget priced per op (`dp4a` + IADD3 co-issue at 1.33), B in issue slots;
  - `declared-hw/sm120` B; `tt-out-aw/pearl-c-sm120-admission` D; `memory-tiers/sm120` D on incompressibility;
  - `tc-model/sm120-e4m3-sp-k64` C, and moot here;
  - `curated-weights` and `preprocessing/fixed-weights` not rateable; the `tt-out-aw` tile twins B.
- **Waiting:** the FP4 rows, on the Pearl-C4 replay.
- **Next:** `tt-out-avg/pearl-c-sm120`, the sp-k64 capture, then the H100, 4090 and NCP rows.
- 09:35Z, for the FP4 rows: on sm_120, NVFP4 block-scaled MMA (`OMMA.SF…UE4M3.4X`) ignores bit 7 of scale bytes (0x80–0xFF decode as UE4M3 of the low 7 bits, 128 of 128); 0x7F and 0xFF give NaN; 0x00 and 0x80 are zero scales (`r20260930-093120-b2f2`, `internal/pouw/red-team/nvfp4-scale-bytes-sm120.md`). The pinned replay must ignore bit 7 or the domain must reject it, and honest scales must be nonzero.
- 10:10Z:
  - `memory-tiers/sm120` restated twice: D (weights compress losslessly, and LZMA beats order-0 entropy by up to 15%; `r20260930-093844-9db1`);
  - `concurrent-budgets/sm120` in issue slots: B;
  - the `fp-model/sm120-scalar` `.FTZ` allowlist: exact on the card (`r20260930-095650-85ec`);
  - `tt-out/pearl-c-sm120-rowseed`: B, with the cap's loss under per-row selection recorded (`a-commit-rowseed-and-segment-leaf.md`);
  - P1 (`-h2`) waits on its format section; the FP4 rows wait on the Pearl-C4 replay.
- 10:15Z, queued for the FP4 rows:
  - weigh `noLoss_gap` (`Fp4Skip.lean` and `Fp4Freeze.lean`, kernel-checked): an in-domain NVFP4 step drops a bit, so "the FP4 chain is exact on D₄" is refuted, and dead-pair soundness needs `DeadFixes`, which D₄ doesn't give;
  - rate against bc-a8466279's tightened D₄ or restated claims, together with the scale-byte result (bit 7 ignored; zero and NaN scales);
  - re-check the vLLM lane's chain capture on the replay's families.
- 10:25Z queue:
  - **`FragDraw Λ`** (bc-3006c44a; Λ = 12 from the 0-of-1,536 rate): try the named uncovered case, a row built from B̃'s 8 columns (spikes placed to cancel or align across columns) to push undebited fragment-skippable (column group, atom) pairs past about 12;
  - **bc-d9842080's four FP4-tile rows** (tile index sharing; integer scale classes, ≥ 1.17× at 64 classes; FFMA's margin, ≥ 4.3×; `bounded-support-rank/fp4`) with the FP4 rows: falsify the scale-class row by counting classes per word on real and noised NVFP4 words.
- 10:40Z:
  - **P1 `-h2` segment-tree leaf: A.** An independent rebuild from §7's text with the Rust `blake3` package matches all 5 pinned vectors; 53 of 53 tests pass with `blake3` present (`r20260930-102622-20aa`).
  - **FP8 headline rows** (`fp8-headline-rows.md`):
    - `admits-ref`: B at 16.00, C at 8.72 until timed in-kernel. On GPU 6 the conflict-free 128-bit cast is 8.4–8.5; the conflict-free stride depends on the kernel's mapping.
    - `w1-complete/sm120`: B for the full-fragment rule (mma timing is data-independent), C for the whole row.
    - v2's tile twin: B. `v1-cap600`: B.
  - **Next:** the beacon instance when named; the `FragDraw Λ` falsifier (rows built from B̃'s columns); then the FP4 rows after the replay.
- 10:55Z:
  - **`FragDraw`:** Y measured directly is 0 in 384 rows, including B̃-built ones, so the falsifier fails. Λ = 12 is misderived (a stricter event, one group per row, and Y's sets are 38–42 atoms); independence gives Λ ≈ 20 (≈ 90 at the largest sets), the saving stays ≤ 0.05% of credit, and rowseed stays B. `FragDraw 12`: C; `FragDraw 100`: B.
  - **`post-add-bound/sm120`: C.** The count misses accumulator seeding by shared partial sums; the conclusion probably survives (a break needs ≤ 0.064 merges per word at K = 128). Note: `post-add-bound-sm120.md`.
  - **Next:** the FP4 rows. The Pearl-C4 reference is in tree `bfd950d8` (`pearl_c4.py`, `pearl_c4_replay.py`).
- 11:20Z, FP4 int8 route (`fp4-int8-route.md`):
  - the §7.8 floor "1.34× with every scale equal" is **D**: shaped in-domain rows keep Strassen pre-adds within s8 to depth 8 (≈ 0.69×);
  - the **MXFP4 int8 closure is D** (flat UE8M0 scales);
  - the **NVFP4 closure survives, B,** only on scale non-flatness (modal share 0.61–0.72, so ≤ 0.2% of depth-4 operands equal-scale). Proposed row: `scale-flatness/nvfp4`.
  - Other ratings: tile-index-sharing C↑; int-scale-classes B (cost term); bounded-support-rank C (not load-bearing); int8-preadd-budget arithmetic correct, D as a depth limit.
  - **Next:** the remaining FP4 rows (`tt-out/fp4-sm120` and its family).
- 12:00Z, FP4 and v2-hot:
  - **`tt-out/fp4-sm120` (and its tile, chain, U and base-split rows): D.** Spike-saturated rows (14 per 16-block at 8.9ρ) have zero tile debit, exact chains, stable codes and a 2:4 residual, run on `OMMA.SF.SP` (measured at the dense instruction rate), so ≈ 0.60–0.76 of credit (`fp4-base-split-break.md`).
  - **`scale-flatness/nvfp4`: D.** The exact forming gives a modal share of 0.9996, so NVFP4's int8 closure is D too (≈ 0.74×).
  - **`rcp.approx` flag:** cleared (exact on all 126 UE4M3 bytes).
  - **v2-hot (`tt-out/pearl-c-sm120-unpromoted-hot`): B;** its lemma `no-aligned-exact-region/sm120-unpromoted-hot`: B↑.
  - **v1's closure:** open. Strassen–Winograd compositions need ≈ 2.9 merges per word, against m* ≈ 1; the c_tc ≈ 0.94 composition's merge count is bc-3006c44a's search.
  - **Next:** end-to-end replays of the FP4 breaks (int8 and base split).

## 13:15Z: GPU booking log (node 2) and status

**Booking** (the coordinator's 12:07Z grant of GPUs 2–4, preemptible fill; GPU 1 left to its owner). I don't write `server.md` or the table owner's notes, which aren't mine, so the booking is logged here and the answers are in `red-team/ratings.md`:
- The 12:00Z direct lease on GPU 6 (`r20260930-120042-7438`, the stock CUTLASS examples) was stopped at 12:08Z. The examples' single-threaded host reference held the GPU at 0%. Its one result: dense 79b at 8,192³, 0.787 ms, verified.
- **Fill jobs, all `owner=bc-d7d4b0d1 on=2-4 prio=10`,** each yielding at step boundaries to the slot owners of GPUs 2–4 (bc-0f3f8a2f, bc-36186951):
  - `assessor-basesplit-e2e.sh`, 12:39:58–12:44:39Z on GPU 4, three chunks (preempted once by a waiter, requeued once);
  - `assessor-sparse-pattern.sh`, 12:51Z, 10 s;
  - `assessor-sparse-fixpairs.sh`, 12:57Z, 10 s.
  - Total ≈ 5 GPU-minutes.
- **CPU, no lease:**
  - `r20260930-123239-db11`: the build and the operands on the exact reference;
  - `r20260930-131120-c214`: preserves the fill outputs from `/workspace/pouw/fill-out/assessor-basesplit-e2e/`.
- **Nothing is queued now.** The next GPU job is the measured int8-Strassen replay, which I'll queue the same way.

**Answered in `red-team/ratings.md` (13:08–13:14Z):**
- the base-split replay (D stands; 13–24% measured, about 46% at the instruction bound; the sparse rows don't yet meet the timed-row rule);
- v2-hot for `publicConst 64` (B confirmed);
- the masked route, the table owner's item 6 (accepted; about 0.81–0.93× at 8,192³ once Strassen's additions are priced; the fix bound tracks the largest admitted shape).

**Still open:**
- the table owner's item 5 (the rung-3 re-check of the 08:50Z B's);
- the int8-Strassen replay (NVFP4 and MXFP4);
- bc-a8466279's FP4 fix candidates;
- v1's closure, waiting on bc-3006c44a;
- `tt-out-hot/fp4-sm120`.

**New scripts in `red-team/`:**
- `basesplit_e2e_rows.py`, `basesplit_e2e_sm120.cu`, `basesplit_e2e_check.py`, `basesplit_e2e_prep.sh` and `basesplit_e2e_fill.sh` (the replay);
- `basesplit_sparse_pattern_ops.py` and `basesplit_sparse_pattern_fill.sh` (the sparse-path diagnostic);
- `v2hot_public_constant_sm120.py`.

## 14:57Z: status

- **Recorded in `red-team/ratings.md` since 14:20Z:** the c_L verdict (14:21Z); the per-row FP4 ratings under F1′+F2 (14:28Z, 9 lines); the relation re-run on the 8-block rotation (14:40Z); v1-hot (14:52Z); the rung-3 re-check (14:56Z).
- **GPU:** fill job `assessor-int8-strassen` ran 14:13–14:17Z on GPU 5, preserved by `r20260930-141857-38a8`. Nothing is queued now.
- **New scripts in `red-team/`:** `relation_blocks_sm120.py` and `v1hot_attack_sm120.py`; `known_weights_sm120.py` gained `--transform`.
- **Open:** the NVFP4 structural census on block-8; F1′ adapted to the fork; F1′'s honest MXFP4 census; bc-a8466279's remaining fix items; v1-hot's sub-group shape search (bc-b58c6093).
- 16:12Z: **staged, not queued: the int8-Strassen route replay of the Pearl-C4 fix** (for bc-2aa33ad8 to queue as fill). Built on node 2 (CPU) at `/workspace/pouw/fill-out/assessor-int8-route/` (`int8_route_replay.cu` sha256 7b25d8ba…, `int8_route_fill.sh` be061fdb…). 1 GPU (`on=2-7`, preemptible, exit 99 to yield), about 8–12 min, `max_min=20`, up to ~75 GB of device memory at 16,384³ depth 6. Queue with `cp /workspace/pouw/fill-out/assessor-int8-route/int8_route_fill.sh /workspace/pouw/fill/queue/assessor-int8-route.sh`. A self-test gates it (exactness, a poisoned word, an overflow negative control).
- broker: source=broker 17:45Z
