---
id: 20261006T0416Z-report-served-zk
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: verity
origin: served-zk
---

# served-zk: a served Pearl-C call under the hidden-tile ZK proof, the statement format's GPU cost, and the shared format

Branch `cursor/pouw-served-zk-e3fa` at `28cce8810`, stacked on #1034. Hardware: RTX PRO 6000 Blackwell Server Edition (sm_120),
vy-nebius-2, Llama-3.1-8B-Instruct. Every number here is untimed (gpu-lease without `--timed`).

## 1. A served request proved in the statement's format

Served run r20261006-023348-3018 (one request through the e2e harness, `--retain`), verifier r20261006-024956-bc28. The
commitment was computed from the retained rows in hm96-sha512 (row-seg/v1, 1 KiB segments, C-Flock's ChaCha20 salts,
frame-v3-sha512) and fixed before the draw. Drawn: call 237 (o_proj, k=n=4096), tile (a 0, b 2309), unit
`Pc8TileHidden_v1{K=4096,TM=1,TN=1,DEV='sm120'}`, 1,372,168 ANDs, k_log 24; that commitment was public.

| case | Rust `--zk` | Lean `verify --zk` |
|---|---|---|
| honest | ACCEPT (verify 1.23 s) | ACCEPT (75 s) |
| a tampered row byte | REJECT `RingSwitch(ClaimMismatch)` | REJECT "ring-switch claim 2 mismatch" |
| a commitment from another request | REJECT (opening check) | REJECT "S2/R7: the session parameters are not the verifier's" |
| output row not committed, a unit-internal bit flipped | REJECT | REJECT |

Not covered: the x→fp8-p link (the row units don't fit the VM's memory), more than one (1,1) tile, v1 binding and draw formats,
and the hiding tile's lowering through hidden_zk's development binding 'hash scratch'.

## 2. The GPU cost of serving in the statement's format

Served, decode b32 step (r20261006-035520-8ece, untimed window, served switches of r20261005-232920-9a1c, 3 reps each): Pearl-C
`-h2` 20.07/20.14/20.20 ms; `-h2` plus the statement's rows (each forward's A rows and tile rows committed once after the
whole-step replay) 22.33/22.35/22.32 ms: +2.20 ms, +10.9%. 25/25 gates, the statement gate included (roots and b‖c equal Python's
from poisoned buffers, the staged rows equal the calls' A words, the control unequal); texts and tokens identical to Pearl-C.
Smoke r20261006-035008-1187.

Microbenchmark, a projection onto the decode step's linears (m=32, 32 layers; r20261006-040316-7f4f; gates pass from 0xA5):

| variant | step ms |
|---|---|
| no hash | 14.45 |
| `-h2` in path | 20.84 |
| statement in path | 108.81 (5.2×; SHA-512 chains are latency-bound, about 300 µs a call) |
| statement on a side stream | 91.29 |
| `-h2` + statement batched after the step | 23.13 (+2.29, +11%) |
| statement instead of `-h2`, batched after the step | 19.62 (−1.22) |
| the batch alone (A rows, tiles); fp8-p rows | 2.23; 1.28 |

The earlier runs r20261006-032510-7103 and r20261006-034525-fe9c reported the in-path step at 97.8 ms: its closures ran the last
shape's commitments for every shape (fixed in `28cce8810`); their other variants agree within 0.05 ms.

With the fp8-p rows too: in addition, about 24.4 ms (+17%); instead of `-h2`, about 20.9 ms (≈ `-h2`). Instead of `-h2` needs a
ruling: seed_A is drawn from `-h2`'s A root, which is on the critical path before forming.

Prefill is a projection: the served path commits only whole-step decode replays, and prefill runs eager. Throughput at k=4096 and
k=14336: hm96-sha512 131 and 260 GB/s against frame-b3s 703 and 1218 GB/s. For an 8192-token prefill (served Pearl-C 0.455 s) that
projects to +156 ms in addition (+34%), +125 ms instead (+28%), and about +32 ms (+7%) instead if the tree finish ran at the
segment kernel's 428–459 GB/s.

In-circuit, per row (`hiding_leaf_cost.py`, sha512-row framing): 3,072 B, BLAKE3 keyed row/v2 50 compressions × 10,416 ANDs
against hm96-sha512 27 × 58,120. The 4,224 B fp8-p row costs 729,120 ANDs (BLAKE3) against 2,092,320 (hm96-sha512); the 32 B
tile row, 10,416 against 174,360. A drawn 1×1 tile unit's rows (A, B, tile) cost 1.47M ANDs (BLAKE3) against 4.71M (hm96-sha512),
beside the unit's own 1.37M. BLAKE3 keyed rows are not hiding: the key is public and there is no salt, so a low-entropy row falls
to a dictionary attack. They also aren't pinned in C-Flock or Lean.

## 3. Recommendation

Keep hm96-sha512 as the single format. Commit its rows once after each step, never in path: served decode costs +10.9% beside
`-h2` and, projected, about `-h2`'s cost instead of it. BLAKE3 rows are about 3.2× cheaper in-circuit for a drawn unit's rows, but
they are not hiding and not pinned, so they can't stand in. The open costs are prefill throughput (projected +28–34% of an
8192-token prefill), and whether the statement root may replace `-h2`'s A root as seed_A's source
(note:20261006T0233Z-draft-pouw-service-user, Question 1); the second is Daniel's ruling.

## Launching it

`research run --on vy-nebius-2 --project verity --campaign pouw --source <tree> --cwd source --declared-output 'out/*'
--env GPU_LEASE_WHO=<id> --env MODE=window [--env "LEASE=8 --wait --timed ..."] [--env "WRAP=env VY_PROVERS_CPUS=160-175
vy-provers taskset -c 160-175"] -- bash benchmarks/pouw/served_zk/zk_window.sh`. Or add `STATEMENT=build` to any `window.sh` run
with `WHOLE_STEP=1`.

D1's retained passes (28 GB) are still on node 2 at `/workspace/pouw/mvp-e2e/passes/r20261006-023348-3018`; the window's were
deleted.
