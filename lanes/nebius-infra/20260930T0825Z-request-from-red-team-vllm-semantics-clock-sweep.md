---
id: 20260930T0825Z-request-from-red-team-vllm-semantics-clock-sweep
campaign: overnight-sep30
lane: red-team-vllm-semantics
kind: handoff
status: open
repo: danielreuter/verity
origin: red-team-vllm-semantics
cursor:
  subagentId: "bc-05c0bb3e-507d-57b1-ae79-cac14d00af0d"
---

# Request to bc-96a2e856: one clock/power sweep for `clock-and-power-invariant`

This is optional and needs no reply if the answer is no. I have rated the row **conditions**: it is shown only at the locked 2,100 MHz, plus the unlocked RunPod capture.

- **Ask:** on one Kueue GPU, while it is held for this, run the same command at three settings and keep the output digests:
  - the locked 2,100 MHz;
  - a lower locked graphics clock (for example 1,200 MHz);
  - a reduced power cap (for example 300 W).
- **Command:** `bash rt-redteam/edges_job.sh`, from the synced tree `/workspace/research/trees/red-team-vllm-semantics`. It is about 20 minutes, one GPU, no clock changes of its own. It writes the MUFU device sha256 over all 2^32 inputs, the RoPE/SiLU words, and the sm_120 mma floor probe.
- **The row holds** if the three digests are equal.
- **Timing:** not in 12:30–13:30Z. Any time before 12:30Z suits me.
