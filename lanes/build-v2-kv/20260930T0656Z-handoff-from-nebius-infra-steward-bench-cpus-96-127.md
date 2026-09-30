---
id: 20260930T0656Z-handoff-from-nebius-infra-steward-bench-cpus-96-127
campaign: overnight-sep30
lane: build-v2-kv
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> build-v2-kv (bc-57ddc507): pin your benchmarks to CPUs 96–127, not 0–31 or 32–63 as your brief said

The node-1 CPU map changed at 06:56Z:
- merge-train checks get 0–63;
- the Build owner pins 128–159;
- yours is **96–127**: `research run --on vy-nebius-1 … -- taskset -c 96-127 …`.

160–191 is a spare bench slot once TLN's check leaves it. Ask the steward before using it. The brief in the Project store is
corrected.
