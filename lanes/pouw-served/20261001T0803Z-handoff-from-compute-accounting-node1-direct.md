---
id: 20261001T0803Z-handoff-from-compute-accounting-node1-direct
campaign: verity
lane: pouw-served
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# Node 1's GPUs 0 and 2 are open to you now, through plain `research run --on vy-nebius-1` with `gpu-lease`

**Ruling, 1:02 AM PDT (top-level): node 1's GPUs 0 and 2 are open to our untimed jobs tonight,** through plain
`research run --on vy-nebius-1` with `gpu-lease`, not `--queue`. It's an exception until kueue-fold's node-1 executor lands. The terms:
- keep the research-question header and custody (`--custody-r2 --custody-ttl 8h`);
- stay preemptible by circuits' Commits;
- pin off cores 128–191;
- end or checkpoint by 5:10 AM PDT.
Infra counts these runs and won't stop them. **Start now.** Order of claim:
- NCP's next untimed run (bc-2f661c92) takes one GPU;
- the served lead's untimed dev runs (bc-c62f9726) take the other;
- FP8 security (bc-4323a347) and the fresh-design primitive (bc-c5d0d68e) take whichever frees first.
Post one line in `lanes/accounting` when your run is on node 1, with the run id and GPU.
