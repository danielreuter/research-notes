---
id: 20260930T1050Z-note-from-nebius-infra-clock-sweep-needs-a-slot
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra
cursor:
  subagentId: "bc-96a2e856-76ff-54b4-a303-b9b1e0a69896"
---

`clock-and-power-invariant` sweep (row 42) not run: at 10:45Z Kueue had all 8 of vy-nebius-1's GPUs admitted (circuits 7, provers 1) with 7 workloads pending, so there was no free GPU to take without jumping your queue. To run it, slot one `port-capture` job (1 GPU, about 20 min) with the deterministic probe command you want compared, for example a `tc_probe` FP8 sweep. While it holds the GPU, the Nebius owner (bc-96a2e856) runs that probe from the host as root at 2,100, 1,800 and 1,500 MHz and at a 400 W cap, then restores 2,100 MHz and 600 W, and labels the run `semantic-assumption clock-and-power-invariant`. It needs no Daniel decision, only the slot and the probe command.
