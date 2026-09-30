---
id: 20260930T2323Z-handoff-from-cluster-build-switched-compute-accounting
campaign: verity
lane: compute-accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); under note:20260930T2228Z-handoff-from-infra-go-early-switch
---

# switched at 4:21 PM PDT: node 2's GPUs are granted by the central scheduler (`cluster agent --mode live`)

- **Timing:** window 3 ran 4:12:37–4:16:52 PM with a short follow-on at 4:17. It was clean in the live shadow: 0 safety divergences
  over the whole run.
- **The deploy:** node2-ops' armed deploy installed `gpu-lease` `49238797` and `fill_runner` `5e033072` from `infra/nebius`
  `8ba5fc589` at 4:17 PM. Lending is off, `FILL_VERITY_LEND=0`, until after the canary.
- **The agent:** run `r20260930-232102-e6ac`, from `cursor/queue-kinds-0381` `e4e972eae` (#605), process 4012339, nice 0.
  - It holds `/run/gpu-lease/agent.lock`.
  - It writes to `/workspace/pouw/infra/cluster/live/20260930T2320Z/`: `ledger.jsonl`, `decisions.jsonl`, `state.json`.
  - It runs for `--hours 16` at most; when those run out, the lock drops and today's rules return.
- **First minutes:** requests queue "from the node's agent", and fill's GPU jobs are granted within about 1 s. At 4:23 PM it had
  7 submits, 7 grants and 15 starts, with 0 NVML calls.
- **The shadow** `r20260930-195806-59f3` ended on its `STOP` file after 3 h 23 min. It saw 3 windows, 0 safety divergences and 5
  design divergences: tie-breaks between victim sets, and once the planner earlier than `gpu-lease`. It used 0.25% of a core
  and made no NVML calls.
- **Stop:** `touch /workspace/pouw/infra/cluster/live/STOP`. Any exit frees the lock, and `gpu-lease` and `fill_runner` then fall
  back to today's rules on their next poll.
- **The canary (compute-accounting and PoUW):** the 5:00 PM PDT window, attempt 67. If it lands outside the 0.13–0.15% prefill
  spread, stop the agent at once, and I'll post the stop here.
- **The rollback drill (node2-ops):** after the canary lands, as you planned.
- **Quiet by run id:** `PYTHONPATH=<tree>/tools/cluster/src python3 -m cluster ledger quiet
  /workspace/pouw/infra/cluster/live/20260930T2320Z/ledger.jsonl <run id>`.
