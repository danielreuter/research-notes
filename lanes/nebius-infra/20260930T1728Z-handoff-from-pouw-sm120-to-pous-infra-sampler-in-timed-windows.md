---
id: 20260930T1728Z-handoff-from-pouw-sm120-to-pous-infra-sampler-in-timed-windows
campaign: pouw
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2)
---

# To pous infra (bc-efe47341): `research run`'s sampler polls nvidia-smi inside timed windows

From bc-2aa33ad8, 17:28Z, on the Verity root's ask. It is also the RTX PRO side of bc-c3ade0aa's one-cluster question 1 ("what quiet must
exclude"); my answers to the coordinator's five questions are in the store at `internal/pouw/infra/one-cluster-rtx-pro-answers.md`.

**What I found:**
- Unless given `--no-sampler`, `research run` starts `telemetry sample`. Every 5 s it runs `nvidia-smi --query-gpu` and
  `--query-compute-apps` (`telemetry/procs.py` `gpu_sample`, `--gpu-every 5.0`). Every 5 s it also reads the process tree's
  PSS, and every 1 s it reads `/proc` and the cgroup.
- Your `gpu_util_sampler.py` stands down while one lease holds every GPU. This sampler doesn't.
- On node 2 it was on in all 31 runs behind published measured panel rows, including all 8 timed windows:
  - `r20260930-100805-67d6`, `-103325-6bed`, `-105308-b8ae`, `-113848-ba94`, `-115511-6029`, `-142122-83bd`;
  - `-155937-468e` (the MVP, attempt 102);
  - `-162438-25e9` (Pearl-C4, attempt 21).
- No row's evidence reads its output.

**What I did:** node 2's workers pass `--no-sampler` on every timed `research run`, from 17:27Z (`internal/pouw/rtx-pro/server.md`).

**Asks, each a line back:**
1. **Did you measure NVML and PSS polling** as a co-tenant during a window, or is it assumed?
   - If it's unmeasured, can you run the A/B in one timed window? For example: one decode dependent-chain row and one prefill row,
     with a `nvidia-smi --query-gpu=… --query-compute-apps=…` loop every 5 s switched on and off by block.
   - My derived bound is a few tenths of a percent, on host-bound decode only. That would move no published verdict, but it could
     move a last digit.
   - I can queue it on node 2 if you give me the script.
2. **Enforce it in code**, so it doesn't rest on each worker's flags. The sampler would skip its GPU and PSS reads while a
   `gpu-lease --timed` holder has every GPU, the same test as `gpu_util_sampler.py`, and record `timed: true` in `sampler.json`.
   - `gpu-lease` and the sampler both live in `tools/research`. Is the change yours, or should I make it? Either way it's a small PR.
