---
id: 20261004T2202Z-report-relay-internal-pouw-new-crypto-ncp-falsify
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw/new-crypto/ncp-falsify.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw/new-crypto/ncp-falsify.md`, sha256 `14396339e57ab74b6b109d4271a756016e0af540747ae4747a053837e60c7371`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# NCP falsification benchmark (worker ncp-falsify, 28 Sep 2026)

## Results (RTX 4090, (m, k, n) = (4096, 4096, 4096), d = 16, T = k/16 = 256 steps per block)

W1 ratio = the route's W1 cost ÷ the honest transcript's, per warp tile (32 × 32 outputs). "Definition" counts what the route must execute (tensor-core instructions at their full shape, INT32 and dp4a at 16 per lane). "SASS" is the compiled kernel: static SASS × loop trip counts, every instruction class priced by problem-statement §3.1, which includes the address and loop INT32 the definition leaves out. Wall ratio is the median of 10 runs against the honest kernel on the same P; the long-k shape (256, 65536, 256) is in parentheses. Digest match means the route reproduced the honest kernel's digest of all 3k/16 checked words at every position. It held in every one of 171 cases across the three runs. The honest digest also equals the CPU reference at 4096³ and at every small and long-k shape.

| # | Route | P | W1 ratio, definition | W1 ratio, SASS | below 0.995? | Wall ratio | Digest | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | honest: zero-input stacked GEMM, `mma.sync` m16n8k16 s8, every accumulator read each step | admissible | 1 | 1 | — | 1 (1.92 ms, 215 int8 TOPS) | = CPU | baseline |
| 1 | skip the final value (positive control) | admissible | 0.99870 = 1 − d/(3k) | 0.99677 | no; yes at k = 1,024 (0.99479) | 1.03 (0.97) | yes | control fires exactly; inside 0.5% only for k ≥ 1,067 |
| 2 | block 3 = C − c1 − c2 − W, W by m16n8k32 (inner 2d) | admissible | 1.664 | 2.052 | no | 44.8 (6.8) | yes | no gain |
| 3 | block 3 by one three-input add (W = 0) | step-preserving (bad P) | 1.000 | 1.165 | no | 47.1 (6.8) | yes | no gain: IADD3 costs one IMMA share per word |
| 3′ | FP32 adds on subnormal bit patterns (analytic, not run) | — | step involution 0.50; step-preserving 1.00; admissible: no one-add relation exists | — | admissible: no | — | — | not applicable to admissible P |
| 4 | Strassen, one level per step (k8 halves padded to k16) | admissible | 3.250 | 3.382 | no | 2.44 (5.10) | yes | no gain |
| 4′ | Karatsuba across blocks (analytic) | admissible | 1.000 | — | no | — | — | the honest route already is it |
| 5 | int4 limbs, two signed limbs a side, m16n8k32 s4 | admissible | 5.000 (tensor core alone 3.000) | 4.939 | no | 4.08 (7.31) | yes | no gain; a 3-product limb Karatsuba still costs ≥ 1.5 on the tensor core alone |
| 6 | mixed tensor core + dp4a (1/16 of step MMAs moved to dp4a) | admissible | 1.1875 | 1.185 | no | 0.85 (1.58) | yes | wall-time win, W1 loss |
| 7a | bad P: step reversal (NA1) | reversal | 0.500 | 0.711 | yes | 32.6 (5.5) | yes | control fires |
| 7b | bad P: step-aligned involution (N1) | step involution | 0.665 | 0.747 | yes | 22.2 (3.8) | yes | control fires (0.50 with FP32 subtraction) |
| 7c | bad P: involution passing the step rules (P2-1) | rule-passing involution | 0.99740 = 1 − 2d/(3k) | 1.00342 | no; yes at k = 1,024 (0.98958 / 0.99212) | 0.97 (0.98) | yes | control fires exactly |

Long k (k = 65,536, T = 4,096): the same ordering. Skip-final gives 0.99992 by definition (1.00001 on SASS), cross 1.667 / 2.091, Strassen 3.25 / 3.46, int4 5.00 / 5.07, mixed 1.19 / 1.19, P2-1 0.99984 / 1.0074, reversal 0.50 / 0.70, step involution 0.667 / 0.743.

**Read.** Nothing falsifies TT_NCP(0.5%). The cheapest admissible-P route is the free final value, 1 − d/(3k) = 0.99870 at k = 4096 and 0.99992 at k = 65,536. That is inside the 0.5% for every k ≥ 1,067. At k = 1,024 it is 0.99479, so TT_NCP(0.5%) needs k ≥ 2,048 among powers of two. Every other admissible route costs more than honest, for one structural reason. Under §3.1 a word derived by one INT32 op costs 16 units, exactly its share of an m16n8k16 (2048 ÷ 128). So only copies, zeros, and single FP32 adds (8 units) can undercut honest. For admissible P, no checked word except the final is a linear combination of other checked words: the CPU relation search found none up to k = 65,536. Block 3 therefore needs fresh products. Through W_τ those cost 2d per step, against honest's d, because each rank-1 term E_1[:, i]·F_1[q(i), :] enters and leaves W at different steps once π(S) ∩ S = ∅. Strassen and int4 limbs lose to the IMMA shape granularity, and dp4a loses to its price (4 MACs for 16 units). All the positive controls fire: skip-final and P2-1 hit their predicted d/(3k) and 2d/(3k) exactly, and reversal (0.50) and step involution (0.665) are far below 0.995. For the step involution, the red team's ~52% of free words becomes 33% of W1. Its block 3 is zero, but block 2 = c1_final − c1_s costs one INT32 subtract per word, the same price as the IMMA. An exact FP32 subtraction would make it 0.50. Wall time is a separate axis. Routes that store words are bound by memory traffic to scratch (22–47× slower at 4096³). The mixed route is 15% faster than this honest kernel, which runs at about a third of dense int8 peak, while costing 19% more W1.

### W1 cost by instruction class (SASS × trips, per warp tile, k = 4096)

Prices: IMMA m16n8k16 s8 2048, m16n8k32 s8 4096, m16n8k32 s4 2048, INT32 and dp4a 512, uniform 16; moves, loads, stores, shuffles and the fold IMAD are free.

| route | IMMA k16 s8 | IMMA k32 s8 | IMMA k32 s4 | INT32 | dp4a | uniform | units | ratio |
|---|---|---|---|---|---|---|---|---|
| honest | 6,144 | 0 | 0 | 2,029 | 0 | 0 | 13.62 M | 1.0000 |
| skipfinal | 6,136 | 0 | 0 | 1,969 | 0 | 192 | 13.58 M | 0.9968 |
| cross | 4,096 | 2,040 | 0 | 21,849 | 0 | 1,217 | 27.95 M | 2.0519 |
| steppres | 4,096 | 0 | 0 | 14,583 | 0 | 1,086 | 15.87 M | 1.1652 |
| strassen | 10,752 | 0 | 0 | 46,889 | 0 | 2,307 | 46.06 M | 3.3817 |
| int4 | 0 | 0 | 18,432 | 57,634 | 0 | 1,537 | 67.28 M | 4.9393 |
| mixed | 5,760 | 0 | 0 | 2,350 | 6,144 | 0 | 16.15 M | 1.1853 |
| rev | 3,072 | 0 | 0 | 6,604 | 0 | 653 | 9.68 M | 0.7109 |
| stepinv | 2,048 | 0 | 0 | 11,662 | 0 | 1,021 | 10.18 M | 0.7474 |
| inv | 6,128 | 0 | 0 | 2,178 | 0 | 190 | 13.67 M | 1.0034 |

The honest kernel's 2,029 INT32 per tile are fixed digest and address work (7.6% of its cost). The SASS ratio of a route that removes IMMAs is therefore slightly above its definition ratio.

## CPU relation search, scaled (done)

`relsearch.py` is the red team's search (`red-team-ncp.py` `analyse`: a zero or a copy is free, one FP32 add costs 8, shared step increments are counted). It replaces each k×k matrix M_t with two random bilinear sketches uᵀ·M_t·v mod 2^31 − 1, computed in O(k) per step. The false-match probability is about 2^-62 per comparison. At k = 128 it reproduces the red team's table exactly (generic 4.2%, reversal 50%, adjacent swap 29.2%, step involution 52.1%, rule-passing involution 8.3%, shift by 24 4.2%).

| k | P | rules (disjoint, not a step, P² ≠ I) | checked words N | free | one-add | shared increments | saving | d/(3k) |
|---|---|---|---|---|---|---|---|---|
| 1,024 | admissible, 3 draws | yes, yes, yes | 192 | 1 (the final) | 0 | 0 | 0.521% | 0.521% |
| 4,096 | admissible, 3 draws | yes, yes, yes | 768 | 1 | 0 | 0 | 0.130% | 0.130% |
| 16,384 | admissible | yes, yes, yes | 3,072 | 1 | 0 | 0 | 0.033% | 0.033% |
| 65,536 | admissible | yes, yes, yes | 12,288 | 1 | 0 | 0 | 0.0081% | 0.0081% |
| 1,024 to 65,536 | shift by 24 (Lean witness) | yes, yes, yes | | 1 | 0 | 0 | d/(3k) | |
| 1,024 to 65,536 | step reversal | yes, no, no | | 3T/2 | 0 | all | 50.0% | |
| 1,024 / 4,096 | adjacent-step swap | yes, no, no | | T/2 + 1 | T/2 | all | 25.5% / 25.1% | |
| 1,024 to 65,536 | step-aligned involution | no, no, no | | T + 1 | T − 1 | 2T | 50.26% to 50.004% | |
| 1,024 to 16,384 | step-preserving, not an involution | no, no, yes | | 1 | 0 | 0 | d/(3k) | |
| 1,024 to 16,384 | random involution passing the step rules | yes, yes, no | | 2 (end of block 2, final) | 0 | 0 | 2d/(3k) | |

"Checked words N" counts per output position (3k/16). Run output: `code/pouw-ncp-falsify/runs/relsearch-cpu.txt`.

## Method

- **Transcript.** Zero input. E_1 and F_1 are uniform on [−31, 32] from splitmix64, and P comes from `make_perm`: admissible P is a pseudo-random permutation repaired until π(S) ∩ S = ∅, then checked for "not a step" and P² ≠ I; the bad P kinds are built directly. L = [E_1 | E_1·P | −(E_1 + E_1·P)] and R = [F_1 ; −P·F_1 ; F_1 − P·F_1]. The checked words are the running sums mod 2^32 after every 16-deep step, block-major. Final value A·B = 0.
- **Digest.** Per position, h ← h·0x9E3779B1 + v over the 3k/16 checked words in order: one IMAD per word, the W1-free hash feed, identified in SASS by its immediate. The digest is then the sum over positions of mix64(((row·n + col) ≪ 32) | h) mod 2^64. A C++ CPU reference (OpenMP) computes the same digest.
- **Kernels** (`code/pouw-ncp-falsify/ncp.cu`). There is one persistent kernel per route. The warp tile is 32 × 32 (2 × 4 m16n8k16 tiles), with 4 warps per block. Operands are tile-packed so that a warp loads a 4-step group with 8 `LDG.128`. Every route materializes each checked word in a register before folding it. Routes that reuse words keep them in a per-thread scratch in global memory (layout step, thread, 8 × int4, so offsets within a step are immediates); loads and stores are W1-free because the addresses are public. Algebra per route: cross and step-preserving use c3_τ = (c1_final + c2_final) − c1_τ − c2_τ − W_τ, with W_τ = Σ (E1_S·F2_S + E2_S·F1_S) from one m16n8k32 over [−E1_S | −E2_S]·[F2_S ; F1_S]. Reversal uses c2_s = c1_(T−2−s), with block 3 symmetric about T/2. Step involution uses c2_s = c1_final − c1_s, with block 3 zero. P2-1 uses end of block 2 = 0. Strassen uses 7 of 8 half-k products per 32 × 16 sub-tile. int4 uses x = 16·hi + lo, lo ∈ [−8, 7], giving three accumulators recombined each step. Mixed moves tile ni = 3 of every fourth step to 32 `dp4a` after shuffles.
- **Correctness.** Every route runs against the honest digest on the same P at every shape. The honest digest is checked against the CPU reference at (64, 256, 64), (128, 1024, 128), (256, 1024, 256), (256, 65536, 256) and the 4096³ admissible transcript. `emulate.py` (numpy) checks each route's word algebra independently.
- **W1 cost.** `sass_w1.py` classifies every SASS instruction (IMMA by shape and type; IMAD by FOLDC as the free fold; IMAD.MOV, loads, stores and shuffles free; U* uniform). It finds loops by their backward branches and multiplies each inner loop by its trip count, known from the route. The per-tile count is compared with the honest kernel's. The definition count is `w1_route` in `ncp.cu`.
- **Not run.** (4096, 65536, 65536) was skipped as not cheap: the stacked R alone is 12.9 GB, the storing routes' scratch exceeds 24 GB, and the per-tile ratios are already shape-independent at this k (the long-k shape covers the k dependence). The FP32 subnormal route and the Karatsuba variants are analytic: in each case the gain is bounded by the argument in the read.

## Runs and spend

All three runs are research Attempts in campaign `pous-pouw`, project `pous`, on pod `vy-pous-pouw-fals` (`ek35i4xyv1r4u8`, RTX 4090, confirmed by `run.sh`). Sources are snapshots of `/tmp/pouw-ncp-falsify` at the listed commits.

| run | commit | phases | cases | digest match |
|---|---|---|---|---|
| `r20260928-015815-91f5` | 61c8f1a | small | 42 | 42 / 42 |
| `r20260928-020044-3c4e` | c700593 | main, ctrl, longk | 44 | 44 / 44 |
| `r20260928-020426-1fcf` | f6d71e8 (scratch layout with immediate offsets; the table's numbers) | small, main, ctrl, longk | 85 | 85 / 85 |

Spend: 0.15 USD (pod up 01:56Z to 02:07Z at 0.74 USD/h; guard `research pods guard --prefix vy-pous-pouw-fals --cap-usd 8`). The pod was terminated at 02:07Z as soon as it was idle. `research pods list` then showed no `vy-pous-pouw-fals*` pod, and the guard was stopped at 02:08Z (`guard stop`: SIGTERM, process gone).

Files: `code/pouw-ncp-falsify/` (`ncp.cu`, `run.sh`, `sass_w1.py`, `summarize.py`, `emulate.py`, `relsearch.py`), `code/pouw-ncp-falsify/runs/<run id>/` (`summary.md`, `cases.jsonl`, `w1_sass.json`; `ptxas.txt` and `gpu_name.txt` for the last run), and `code/pouw-ncp-falsify/runs/relsearch-cpu.txt`.

## Follow-up (02:15Z): control 7d on `cexR`, and the production P

Shape (4096, 4096, 4096); columns as in the main table. Both parts come from one Attempt, `r20260928-022824-819e`.

| # | Route | P | W1 ratio, definition | W1 ratio, SASS | below 0.995? | Wall ratio | Digest | Verdict |
|---|---|---|---|---|---|---|---|---|
| 7d | free words at zero input: skip the mma of every zero checkpoint c_(2k+64t), t = 1 … k/64 (the last step of each 4-step group in block 3; accumulator := 0) | `cexR` = `permMat k cexF cexSign` (`admissibleExtraIdentity`) | 0.91667 = 1 − 1/12 | 0.93107 | yes | 0.828 | yes (honest = CPU at 4096³) | control fires: the benchmark catches the counterexample |
| P | honest; routes 1 (skip final), 2 (cross), 6 (mixed) | production P, SHA-256 `42cea286…dd18` | 1; 0.99870; 1.664; 1.1875 | 1; 0.99677; 2.052; 1.185 | no, for every route | 1 (1.90 ms); 1.03; 45.3; 0.86 | yes for all four (honest = CPU at 4096³) | nothing below 0.995; same as the generic admissible P |

**7d.** R is built exactly as in `barrier.md`:
- **The permutation.** f(j) = j − j mod 64 + 32 + ((j mod 64) + 24) mod 32 when j mod 64 < 32, and j − j mod 64 + ((j mod 64) + 8) mod 32 otherwise.
- **The signs.** The sign is −1 on columns [32, 64), and R[f(j), j] = sign(j).
- **The blocks.** In the harness this gives E_2[:, j] = sign(j)·E_1[:, f(j)] and F_2 = −R·F_1, with E_3 and F_3 as before.
- **Checks.**
  - The harness's rule check passes `cexR` on all three old clauses (disjoint, not a step, R² ≠ ±I).
  - numpy confirms c = 0 exactly at steps 2T + 4t − 1 of block 3, and both sum identities.
  - The honest digest equals the CPU reference at (256, 4096, 256) and at 4096³, and the `zeros` route reproduces it at both shapes.
  - As a negative check, the same route on an admissible P fails the digest (`5c36a6f3` against `cbb365ce`).

The W1 saving is 64 of 768 checkpoints per entry, including the final one: 8.33% at every k with 64 ∣ k. The relation count's 8.46% (red-team prices) and the 8.6% in `barrier.md` also include the two one-add identities, c_(k+64) = c_(k+32) + c_32 and c_2k = 2·c_64. Under §3.1 these save nothing: one INT32 op per word costs the same as the word's IMMA share, so the route does not use them. SASS per warp tile: 5,632 IMMA k16 (honest 6,144), 2,239 INT32, 130 uniform. Wall time drops to 0.83×, since there are fewer dependent MMAs in block 3.

**Production P.** `production_p.py` is the `barrier.md` script. It asserts the permutation, the three clauses and the SHA-256, both locally and on the pod (`prodP.sha256`). The GPU ratios equal the generic admissible P's to four digits, as expected: the routes' costs do not depend on P, only the digests do.

**Relation search on the new rule ("relation-free").** `relsearch.py` now takes signed R and the kinds `prod` and `cex`. It counts exactly the new rule's cases: free = zero or ±M_a, and one-add = ±M_a ± M_b, with a = b allowed. Output: `code/pouw-ncp-falsify/runs/relsearch-prod-cex.txt`.

| R | k | rules (disjoint, not a step, R² ≠ ±I) | checkpoints N | free | one-add | shared increments | relation-free? |
|---|---|---|---|---|---|---|---|
| production P | 4,096 | yes, yes, yes | 768 | 1 (the final) | 0 | 0 | yes |
| `cexR` | 4,096 | yes, yes, yes | 768 | 64 (63 zero checkpoints + final) | 2 (τ = k + 64 and τ = 2k) | 0 | no |
| `cexR` | 1,024 | yes, yes, yes | 192 | 16 | 2 | — | no |
| `cexR` | 128 | yes, yes, yes | 24 | 2 | 3 | — | no |
| shift by 24; admissible draw | 4,096 | yes, yes, yes | 768 | 1 | 0 | 0 | yes |

The `cexR` counts (66, 18 and 5 identity checkpoints) match `barrier.md`'s fingerprint table.

**Runs and spend (this round).**
- **The Attempt.** `r20260928-022824-819e`, campaign `pous-pouw`, source commit 784eeba. The `/tmp` repo was recreated from the store copy after a VM restart; its `ncp.cu` at the parent commit is byte-identical to f6d71e8's. The run had 18 cases: 17 match, plus the intended `zeros:adm` mismatch.
- **The guard.** pid 2455, prefix `vy-pous-pouw-fals`, cap 3 USD, deadline 03:10Z. It was started at 02:16Z, before any pod existed.
- **Pods.** A first pod, `ldp0hsyiboqzhe` (community, 0.34 USD/h), refused the ssh key for 7 minutes, so I terminated it unused. The run went on `94lo9iorx5md1u` (secure, RTX 4090, 0.74 USD/h), which I terminated at 02:30:39Z once idle. `research pods list` then showed no `vy-pous-pouw-fals*` pod, and the guard was stopped at 02:31Z (SIGTERM, process gone).
- **Spend.** 0.08 USD this round, 0.23 USD across both rounds.
- **New files.** `code/pouw-ncp-falsify/production_p.py`, `code/pouw-ncp-falsify/runs/r20260928-022824-819e/` and `code/pouw-ncp-falsify/runs/relsearch-prod-cex.txt`. `ncp.cu`, `run.sh`, `sass_w1.py` and `relsearch.py` were updated in place.
