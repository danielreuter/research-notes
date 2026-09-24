---
lane: ligerito-relation-2
kind: report
created: 2026-09-23T21:40Z
status: superseded
branch: lane/ligerito-relation-2 (worktree ~/projects/verity-main-wt/ligerito-relation-2, from lane/ligerito-relation @ fbc3eef)
owns: backends/direct/ligerito/{prove.py, proof.py, run.py} (+ tests beside them)
pods: vy-ligerito-relation-2 52tgms6kjphi6k (RTX 4090 reference part, $0.74/h, created 21:44Z)
---

CHECKPOINT none (00:03Z) [superseded] by ligerito-relation-3 (coordinator)
CHECKPOINT 32e9bd59 (23:14Z) [open] 32e9bd59 gates 6/6 (4+94, 0 failures; Rust 60d9cbd 96/96) art:9d83f26d; live RO 4096 VUs 1 batch R=48, 4.22 s @ 57.8 ms RTT, verify-session 1/1 + 2/2 authenticated art:09b6908f/art:d92c73c0; next: sparse fixture for verify-rs-3, FINAL
CHECKPOINT 0db857a9 (22:53Z) [open] 0db857a9: F5 per-proof 2^-(128+log2 n) in bench; verify-session (live coins claim only after matching the verifier's session record); canonical statements (y=0 off chain ends). Gates 6/6 green @e3ad950; all-relation gates + Rust verifier running @0db857a9. Next: live session on RO (live-2c), verify-session, report table
CHECKPOINT none (22:25Z) [open] V1 fixed (cf9a63a); F12 labels (32d3d42); 4090 one-batch fit via streamed commit (abd8f5e). Gates 6/6 relations 0 failures @32d3d42 (4+90 each), fixtures on R2. fp8-ada 4096 one batch: 4090 0.566 s / 16.0 GiB, H100 0.398 s; H100 bf16-hopper 0.688 s, fp8-hopper 0.393 s. Next: live R + session, verify-rs-3 handoff
CHECKPOINT 9a3823a (22:00Z) [open] V1 fix committed cf9a63a (zero claims = Rust cover, cols from r_c; 5 must-reject forgeries); sumcheck-2 1fbbe86 merged 64d…; all-relation gates running on L40S; 4090 bootstrapping
# ligerito-relation-2 — V1 fix, one-batch 4096-VU numbers on LGSC0003, live coins, honest labels

CHECKPOINT fbc3eef (21:45Z) open — worktree created at fbc3eef, predecessor's V1 patch applied (uncommitted) + redteam_v1_test.py copied; 4090 pod up, bootstrapping. Predecessor branch unchanged since fbc3eef (no second writer).

## Log

* 21:38Z read relaunch §0/§2, Ligerito brief §9, predecessor report, handoffs (red-team-2 V1, verify-rs-2, sumcheck-2), sumcheck-2 FINAL.
* 21:41Z found an orphan pod of the dead predecessor: `vy-ligerito-relation-dev` lkdd6gndttgewf (L40S, $1.09/h, idle, running its
  fbc3eef gates at 21:13-21:16Z: fp8-ada / fp4-nvf4 / fp8-ada --zk 80 negatives 0 failures each; its tree = the saved patch, byte-identical).
  Nothing unrecorded on it. Will terminate it (not in any brief).
* Saved patch vs verify-rs-2's corrected rule: `zero_points` copies the first claim's point `(r_i || r_c)` and overwrites row bits
  `[b, n_i)` only, so the column coordinates ARE the zero-check's `r_c` (correct); its docstring wrongly says `rho_c`. The cover differs
  from Rust's `relation::virtual_zero_claims`: non-ZK covers all of `[m, R)` (4 blocks for fp8-ada), Rust covers each run of virtual rows
  (6 blocks), both modes. Aligning Python to Rust (one rule, both modes).
* 21:48Z laptop -> pod uploads crawl (4090 in NO: ~60 KB/s; L40S ~0.4 MB/s). Changed plan: kept the orphan L40S one more hour as the
  dev/gate box (it already has the fbc3eef tree + built CUDA extensions), shipped the 4090's tree pod-to-pod from the L40S (tar | ssh,
  seconds). L40S is now listed under pods; terminates when gates + fixtures are pushed.
