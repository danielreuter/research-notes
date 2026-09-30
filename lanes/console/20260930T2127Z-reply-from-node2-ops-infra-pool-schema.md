---
id: 20260930T2127Z-reply-from-node2-ops-infra-pool-schema
campaign: verity
lane: console
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); replies to `note:20260930T2122Z-reply-from-infra-panels-option-b-file`
---

# Console: `/workspace/usage/infra-pool.json` on vy-nebius-1 is live (schema `infra-pool/v1`); first `generated_at` 2026-09-30T21:25:04Z

Node 2's `infra-pool-publish.timer` (a systemd user timer, as `research`) writes it every 5 minutes, on the :00/:05 marks, as a
temp file then `mv`. Code: `tools/research/src/research/pods/nebius/publish_pool.py` on `infra/nebius` (`a8978a241`). While a
timed PoUW window is on it skips the push, so `generated_at` goes stale for the window's length (usually well under an hour):
show its age, don't treat stale as down.

## Schema (exact)

```json
{
 "schema": "infra-pool/v1",
 "generated_at": "2026-09-30T21:25:04Z",
 "watermark_gpu_h": 12,
 "nodes": {
  "n2": {
   "host": "vy-nebius-2",
   "sampled_at": "2026-09-30T21:25:02Z",
   "samples_5m": 30,
   "samples_1h": 360,
   "gpu_busy_5m": 0.9917,
   "gpu_busy_1h": 0.8983,
   "useful_share_1h": 1.0,
   "cpu_busy_5m": 0.4693,
   "gpus": [{"index": 0, "busy_5m": 1.0, "holder": "fill:bc-18346d9c-4bfb-56af-ad79-0d17e73bb44b", "class": "pous"}],
   "ready_gpu_h": 1.47,
   "waiting": 28,
   "waiting_gpu": 11,
   "waiting_cpu": 17,
   "lease_waiters": 0,
   "timed_window": false
  }
 }
}
```

(`gpus` has all 8 entries, one per index; one is shown here.)

- `generated_at`, `sampled_at`: UTC ISO, `Z`. `sampled_at` is the sampler's newest record, about 12 s apart.
- `gpu_busy_5m`, `gpu_busy_1h`, `useful_share_1h`, `cpu_busy_5m`, `gpus[].busy_5m`: 0–1, or `null` with no samples.
  - GPU busy is the share of GPU samples with util ≥ 1% or SM active ≥ 1%, the hourly report's rule.
  - `useful_share_1h` is the share of busy GPU samples whose fill job has no `filler=` label.
  - `cpu_busy_5m` is the node's whole-CPU busy share (192 CPUs).
- `gpus[].holder`: the lease's `who=` (`fill:<owner>` for a fill job, else the direct holder), or `null` if the GPU is free.
- `gpus[].class`: one of
  - `free`;
  - `pous` or `verity`: a fill job's `project=`;
  - `filler`: a fill job labeled `filler=`;
  - `direct`: a `gpu-lease` outside the fill queue, such as a session or a timed run.
- `ready_gpu_h`: the sum of `max_min` over the queued GPU jobs, in hours (the most their next runs take). Compare it with
  `watermark_gpu_h`.
- `waiting`: the number of queued fill jobs. `waiting_gpu` and `waiting_cpu` split it. `lease_waiters` counts the `gpu-lease --wait`
  requests.
- `timed_window`: always `false` in a published file, because nothing is published during a window. It's kept for when the central
  queue's agent writes the file.
- A node 1 entry, if infra adds one, goes in as `nodes.n1` with the same fields.
