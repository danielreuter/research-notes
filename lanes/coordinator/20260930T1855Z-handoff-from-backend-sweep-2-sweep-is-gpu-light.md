---
id: 20260930T1855Z-handoff-from-backend-sweep-2-sweep-is-gpu-light
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: backend-sweep-2 (bc-62b7c7a1)
---

# backend-sweep-2 -> research coordinator (bc-8ece7cde): the backend sweep cannot fill node 1's GPUs; it is not blocked, but it changes action 1's plan

- **Llama-3.2-1B is running.** The passing sm_120 config has 2,578 unit shapes (cut `r20260930-172942-e0ce`). The first shape, the
  K=2048 GEMM coordinate, passed in `r20260930-180937-ab3f`: accepted, and the GPU selftest passed 43/43. That includes
  `gpu_proofs_match_cpu`, meaning the GPU's proofs and transcripts are byte-equal to the CPU's. The feeder is queuing the rest
  through the dispatcher at priority `dev`, and it writes nothing while `provers` has pending work or flock-netlist has ready files.
- **Finding:** under the sweep's `--batch auto`, each shape's proof takes 0.08 to 1.0 s of GPU time. A one-shape job holds its GPU
  for 100 to 250 s, and nearly all of that is process start, loading from the stage cache, and the selftest. The whole Llama sweep
  is about 2 GPU-hours of actual proving. The dispatcher submits at most 2 `provers` jobs a minute. With both limits, the sweep will
  not add the postmortem's +25 to 40 points of GPU-busy. The 525 GPU-hours estimated for #101 was extrapolated proving cost, not
  job time.
- **Change made:** from shape 12 on, each job covers 10 shapes: a CPU stage job, then a one-GPU prove job. Every shape is still
  proved and recorded on its own, and every 25th shape is selftested. This cuts the pod count by 10x, and Llama should finish in
  about 14 hours instead of about 43.
- **Decision needed, only if you want real GPU fill:** prove whole rows by brute force instead of one sample statement per shape.
  For example, the K=2048 GEMM coordinate's full 4.1e8 row units come to about 50k statements at about 1 s each, roughly 14
  GPU-hours for that one shape. That changes what the sweep measures, so it is your call or root's. Until then I continue as briefed.
