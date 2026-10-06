---
id: network-accounting/network-accounting/20261006T0418Z-report-covert-sync-rate
campaign: network-accounting
lane: network-accounting
kind: report
status: open
repo: verity@cursor/network-warden-covert-sync-rate-728f
origin: worker for the network-accounting lead (bc-ecea50f6), covert-sync-rate question, 6 Oct
---

# The covert rate a colluding sender achieves through the online prover's declared sync

The question: the egress bound charges `log2 #Σ_sync` = 7 bits per window (16 × 8) for the declared clock sync. With
an online prover (`last`, `cover-K-M`), a sender inside the boundary moves that declaration by when it writes. What
rate does it achieve, with every window accepted, as decoded by a receiver who reads only the declared syncs?

Code: branch `cursor/network-warden-covert-sync-rate-728f`, `benchmarks/network_traces/covert.py` (the sender, the
decoder, the measure), `active_replay.py --strategies honest,covert,...` (replay and live), `covert.sh` (the run),
`tool.py` (store tools `network_covert_sync`, `network_covert_steady`). Tests are under
`benchmarks/network_traces/tests/test_covert.py` and use an injected clock only.

## The sender and the decoder

For each window w, the sender draws a symbol `g_w` uniformly from `[1, δ_declared(w)]`. It then writes every frame
anchored in w at `anchor + g_w − 1`, which sets w's frontier to `g_w`. Drawing at most `δ_declared(w)` keeps w
accepted. The sender runs a replica of the proxy's prover, so it knows `δ_declared(w)`. Under `last`, window w+1 then
declares `δ = g_w`. Under `cover-K-M`, it declares `max(g over the last K windows) + M`. The receiver decodes
`ĝ_w = δ_declared(w+1) − M`.

The rate is the plug-in mutual information between `g_w` and the full declared sync of window w+1. It is reported
raw, with its shuffle null, and corrected (raw minus null). The decoded rate is the mutual information between the
symbol and the decoder's output, minus its null, so a decoder that guesses scores 0. Pooled configurations carry
independent messages (seeded per configuration).

## Deliverable 1: the injected-clock replay (CPU)

The traces are the 20 out-of-sample Llama-3.1-8B node-1 traces (`art:962e249a`, oos2) at the llama8b-node1
calibration (T = 600 × 100 ms, 16 × 8). The run covers all 108 configurations: 528 windows, 1,056 link-windows and
420 window-decisions per policy.

- Run: `r20261006-032829-a595` (`network_covert_sync@1`, commit `d4c5861a9`, vy-nebius-2), record `art:ab7a638e`.

| policy | strategy | MI raw / null / corrected (bits/window) | decoded | symbol error rate | accepted (raw = committed) |
|---|---|---|---|---|---|
| `last` | covert | 1.950 / 0.140 / **1.810** | 1.787 | 0.017 | 1,056 of 1,056 |
| `last` | honest (random symbols) | 0.138 / 0.153 / 0.000 | 0.000 | 0.943 | 930 of 1,056 |
| `last` | bits | 0.942 / 0.243 / 0.699 | 0.643 | 1.000 | 903 of 1,056 (153 `mismatch`) |
| `cover-3-2` | covert | 1.482 / 0.224 / **1.258** | 1.262 | 0.429 | 1,056 of 1,056 |
| `cover-3-2` | honest | 0.099 / 0.098 / 0.001 | 0.005 | 0.950 | 1,055 of 1,056 |
| `cover-3-2` | bits | 1.221 / 0.114 / 1.107 | 0.501 | 1.000 | 1,056 of 1,056 |
| `envelope` (fixed, control) | covert | 0 / 0 / **0** | 0 | 0.921 | 1,056 of 1,056 |
| `envelope` (fixed, control) | honest | 0 / 0 / 0 | 0 | 0.917 | 1,056 of 1,056 |

- **Nothing is above 7 bits.** The highest is 1.81 bits/window (covert under `last`), about a quarter of the bound.
- **The covert sender was accepted in every window, raw and committed.** In every configuration and policy, the
  proxy's declarations equal the ones the sender's replica predicted. Its records are `run_shaper`'s on the Program.
  Its wire is the records. No window was accepted with a wire other than the Program's shaping.
- **The controls are 0.**
  - The honest run, scored against an independent random message, has a corrected MI of at most 0.001.
  - Under `envelope`, the same covert sender has a corrected MI of 0, and its wire is byte-identical to honest's in
    all 108 configurations.
