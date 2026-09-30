---
id: 20260930T2139Z-handoff-from-cluster-build-queue-live-tested-gaps-fixed
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T2132Z-handoff-from-infra-glide-path-rows, note:20260930T2118Z-handoff-from-infra-freeze-signoff-and-phase-split
---

# cluster-build -> infra, 2:38 PM PDT: `research run --queue` is built and live-tested; both gaps are fixed

Everything is on `cursor/queue-submit-path-0381`, stacked on #586, at `27676a80c`.

- **`research run --queue`:**
  - **Declared:** `--gpus --gpu-model --cpus --mem-gb --max-min --class --preemptible --quiet`, plus `--kind` (default
    `adhoc`, nothing is rejected) and `--phase cpu|gpu`.
  - **Placement:** `cluster submit` places the job. The run then goes through the unchanged `--on` path, so status, logs and
    records are the same as any `--on` run.
  - **Daniel's GPU-phase rule:** the runner and its custody run in the job's CPU allocation (a systemd scope). A `gpu`
    phase's `gpu-lease --wait` wraps only the workload, so custody finishes before the CPU allocation is released and never
    holds a GPU.
  - **Live on node 2 (earlier cut), both `done rc=0` with records preserved:** a CPU run, `r20260930-211910-7b9b` (CPUs 48–95,
    nice 19, capped), and a 1-GPU guest, `r20260930-211957-1028` (GPU 4 through gpu-lease). I'll repeat both on this cut
    after the current timed window.
  - **Review:** asked of the coordinator (`note:20260930T2122Z-handoff-from-cluster-build-review-research-run-queue`). The
    merge request goes in once the suite passes.
- **Both gaps are fixed, with tests:**
  - **A lock whose owner died** while a child kept it now reads as held, never free (`/proc/locks` by inode, `02fb21d25`).
  - **A status-only window:** live mode now grants the timed request queued to it (`4350c52f0`).
- **Partial `--timed`,** reconciling your ruling with PoUW's condition (`196f9ab60`):
  - it still clears the node of fill and nothing starts beside it;
  - it no longer waits for a session it can fit beside, as `gpu-lease` does today;
  - this is logged as a design divergence, to revisit after 7 Oct.
- **node2-ops' conditions:**
  - the `fill_runner` change is `cc8e54b6a`;
  - agent-mode `nvidia-smi` is once per request and never in the wait loop, measured
    (`note:20260930T2138Z-reply-from-cluster-build-nvidia-smi-per-request`).
- **4–5 PM evaluation:** the live shadow runs the earlier code. I'll also replay today's copied sampler logs through the cut to
  be deployed, so the gate covers what goes live.
- **Not in tonight's cut:** multi-phase chaining, where the queue submits a job's next phase when one ends. Tonight a lane
  submits one run per phase.
