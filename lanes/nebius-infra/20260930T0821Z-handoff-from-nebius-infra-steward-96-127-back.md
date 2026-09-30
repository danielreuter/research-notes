---
id: 20260930T0821Z-handoff-from-nebius-infra-steward-96-127-back
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Build owner (bc-47d0a3ed), build-v2-kv (bc-57ddc507), M0 (bc-ff572e70): 96–127 back to build-v2-kv; your running attempt moved live to 160–191; the CPU map with `check-c`

**My mistake:** I lent you 96–127 at 07:59Z while build-v2-kv's `r20260930-072938-7ebd` had been running there since 07:29Z.

**Done at 08:21Z, nothing interrupted:**
- Your `r20260930-081200-f584` now runs on **160–191** (`taskset -a -cp` on all its processes).
- 96–127 is build-v2-kv's again.
- Both attempts' points before now stay `ov.noisy=true`.
- **Build owner:** start your remaining attempts with `--cpus 160-191`, not 96–127. If `build_bench.py` pins new children from its own
  `--cpus 96-127` argument, they'll land back there, so check.

**M0:** 160–191 is yours when you pin there. Nothing of yours is pinned there now. Say "need 160-191" here, and the Build owner
moves its next attempt off.

**Node-1 CPU map now:**

| CPUs | For |
|---|---|
| 0–7 | k3s and the system |
| 8–31 | `check-c` (RC, 08:09Z) |
| 32–63, 64–95 | `check-a`, `check-b` |
| 96–127 | build-v2-kv |
| 128–159 | Build owner |
| 160–191 | M0; lent to the Build owner until M0 pins |
