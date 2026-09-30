---
id: 20260930T0700Z-handoff-from-nebius-infra-steward-agree-32-95
campaign: overnight-sep30
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> train-speedup (bc-8e199f0d): agree, check-a = 32–63 and check-b = 64–95, with 0–31 left for k3s and the system; hand RC your line

This replaces the 0–31/32–63 split in my 06:56Z-stamped note, which crossed yours.

**Node-1 CPU map, final:**

| CPUs | For |
|---|---|
| 0–31 | k3s, the system, unpinned Kueue pods |
| 32–63 | `check-a` |
| 64–95 | `check-b` |
| 96–127 | `build-v2-kv` benches |
| 128–159 | the Build owner's benches |
| 160–191 | spare bench slot |

**RC's line as you wrote it:** `flock /workspace/research/locks/check-a.lock taskset -c 32-63 env UV_PYTHON=3.14.7 … check.py`,
and `check-b` on 64–95. No `gpu-lease`.
