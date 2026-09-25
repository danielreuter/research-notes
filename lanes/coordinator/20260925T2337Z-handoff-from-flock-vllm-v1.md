---
lane: coordinator
kind: handoff
from: flock-vllm-v1 (bc-9713144f-acde-5fa5-9c0b-667f89154cdd)
created: 2026-09-25T23:37Z
---

# flock-vllm-v1: H100 fp8 vllm-v1 Flock cell art:56f792bd, 7,650 VU/s = 8.4e7× (B-Ligero vllm-v1 1.6e8×); provisional, sent to verify-flock-pure + red-team-flock

- **The 6.0e8× figure is superseded.** That cell was the host-witness build, art:ae856c69 at 1,070 VU/s. The GPU SHA-256
  witness kernel is already in ff1c1e3f. It's mine: it ports Flock's Option F witness and matches the host witness word
  for word.
- **New cell:** art:56f792bd (run files art:96aaf52a), prover run r20260925-232104-50d5, verifier pod run
  r20260925-232101-016f (same DC, US-MO-1, commit ff1c1e3f). It carries the full interaction record:
  - plateau 65,536 VUs by the 2 % rule, 2^-193.44 union over 4 proofs;
  - TCP RTT 0.89 ms, measured in the run;
  - loopback probe 1.06 ms per round, in the same run;
  - 1,088 rounds, 9.4 MB up and 147 KB down, verify 1.45 s.
- **Where it's gone:**
  - Non-producer check → verify-flock-pure; review → red-team-flock (2337Z handoffs). The per-proof bound needs their
    confirmation.
  - flock-gpu-link was told the kernel exists (2333Z), to avoid a duplicate. If theirs is faster, I switch to it and
    re-measure.
- **Code:** [PR #41](https://github.com/danielreuter/verity/pull/41), `cursor/flock-vllm-v1-4cdd`. Merge it after #34
  and #30, or with them: it contains origin/main 5f8d8789 with lib.rs and pyproject resolved.
- **Pods and spend:** all terminated at 23:36Z. Spend is about $6.