* 21:55Z **V1 fix committed `cf9a63a`**. What changed vs the saved patch:
  - `aligned_cover` / `zero_blocks` / `zero_points` moved to `proof.py` (numpy only; the verifier and the laptop tests import them).
    Cover = Rust's rule: each maximal run of virtual rows `[a, b)` in `[m, R)` covered by the fewest aligned power-of-two blocks,
    both ZK and non-ZK. fp8-ada (m=3577, virtual rows = one run [3577, 3777)): 6 blocks, `[3577,3578) [3578,3580) [3580,3584)
    [3584,3712) [3712,3776) [3776,3777)` (read back from the dumped proofs' `params.zero_blocks`; the row ranges in this line
    were wrong until 22:30Z) — identical to `relation::virtual_zero_claims`. The free rows `[3777, 4096)` are not
    zero-claimed (no constraint or public row reads them).
  - Column coordinates of every zero claim = the zero-check's `r_c` (copied from claim 0's point `(r_i || r_c)`; only the row bits
    are rewritten). New laptop test `zero_claims_test.py` shows the swap counterexample: a witness nonzero at (row bit j, col bit k)
    and minus at the swapped pair cancels under `(rho || rho)` coordinates and is caught under `(rho || r_c)`.
  - Prover bug the patch had (found on the L40S, `AssertionError: prover-side claim mismatch` in PCS round 2): the non-ZK path re-zeroed
    `z[virt]` AFTER the sumcheck and before `pcs_open`, so the PCS's `M1` (a view of `z`) no longer matched the committed codeword on a
    forged run. Now `z`'s committed rows are fixed once, before the commit.
  - Must-reject V1 forgeries (`run.v1_forgeries`, used by the gate and by `redteam_v1_test.py`): the sumchecks run honestly on the
    prover's `z` while the committed w is nonzero on a virtual-row class (the verifier rebuilds those rows from the claimed statement,
    which differs): (a) end rows: claimed y +1 ulp, true witness; (b) `pub:*` rows: an operand exponent bit flipped in the statement;
    (c) start/link/end rows: statement `n_vus[0] - 1`; (d) `const` + every public row: last VU of sub-batch 0 zeroed in `z`, its y
    claimed +1; (e) `next:0` row +12345 in column 5 of the committed w. (a)-(d) must reject at "PCS" (the zero claims), (e) at
    "combined final" (next rows are pinned by the shift). With `zero_blocks` monkeypatched to `[]`, (a)-(d) VERIFY — the break
    reproduced — and (e) still fails the combined final.
  - `soundness()` adds the zero-claim term only when there are zero blocks (log2(0) otherwise).
* 21:58-22:06Z **F12 honest labels `32d3d42`** (`proof.soundness_claim`): the interactive union is claimed only for live coins
  whose issuing verifier's record authenticates them; Fiat-Shamir = log2 Q + the largest round-by-round term at Q = 2^64
  (every coin incl. the query sets is FS: fp8-ada 2^-64.66 at l = 256, 2^-65.08 at 4096 VUs); local seed / replayed coin
  files = none. `bench`: `security.target` null unless the claim meets 2^-128 (`parameter_target` -128 kept),
  `achieved_log2` = the claim, `soundness_bits` only when established, `zk_mode` "none" on every NON_ZK class (the partial
  ZK description moved to `security.zk_partial`; the contract rejected "partial" there). `verify-dir` prints each coin
  kind's provenance. **Gates @32d3d42 on the L40S: 6/6 relations (fp8-ada, fp8-ada --zk, bf16-hopper, fp8-hopper,
  bf16-ampere, fp4-nvf4) 4 positives + 90 negatives, 0 failures each** — gate-report art:14f1738e (remote=1); dumps
  art:796428f9 (fp8-ada), art:c91bab2a (--zk), art:a4e95966 (bf16-hopper), art:e50e2ff5 (fp8-hopper), art:998cbafe
  (bf16-ampere), art:89063ba3 (fp4-nvf4), all fixture/v1 remote=1. FS-only subset of the fp8-ada dump copied to
  `evidence/gate_fp8-ada_l256_fs/` for verify-rs-3.
