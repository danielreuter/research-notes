---
id: 20260930T0627Z-handoff-from-nebius-infra-steward-checks-drop-gpu-lease
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# URGENT, nebius-infra steward -> research coordinator (bc-8ece7cde), cc Kueue worker (bc-c445c55b): drop `gpu-lease` from train checks on vy-nebius-1 before cutover; checks get CPUs 128–191

**What breaks.** Train checks on vy-nebius-1 run as `gpu-lease 1 --wait -- taskset -c 160-191 … check.py` (your 06:10Z note).
They're CPU-only (`--extra torch-cpu`), but:
1. **They block the cutover.** `cutover.sh` has been waiting on node 1 since before 06:26Z. It proceeds only when no `gpu-lease`
   lock is held. Check `r20260930-060431-64e5` holds GPU 0 (a Kubernetes GPU, taken before the allow-list), and every new check
   takes one of 4–7.
2. **After cutover every check fails at once.** `/etc/vy/direct-gpus` becomes `none`, and `gpu-lease` exits 2 ("no GPU is for
   direct runs here").

**Fix, in your check command on node 1:**
- Replace `gpu-lease 1 --wait --` with a slot lock:
  `flock /workspace/research/locks/check-a.lock taskset -c 128-159 …` or
  `flock /workspace/research/locks/check-b.lock taskset -c 160-191 …`.
- No GPU is taken, so the check doesn't wait on GPU traffic. It only serializes with the other check using that slot.
- If some step truly needs a GPU, say so here and I'll get it a Kueue `prover-dev` slot instead.

**Your CPU share on node 1 (Daniel: merge velocity first):**
- CPUs **128–191** (64 vCPU) are for train checks: two parallel 32-vCPU slots, `check-a` = 128–159 and `check-b` = 160–191.
- Node 1 ran at 9% CPU from 05:16 to 06:25Z, so this displaces nothing running now.
- M0's old benchmark pin (144–191) moves into Kueue at cutover.
- I'm asking the Kueue worker to cut Kueue's CPU nominal by 64 (to 128 of 192), so queued jobs don't count on those cores.
- The train-speedup worker can have more if it needs it. Ask here.
