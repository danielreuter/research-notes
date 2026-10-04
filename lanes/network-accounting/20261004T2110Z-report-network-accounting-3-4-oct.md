---
id: network-accounting/network-accounting/20261004T2110Z-report-network-accounting-3-4-oct
campaign: network-accounting
lane: network-accounting
kind: report
status: open
repo: verity@main (c05f14179 and later)
origin: relayed from the coordinator store's internal/network-accounting/ (agent bc-ecea50f6), per Daniel's 4 Oct ruling that nothing others need lives only in an agent store
---

# Network accounting, 3–4 Oct: what landed, what was measured, what's open

This note covers the network warden (`protocols/network_warden`, Lean package `NetTiming`), its vLLM trace calibration
and the active warden. Each approach is in the registry under `network-accounting/` (`research notes approaches --campaign network-accounting`).

## On main

- **The per-window guarantees: verity#994.**
  - Egress is `EncardAccSeqsLeConstantRate*`: per window `#Ac·(#Σ_sync·D^T)^m`, about 7 bits per window at 16 × 8.
  - Ingress is `EncardIngressObsDecodableLe*`: per window `(∏ℓ(rℓ+1)^T·D^T)^m`. That's the K charge's unit.
  - Both count from the run's first window, which was the red team's condition M1. No chain rule holds for the egress
    count, so a charge starting mid-run would need a conditional-count statement (`network-accounting/egress-chain-rule`,
    killed).
- **The warden follow-ups: verity#1005.**
  - `LogicalFrame` rejects negative indices.
  - `choose_syncs` chooses across all links jointly.
  - The block-cap paragraph is written.
- **The audit replay: verity#1016.** `benchmarks/network_traces/replay.py` runs the real audit over recorded traces.
  `convert` now refuses a missing `requests.jsonl`.
- **The GC freeze before t0 in the offline modes: verity#1029.**
- **The Python audit against the Lean definitions: verity#1089.**
  - It ran 10,000 random instances with 0 differences, and caught all 6 mutants of the Python audit.
  - It runs in `check` as lean-audit's `runs.NetTimingDifftest`, following `PouwBulk`'s pattern.
  - None of the 51 pins changed.
- **The active warden: verity#1101.** `verity_network_warden.active` is an asyncio TCP proxy that enforces the reference
  warden on a live byte stream, with `benchmarks/network_traces/active_replay.py` driving it.

## Measured

- **The vLLM trace calibration, pass 3** (`art:9c9c5f93`, with traces `art:a0d64641` and `art:663168ff`):
  - 195 chunks gave 5,290 kept windows, 88.17 GPU-h on node 1 and node 2, with 0 honest misses.
  - Pooled plaintext: honest misses ≤ 0.057% at 95%, r 1,766, Σ_sync 128 (7 bits per window).
  - The full report through pass 3 is `art:cea116fb`. The campaign is parked
    (`network-accounting/vllm-trace-calibration`): a 10⁻⁴ bound needs about 30,000 windows, roughly 550 GPU-h.
- **The real audit over every kept window** (`art:12570076`):
  - At the pooled calibration, 5,289 of 5,290 windows were accepted raw and committed, and all 5,290 ingress windows.
  - The one miss is a Commit-mode window, whose first frame came at 1.8 s against the plaintext set's 1.5 s. Commit's
    own calibration accepts it.
  - The plaintext pool alone: 5,228 of 5,228 accepted.
- **Lane F's audit replay:** 100% of 13,520 verdicts accepted, raw and committed (`art:a3c3281f`, `art:6e76ba7b`,
  `art:5f041477`).
- **The active warden, replaying 20 out-of-sample Llama-3.1-8B traces** (`art:962e249a`): 65 windows, 130 link-windows.

  | Run | Accepted, raw and committed | Evidence |
  |---|---|---|
  | Injected clock | 130 of 130 | `art:73bbd0a9` |
  | Real time, VM shared with other work | 122 of 130 | `art:73bbd0a9` |
  | Real time, idle VM | 128 of 130 | `art:92d55b2d` |

  - Every real-time miss is a fail-closed `monitor-unavailable`: a tick later than the 25 ms slack. There are no
    mismatches and no slipped buckets.
  - Burst, spread and random-bit senders produce a byte-identical wire. A sender that holds frames late is rejected as
    a `mismatch`.
  - Against the replay model, the proxy adds no padding and no grid latency, only the wire lag (p99 16 ms).
- **The active warden in front of a live vLLM** (verity#1125, queued; `art:d082f621`, 1.32 GPU-h on node 1):
  - 65 windows of real Llama-3.1-8B serving: 127 of 130 link-windows accepted, raw and committed. The 3 misses are
    fail-closed ingress ticks. 0 mismatches, and the wire equals the records.
  - **The finding:** a live prover can't choose its syncs in hindsight, so it declares the envelope sync (δ 14, ρ 203/66).
    That makes shaping p99 3.6 s against the model's 1.5 s, and first frame p99 3.7 s against 1.7 s. A hindsight
    prover would have missed 0 windows. An online sync choice is the open question
    (`network-accounting/online-sync-choice`, parked).

## Causes found along the way

- **Node 1's 5 s stalls:** PoUW's Lean audit kernel replays size their thread pool from the whole machine, not the
  job's affinity. verity#1038 sets `LEAN_NUM_THREADS` from the affinity, and verity#1039 puts CPU-only queue jobs in an
  idle cgroup scope.
- **Real-time stalls on a 4-vCPU VM:** on a loaded host the proxy stalled 33–35 ms even at nice −20. On an idle host no
  tick went past 12 ms. The VM refuses SCHED_FIFO, because the pod's cgroup has no real-time budget. A deployment pins
  the proxy to a reserved core, or sets the slack from the jitter it measures.

## Open

- Egress option (d), per-grid-class allocation, is held for Daniel (`network-accounting/egress-per-grid-class-allocation`).
- Lane J's follow-up, `cursor/network-warden-active-pinning-728f` (`--cpus`), is the pinned real-time hour, with a
  target of at least 129 of 130.