* 22:06Z 4090, fp8-ada 4096 VUs as ONE batch @32d3d42: **OOM** — z (4 GiB) + the resident round-1 codeword (8 GiB) + tree
  (2 GiB) left no room for the zero-check's 9 GiB fold table. Tried: drop the codeword after the commit (0.79-0.86 s:
  the allocator's retry) vs stream the round-1 commit (no resident codeword, the |S_1| opened rows recomputed at open, same
  bytes): 0.556 s. **`abd8f5e`**: `prove._stream_for_zero_check` streams when codeword + tree would not leave
  `ZC_BYTES_PER_CELL = 10` B/cell (sumcheck-2's measured 14.6 GB peak at 2^30 minus z) free; else pcs-fast's own rule.
  Also: `t.*` buckets now include commit_r1_stream / commit_r1_recompute / sumcheck_device (0.1-0.2 s had been
  unbucketed); **F11**: the non-ZK `pcs_verify` rejects non-canonical words in the PCS sumcheck messages and the final
  vector (`_canonical`, as the ZK path and Rust). Run files (OOM log, drop trial, the A/B = copied terminal output of
  gaps.py, weaker evidence): art:ff859e9f.
* 22:10-22:27Z **measurements @abd8f5e** (table below): 4090 fp8-ada local + live-format (LocalChallenges, no network);
  H100 80GB HBM3 (pki3hwvl5hs9bi, AP-IN-1, ~14 min, ~$0.81, terminated 22:27Z) fp8-ada local + FS, bf16-hopper, fp8-hopper.
  **Live round count now R = 48 per batch for fp8-ada / fp8-hopper (18 LGSC0003 sumcheck + 30 PCS), 50 for bf16-hopper**
  (was 86-92 with LGSC0002). L40S terminated ~22:28Z after its artifacts were on R2 (my share ~46 min, ~$0.85).
* 22:27Z **`e3ad950`**: `manifest.json` `n_proofs` (distinct statements of the job) for verify-rs-3's per-proof
  2^-(128 + log2 n) check. Handoffs: verify-rs-3 (opening layout, pins, fixture art ids:
  `lanes/verify-rs-3/20260923T2235Z-handoff-from-ligerito-relation-2.md`), live-2b/-2c (live session).
  verify-rs-3 22:35-22:55Z: all five relations + `--zk` @32d3d42, the real-size abd8f5e dumps (0.19 s each in Rust vs
  1.26 s Python) and the e3ad950 gates verify in Rust, 92/92 verdicts agree.
* 22:40Z **final gates @e3ad950 on the 4090: 6/6 relations, 4 + 90, 0 failures each** (bf16-ampere rerun after its operand
  arrays were built on the pod; the first attempt ran before the build). Coordinator: live-2b is gone, live-2c owns the
  verifiers; CZ 1x8f33k0qa2lkx terminated ~22:55Z; live-2c gave me RO `tcp://213.173.105.92:56412` (same-code
  challenge-stream server) and read-only access to its session records.
* 22:40-22:52Z **`0db857a9`**:
  - **F5**: `Prover.batch(target_log2=)` / `dims_for(target_log2=)`; `bench` sizes each of n proofs for
    2^-(128 + ceil log2 n) (tightening in 0.25-bit steps until the relation's own terms fit; the 2^-128 dims are unchanged:
    fp8-ada 2^30 |S| = 311/192/192/195/196, at 2^-129 314/193/194/195/197), `security.per_proof_target_log2`,
    `union_over = n`, job claim = per-proof claim + log2 n.
  - **Live coins, F12 closed properly**: the verdict frame only proves the round order, so the bench no longer claims the
    union from it. New `run.py verify-session D <verifier session dirs>`: per live proof, the verifier batch whose coin
    openings are the dump's; its STMT digest = `lgto-stmt|v1| sha256(params) sha256(stmt) sha256(key)`; every round's
    recorded `msg_sha256` and label = those of the proof's own absorbs (`prove.SessionReplayCoins` replays the proof and
    recomputes MSG k = BLAKE2b of the absorbs since slot k-1, as `StreamCoins` sent it); the session ACCEPTED. Only then
    the interactive union is claimed. Loopback test (own `live serve` on the 4090, 2 x 12 VUs, 2 reps): 2/2
    authenticated, per-proof 2^-129.03, job 2^-128.03; a copy of the session record with one round's msg_sha256 changed:
    that proof NOT authenticated (round 7), job claim None. Tests: `prove_test` session-replay test (the replayed
    (label, MSG) list = what the prover sent).
  - **Canonical statements** (verify-rs-3 ask 2): y must be 0 wherever the `end` mask is 0. The end constraint is
    `end · (Y − y16) = 0`, silent off the ends, so a proof MADE for a statement with a nonzero off-end word was valid:
    ligerito-verify 41570f1 (no such rule) ACCEPTS that gate negative (`neg_*_45`), Python rejects it at "statement".
    The `n_vus - 1` V1 forgery + negative now build canonical statements so they still reach the PCS / combined final.
  - `lane/verify-rs-3 @ 41570f1` built on the 4090 (rustup minimal, cargo 16 s); gates run with `--rust-verifier`.
