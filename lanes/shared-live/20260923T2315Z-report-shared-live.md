---
lane: shared-live
kind: report
created: 2026-09-23T23:15Z
status: open
---

CHECKPOINT fe0c4f48 (23:27Z) [open] G3 fix fe0c4f48: +shared pair gets G AND H coins from the live verifier (H on wire idx i+2^30, F in G's TESTS, H slot1 gated on G's TESTS); first live ZK p4 session on 4090 hinjpqggt7riic: 13/13 pairs ACCEPTED by Rust w/ own coins both sides (batch 26 proofs 2^-128.66); running G3 negative + sequential live
# shared-live — `+shared` (tile64 G/H pair) with a LIVE verifier supplying every coin, ZK, 4090 measurement

Brief: coordinator `20260923T2100Z-brief-relaunch.md` §0/§3 + the lane message (G3 fix, ZK, 4090 local/live bare vs shared, stretch
LogUp range cut). Worktree `~/projects/verity-main-wt/shared-live`, branch `lane/shared-live` @ 453d7cf4 (share-logup-3 FINAL).

## Log
* 23:13Z read brief §0/§3, share-logup-3 FINAL, red-team-leaf-2 G3, red-team-leaf-3 G3 PARTIAL, live-2c FINAL + RUNBOOK.
* 23:14Z worktree at 453d7cf4; merged `lane/live-2c` 54e748f6 -> e8cf00f9: **no conflicts** (live-2c touched live.py, live_serve.sh,
  live_test.py, rtt_matrix.py, run.py, vu.py; share-logup-3 touched run.py in another hunk). Pod: creating vy-shared-live (4090, EU-RO-1).
* 23:14Z pod **vy-shared-live = RunPod hinjpqggt7riic** (RTX 4090 reference part, EU-RO-1, 40 host cores), bootstrapped with qol's
  `pod_bootstrap.sh` (RELS=fp8-ada,bf16-hopper TILE64=fp8-ada,bf16-hopper) in ~4 min: BOOTSTRAP_OK.
* 23:21Z **fe0c4f48 the G3 fix** (live.py / relchain.py / protocol.py; no system, statement or proof format change):
  - wire: a `+shared` session says HELLO `pair: true` + `system_h_bytes` (system.bin of G then of H). Per sub-batch i the verifier
    commits TWO fresh coin sets before anything of i: G on wire index i, H on i + 2^30 (`live.PAIR_H`).
  - G's TESTS i carries the fingerprint message F as a 5th array (`protocol._prove_stages` hands F to a live source via
    `provide_fp` right before open2; a local `Coins` has no such hook, so the local path is unchanged). The verifier opens H's
    slot 1 only after ROOT_H i AND G's TESTS i are in: rho (G's slot-1 coin, the fingerprint challenge that binds G to H) and F
    -- H's statement values -- are fixed before any coin of H is known; H's slot 2 after TESTS_H.
  - PROOF i = G's bytes + H's bytes (`meta.pair_bytes`); the verifier checks BOTH transcripts' coins/commitments, roots, test
    messages (+ G's F against the one sent before slot 2), writes sub_NN.{stmt,proof,hproof,coins,hcoins} + system_h.bin, and
    runs `ligero-verify verify --system-h --proof-h --coins-h` per pair and `batch --system-h` at END.
  - prover: `SharedHashedRunner._coins_h_for`: when G's source is live, H's is `coins.h_coins()` (the same session's second
    coin set); anything else -> ValueError "prover-sampled coins_h refused"; `BenchLive.proved` refuses a pair whose H source
    is not live. Pipelined (`_pipelined(live_statement=...)`: the v6 statement incl. multiproofs built on the pool before either
    root) and sequential (`prove_vus`: statement from `marshal_shared` before G's root) both wired.
  - negative knob: `LIVE_NEGATIVE=own-coins-h` makes H's source a `ForwardingCoins` (talks to the verifier, proves H on
    prover-sampled coins; now also for the pipelined futures).
* 23:26Z first live session (`t1`, fp8-ada+shared `--zk --mode interactive --pipeline 4`, 4096 VUs, l=16384, 1 rep, verifier
  `live serve` on the SAME pod at tcp://127.0.0.1:7000, jobs 4): **ACCEPTED 13/13 pairs**, Rust per pair "coins are this
  verifier's step-0 coins" + batch "all 26 sub-batches accepted; union bound 2^-128.66", 52 round trips (4 per pair). Cold rep:
  t.total 0.741 s, t.total_live 0.745 s.
* 23:28Z **G3 negative** (`t2`, same config, `LIVE_NEGATIVE=own-coins-h`): every pair **REJECTED by the live check: "H: coins are
  not this session's step-0 coins (replayed / prover-chosen coins)"**.
* ZK masks cover H: `SharedHashedRunner.cfg_h` = `config_for(..., zk=self.zk)`; the Rust v6 parser gives H the pair's zk flag
  and requires t_pad_h > 0 under zk (format.rs 863 / 929, check_config), mask rows `m + 6 D` and the v message (format.rs 808,
  1011) -- a non-masked H is unparseable in a zk statement.
