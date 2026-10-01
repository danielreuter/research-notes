---
id: 20261001T1750Z-report-from-proofs-bf16-hill-prover-1a-9
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c-997f-5c36-9346-e43f88011d95)
---

# Prover changes 1a and 9: byte-identical, each negative control fails, no floor met; change 5 not started

From proofs-bf16-hill, on `note:proofs-bf16-hill/20261001T1548Z-handoff-from-proofs-owner-yes-prover-changes-1a-5-9` and
`note:proofs-bf16-hill/20261001T1602Z-handoff-from-proofs-root-yes-and-m0-gates-1a-5-9`. A record, not a message.

## The changes

- **Branch:** `cursor/bf16-hill-prover-1a-9-1d95` off `85c862521` (bf16-hill's accepted tree). No PR, M0's tree untouched.
  - **1a, `c621375b4`:** zerocheck round 1's GF(2^8) products move onto the ALU (SWAR, prmt byte masks), ported from the
    zc1a microbenchmark's MODE 0 (`backends/flock/cuda/zerocheck_round1_alu.cuh`). No new table: it reads the `g_zc_t0` and
    `g_zc_phi` tables the old kernel already used. Switches:
    - `FC_ZC_TABLES=1` launches the old `zerocheck_first_round_cpu_structured<14>` in the same build (the same-job control).
    - `FC_ZC_ALU_BREAK=1` reduces by 0x1d instead of 0x1b (the negative control).
    - The gate's `gpu_proofs_match_cpu` now records the device proofs' SHA-512.
  - **9, `1398fa294`:** after a table's last rep, the session's witnesses go to `retire_witness`. It returns pooled device
    and mapped host buffers to their pools inline, so the next upload finds them, and frees the rest on a thread of its own.
    Nothing touching the transcript moves. Switches:
    - `FC_DROP_INLINE=1` frees everything on the session's thread (the control).
    - `FC_DROP_BREAK=1` retires the witnesses before rep 1, their last use (the negative control).
- **Packed tree:** `cursor/flock-fp-prover-1a-9-1d95` is flock-fp's `a30bc8e5b` with both commits cherry-picked cleanly
  (`5e250507c`, `a576e040d`).
- **Builds:** `r20261001-171349-5563` (rc 0, 245 s, 0 GPUs) and the packed tree's build and stage for NVF4 K=2048,
  `r20261001-172254-5fb5` (rc 0).

## Byte identity

- **Scope:** every point below passed the gate (B = 16, injected seeds): `gpu_paths_agree`, `gpu_proofs_match_cpu` and
  `verify_ahead_matches_serial` all passed, with equal proofs and equal transcripts.
- **Same build, switches flipped:** the device proofs' SHA-512 is identical with both changes on and with both off. Off is
  the step's code path, run on the same build.
- **Against each step's best:** the statement digest and the gate's statement digest equal that best's, and rep 1 reuses
  rep 0's witness (`rep_reused`) everywhere.

| K | Step compared | Statement digest | Gate digest | Proof SHA-512, rep 0 / rep 1 (16 hex): on = off | Runs: on / off |
|---|---|---|---|---|---|
| 2048 | s6 `4a30` | `7f39853935e48dec` | `d6476e1cba912981` | `a75cc656955f79c8` / `0cb23694b0d823be` | `72f8`, `c006` / `0e48` |
| 4096 | s3 `2e7e` | `accf43c64453ae67` | `801a4254cce7042d` | `e484ec4de23a30a7` / `e59c130cb111b4af` | `2e74`, `ec40` / `fcec` |
| 8192 | s5 `cab4` | `46d84a0e1c724796` | `964f63d6639b3876` | `1400970997a72e53` / `e78b07c5643c81de` | `8441`, `15bb` / `97ff` |
| 16384 | s4 `f010`, `6c85` | `bbb79d7042330283` | `5021e06ae78b40ba` | `afccd0b6d76642db` / `9176b778ff29d39d` | `440c`, `0acc`, `6b46` / `cc1e`, `5d8f`, `4e4d` |
| NVF4 K=2048 packed | packed `a668` | `1abd835db3377aca` | `d474eed5a3e6e7fb` | `b7e30f430dfda187` / `e68bfae545efb7f8` | `e8f3`, `ec2d` / `dd0e` |

## Negative controls (K=2048, each with its gate run)

- **1a, `FC_ZC_ALU_BREAK=1` (`r20261001-171723-ca51`):** the gate failed.
  - `gpu_proofs_match_cpu` failed, with proofs and transcripts both unequal.
  - Every session was rejected, so `gpu_paths_agree` and `verify_ahead_matches_serial` failed too.
  - No timed sweep ran.
- **9, `FC_DROP_BREAK=1` (`r20261001-172146-12d6`):** the gate failed.
  - Rep 1 panicked with "a rep's witness".
  - Every device session was rejected and returned no proofs, so `gpu_proofs_match_cpu` failed.

## What each change does to a session (medians over the 24 timed sessions)

- **1a, zerocheck bucket per rep:** 112–113 ms with the tables (`f010`, `cc1e`, `5d8f`) against 100–103 ms on the ALU, at
  every K. That is −10 to −12 ms per rep, as the microbenchmark predicted (−11.6 ms per launch).
- **9, e2e minus prove_total per session:**
  - Before: 40 ms on step 4's binary (`f010`), and 15–18 ms with `FC_DROP_INLINE=1` on this build (`cc1e`, `5d8f`).
  - After: 0.4–0.6 ms at every K.
- **Per-session e2e, against each step's best:**

  | K | Change |
  |---|---|
  | 2048 | −4.9% |
  | 4096 | −7.0% |
  | 8192 | −2.2% |
  | 16384 | −4.0% |
  | NVF4 K=2048 packed | −2.6% |

- **The back-to-back pair at K=16384 (`0acc` on, `5d8f` off):** e2e is 0.814 s against 0.817 s, and both cells are
  2.67e7. The prove got about 20 ms slower and cancelled the drop's saving. My guess is that the drop's unmapping now
  overlaps the next prove. The two windows' host pressure differed too: 108 compaction stalls for `0acc`, 65,504 for `5d8f`.
- **The clean pair at K=16384 (`6b46` on, `4e4d` off, after the pressure cleared):** the cell is 2.55e7 against 2.71e7
  (−5.8%), and e2e is 0.794 s against 0.807 s. In both pairs, the prove-only overhead is 3–4% higher with the changes on
  (2.37e7 against 2.27e7 here), while the boundary gap falls by 15–20 ms. So 9's freeing still costs the prover something.
  The next test is 1a alone against 9 alone in a clean window.
- **The 1a-only run at K=16384 (`r20261001-174151-27f4`, `FC_DROP_INLINE=1`)** ran under the worst pressure of the hour:
  54,131 stalls and 204,131 direct reclaims in 48 s. Its cell, 5.73e7, is not a point. Its inline drop took 47.8 ms
  median and 110 ms mean per session, the cost 9 takes off the session's thread.

## Cells against the floors (node 1)

Means are over the samples listed. A sample taken after the host's pressure cleared (17:52Z) is marked "clean".

| Cell | Floor | Before (step best) | With 1a + 9 | Mean | Met |
|---|---|---|---|---|---|
| BF16 K=2048 | ≤ 3.95e7 | 4.36e7 `4a30`, 4.27e7 `9094` | 4.68e7 `72f8`, 4.24e7 `c006` (clean) | 4.46e7 | no |
| BF16 K=4096 | ≤ 2.12e7 | 2.37e7 `2e7e` | 2.55e7 `2e74`, 2.24e7 `ec40` (clean) | 2.40e7 | no |
| BF16 K=8192 | ≤ 2.14e7 | 2.38e7 `cab4` | 2.31e7 `8441`, 2.28e7 `15bb` (clean) | 2.29e7 | no |
| BF16 K=16384 | ≤ 2.30e7 | 2.70e7 `f010`, 2.61e7 `6c85` | 2.67e7 `0acc`, 2.55e7 `6b46` (clean); controls 2.67e7 `5d8f`, 2.71e7 `4e4d` (clean) | 2.61e7 | no |
| NVF4 K=2048 packed (n ×2) | −6%: ≤ 4.09e7 | 4.36e7 `a668` | 4.32e7 `e8f3`, 4.25e7 `ec2d`; same-build control 4.60e7 `dd0e` | 4.29e7 (−1.6%) | no |

**The host was under memory pressure in every window of this hour.**

- NUMA node 0 had about 3 GB free.
- `compact_stall` and `pgsteal_direct` rose by tens of thousands in each timed window (K=2048 `72f8`: 116,671 stalls in
  20 s), against 0 for `f010`.
- Other tenants' cores ran at 64–104, against 35–62 for the bests.

The prove-only overheads fell 4.2% at K=2048, 6.1% at K=4096 and 0.4% at K=8192, and the session overheads at K=2048 and
4096 rose. So these
cells measure the host as much as the changes. `cc1e` and `440c` ran two K=16384 points side by side, which put 1.2e8 into
both. Those two are not points.

## Not done

- **Change 5** (no `cudaMalloc`/`cudaFree` in steady sessions; arena-owned `d_tape`, `d_hin`, host-slot indices, `Hm96Guard`
  tables and midstates, `DevBuf` pool): not started. M0's `rep_reused` gate is checked above for 1a + 9 only.
- **Packed cells:** only NVF4 K=2048 was measured. Nothing at n ×4.

## Owed from 7:53 AM PDT

- **Item 1, `r20261001-151503-1995`** (K=16384 nsys trace with CPU sampling), `art:7c5510bcf5dc0649fdeeed197ca236ca42d9f7d5852ff62c6449e783fc3f4d1a`.
  - The 35 ms of e2e − prove_total is the synchronous drop of the session's host witness: `drop_glue<WitData>`, then
    `munmap`, then `zap_pte_range`.
  - It matches the stamps within 0.8–2.3 ms at each boundary (mean 29.7 ms) and makes 0 CUDA calls. 8–14 ms of it is on-CPU;
    the rest is sleep, alongside the next prebuild's page freeing.
- **Item 2, `r20261001-151504-f072`** (ncu of the column fold): rc 0, outputs on node 1, not analysed.
- **Item 3, `r20261001-153238-8105`** (the zc1a microbenchmark), `art:70df931d3a98a172d0160194e59568577e4f22ae06061b8dd098533f4e074fd8`.
  - Branch `cursor/zc-round1-swar-bench-1d95` at `7a9a978e0`.
  - At m = 35, the tables take 64.6 ms per launch, prmt 52.9 ms, imad 56.4 ms and clmad 62.5 ms.
  - `all_identical` is true, and the exhaustive product, reduce and index checks have 0 bad.