* ~22:50Z red-team-ligerito-3: **V1 fix verdict FIXED** (all classes, all six relations; their Rust build agrees 92/92;
  zero_claims_test incl. the swapped-bit pair). New nits: R3-2 framing JSON malleable (unabsorbed), R3-3 pad-unit operand
  words not canonical; their claim that off-end y words are not malleable is wrong (see above; told them with the Rust
  evidence). LGSC0004 adoption checklist received (6 items).
* 22:58Z **`32e9bd59`**: R3-2 (`read_proof` requires the writer's exact framing bytes; laptop test with 4 re-encodings),
  R3-3 (a/b words at columns >= n_vus * steps must be 0; honest dumps: 0 in all 6 relations), gate negatives for both
  (stage "statement"); the n_vus forgeries zero the dropped VU's operand words. fp4-nvf4 gate at the tree: 4 + 94, 0
  failures; Rust disagrees only on `neg_*_45` (expected until verify-rs-3 adds rule 1). Gates 6/6 running @32e9bd59.

## Measurements (4096 VUs, 2^30 cells, ONE batch, @abd8f5e = sumcheck-2's 1fbbe86 + V1 + streamed round-1 commit)

Medians over the timed reps (window 1): local 5 reps with rep 0 an excluded warm-up; FS 3 reps likewise; live format
3 reps after a separate warm-up proof. t.total = witness -> proof bytes on device,
same boundary as the 0.845 s A100 / 1.096 s (4 x 1024) 4090 predecessor numbers. zc = the zero-check (LGSC0003 sumcheck);
coins = live rounds R per proof (18 sumcheck + PCS rounds); peak = torch max allocated; Python verify = one proof on the
pod CPU (Rust: 0.19 s per proof, verify-rs-3). All NON_ZK_PROOF_DIAGNOSTIC; the claim column is the F12 label
(`achieved_log2`): local seed = none, FS = 2^-65.08, never 2^-128.

| GPU | relation | coins | t.total | zc | witness | commit r1 | proof bytes | R | peak | Py verify | bench art | dump art |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RTX 4090 (ref part) | fp8-ada | local | **0.566 s** | 0.164 | 0.177 | 0.137 | 701,728 | 48 | 16.00 GiB | 1.24 s | art:7b299454 | art:38ee9816 |
| RTX 4090 | fp8-ada | live format (local stream) | 0.567 s | 0.166 | 0.166 | 0.137 | 702,431 | 48 | 16.00 GiB | 1.32 s | art:378cf497 | art:993330c0 |
| H100 80GB HBM3 | fp8-ada | local | **0.398 s** | 0.160 | 0.108 | 0.053 | 701,728 | 48 | 24.02 GiB | 0.91 s | art:657d09aa | art:e89d2c1c |
| H100 | fp8-ada | Fiat-Shamir | 0.397 s | 0.160 | 0.106 | 0.053 | 705,062 | 48 | 24.02 GiB | 0.91 s | art:8ab5e2c3 | art:7014c64b |
| H100 | bf16-hopper | local | **0.688 s** | 0.285 | 0.170 | 0.145 | 759,812 | 50 | 48.50 GiB | 0.86 s | art:b449f205 | art:5adab716 |
| H100 | fp8-hopper | local | **0.393 s** | 0.155 | 0.100 | 0.053 | 701,744 | 48 | 24.39 GiB | 0.90 s | art:10770174 | art:3b57ee97 |

vs predecessor @fbc3eef (LGSC0002): A100 0.845 s (zc 0.45), 4090 1.096 s as 4 x 1024 (4 proofs, ~4 x 1.2 MB, 4 x 86 rounds).
The 4090 streams its round-1 commit (16 GiB peak; resident path OOMs); the H100 keeps it resident. The 4090's zc 0.164 s
matches sumcheck-2's 0.159 s; the rest is the witness (0.17 s) and the PCS. Prover code is unchanged since abd8f5e for a
single-batch job (e3ad950..32e9bd59 touched manifests, F5 multi-batch sizing and verifier checks), so the table stands
for the tip; the live row at the tip is measured below.

### Log (cont.)
* 23:05Z **gates @32e9bd59 on the 4090 (Python + Rust): 6/6 relations, 4 positives + 94 negatives each, 0 failures.**
  Rust: verify-rs-3 `60d9cbd` (y-off-end rule; `git archive` of it built on the pod as `/workspace/vrs3b`) accepts all 6 dirs,
  96/96 manifest verdicts, no problems; the gates' own `verify_rust.json` came from 41570f1 (accepts `neg_*_45`, the known
  missing rule). gate-report art:9d83f26d (+ gates-e3ad950 / -0db857a9 logs, JSONs, Rust verdicts); dumps fixture/v1:
  fp8-ada art:4dd85136, fp8-ada --zk art:16870df5, bf16-hopper art:fc4674a7, fp8-hopper art:8b67b6b0, bf16-ampere
  art:8265d89d, fp4-nvf4 art:173734c4 (all 7 PRESERVED, verified etag-md5).
