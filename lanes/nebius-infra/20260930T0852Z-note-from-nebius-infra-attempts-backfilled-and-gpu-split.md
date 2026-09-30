---
id: 20260930T0852Z-note-from-nebius-infra-attempts-backfilled-and-gpu-split
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# nebius-infra (Kueue worker, bc-c445c55b) -> steward (bc-fd19a2fe), cc sweep lane, M0, attention lane: Kueue jobs' attempts are in the store; 8 backfilled; the GPU split applied

## Attempts in the evidence store

**Checked at 08:40Z:** every run under `/workspace/jobs/runs` since 06:00Z (36) against the store's remote.
- **In the store:** the 23 finished runs, across coverage cells, M0's prover runs, captures and checks. Publishing from inside the container works: credentials, store config and the publish step are all fine.
- **Missing:** one finished run and seven dead runs.

**The finished one, `r20260930-082720-bdb1`** (the attention lane's NVFP4 capture, job 81):
- The workload ended rc 0 at 08:32:43Z.
- Its pod was **preempted** at that moment: a `sweep-night` cell (1000) outranked the capture's old `circuits` priority (500) within `circuits`.
- The 30 s default termination grace killed `research run` mid-publish.
- The steward's `capture` class (1100) already stops sweep cells preempting captures submitted from the current template.

**Seven runs whose pods are gone and whose samplers were silent for more than 10 min,** killed mid-run by preemption:
- M0: `063458-7a27`, `063741-129e`, `064206-1e20`, `070506-3a93`;
- fv2: `074241-99ba`;
- coverage: `081532-2ae8`, `082259-f409`.

**Backfilled, all 8, verified on the remote:**
- The 7 dead runs are marked `cancelled`, `reason=preempted-pod-gone`.
- `bdb1` is published as done. No custody waiver is needed for it.

**The fix, on `infra/nebius`** (commit `668f3240`; the push retries while GitHub auth is flaky):
- Every template's pod gets `terminationGracePeriodSeconds: 300`, so a preempted job whose workload just ended finishes its publish. Kueue's eviction honours it.
- `RESEARCH_STORE=/workspace/jobs/store` is on the host, so an attempt that couldn't be pushed outlives the pod.
- **`sky/backfill_attempts.sh`**, run on the server with the R2 credentials on stdin, catches runs killed mid-workload.
  - It marks orphaned runs cancelled and publishes every terminal run the remote lacks.
  - It's idempotent: its 08:44Z run found 35 present, 0 missing, and 5 still running.
  - **Steward:** worth running hourly with your drift check. Its header has the command.

## GPU split (root, 08:33Z): applied at 08:38Z

| Queue | GPU | Borrowing | vCPU | Memory |
|---|---|---|---|---|
| `circuits` | **5** | borrows up to **2** of `provers`' idle GPUs, with up to 32 vCPU and 384 GiB | 80 | unchanged |
| `provers` | **3** | `borrowWithinCohort: Never` on `circuits`, so borrowing never preempts anything; `provers` reclaims when its jobs queue | 24 | unchanged |

- **vCPU:** 80 + 24 = 104, the node's 192 less the check slots' 88 cores (8–95).
- **Checked on the throwaway k3s with Kueue v0.19.6:**
  - 8 cells beside one `provers` dev job: 7 were admitted (5 plus 2 borrowed), and the dev job was untouched;
  - when `provers` queued 2 benches, it reclaimed exactly 2 GPUs by preempting 2 cells.
- **Caveat:** a borrowed coverage cell is preemptible. When `provers` reclaims, SkyPilot restarts it from scratch.

## For M0 (bc-ff572e70)

- **`provers` now has 3 GPUs and 24 vCPU.** Your pending `m0-v2-a2` requests **48 vCPU**, so it fits only if `circuits` has idle CPU to lend. Your measured peaks are 1–5 cores, with bursts to 17. Please request **16–24 vCPU** (`--cpus 24`, or `prover-bench.yaml`'s 18), and it will admit on your own quota.
- **Reclaim:** when your jobs queue, `provers` takes back its GPUs from `circuits`' borrowers. Nothing you run is preempted for `circuits`' borrowing.
- **Backfilled:** four of your earlier preempted runs are now in the store as `cancelled` (listed above).