- **`bits` (the existing strategy) moves the declaration too.** Its corrected MI is 0.70 (`last`) and 1.11
  (`cover-3-2`). But its symbol (how many of a window's sessions burst) tracks the window's load, which moves the
  honest declaration as well. So part of that is not steering, and its decoder (built for `covert`) reads nothing.
- **Honest traffic under `last` is rejected in 126 of 528 egress windows.** Under `cover-3-2` it is rejected in 1
  of 528, and under `envelope` in 0.

**The per-window rate is mostly a start-up transient.** Every configuration's prover starts with no history and
declares the envelope (δ = 10). The configurations are short (a median of 3 windows), so most decisions sit near a
start. The corrected MI by decision position:

| policy | 1st | 2nd | 3rd | 4th | 5th |
|---|---|---|---|---|---|
| `last` | 2.36 (81) | 2.00 (69) | 1.56 (51) | 0.75 (32) | 0.43 (31) |
| `cover-3-2` | 2.36 (81) | 0.58 (69) | 0.71 (51) | 0.43 (32) | 0.72 (31) |

The count of decisions at each position is in parentheses.

**The steady state.** The same sender ran on a noiseless link, one frame per window, over 5,000 windows.

- Run: `r20261006-035157-80d1` (`network_covert_steady@1`, commit `575748ba7`), record `art:a47c36af`.
- Corrected MI: `last` 0.003, `cover-1-1` 1.898, `cover-2-1` 1.152, `cover-3-2` 1.038, `envelope` 0.
- Accepted under `last`, a window's frontier is at most its declared δ, and the next window declares that frontier.
  So δ never rises: the accepted declaration sequences grow polynomially in the number of windows, and the long-run
  rate of any sender is 0.
- A margin M lets δ rise by up to M per window, which keeps a channel open. A scratch count of the distinct accepted
  declaration sequences in this model gives about 1.9–2.0 bits/window as the most any sender gets from δ under
  `cover-1-1` and `cover-3-2`. That is a calculation, not a measured run.

**Caveats.**

- The replay's server may write a frame before the trace says the model produced it, as `burst` does. That makes it
  a sender that controls its own scheduling.
- The sender steers δ only. Shaping the frames' spacing so that frontiers differ across ρ, which would move the
  declared ρ, is not explored here. The 7-bit bound covers that lever.

## Deliverable 2: a live vLLM link (one GPU)

Run `r20261006-035423-2cd5` (queue, preemptible, one RTX PRO 6000 on vy-nebius-2, lease until 05:24Z), serving
`unsloth/Meta-Llama-3.1-8B-Instruct`. It runs `cover-3-2` with honest and covert first, then the `envelope` control
with honest and covert, on configurations of 4–8 windows from 10 of the traces.

The live sender (`covert.LiveSender`, in the shim) can only delay what the model writes. It holds each stream's first
event until `anchor + g_w − 1`, so a window's frontier is `max(g_w, the model's own)`. It draws `g_w` as the replay's
sender does, from its own replica of the proxy's prover.

Run `r20261006-035423-2cd5` was preempted (SIGTERM at 04:45:59Z, 51 min of GPU) after its `cover-3-2` phase, before
the envelope control started. Record `art:cc136bcf`. The control was rerun first in `r20261006-050809-0b8d` (same
inputs, GPU 3). That run was evicted too, at 05:28:09Z after 17 min of GPU (`stopped: evicted`), so its second
`cover-3-2` phase never ran. Windows are 60 s.

| phase (run) | strategy | windows | accepted egress / ingress | MI raw / null / corrected | decoded | SER | decisions |
|---|---|---|---|---|---|---|---|
| `cover-3-2` (`035423-2cd5`) | covert | 20 | 7/20 / 8/20 | 1.170 / 0.963 / 0.206 | 0.206 | 0.81 | 16 |
| `cover-3-2` (`035423-2cd5`) | honest (random symbols) | 24 | 9/24 / 8/24 | 1.202 / 0.920 / 0.282 | 0.282 | 1.00 | 19 |
| `envelope` (`050809-0b8d`) | covert | 4 | 4/4 / 4/4 | 0 / 0 / 0 | 0 | 1.00 | 3 |
| `envelope` (`050809-0b8d`) | honest | 10 | 9/10 / 9/10 | 0 / 0 / 0 | 0 | 0.75 | 8 |

- **No measurable live rate.** The covert sender's corrected MI (0.21) is below the honest control's (0.28, against a
  message it never encoded). At about 16 decisions, both are small-sample bias. Under `envelope` everything is 0.
- **Why it is low.**
  - The live sender can only delay, so a symbol below the model's own frontier is masked. The honest frontier here
    is 7–11 buckets, so most symbols in `[1, δ]` are invisible: SER 0.81.
  - Most rejections, for both honest and covert, are `status:monitor-unavailable`: monitor ticks stalled past the
    25 ms slack (p99.9 325–440 ms, 46 and 55 ticks over slack). The rest are `delivery-refused`. The node's load
    (150–250) was first blamed for the stalls. The pooled section below finds the cause: the online prover's
    `declare()`, run on the proxy's tick.
  - On the quiet node (envelope phase), ticks stayed within slack (max 15 ms).
- **The sender's replica was exact.** In every live covert configuration, the declarations the proxy made equal the
  ones the sender predicted.
- **One covert `mismatch` (egress), and it is not the sender's doing.** In window 2 of b451 under `cover-3-2`, the
  symbol was 1 (no hold), and the model's own burst exceeded the declared δ = 7. Honest traffic gets such rejections
  under online rules too.
- No accepted window had a wire other than the Program's shaping.
- GPU: 0.85 h plus 0.29 h, 1.14 GPU-h for these two runs (both evicted).

## Deliverable 2, pooled: every live window

All live runs are on vy-nebius-2 through the queue: preemptible, one RTX PRO 6000, `unsloth/Meta-Llama-3.1-8B-Instruct`,
60 s windows.

| run | what it added | GPU |
|---|---|---|
| `r20261006-035423-2cd5` (`art:cc136bcf`) | `cover-3-2`, 4–8 window configurations, loaded node; evicted after the phase | 51 min |
| `r20261006-050809-0b8d` | `envelope`, 4–8 windows; evicted mid-phase | 17 min |
| `r20261006-060323-7b56` | nothing: it waited out the 07:00–08:30Z timed window, then died in the node's restart before a lease | 0 |
| `r20261006-084216-ea62` (`art:eb0717b5`) | nothing: evicted by a timed job before its first configuration | 1.5 min |
| `r20261006-094309-7bf2` (`art:94ad30e3`) | nothing: evicted the same way | 5.5 min |
| `r20261006-095426-a0f8` (`art:36409a35`) | `cover-3-2`, 3–5 windows, the full 45 min phase; its envelope phase was evicted | 47 min |
| `r20261006-104423-6cae` (`art:b23ce3ac`) | `envelope`, 3–5 windows, 26 min, finished | 28 min |

Total: 2.51 GPU-h. The node ran a series of short quiet timed jobs from 08:42Z. Each one that starts evicts every
fill job, so the later runs used 3–5 window configurations, which complete within a slot. Short configurations sit
nearer the start, where the replay's per-window rate is highest, so they favour the sender.

Pooled with `covert.py` over the runs' `summary.json`:

| policy | strategy | decisions | MI raw / null / corrected | decoded | SER | accepted egress | accepted ingress |
|---|---|---|---|---|---|---|---|
| `cover-3-2` | covert | 32 | 1.333 / 1.183 / **0.151** | 0.151 | 0.750 | 16/42 | 16/42 |
| `cover-3-2` | honest (random symbols) | 35 | 0.903 / 0.727 / 0.176 | 0.176 | 0.971 | 17/46 | 15/46 |
| `envelope` | covert | 12 | 0 / 0 / **0** | 0 | 1.000 | 16/17 | 16/17 |
| `envelope` | honest | 17 | 0 / 0 / 0 | 0 | 0.882 | 21/23 | 21/23 |

Rejection reasons, egress and ingress together:

| policy | strategy | `monitor-unavailable` | `delivery-refused` | `mismatch` |
|---|---|---|---|---|
| `cover-3-2` | covert | 45 | 6 | 1 |
| `cover-3-2` | honest | 46 | 14 | 0 |
| `envelope` | covert | 0 | 2 | 0 |
| `envelope` | honest | 0 | 4 | 0 |

- **No measurable live rate.** Over 67 `cover-3-2` decisions, the covert sender's corrected MI (0.151) is below the
  honest control's (0.176), which is scored against a message nobody encoded. Both are estimator bias at this
  sample size (null about 0.7–1.2 bits). Under `envelope` everything is exactly 0.
- The sender's replica matched the proxy's declarations in every live covert configuration (`declared_are_predicted`).
  No accepted window had a wire other than the Program's shaping.
- The one `mismatch` is the natural spike already described (b451 window 2, symbol 1).
- **Most live rejections come from the online prover itself, not from the sender or the node's load.**
  - `Shaper.tick()` (`warden/active.py`) calls `prover.declare()` inline at each window's first bucket.
  - `declare()` summarises each past window: a binary search over δ for each of the 8 ρ, and every probe walks
    all of that window's frames.
  - Timed on the pod, over the 17 configurations the live runs selected (`r20261006-111646-920d`, `art:1d62db65`,
    `out/declare-ms.txt`), it takes 158–434 ms per window after the first, against a 25 ms monitor slack.
  - The evidence lines up:
    - Ticks are clean between windows: p99 is 2–5 ms, and the over-slack ticks are about one per window per link.
    - Window 0 has nothing to summarise. Of its 24 link-windows in `r20261006-095426-a0f8`, none failed on
      `monitor-unavailable`; of the 64 later ones, 46 did.
    - Under `envelope` there is no prover, and no tick went over the slack (max 16 ms).
  - So live honest acceptance is 32/92 under `cover-3-2` and 42/46 under `envelope`, on the same node, hours apart.
  - The injected-clock replay cannot see this: its clock does not advance while the proxy computes.
- Until `declare()` is off the tick path (incremental, or computed before the boundary), a live online-sync link
  cannot keep its windows accepted. So "every window accepted" holds only for window 0 of each live configuration,
  and the live covert rate above is measured over mostly rejected windows. The replay's rates (Deliverable 1) remain
  the measurement of what an accepted link carries.
