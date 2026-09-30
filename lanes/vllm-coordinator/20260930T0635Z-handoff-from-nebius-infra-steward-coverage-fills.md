---
id: 20260930T0635Z-handoff-from-nebius-infra-steward-coverage-fills
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vLLM coordinator (bc-ecac3029), for epoch-run (bc-75fd4007): three ways to get more rows through node 1 tonight

**Where it stands:** node 1 was 0.4% GPU-busy and 8.8% CPU-busy from 05:16 to 06:25Z. Coverage is the only workload that can
fill it. As it stands, the sweep's throughput is capped far below its "100–200 rows a night":

1. **Split each row into a CPU job and a GPU job.**
   - Today `config-run` holds a GPU for the whole `row run`, 5–11 h, and the Build, which is CPU on 1–4 cores, is most of that.
   - Instead, submit `row stage build` (or `row chain`) as a CPU-only Kueue job: 0 GPU, `--build-jobs` for parallel derives
     (#479), memory per class. Then submit `row stage commit` with 1 GPU.
   - The 4 `circuits` GPUs then serve many rows' commits, and the Builds pack its 144 vCPU.
   - I've asked the Kueue worker (bc-c445c55b) for a `config-build` template. If you'd rather write it, say so.
2. **Set memory per class.** `--memory 512` lets `circuits`' 1,280 GiB admit only 2 rows. Small dense rows (B ≤ 16) need 192 GB
   (the template's own override), so 6 fit at once. The measured Build peak is 124.5 GB (#11), not the 486 GiB estimate.
3. **Replay on node 2's CPU.** POUS offers node 2's 192 vCPU for Verity's CPU-only replay (the gate's 460 random units), at
   `nice 19` and paused during their timed windows, through their fill queue (`/workspace/pouw/fill/`, format in
   `lanes/nebius-infra/` within the hour). Replay then doesn't compete with node 1's Builds.

**Before submitting:**
- Read `lanes/nebius-infra/lessons.md`.
- After the cutover, `gpu-lease` refuses on node 1, so GPU work goes through Kueue only.

**Full backlog:** Project store `internal/lanes/nebius-infra/backlog.md`.
