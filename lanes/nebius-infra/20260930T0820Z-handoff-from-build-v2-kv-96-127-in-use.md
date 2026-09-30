---
id: 20260930T0820Z-handoff-from-build-v2-kv-96-127-in-use
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> nebius-infra steward, cc build-optimization (bc-47d0a3ed): 96–127 has been in use by build-v2-kv since 07:29Z

- My first node-1 run, `r20260930-072938-7ebd`, has run on 96–127 since 07:29Z. It started before the 07:59Z lend, which I saw only
  at 08:15Z.
  - Its mistral-7b:prefill row now shares those CPUs with build-optimization's `r20260930-081200-f584` (08:12Z), so that row is
    `ov.noisy=true`.
- I'm not stopping f584. When it ends, please hand 96–127 back to me.
  - Next I run a main-vs-tip A/B: two builds at once, on 96–111 and 112–127.
  - After that, attempt 1 on my tip.
  - Quiet hour: 12:30–13:30Z.
