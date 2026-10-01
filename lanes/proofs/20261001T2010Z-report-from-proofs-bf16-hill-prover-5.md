---
id: 20261001T2010Z-report-from-proofs-bf16-hill-prover-5
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c-997f-5c36-9346-e43f88011d95)
---

# Prover change 5 and the 1a/9 A/B: 5 passes M0's gates and cuts e2e at every K; no floor met

From proofs-bf16-hill, on proofs' 11:18 AM PDT ask (change 5 to M0's gates, then an A/B of 1a against 9 on one build), under
root's yes on 1a, 5 and 9 (`note:proofs-bf16-hill/20261001T1602Z-handoff-from-proofs-root-yes-and-m0-gates-1a-5-9`). Follows
`note:20261001T1750Z-report-from-proofs-bf16-hill-prover-1a-9`. A record, not a message.

## Quiet threshold

A timed window counts as a point only if `compact_stall` and `pgsteal_direct` both rose by 0 over the run's steady window
(`host_vmstat_steady`). Every job was submitted only after 20 s with both deltas at 0, NUMA node 0 at 64 GiB free or more,
and a free `provers` slice. Windows above the threshold are marked "not a point" and left out of every mean.

## The change

- **Change 5, `c13bf7da8`** on `cursor/bf16-hill-prover-1a-9-1d95`, on top of 1a + 9 (`1398fa294`). No PR, M0's tree
  untouched. Build `r20261001-184129-db72` (rc 0, 208 s, 0 GPUs).
  - A proof's scratch comes out of the device arena: `fc_witness`'s inputs, tape, rows and host-slot indices; the hm96
    context's tables, prefixes and midstates (`Hm96Guard`, now installed after the arena opens and released before it
    closes); Ligerito's per-level path gathers (`lf_capped_paths`). The arena grows by the hm96 buffers, and by the witness
    phase's peak where that is larger.
  - `FC_SCRATCH_CUDA=1` keeps `cudaMalloc`/`cudaFree` in the same build (the same-build control).
  - `FC_ARENA_BREAK=1` releases the hm96 tables to the arena right after their upload, so later scratch overwrites them
    (the negative control).
  - The `DevBuf` pool is untouched: prefetch is off in every bench config, so it allocates nothing in a session.

## M0's gates

- **Byte identity at every K:** every change-5 run, on and off, passed the gate (`gpu_paths_agree`,
  `gpu_proofs_match_cpu`, `verify_ahead_matches_serial`). Each run's statement digest, gate digest and both device proofs'
  SHA-512 equal the 1a + 9 head's (the table in `note:20261001T1750Z-report-from-proofs-bf16-hill-prover-1a-9`).
- **`rep_reused`:** true in every run at every K.
- **Negative control, `r20261001-185919-bd6a` (`FC_ARENA_BREAK=1`, K=2048):** the gate failed. Its proofs are
  `e3ec3c0a8876ecf4` / `2a9db8078b5ae642`, against `a75cc656955f79c8` / `0cb23694b0d823be`.
- **No allocation in steady sessions (Nsight Systems, CUDA API calls per session, warm and last sessions apart):**

  | Run | K | Change 5 | Steady sessions | `cudaMalloc` | `cudaFree` |
  |---|---|---|---|---|---|
  | `r20261001-191708-7e90` | 2048 | on | 11 | 0 | 0 |
  | `r20261001-193710-0def` | 8192 | on | 11 | 0 | 0 |
  | `r20261001-192029-83c9` | 2048 | off (`FC_SCRATCH_CUDA=1`) | 11 | 39 | 39 |

  With change 5 on, all 33 `cudaMalloc` calls fall in the warm session.

## Change 5, on against off on the same build (means over quiet samples)

| K | Cell on | Cell off | Cell | Prove-only | e2e (s) on / off | e2e |
|---|---|---|---|---|---|---|
| 2048 | 4.185e7 (`9023`, `21ea`, `feb2`) | 4.236e7 (`767d`, `58c0`, `5ca1`) | −1.2% | −2.0% | 0.700 / 0.713 | −1.8% |
| 4096 | 2.223e7 (`1c69`, `d2ea`) | 2.339e7 (`bf53`, `f216`) | −5.0% | −4.6% | 0.704 / 0.735 | −4.3% |
| 8192 | 2.200e7 (`f9bb`, `3a45`) | 2.312e7 (`07c5`, `acb9`) | −4.8% | −4.5% | 0.698 / 0.728 | −4.0% |
| 16384 | 2.381e7 (`af18`, `8678`); 2.468e7 with `bf39` | 2.582e7 (`f7f4`, `6d22`; `7d93` not a point) | −7.8% / −4.4% | −8.0% | 0.733 / 0.795 | −7.8% |

- Change 5 cuts per-session e2e at every K, and prove-only falls with it: prove_total included the allocations.
- The e2e saving at K ≥ 4096 (29–62 ms) is larger than the allocation calls' own time (at K=2048, a median of 6.0 ms of
  `cudaMalloc` and 3.2 ms of `cudaFree` per session). My guess is that each `cudaFree` also synchronized the device, which
  stalled the work queued behind it.
- **`bf39` (K=16384 on, sample b)** is quiet by the threshold and counts. Two of its sessions stalled in rep 0's witness
  phase (1.14 s and 0.97 s, against 0.08 s typical), waiting on the prebuilt host witness. That puts its cell 21% above its
  prove-only. Stalls of 0.3 s or more show up in about a third of this hour's runs, in every variant with or without change
  5, so this is an existing intermittent wait, not change 5.

## A/B on one build, `1398fa294` (means over quiet samples)

Variants: 1a alone is `FC_DROP_INLINE=1`, 9 alone is `FC_ZC_TABLES=1`, and off sets both.

