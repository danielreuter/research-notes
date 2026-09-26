---
lane: vllm-coordinator
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T13:23Z
---

# vllm-more-exports: both pods terminated (12:29Z, 13:20Z) at about $26.7 of $30. No captured sets: #74's Commit doesn't fit 251 GB, #67's export drew 0 VUs. FINAL next

- **Pods:** vyv-more-exports-h100 was terminated at 12:29Z (6 runs preserved, about $15.4). vyv-more-exports-moe was terminated at 13:20Z (2 runs preserved, about $11.4). None of mine is running.
- **#74** (`r20260926-101428-71e2`, `r20260926-115930-46a1`) passed Build and Match, but the Match needed the 32 MiB snapshot cap: the derived cap thrashed at 234 GiB.
  - The unbounded Commit needs about 300 GiB: 197 GiB of pinned staging (the FA3 hidden stream is 136 GiB of it) plus 69 GiB of C2 Programs objects.
  - `--bounded-staging --retain-exclude fa3_hidden_m1` would fit, but it crashes in finalize (`vllm_v1.fold`: "leaf must be a 32-byte digest").
  - **Needs:** an H100 host with at least 320 GB RAM, or that finalize fixed. This bears on goal 8's #73/#74: the same Commit memory applies.
- **#67** (`r20260926-082002-43e0`) passed Build, Match and the Commit through the sampled replay. Coverage was 406220 with 0 missing (the epoch's run had 20,928 missing), C2 was 16120/16120 equal, and the replay had 0 failed.
  - The default-on export stored 0 VUs: `vu_store`'s `max_seconds` clock includes a population build of more than 18 minutes over 33 request Programs, so it expires before the first draw.
  - I stopped the run at 13:17Z for the budget and deadline. Its Commit evidence is copied into the run's `evidence/`.
  - This affects every large default-on row. I've sent the finding to vllm-vu-export.
- **Exporter code:** PR #63, with the FP8 block and MoE expert coordinates the rows would have needed. Merge request to the research coordinator at 1322Z. The FP8 lanes were told (1228Z).
