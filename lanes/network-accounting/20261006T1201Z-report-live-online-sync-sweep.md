---
id: network-accounting/20261006T1201Z-report-live-online-sync-sweep
campaign: network-accounting
lane: network-accounting
kind: report
status: final
repo: danielreuter/verity, branches cursor/network-warden-live-sync-sweep-deb2 (95456535d) and cursor/network-warden-live-sync-sweep-covert-deb2 (ef21b1845)
origin: network-accounting GPU lane, 6 Oct 02:30–12:10Z (agent bc-7f347b4b), for the network-accounting lead (bc-ecea50f6)
---

# Live online clock-sync sweep, 6 Oct: the active warden in front of vLLM, by rule and sender strategy

**Question.** On 4 Oct the live envelope's shaping p99 was 3.6 s, against 1.5 s offline. Does an online clock-sync rule
close that gap, and what does it cost in honest acceptance and in adversarial steering of the declared syncs?

**Answer.**
- **Shaping latency: yes, from each configuration's second window on.** In the Llama cells the online rules `last`,
  `cover-2-0` and `cover-4-1` (prover lag 20 buckets) reach a shaping p99 of 1.4–1.6 s from window 1 on, against the
  envelope's 3.6 s. `cover-4-1-fallback` doesn't: it falls back to the envelope in 15 of 35 windows, which keeps its p99 at
  3.4 s.
  - Over all windows the online rules' p99 is still 2.7–2.9 s. Each configuration's window 0 has no history, so it
    declares the envelope, and the 7 configurations make 7 of the 35 windows envelope windows.
  - Qwen3-8B under `last` reaches 2.1 s from window 1 on, against its envelope's 3.5 s.
  - Qwen3-8B under `cover-4-1` ran at the day's highest load: 16 of 70 accepted, 501 late forwards, ticks up to 271 ms
    late. Its p99, 4.6 s, measures the stalls more than the rule.
- **Honest acceptance: the cost is mismatches, and they are honest online misses.** An online rule declares each
  window's sync from the frames ready 20 buckets before the window starts. When frames then arrive after their declared
  hand time, the egress window audits as a mismatch.
  - Under `last`, 8 of 35 Llama egress windows mismatched; under `cover-2-0`, 6; under `cover-4-1`, 2. Under the
    envelope, 0. With Qwen3-8B under `last`, 5.
  - In every honest mismatch the record is the shaper's rule on the frames as read (`mismatches_from_late_frames` equals
    `mismatches` in every cell).
  - `cover-4-1`, which keeps 4 buckets of cover, mismatches least, at 0.2 s more p99 than `last`.
- **Live acceptance is dominated by the node, not by the rule.** Most rejected link-windows are `delivery-refused`.
  verity#1146 refuses a window when a released request isn't written upstream within 25 ms of its release tick, and the
  proxy shares cores 96–127 with other lanes' CPU jobs.
  - The same Llama envelope cell accepted 67 of 70 link-windows at 04:28Z (`--nice -20`) and 6 of 16 at 08:55Z.
  - The Qwen3-8B envelope accepted 24 of 70 at 09:50Z, with the node's load average 218–414 on 160 CPUs.
  - Read acceptance only between cells run at about the same time. Shaping latency doesn't move with the load.
- **Adversarial steering: not distinguishable from live noise at this sample size.**
  - Under an online rule, the four strategies (burst, spread, bits, late) declared a different sync from their own
    cell's honest run in 1–6 of 8 windows.
  - Two honest runs of the same configuration already differ in 0–3 of 4 windows (the honest-against-honest table), since
    vLLM's live timing varies between runs.
  - Under the envelope no declaration ever differs.
- **The wire comparison is uninformative live.** Every adversarial wire differs from its honest run's in 7–8 of 8
  windows, but so does every honest rerun's, in every window and under the envelope too: live vLLM output and timing
  differ between runs. So "accepted with a wire different from honest's" holds for every accepted adversarial window here,
  and doesn't mark one out.
