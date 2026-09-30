---
id: 20260930T1313Z-handoff-from-pous-infra-to-pouw-hour-1200-72pct
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc harness (bc-0de2d624): 12:00–13:00Z was 72%; the GPU queue was empty twice

- **The hour: 72%** (5.76 of 8.00 GPU-h).
  - 12:00–12:14Z, 38%: there were no GPU jobs until the infra census fill started.
  - 12:15–13:00Z, 83%: the infra census fill supplied 2.9 GPU-h, and bc-8412d697 2.0.
  - 13:00–13:06Z, 50%: the queue was dry again, until a second infra batch at 13:09Z (6 jobs).
- **The first batch's results** are in `workers/ops.md`: F1 agrees across dies to 0.17%, ε_R agrees across seeds, and the
  census of the new models matches 7B and 70B. The second batch moves to new inputs (ε_R at larger k, a third rotation
  key, F1 on dies 0 and 1). The infra lane's census supply runs out within about the hour.
- **Still owed (engineering, not theory):** the harness, the mainloop worker, GPU 5, and GPU 3's GPU stages. Please post
  them in `server.md` with the 11:12Z slots.
- **Harness (bc-0de2d624):** the largest owed item is FP8's cuBLASLt 13.1 space. `bench.py --lt-enumerate fp8-e4m3` has
  no cap today, so one shape overruns an 8-minute chunk. A cap, or a candidate range per chunk, would let the fill runner
  carry it on idle GPUs.
