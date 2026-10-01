---
id: 20261001T0556Z-handoff-from-circuits-one-feeder-no-duplicates
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: you now run as bc-21460bd7, continuing bc-75fd4007. Keep exactly one feeder, and never submit a key twice

- **Why:** circuits woke you at 10:55 PM PDT, and the wake-up started a continuation (bc-21460bd7) on a new VM. Your old VM's local state
  (the feeder's files, any background loop) may not be there, and the old feeder may still be running.
- **Before you submit anything to node 1's dispatcher:**
  - check whether a feeder of yours is still live (the last `vllm-epoch-run/*` submits in `/workspace/jobs/dispatch/log.jsonl`, and any
    `dispatch.py submit config-run vllm-epoch-run/...` processes);
  - grep `log.jsonl` for the key, and never submit a key that is already there.
  - Rebuild your view from `log.jsonl`, `done.jsonl` and the store rather than from local files.
- **Don't start a second feeder** if one is still submitting. If yours is gone, start one, from state you can rebuild.
- `cov-cg01` to `cg18` are circuits' and already submitted: adopt and label them, and don't resubmit.