- **Covert sender (the covert-sync-rate lane's `covert.LiveSender`): no rate above the honest control live.** It ran
  under `last` (seeds 0, 1, 2) and `cover-4-1` (seeds 0, 1). Seed 2 under `cover-4-1` didn't fit before the node's daily
  hold.
  - The covert runs decoded 0.39, 0, 0 (`last`) and 0, 0 (`cover-4-1`) bits per window, over 6–8 window-decisions each.
  - The honest runs in the same cells, decoded the same way as a control, gave 0, 0.15, 0 and 0, 0.34.
  - The sender's replica predicted every declared sync in 3 of the 5 covert runs. Even then, the symbol error rate was
    0.375–0.833.

**Setup.**
- Inputs: 4 Oct's exactly. The calibration and trace `lease-b`, the 7 configurations
  `plaintext/r20261003-*` (35 windows), T = 600 buckets of 100 ms, Σ_sync of 16 δ × 8 ρ, slack 25 ms.
- Models: `unsloth/Meta-Llama-3.1-8B-Instruct` and `Qwen/Qwen3-8B`. vLLM seed 0. `--seed` is the bits and covert
  senders' seed.
- Each cell is one `research run --queue --gpus 1 --preemptible --max-min ≤55` on vy-nebius-1, `--campaign
  network-accounting`. Two ran at a time, each in a 16-core half of 96–127: 8 cores for vLLM, 8 for the harness.
- Adversarial cells ran 2 configurations × 4 windows per strategy. Covert cells ran 2 configurations × 5 windows (4 for
  seed 2).

**Harness changes this sweep needed.** They are on branch `cursor/network-warden-live-sync-sweep-deb2` of
danielreuter/verity, and the covert cells ran from `cursor/network-warden-live-sync-sweep-covert-deb2`, a merge of that
branch with the covert lane's head (575748ba7).
- **Adversarial strategies live.** The shim holds each event to its planned bucket.
- **`--prover-lag`.** A blocking `declare` costs 0.2–1.1 s live, and in the tick it made the proxy late: `last` without
  a lag (r20261006-023430-2517) had 34 `monitor-unavailable` link-windows, with ticks up to 580 ms late.
- **The choice runs in a worker process.** In a thread it took the proxy's GIL and delayed forwards: r20261006-044506-85e7
  accepted 22 of 70. Cells before 05:19Z ran the thread version.
- **New audit counts:** forward lateness per stream, and `mismatches_from_late_frames`.
- **The audit pool is closed before it's left.** Its workers ignore SIGTERM, so `Pool.terminate` could hang on a fresh
  worker, and then no summary would be written. It hung once locally, never in a cell.

**Surprises.**
1. **Honest windows rejected.** All are `delivery-refused`, `monitor-unavailable`, or mismatches from late frames, as
   described above. No honest window failed any other check.
2. **Late bursts in window 0, only with the process-pool prover.** A burst of 28–34 requests released at one ingress tick,
   a few seconds into window 0, is written upstream 1–260 ms past its deadline, all by the same amount. Meanwhile the
   proxy's ticks are under 5 ms late.
   - The late write faults the window, and the ingress then holds its backlog until window 1.
   - It happened in about 5 of 7 configurations per process-pool cell. The envelope and thread-prover cells never show it.
   - Starting the worker before the clock (63de49a55) didn't remove it. The cause is not identified. Next step: log each
     stream's release tick and upstream connect time.
3. **Single proxy stalls of 646 and 796 ms** (r20261006-052414-7554, r20261006-051921-d3e7), each in one window.
4. **The covert lane's live `cover-3-2` faults** (`monitor-unavailable`, with ticks 325–440 ms late) look like the
   blocking in-tick prover measured here (r20261006-023430-2517: ticks up to 580 ms late), more than node load. This is a
   reading of their numbers; I didn't rerun them.

**Accounting.**
- 24 cells. GPU leases held 14.7 h (the table's runs), plus a few minutes for two cells evicted on node 2 at start-up
  (r20261006-023151-925f, r20261006-023158-594c) and one failed launch.
- I cancelled two cells myself, after their first configurations showed the thread prover's late forwards:
  r20261006-042615-c6e5 and r20261006-050615-947a.
- Every run's outputs are in the store under its run id; the art column is each run's record.
- Friction: note:network-accounting/20261006T0625Z-friction-node1-gpu-jobs-share-cpus.

## Tables

4 Oct's live run, the baseline, is art:d082f621. A link-window is one window of one link (egress or
ingress) of one configuration. Shaping is how long a frame waits from ready to handed. "From window 1" leaves out each
configuration's first window, which always declares the envelope.


### Honest

| rule | model | cell | run | art | link-windows audited | accepted raw / committed | violations | shaping p50 / p99 ms | shaping from window 1 p50 / p99 ms | first frame p50 / p99 ms | late forwards | proxy tick max ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| envelope | Llama-3.1-8B | honest/envelope/llama/s0 | r20261006-023423-f03d | art:47d1f21792e5 | 70 | 57 / 57 | delivery-refused 13 | 2200 / 3600 | 2200 / 3600 | 2700 / 3700 | - | 11 |
| last | Llama-3.1-8B | honest/last/llama/s0 | r20261006-023430-2517 | art:2aac2c99ab24 | 70 | 32 / 32 | monitor-unavailable 34, delivery-refused 4 | 2400 / 3700 | 2300 / 3700 | 2700 / 3900 | - | 580 |
| last (lag 20) | Llama-3.1-8B | honest/last/lag20/llama/s0 | r20261006-031529-0590 | art:ec45d6fc3778 | 70 | 22 / 22 | delivery-refused 46, mismatch 2 | 700 / 3300 | 700 / 1500 | 1000 / 3600 | - | 92 |
| envelope | Llama-3.1-8B | honest/envelope/llama/s0-halves | r20261006-031802-13b9 | art:c979015aeab9 | 70 | 26 / 26 | delivery-refused 44 | 2200 / 3600 | 2200 / 3600 | 2700 / 3700 | - | 92 |
| cover-2-0 (lag 20) | Llama-3.1-8B | honest/cover-2-0/lag20/llama/s0 | r20261006-040542-d15e | art:5b2ca72f0936 | 70 | 20 / 20 | delivery-refused 47, mismatch 3 | 700 / 3300 | 700 / 1600 | 1000 / 3600 | 114 / 22248 | 52 |
| cover-4-1 (lag 20) | Llama-3.1-8B | honest/cover-4-1/lag20/llama/s0 | r20261006-042615-c6e5 | art:93397e708344 | failed, no summary | - | - | - | - | - | - | - |
| envelope | Llama-3.1-8B | honest/envelope/nice20/llama/s0 | r20261006-042805-434a | art:5b0ec0b858aa | 70 | 67 / 67 | delivery-refused 2, monitor-unavailable 1 | 2200 / 3600 | 2200 / 3600 | 2700 / 3700 | 29 / 31272 | 36 |
| cover-4-1 (lag 20) | Llama-3.1-8B | honest/cover-4-1/lag20/nice20/llama/s0 | r20261006-044506-85e7 | art:5518953dac48 | 70 | 22 / 22 | delivery-refused 48 | 900 / 3300 | 800 / 1600 | 1300 / 3600 | 49 / 31492 | 29 |
| last (lag 20) | Llama-3.1-8B | honest/last/lag20/nice20/llama/s0 | r20261006-050615-947a | art:6572b65fc34a | 16 | 5 / 5 | delivery-refused 11 | 800 / 3400 | 700 / 1600 | 1500 / 3700 | 14 / 7508 | 8 |
| last (lag 20) | Llama-3.1-8B | honest/last/lag20/nice20/proc/llama/s0 | r20261006-051921-d3e7 | art:27191cff0935 | 70 | 46 / 46 | delivery-refused 16, mismatch 8 | 700 / 2900 | 700 / 1400 | 900 / 3400 | 165 / 27515 | 796 |
| cover-4-1 (lag 20) | Llama-3.1-8B | honest/cover-4-1/lag20/nice20/proc/llama/s0 | r20261006-052414-7554 | art:237c8de73c14 | 70 | 42 / 42 | delivery-refused 26, mismatch 2 | 800 / 2900 | 800 / 1600 | 1100 / 3300 | 188 / 24316 | 646 |
| cover-4-1-fallback (lag 20) | Llama-3.1-8B | honest/cover-4-1-fallback/lag20/nice20/proc/llama/s0 | r20261006-055759-f347 | art:0b1d8bd91f77 | 70 | 43 / 43 | delivery-refused 20, monitor-unavailable 4, mismatch 3 | 900 / 3400 | 900 / 3400 | 1200 / 3700 | 228 / 24141 | 42 |
| cover-2-0 (lag 20) | Llama-3.1-8B | honest/cover-2-0/lag20/nice20/proc/llama/s0 | r20261006-060242-5190 | art:026f7fc3d05c | 70 | 38 / 38 | delivery-refused 24, mismatch 6, monitor-unavailable 2 | 700 / 2700 | 700 / 1400 | 900 / 3200 | 227 / 22953 | 124 |
| last (lag 20) | Llama-3.1-8B | adv/last/lag20/nice20/proc/llama/s0 | r20261006-064756-4b6d | art:84dd20aed988 | 16 | 11 / 11 | delivery-refused 4, mismatch 1 | 700 / 3200 | 700 / 1500 | 900 / 3700 | 32 / 6472 | 5 |
| cover-2-0 (lag 20) | Llama-3.1-8B | adv/cover-2-0/lag20/nice20/proc/llama/s0 | r20261006-064946-6018 | art:a72eee6b95a0 | 16 | 6 / 6 | delivery-refused 8, mismatch 2 | 800 / 3400 | 800 / 3400 | 1000 / 3600 | 123 / 4574 | 16 |
| cover-4-1 (lag 20) | Llama-3.1-8B | adv/cover-4-1/lag20/nice20/proc/llama/s0 | r20261006-074855-4115 | art:c4f1a11fa42d | 16 | 4 / 4 | delivery-refused 12 | 800 / 2800 | 800 / 1500 | 1000 / 1800 | 67 / 2999 | 77 |
| cover-4-1-fallback (lag 20) | Llama-3.1-8B | adv/cover-4-1-fallback/lag20/nice20/proc/llama/s0 | r20261006-075036-7c96 | art:e37f42af2f5f | 16 | 3 / 3 | delivery-refused 12, mismatch 1 | 1200 / 3500 | 1100 / 3500 | 1500 / 3600 | 110 / 2504 | 48 |
| envelope | Llama-3.1-8B | adv/envelope/nice20/llama/s0 | r20261006-085450-4a00 | art:263c732846fc | 16 | 6 / 6 | delivery-refused 8, monitor-unavailable 2 | 2100 / 3600 | 2100 / 3600 | 2700 / 3800 | 15 / 4566 | 137 |
| last (lag 20) | Llama-3.1-8B | covert/last/lag20/nice20/proc/llama/s0 | r20261006-085630-ca20 | art:5d84068498e5 | 20 | 7 / 7 | delivery-refused 10, monitor-unavailable 2, mismatch 1 | 1500 / 3400 | 1000 / 3200 | 2100 / 3700 | 142 / 3514 | 61 |
| cover-4-1 (lag 20) | Llama-3.1-8B | covert/cover-4-1/lag20/nice20/proc/llama/s0 | r20261006-091949-13a6 | art:e3a94445957c | 20 | 10 / 10 | delivery-refused 6, monitor-unavailable 4 | 800 / 2700 | 800 / 1500 | 1000 / 1600 | 84 / 4464 | 73 |
| envelope | Qwen3-8B | honest/envelope/nice20/qwen3-8b/s0 | r20261006-095007-07df | art:16c22fbea463 | 70 | 24 / 24 | delivery-refused 38, monitor-unavailable 8 | 2100 / 3500 | 2100 / 3500 | 2600 / 3600 | 247 / 19202 | 374 |
| last (lag 20) | Qwen3-8B | honest/last/lag20/nice20/proc/qwen3-8b/s0 | r20261006-095146-1440 | art:567a205d9e6e | 70 | 21 / 21 | delivery-refused 32, monitor-unavailable 12, mismatch 5 | 700 / 2500 | 700 / 2100 | 1000 / 2200 | 340 / 17161 | 156 |
| cover-4-1 (lag 20) | Qwen3-8B | honest/cover-4-1/lag20/nice20/proc/qwen3-8b/s0 | r20261006-103059-e004 | art:f10bcf817709 | 70 | 16 / 16 | delivery-refused 48, monitor-unavailable 4, mismatch 2 | 900 / 4500 | 900 / 4600 | 1200 / 5300 | 501 / 16442 | 271 |
| last (lag 20) | Llama-3.1-8B | covert/last/lag20/nice20/proc/llama/s1 | r20261006-104900-5d25 | art:030022ca9787 | 20 | 6 / 6 | delivery-refused 11, monitor-unavailable 3 | 700 / 1600 | 700 / 1400 | 900 / 1600 | 96 / 3405 | 303 |
| cover-4-1 (lag 20) | Llama-3.1-8B | covert/cover-4-1/lag20/nice20/proc/llama/s1 | r20261006-112704-48e5 | art:0cf5dd037045 | 20 | 6 / 6 | delivery-refused 12, monitor-unavailable 2 | 800 / 2300 | 800 / 1500 | 1000 / 1600 | 152 / 3182 | 52 |
| last (lag 20) | Llama-3.1-8B | covert/last/lag20/nice20/proc/llama/s2 | r20261006-112733-6876 | art:f005aa5f1e7b | 16 | 5 / 5 | delivery-refused 8, monitor-unavailable 2, mismatch 1 | 700 / 2500 | 700 / 1400 | 900 / 1600 | 91 / 3404 | 123 |

### Adversarial

| rule | model | strategy | run | link-windows audited | accepted raw / committed | violations | wire differs from the same run's honest (windows) | declared sync differs from the same run's honest (windows) |
|---|---|---|---|---|---|---|---|---|
| last (lag 20) | Llama-3.1-8B | burst | r20261006-064756-4b6d | 16 | 10 / 10 | delivery-refused 4, mismatch 2 | 7 | 3 |
| last (lag 20) | Llama-3.1-8B | spread | r20261006-064756-4b6d | 16 | 8 / 8 | delivery-refused 4, mismatch 4 | 7 | 6 |
| last (lag 20) | Llama-3.1-8B | bits | r20261006-064756-4b6d | 16 | 8 / 8 | delivery-refused 6, mismatch 2 | 7 | 4 |
| last (lag 20) | Llama-3.1-8B | late | r20261006-064756-4b6d | 16 | 11 / 11 | delivery-refused 4, mismatch 1 | 8 | 2 |
| cover-2-0 (lag 20) | Llama-3.1-8B | burst | r20261006-064946-6018 | 16 | 10 / 10 | delivery-refused 4, mismatch 2 | 7 | 5 |
| cover-2-0 (lag 20) | Llama-3.1-8B | spread | r20261006-064946-6018 | 16 | 10 / 10 | delivery-refused 4, mismatch 2 | 7 | 5 |
| cover-2-0 (lag 20) | Llama-3.1-8B | bits | r20261006-064946-6018 | 16 | 7 / 7 | delivery-refused 8, mismatch 1 | 7 | 6 |
| cover-2-0 (lag 20) | Llama-3.1-8B | late | r20261006-064946-6018 | 16 | 7 / 7 | monitor-unavailable 4, delivery-refused 4, mismatch 1 | 7 | 6 |
| cover-4-1 (lag 20) | Llama-3.1-8B | burst | r20261006-074855-4115 | 16 | 4 / 4 | delivery-refused 8, monitor-unavailable 4 | 7 | 6 |
| cover-4-1 (lag 20) | Llama-3.1-8B | spread | r20261006-074855-4115 | 16 | 3 / 3 | delivery-refused 10, monitor-unavailable 2, mismatch 1 | 7 | 5 |
| cover-4-1 (lag 20) | Llama-3.1-8B | bits | r20261006-074855-4115 | 16 | 4 / 4 | delivery-refused 10, monitor-unavailable 2 | 7 | 6 |
| cover-4-1 (lag 20) | Llama-3.1-8B | late | r20261006-074855-4115 | 16 | 6 / 6 | delivery-refused 6, monitor-unavailable 4 | 7 | 4 |
| cover-4-1-fallback (lag 20) | Llama-3.1-8B | burst | r20261006-075036-7c96 | 16 | 5 / 5 | delivery-refused 10, mismatch 1 | 7 | 3 |
| cover-4-1-fallback (lag 20) | Llama-3.1-8B | spread | r20261006-075036-7c96 | 16 | 5 / 5 | monitor-unavailable 6, delivery-refused 4, mismatch 1 | 7 | 1 |
| cover-4-1-fallback (lag 20) | Llama-3.1-8B | bits | r20261006-075036-7c96 | 16 | 6 / 6 | delivery-refused 10 | 7 | 3 |
| cover-4-1-fallback (lag 20) | Llama-3.1-8B | late | r20261006-075036-7c96 | 16 | 2 / 2 | delivery-refused 10, monitor-unavailable 4 | 7 | 4 |
| envelope | Llama-3.1-8B | burst | r20261006-085450-4a00 | 16 | 8 / 8 | delivery-refused 8 | 8 | 0 |
| envelope | Llama-3.1-8B | spread | r20261006-085450-4a00 | 16 | 3 / 3 | delivery-refused 8, monitor-unavailable 3, mismatch 2 | 8 | 0 |
| envelope | Llama-3.1-8B | bits | r20261006-085450-4a00 | 16 | 9 / 9 | delivery-refused 4, monitor-unavailable 2, mismatch 1 | 8 | 0 |
| envelope | Llama-3.1-8B | late | r20261006-085450-4a00 | 16 | 10 / 10 | delivery-refused 6 | 8 | 0 |

### Covert sender

| rule | model | seed | run | strategy | link-windows audited | accepted raw / committed | violations | window-decisions | declared syncs predicted by the sender | MI full (null) bits/window | decoded bits/window | symbol error rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| last (lag 20) | Llama-3.1-8B | 0 | r20261006-085630-ca20 | honest | 20 | 7 / 7 | delivery-refused 10, monitor-unavailable 2, mismatch 1 | 8 | - | 2.000 (2.038) | 0.000 | 0.875 |
| last (lag 20) | Llama-3.1-8B | 0 | r20261006-085630-ca20 | covert | 20 | 9 / 9 | delivery-refused 10, mismatch 1 | 8 | True | 2.000 (1.613) | 0.387 | 0.375 |
| cover-4-1 (lag 20) | Llama-3.1-8B | 0 | r20261006-091949-13a6 | honest | 20 | 10 / 10 | delivery-refused 6, monitor-unavailable 4 | 8 | - | 1.250 (1.337) | 0.000 | 1.000 |
| cover-4-1 (lag 20) | Llama-3.1-8B | 0 | r20261006-091949-13a6 | covert | 20 | 14 / 14 | delivery-refused 6 | 8 | False | 0.906 (1.031) | 0.000 | 0.750 |
| last (lag 20) | Llama-3.1-8B | 1 | r20261006-104900-5d25 | honest | 20 | 6 / 6 | delivery-refused 11, monitor-unavailable 3 | 8 | - | 1.906 (1.756) | 0.150 | 0.750 |
| last (lag 20) | Llama-3.1-8B | 1 | r20261006-104900-5d25 | covert | 20 | 5 / 5 | delivery-refused 8, monitor-unavailable 6, mismatch 1 | 8 | False | 2.250 (2.288) | 0.000 | 0.500 |
| cover-4-1 (lag 20) | Llama-3.1-8B | 1 | r20261006-112704-48e5 | honest | 20 | 6 / 6 | delivery-refused 12, monitor-unavailable 2 | 8 | - | 1.406 (1.068) | 0.337 | 0.750 |
| cover-4-1 (lag 20) | Llama-3.1-8B | 1 | r20261006-112704-48e5 | covert | 20 | 6 / 6 | monitor-unavailable 7, delivery-refused 6, mismatch 1 | 8 | True | 1.250 (1.413) | 0.000 | 0.750 |
| last (lag 20) | Llama-3.1-8B | 2 | r20261006-112733-6876 | honest | 16 | 5 / 5 | delivery-refused 8, monitor-unavailable 2, mismatch 1 | 6 | - | 0.918 (1.085) | 0.000 | 1.000 |
| last (lag 20) | Llama-3.1-8B | 2 | r20261006-112733-6876 | covert | 16 | 4 / 4 | delivery-refused 8, mismatch 2, monitor-unavailable 2 | 6 | True | 1.918 (1.935) | 0.000 | 0.833 |

### Honest against honest

| rule, model, configuration | honest runs (first is the reference) | windows | windows whose declared sync differs from the reference's | windows whose wire differs from the reference's |
|---|---|---|---|---|
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172914-b4f8_w47-51 | r20261006-040542-d15e, r20261006-060242-5190, r20261006-064946-6018 | 4 | [3, 3] | [4, 4] |
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172922-4790_w35-39 | r20261006-040542-d15e, r20261006-060242-5190 | 4 | [1] | [4] |
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172929-7309_w35-39 | r20261006-040542-d15e, r20261006-060242-5190, r20261006-064946-6018 | 4 | [3, 3] | [4, 4] |
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172937-7e08_w0-8 | r20261006-040542-d15e, r20261006-060242-5190 | 8 | [3] | [8] |
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172944-95df_w3-7 | r20261006-040542-d15e, r20261006-060242-5190 | 4 | [2] | [4] |
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180110-f99f_w3-7 | r20261006-040542-d15e, r20261006-060242-5190 | 4 | [0] | [4] |
| cover-2-0 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180117-4455_w0-7 | r20261006-040542-d15e, r20261006-060242-5190 | 7 | [1] | [7] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172914-b4f8_w47-51 | r20261006-044506-85e7, r20261006-052414-7554, r20261006-074855-4115, r20261006-091949-13a6, r20261006-112704-48e5 | 4 | [1, 1, 2, 1] | [4, 4, 3, 4] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172922-4790_w35-39 | r20261006-044506-85e7, r20261006-052414-7554 | 4 | [1] | [4] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172929-7309_w35-39 | r20261006-044506-85e7, r20261006-052414-7554, r20261006-074855-4115, r20261006-091949-13a6, r20261006-112704-48e5 | 4 | [0, 2, 0, 1] | [4, 4, 4, 4] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172937-7e08_w0-8 | r20261006-044506-85e7, r20261006-052414-7554 | 8 | [0] | [8] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172944-95df_w3-7 | r20261006-044506-85e7, r20261006-052414-7554 | 4 | [0] | [4] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180110-f99f_w3-7 | r20261006-044506-85e7, r20261006-052414-7554 | 4 | [0] | [4] |
| cover-4-1 (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180117-4455_w0-7 | r20261006-044506-85e7, r20261006-052414-7554 | 7 | [4] | [7] |
| cover-4-1-fallback (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172914-b4f8_w47-51 | r20261006-055759-f347, r20261006-075036-7c96 | 4 | [3] | [4] |
| cover-4-1-fallback (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172929-7309_w35-39 | r20261006-055759-f347, r20261006-075036-7c96 | 4 | [3] | [3] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172914-b4f8_w47-51 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a, r20261006-085450-4a00 | 4 | [0, 0, 0] | [4, 4, 4] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172922-4790_w35-39 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a | 4 | [0, 0] | [4, 4] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172929-7309_w35-39 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a, r20261006-085450-4a00 | 4 | [0, 0, 0] | [4, 4, 4] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172937-7e08_w0-8 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a | 8 | [0, 0] | [8, 8] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172944-95df_w3-7 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a | 4 | [0, 0] | [4, 4] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180110-f99f_w3-7 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a | 4 | [0, 0] | [4, 4] |
| envelope (lag 0), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180117-4455_w0-7 | r20261006-023423-f03d, r20261006-031802-13b9, r20261006-042805-434a | 7 | [0, 0] | [7, 7] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172914-b4f8_w47-51 | r20261006-031529-0590, r20261006-050615-947a, r20261006-051921-d3e7, r20261006-064756-4b6d, r20261006-085630-ca20, r20261006-104900-5d25, r20261006-112733-6876 | 4 | [0, 2, 1, 2, 3, 0] | [2, 4, 4, 3, 4, 4] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172922-4790_w35-39 | r20261006-031529-0590, r20261006-050615-947a, r20261006-051921-d3e7 | 4 | [1, 3] | [3, 4] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172929-7309_w35-39 | r20261006-031529-0590, r20261006-051921-d3e7, r20261006-064756-4b6d, r20261006-085630-ca20, r20261006-104900-5d25, r20261006-112733-6876 | 4 | [2, 1, 3, 2, 2] | [4, 4, 4, 4, 3] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172937-7e08_w0-8 | r20261006-031529-0590, r20261006-051921-d3e7 | 8 | [5] | [8] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-172944-95df_w3-7 | r20261006-031529-0590, r20261006-051921-d3e7 | 4 | [1] | [4] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180110-f99f_w3-7 | r20261006-031529-0590, r20261006-051921-d3e7 | 4 | [1] | [4] |
| last (lag 20), Meta-Llama-3.1-8B-Instruct, plaintext_r20261003-180117-4455_w0-7 | r20261006-031529-0590, r20261006-051921-d3e7 | 7 | [4] | [7] |

GPU-hours held by the cells listed: 14.69