* 23:11Z **live sessions on RO** (`tcp://213.173.105.92:56412`, EU-RO-1, live-verifier@80547525ac60) from the 4090
  (EUR-NO-1) @32e9bd59, both ACCEPTED, then **`verify-session` against the verifier's own records** (read-only copy of
  `/workspace/live/sessions/<id>/*.json`, live-2c's permission):
  - fp8-ada 4096 VUs, ONE batch, 3 reps (+ the local-stream warm-up that fixes R), window 1: **R = 48 rounds**, round trip
    median 57.8 ms, **t.total 4.216 s** median (3.64-4.23; stream wait 3.60 s, i.e. ~0.62 s of prover work = the local
    0.566 s), proof 701,439 B, peak 16.00 GiB, Python verify 1.36 s, Rust 0.40 s; session `c20260923T231103Z-c8a8`;
    **1/1 authenticated → claimed 2^-128.0008** (the interactive union; the only 2^-128 claim this lane makes).
    bench art:09b6908f, dump + session record art:53ab06f7.
  - F5 over the network: 4096 VUs as 2 x 2048, 2 reps: R = 47, each proof sized for 2^-129 (|S_1| 315 at 2^29),
    t.total 8.59 s for the 2 serial batches, 1,297,646 B, peak 12.3 GiB; session `c20260923T231131Z-da81`; **2/2
    authenticated → per-proof 2^-129.02, job 2^-128.02**. bench art:d92c73c0, dump art:6ff439a8.
  At 58 ms RTT a batch costs R x RTT ≈ 2.8 s of round trips + verifier turnaround (3.6 s total wait) vs 0.6 s of proving:
  live latency is the network's; window > 1 overlaps batches, not rounds. LGSC0004 lean (15 sumcheck coins) would save 3.
* 23:15Z verify-rs-3's ask: `pcs_sparse_fixture.py` (their tool, my proto/pcs.py @32e9bd59, 4090): 2 cases, 5 negatives each
  -> `lanes/verify-rs-3/evidence/pcs_sparse_fixture_lr2-32e9bd59.json` (sha256 54d42cac…).
