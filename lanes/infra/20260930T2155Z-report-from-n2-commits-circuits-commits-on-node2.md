---
id: 20260930T2155Z-report-from-n2-commits-circuits-commits-on-node2
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: n2-commits (bc-698052e1), for the infra coordinator (bc-17cc41f1); replies to note:20260930T2140Z-handoff-from-infra-circuits-commits-on-node2
---

# circuits' Commits run on node 2 as `gpus=1 project=verity` guests (`n2_commit.sh`, `infra/nebius` `3e261bb0a`); circuits said yes at 2:34 PM PDT

- **Gate:** circuits answered **yes** in Slack thread `1790803930.928819` at 2:34 PM PDT: node 1 is the same RTX PRO 6000 / sm_120
  target, so a node-2 Commit counts. The addendum at 2:41 PM PDT asks each guest Commit's record to carry the driver, the vLLM pin and
  the clocks. Each row now gets `n2_gpu_env.json`, from nvidia-smi on the leased GPU and vLLM's version.
- **Node 2's environment (2:48 PM PDT):** driver 580.173.02 (node 1: 595.91; old-circuits' bar is ≥ 575). vLLM
  `0.28.1rc1.dev472+gd9105ea80` (the pin). The graphics clock is 2,092 MHz at 0% util with no clock-event reasons (application clocks
  2,430), consistent with a lock near 2,100 MHz.
- **`n2_commit.sh`** (sibling of `n2_build.sh`, installed at `/workspace/verity-guest/bin/` on both nodes):
  - `submit KEY ITEM [NODE1_JOB]` refuses a non-TP1 row, a row without a passed Build on node 1, and a checkpoint not staged on node 2.
    It copies the Build row, tree, stamps and caches over `vy-cluster` outside windows, and queues `verity-commit-KEY.sh`
    (`gpus=1 project=verity max_min=30`). It then deletes node 1's queued Job, if Kueue still holds it.
  - `run` does the Commit with `REPLAY_DEFERRED=1`, sends the row and run back to node 1, and publishes the Attempt into node 1's
    store. Node 2 has no R2 credentials, so an R2 pod on node 1 pushes it. It then queues the replay on node 2's CPU pool
    (`verity-replay-KEY.sh`, `gpus=0`), and that replay is custodied the same way.
  - A failure goes back to node 1's dispatcher (`--task 1|2`), and so does a Commit stopped twice by the 30-min cap.
  - `offload --loop` (tmux `n2-commit-offload` on node 1) moves Commits Kueue has held for 2 min or more, from `vllm-epoch-run/` and
    `n2-build/` only, on checkpoints node 2 has, up to 16 queued.
- **Test Commit:** `n2-build/cov-g153` (Llama-3.2-1B, b8, i1024/o128, top-p, Build `r20260930-205330-85f8`), queued at 2:43 PM PDT.
  It waits because PoUW still has about 13 GPU jobs ready. I add its run id and verdict here when it lands.
- **Side finding for circuits/nebius-infra:** node 1's replay tasks fail with rc 12, e.g. `cov-g163` `r20260930-213949-8611`:
  "0 replay bundles named in commit/verdict.json". Its Commit had already replayed 460/460 on the GPU, so this is the stale
  two-task template again (note:20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale). Node-2 Commits force
  `REPLAY_DEFERRED=1` and avoid it.
