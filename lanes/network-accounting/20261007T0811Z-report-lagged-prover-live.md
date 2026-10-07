---
id: network-accounting/20261007T0811Z-report-lagged-prover-live
campaign: network-accounting
lane: network-accounting
kind: report
status: final
repo: danielreuter/verity, branch cursor/lagged-prover-live-check-728f (0c7ff89f0), on PR #1359's head 52cfee567
origin: worker for the network-accounting lead (bc-ecea50f6), lagged-prover live check, 7 Oct 05:29–08:20Z (agent bc-b8f3ed9f)
---

# #1359's in-core lagged prover in front of live vLLM, 7 Oct

**Question.** Does PR #1359's in-core lagged online prover (52cfee567: `active.Proxy(prover=..., executor=...)`,
`LaggedChoices`, the choice made in a spawned worker after tick w·T − lag) reproduce, live, what the benchmark-only
lagged prover (#1346) gave on 6 Oct? That is: no `monitor-unavailable` from an inline `declare()`, and an online-rule
shaping p99 of about 1.4–1.6 s from window 1 on against the envelope's 3.6 s. And how many choices are unready at lag 20?

**Answer.**
- **The prover itself works live.** Of 90 online choices, 0 were unready. Choices took 21–249 ms at the median and at
  most 996 ms, inside the 2 s lag. No egress tick within 3 ticks of a choice start was more than 2.2 ms late.
- **Shaping matches 6 Oct.** p99 from window 1 on is 1.6 s under `last` (1.4 s in the repeat) and 1.6 s under
  `cover-4-1`, against the envelope's 3.6 s. Over all windows it is 2.9 s for every online cell.
- **Acceptance doesn't match 6 Oct, and the cause is a bug, not the node.**
  - `last` accepted 16 of 70 link-windows (6 Oct: 46 of 70); `cover-4-1` 47 of 70 (6 Oct: 42 of 70).
  - The envelope, run in the same lease at the same node load (mean load average 149 against `last`'s 147, on 160
    CPUs), accepted 70 of 70 with 0 late forwards.
  - Window 0's first burst of 27–34 requests is written upstream 3–725 ms past its deadline. It happened in 3 of 7
    configurations under `last` (one of them with 61 late forwards), 5 of 7 under `cover-4-1`, 3 of 4 in the repeat,
    and 0 of 7 under the envelope. The window faults `delivery-refused`, and the ingress then holds its backlog until
    window 1. This is 6 Oct's unexplained surprise 2, now located (next section).
- **`monitor-unavailable`: 4 link-windows in `last`, 4 in `cover-4-1`, 0 in the repeat. None is at a choice start.**
  They come from whole-process stalls of 0.1–0.6 s, at buckets 0–84 of a window and once at bucket 45. The envelope
  cell had no tick later than 13 ms in 21,000 ticks.
  - In #1359, `declare()` never waits: it takes a finished choice or the envelope. So the inline-declare cost of
    158–434 ms (r20261006-111646-920d) is gone.
  - That the stalls appear only in the online cells points at the same cause as the window-0 burst (next section).
    Unconfirmed.

## Window 0's late burst: Linux's fd-table growth in a proxy with a second thread

In a multithreaded process, Linux grows the fd table only after an RCU grace period (`synchronize_rcu` in
`expand_fdtable`), and it does so inside the `socket()` that needed the room. All threads share one table. #1359's
proxy has a second thread from its start: `worker()`'s `ProcessPoolExecutor` runs a manager thread in the proxy
process. The envelope's proxy has no second thread until the `Publisher` thread starts lazily, at the first window's
close.

Window 0's first burst opens about 28 upstream sockets at once, which is the first time the proxy's fd count passes
the initial 64. So every connect in the burst waits for the grace period. Local evidence, window 0 of
`plaintext/r20261003-172914-b4f8/w47-51`, burst released at 2.9 s, slack 25 ms (art:fede154333bd,
`local-window0-burst.txt`):

| proxy | burst written, ms relative to its deadline |
|---|---|
| envelope | −21.5 |
| `last` with `worker()` (#1359) | −1.6 |
| `last`, choices inline (`InlineExecutor`) | −21.1 |
| `last`, worker exists, window 0's choice never submitted | −7.5 |
| `last`, `ThreadPoolExecutor` instead | +1.8 |
| `last`, choices inline plus an idle `worker()` | +10.3 |
| envelope plus one idle dummy thread | about +2 (written 27 ms after release) |
| `last` with `worker()`, the fd table grown to 4096 before the clock | −21.9 (written 3.5 ms after release) |

Timing `open_connection` shows the same thing: with a worker, each of the burst's connects takes 16–25 ms, against 2 ms
without one. The switch interval doesn't matter (5 ms gives the same 25 ms).

Live, on a node at load 150, the same burst ran 3, 61 and 725 ms late. I expect grace periods to lengthen under load,
which would also explain the online cells' larger stalls. I didn't measure grace periods on the node.

**Fix, on my branch (not on #1359).** Commit 0c7ff89f0 adds `active.reserve_fds()`, which grows the fd table to the
open-files limit (at most 65,536) in `Proxy.__init__`, before the clock starts. It comes with a test against
`/proc/self/status` `FDSize`; the certifier and network_traces suites pass (178). Locally it removes the late burst:
−21.9 ms, and 0 late forwards in 2 windows. It is untested live: the GPU budget was spent.

## Other things the live run showed

- **The wire is a window short after an overrun, while later windows are still accepted.** `last`, configuration
  `plaintext/r20261003-180117-4455/w0-7`: a 128 ms stall in window 2 left the peer's link backlog above 4 buckets. The
  proxy skips writing a row while the backlog exceeds 4 buckets (`active.py`, `if backlog <= 4 * bucket_bytes`,
  line 397 at 52cfee567). From then on, the bytes are a bucket behind the records.
  - The peer hashed 6 of 7 windows, and the wire differs in windows 2–6. Windows 4–6 were accepted on their records,
    so `wire_is_the_records` is False.
  - Only the window of the skipped write faults. The code is the same on `main`, so this predates #1359.
- **Online cells' whole-process stalls, none at a choice start.**
  - `last`: 584, 614, 133, 135, 128, 120, 108 and 100 ms.
  - `cover-4-1`: 169 ms, at bucket 0 of window 4.
  - The `last` repeat: one stall growing from 172 ms to 1.7 s near its last window's end.
- **The worker's choice times vary under load:** 996 ms at most under `cover-4-1`, against 250 ms typical. Still
  inside the lag.

## Setup

- One job, r20261007-053837-fb89: `research run --queue --on vy-nebius-1 --gpus 1 --preemptible --max-min 148`.
  `benchmarks/network_traces/active_live_cells.sh` (13d991808) ran the cells back to back in one lease, each with its
  own vLLM. The CPUs were a 16-core half of 96–127: 8 cores for vLLM, 8 for the harness. Every cell ran at `--nice -20`
  with `--seed 0`.
- Inputs: 6 Oct's exactly. Calibration sha256 2e628d76…, trace `lease-b` sha256 5814f8d2…, the 7 configurations
  `plaintext/r20261003-*` (35 windows), T = 600 buckets of 100 ms, Σ_sync 16 δ × 8 ρ, slack 25 ms, `--prover-lag 20`.
  Model `unsloth/Meta-Llama-3.1-8B-Instruct`.
- The `last` repeat is a rerun with the same arguments: `--seed` changes only the bits and covert senders. The job's
  budget let it run 4 of the 7 configurations (20 windows).
- The GPU lease waited 5 min at the start. A TP8 Qwen3-235B load-test pod held all 8 GPUs of node 1 until the pool
  holder preempted it. Lease held 05:44–08:01Z: 2.29 GPU-h.
- Analysis: `analyze.py` and `detail.py` in art:fede154333bd. Its shaping, late-forward and acceptance numbers
  reproduce 6 Oct's table for r20261006-051921-d3e7 exactly.

## Table

A link-window is one window of one link (egress or ingress) of one configuration. Raw and committed verdicts agreed in
every cell. Late forwards: forwards past their deadline / all forwards. Load: the node's 1-minute load average over
the cell, mean (min–max), on 160 CPUs.

| cell | run | link-windows | accepted raw / committed | violations | unready / choices | choose ms p50 / max | tick max ms (egress / ingress) | shaping p50 / p99 ms | from window 1 p50 / p99 ms | late forwards | load | GPU-h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| envelope | r20261007-053837-fb89 `out/envelope` | 70 | 70 / 70 | none | – | – | 4.8 / 13.0 | 2200 / 3600 | 2200 / 3600 | 0 / 33040 | 149 (35–267) | 0.65 |
| last (lag 20) | r20261007-053837-fb89 `out/last` | 70 | 16 / 16 | delivery-refused 45 (22 egress, 23 ingress), mismatch 5, monitor-unavailable 4 | 0 / 35 | 21 / 467 | 614 / 584 | 600 / 2900 | 600 / 1600 | 286 / 12062 | 147 (83–238) | 0.63 |
| cover-4-1 (lag 20) | r20261007-053837-fb89 `out/cover-4-1` | 70 | 47 / 47 | delivery-refused 16, mismatch 3, monitor-unavailable 4 | 0 / 35 | 249 / 996 | 169 / 169 | 800 / 2900 | 800 / 1600 | 160 / 24637 | 128 (60–260) | 0.64 |
| last (lag 20), repeat, 4 configurations | r20261007-053837-fb89 `out/last-rep` | 40 | 20 / 20 | delivery-refused 14, mismatch 6 | 0 / 20 | 233 / 332 | 1669 / 1998 | 600 / 2900 | 600 / 1400 | 93 / 14284 | 70 (24–177) | 0.37 |

6 Oct, for comparison (note:network-accounting/20261006T1201Z-report-live-online-sync-sweep):

| cell | run | accepted | violations | from window 1 p99 ms | tick max ms |
|---|---|---|---|---|---|
| envelope (nice −20) | r20261006-042805-434a | 67 / 70 | delivery-refused 2, monitor-unavailable 1 | 3600 | 36 |
| last (lag 20) | r20261006-051921-d3e7 | 46 / 70 | delivery-refused 16, mismatch 8 | 1400 | 796 |
| cover-4-1 (lag 20) | r20261006-052414-7554 | 42 / 70 | delivery-refused 26, mismatch 2 | 1600 | 646 |

Every mismatch in the 7 Oct cells is an honest online miss: `mismatches_from_late_frames` equals `mismatches` in every
cell.

Window-0 late forwards per configuration, from `detail.txt`:
- envelope: 0 in all 7.
- `last`: 28, 28, 1, 61, 7, 2, 3.
- `cover-4-1`: 28, 28, 28, 27, 0, 0, 34.
- The repeat: 0, 28, 28, 27.

## Accounting

- 1 job, 2.29 GPU-h (lease 05:44–08:01Z), preserved: run record art:e2f757f3fa06.
- Evidence art:fede154333bd: the analysis JSON and scripts, and the local experiments.
- The run carries the `question` label, set by network-accounting.
- No PR opened. Branch `cursor/lagged-prover-live-check-728f`:
  - 13d991808: the cells driver.
  - 0c7ff89f0: the proposed `reserve_fds` fix to core `active.py`, for the lead to take into #1359 or not.
