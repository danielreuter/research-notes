---
id: 20261006T1055Z-report-strong-reason-h3-sha512
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: verity
origin: pouw-h3-sha512
---

# Strong reason: served Pearl-C's device commitment (-h3) can't be SHA-512 alone; keep BLAKE3 behind a flag

For Daniel's proof-service order (top's thread 1791265836.662419), item C1: -h3 entirely on SHA-512, no split hash,
measured against v2's price. The ruling is "one hash: SHA-512". This report asks for one exception, the device-side
commitment hashing on the served path, and says why.

## The ask

Keep served Pearl-C's device commitment on keyed BLAKE3 (-h3, `pearl-c-sm120-v1-h3`) behind a scheme flag, with
SHA-512 (-h3s, `pearl-c-sm120-v1-h3s`) built, gated and selectable beside it. Everything else stays SHA-512: the
statement rows (hm96-sha512, frame-v3-sha512), the protocol's bindings (#1325), registrations, coins and draws.

## Why: the measurement

Lane pouw-h3-sha512 (bc-1beaff8e), Llama-3.1-8B served b32 decode, one RTX PRO 6000 on node 1, untimed, two GPU jobs of
three windows each (ABC then CBA), every window's arm gates passing. Runs r20261006-091845-6504 and
r20261006-100722-c6cb; step timing r20261006-100049-5377; screen and smoke r20261006-090402-0325.

| arm | step (ms, median of 6 reps) | over no-hash | x graphed FP8 |
| --- | --- | --- | --- |
| -h2 | 20.29 | +3.85 (+23.4%) | 2.65 |
| -h3 (BLAKE3) | 20.78 | +4.32 (+26.2%) | 2.72 |
| -h3s (SHA-512 throughout) | 74.91 | +58.37 (+353%) | 9.72 |

- The line was 2x -h3's overhead (8.63 ms). -h3s is 13.5x.
- Against v2's price: v2 (statement rows committed in hm96-sha512 once per step, served-zk's timed node-2 window
  r20261006-073641-19d5) costs +2.14 ms over -h2, 10.9% of served time at b32. -h3s costs +54.13 ms over -h3, 260%.
- Prefill_8192: -h3s 1201.8 ms against no-hash 389.7 ms (3.08x); -h3 453.2 against 405.0.
- -h2's numbers here agree with served-zk's timed node-2 window (+3.85 against +3.88 ms), so the untimed windows are
  not the cause.

## Why it can't be scheduled away

- One SHA-512 compression is about 4 µs on one sm_120 thread: 64-bit words on a 32-bit datapath, about 5,500
  instructions with little ILP. A BLAKE3 compression is about an eighth of that. The kernels run at that limit; the
  parallelism is across rows and segments, never within a compression.
- Forming reads each row's E_A line, so the row digests, row seeds and line keys are on the critical path. Under
  -h3s those are about 19 ms a step; under -h3 the whole commit and the lines are 3.7 ms.
- So moving A's tree (26.0 ms) and the tile hashing (44.7 ms) entirely off the critical path still leaves -h3s at
  about +19 ms over no-hash, 4.4x -h3's overhead. That is the floor of any schedule. Neither of the two remaining
  ideas (A's tree and seed_A off the main lane; side work across several calls) can go below it.

## What the exception costs

- Two hashes in the served path's trusted code, with BLAKE3's security as a named assumption beside SHA-512's.
- The verifier recomputes the drawn tiles' BLAKE3 commitments; Pearl's own FP8 scheme already does (keyed BLAKE3 in its
  seeds, lines and J, pinned by Pearl's `pearl_kw.json` vectors), so that code is not new.
- -h3s stays in the tree, gated, so the flag can flip if a faster SHA-512 kernel or a GPU with 64-bit integer
  throughput appears.

## The second candidate: Pearl's FP8 scheme

Pearl's FP8 scheme is Pearl's definition, and its keyed BLAKE3 is fixed by Pearl's own vectors (`pearl_kw.json`).
Moving it to SHA-512 would make it a different scheme than the one it names. The ask is to leave it as Pearl defines it.

## The row cap is not the reason (no retries)

`served_debit --per-input 1 --fresh-draws 32`, no retries, on B1's retained decode passes: -h3 in r20261006-130453-0637,
-h3s in r20261006-123912-90a0. Each trial is a work-weighted tile under a fresh salt drawn after the pass, replayed with
the row cap and the tile cap as `verify_run` does.

| input (k, n) | -h3 failures | -h3s failures | worst row's debit / its cap (-h3, -h3s) |
| --- | --- | --- | --- |
| (4096, 4096) | 0 / 32 | 0 / 32 | 0.351, 0.585 |
| (4096, 6144) | 0 / 32 | 0 / 32 | 0.470, 0.588 |
| (4096, 28672) | 0 / 32 | 0 / 32 | 0.593, 0.593 |
| (14336, 4096) | 0 / 32 | 0 / 32 | 0.238, 0.238 |

0 of 128 under each arm (each input below 0.128 at 95%, simultaneous over the four). The worst credited row is 1.7x
under its cap on both arms; the worst tile is at 0.048 (-h3) and 0.044 (-h3s) of the tile's cap. So both seed arms
meet "no retries" at served Llama shapes, and the choice between them is cost alone.

## Still pending at 14:00Z

- `verify_run` on the arms' retained passes: B1's (r20261006-094525-d77f) has accepted window 1 (-h2, prefill and decode,
  control REJECT) and is on -h3 and -h3s; B2's is r20261006-112217-7acb. The screen and smoke already gate -h3s on the
  GPU (r20261006-090402-0325: eager and graphed 24/24 ACCEPT, both controls REJECT).
- The lane's PR (`cursor/pouw-h3-sha512-e3fa`, stacked on #1308).

None of these can change the cost, which is the reason.