| K | Variant | Cell | Prove-only | e2e (s) | Samples |
|---|---|---|---|---|---|
| 16384 | off | 2.636e7 | 2.323e7 | 0.829 | `09b9`, `02b4` (`600e` not a point) |
| 16384 | 1a | 2.677e7 (+1.6%) | 2.338e7 (+0.6%) | 0.827 | `4207`, `0e12` |
| 16384 | 9 | 2.577e7 (−2.2%) | 2.359e7 (+1.5%) | 0.790 | `f196`, `e433` |
| 16384 | all | 2.517e7 (−4.5%) | 2.338e7 (+0.6%) | 0.783 (−5.6%) | `9a9c`, `4c9b` |
| 2048 | off | 4.384e7 `52ae`; 5.197e7 `854b` | 4.301e7 | 0.725 | `52ae`, `854b` |
| 2048 | 1a | 4.340e7 | 4.286e7 (−0.3%) | 0.722 | `4bfd`, `6e37` (`8184` not a point) |
| 2048 | 9 | 4.364e7 | 4.249e7 (−1.2%) | 0.713 | `c033`, `5a21` |
| 2048 | all | 4.162e7 (−5.1% against `52ae`) | 4.141e7 (−3.7%) | 0.693 (−4.4%) | `8ee0`, `49b7` |

- **Neither change costs the prove 3–4% in a quiet window.** The largest increase is 9 alone at K=16384, +1.5%
  prove-only. Two samples of one variant already differ by up to 3% (1a: 2.304e7 and 2.372e7). At K=2048, every variant's
  prove-only is at or below off's.
- **What each change does:**
  - 1a cuts the zerocheck bucket to 102–106 ms per rep, against 109–115 ms with the tables.
  - 9 cuts e2e minus prove_total to 0.4–0.8 ms, against 34–49 ms without it at K=16384 and 3.6–4.8 ms at K=2048.
- **The combination does not make 6% in a quiet window:**
  - Cells: −4.5% at K=16384, and −5.1% at K=2048 against `52ae`. The other off sample, `854b`, is quiet but its sessions
    stalled, which puts its cell 22% above its prove-only.
  - e2e: −5.6% at K=16384 and −4.4% at K=2048.
  - With change 5 on as well (a different build, `c13bf7da8`): the K=16384 cell is −9.7% (2.381e7, or −6.4% counting
    `bf39`), and K=2048 is −4.5% (4.185e7 against `52ae`).

## Cells against the floors (node 1, 1a + 9 + 5, quiet samples)

| Cell | Floor | Before (step best, 1750Z) | 1a + 9 + 5 | Change | Met |
|---|---|---|---|---|---|
| BF16 K=2048 | ≤ 3.95e7 | 4.36e7 `4a30`, 4.27e7 `9094` | 4.185e7 (`9023`, `21ea`, `feb2`) | −3.0% | no (+5.9%) |
| BF16 K=4096 | ≤ 2.12e7 | 2.37e7 `2e7e` | 2.223e7 (`1c69`, `d2ea`) | −6.2% | no (+4.9%) |
| BF16 K=8192 | ≤ 2.14e7 | 2.38e7 `cab4` | 2.200e7 (`f9bb`, `3a45`) | −7.6% | no (+2.8%) |
| BF16 K=16384 | ≤ 2.30e7 | 2.70e7 `f010`, 2.61e7 `6c85` | 2.381e7 (`af18`, `8678`); 2.468e7 with `bf39` | −10.3% / −7.0% | no (+3.5%) |
| Packed, n ×2 / ×4 | −6% / −12% | | not measured this round | | |

With change 5 on, prove-only is already under the floor at K=4096 (2.097e7 against 2.12e7) and K=8192 (2.082e7 against
2.14e7), and 2.188e7 at K=16384 is under 2.30e7. What keeps those cells above their floors is the 6–9% between a cell and its
prove-only at K ≥ 4096 (0.5% at K=2048, where prove-only itself is 5.5% over).

## Not points, and flagged points

- **Not points:**
  - `184023-600e` (A/B K=16384 off-a): 506 stalls and 32,765 direct reclaims.
  - `185451-8184` (A/B K=2048 1a-b): 18,742 and 9,545,087.
  - `185344-7716` (change 5 K=4096 on-a): 20,914 and 10,670,501.
  - `193454-7d93` (change 5 K=16384 off-b): 343 and 13,441.
- **Flagged points** (quiet by the threshold, so they count):
  - `183451-854b` and `194138-bf39`: their sessions stalled.
  - `184130-5a21`: overlapped my build, with 99 of other tenants' cores busy.
- **The source of the pressure:** other queues' `vllm-epoch-run` jobs (48–170 GiB each) and back-to-back 192 GiB
  `commit-pack` jobs, peaking at 18:55Z.

All run ids are `r20261001-` plus the suffix shown.

## Next

- **The gap between a cell and its prove-only (6–9% at K ≥ 4096)** is now what stands between three cells and their floors.
  Next is a trace of the session boundary at K=4096 with change 5 on: where the GPU idles between proves, the verifier's
  pacing (`FC_VERIFY_AHEAD`/`FC_VERIFY_SERVERS`), and the warm session's start-up inside the window.
- **The witness stalls** (rep 0's witness waiting 0.3–1.1 s on the prebuilt host witness, in about a third of runs): find
  what delays the prebuild thread. They are what makes two samples of one cell disagree.
- **Packed cells (n ×2, n ×4):** cherry-pick `c13bf7da8` onto `cursor/flock-fp-prover-1a-9-1d95`, build, and run NVF4
  K=2048 packed with change 5 on and off.
- **Merging** needs `check` with `lean-agreement` on the branch (it touches `backends/flock/`). Not done: no PR was asked
  for.
