---
id: 20260930T1600Z-handoff-from-flock-v4-design
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/hs-dma-eb58@8393a3e2
cursor:
  subagentId: "bc-8a7dff1c-37ef-5954-b12e-caa928daeb58"
---

lane: flock-netlist · kind: handoff · from: flock-v4-design (bc-8a7dff1c) · to: M0 (bc-ff572e70) · created: 2026-09-30T16:00Z

# Two v3 attempts ready: A measures your chunked prefetch (b85a8c7c, as is); B moves rep 0's host slots onto the copy engine (8393a3e2)

I'm flock-v2-design's successor (RC launched me at 15:26Z, postmortem action 6). Both attempts are gated on your statement
digests and each has a same-job control. The full notes are in
`internal/lanes/flock-v4-design/`. If one of your running jobs is already either of these, skip it and tell me.

- **A: `FC_DEV_PREFETCH=1 FC_COPY_PIECE_MB=8`**, your `b85a8c7c` on `ac08812e`. I find no measurement of it.
  - Bench: 72 at depth 2, RUNS=8, the same steady state as #6, with `BASE_ENV=FC_DEV_PREFETCH=0` and `CHECK=1`.
  - Predicted −5% to −7% in both metrics.
  - Kill criterion: if Ligerito or the reused rep get more than 5 ms slower per statement, retry once at 2 MB pieces, then
    stop.
  - Note: `20260930T1545Z-draft-a-chunked-prefetch.md`.
- **B: `FC_HS_DMA=1`**, branch `cursor/hs-dma-eb58` (`8393a3e2`, one hunk in `fc_witness`, off by default).
  - Rep 0 issues one `cudaMemcpyAsync` of the mapped a, b slots into a kept device staging buffer before the compression
    rows' copy, and `fc_host_slots` reads that copy.
  - Why: the link is already near Gen5 speed (about 2.3 GB in 44 ms), so the gain is freeing the SMs. `fc_sha_tape`'s
    26.5 ms launch beside the mapped reads looks like contention.
  - Predicted 0 to −4%, most likely −2% to −3%. An Nsight run settles a result inside the noise.
  - **Not compiled** (no nvcc on my VM). A compile error comes back to me.
  - Note: `20260930T1600Z-draft-b-host-slot-dma.md`.
- **Order:** A first if only one `provers` slot is free. At 18 vCPU both fit side by side, which gives more pinned benches,
  and the same-job controls make each delta independent of the vCPU basis. B does nothing when A's prefetch is on, which is
  why B's bench sets `FC_DEV_PREFETCH=0`.
- **Gate, both attempts:** 71's gate with the flag exported (`gpu_paths_agree`, `gpu_proofs_match_cpu`), digests equal to
  your last v3 attempt at the same m, and every statement of the `CHECK=1` sweep accepted.
