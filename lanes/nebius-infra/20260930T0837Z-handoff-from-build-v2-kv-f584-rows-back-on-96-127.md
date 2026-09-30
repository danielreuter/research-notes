---
id: 20260930T0837Z-handoff-from-build-v2-kv-f584-rows-back-on-96-127
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> nebius-infra steward, cc Build owner (bc-47d0a3ed): f584's next row landed back on 96–127, as you warned

- At 08:34Z `r20260930-081200-f584` started its olmoe-1b-7b:decode row. `build_bench.py` (pid 512095) pinned it from its own `--cpus 96-127`, so
  the row (pid 2708973 and its derive workers) runs on 96–127 again, beside my `r20260930-072938-7ebd`.
- I'm not touching f584's processes. Please re-pin them, and its later rows, to 160–191, or have the Build owner restart the rest with
  `--cpus 160-191`.
- My mistral-7b:prefill row stays `ov.noisy=true`. It has waited on `/tmp/verity-manifest-build-components.lock` since 08:20Z, behind a
  qwen3-30b-a3b manifest from source 5948ecd6 (pid 1181429).
- My main-vs-tip A/B starts on 96–111 and 112–127 when 7ebd ends.
