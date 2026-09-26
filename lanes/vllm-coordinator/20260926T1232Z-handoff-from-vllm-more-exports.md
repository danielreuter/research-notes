---
lane: vllm-coordinator
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T12:32Z
---

# vllm-more-exports: H100 terminated (#74 Commit can't fit 251 GB); #67 may pass 13:30Z. Please keep vyv-more-exports-moe until 14:30Z, within my $30

- **vyv-more-exports-h100 terminated at 12:29Z.** All 6 runs are preserved, about $15.4.
  - #74 passed Build and Match; the Match needed the 32 MiB snapshot cap of record, because the derived cap thrashed at 234 GiB.
  - The unbounded Commit needs about 300 GiB: 197 GiB of pinned staging, of which the FA3 hidden stream is 136 GiB, plus 69 GiB of C2 Programs objects. I stopped it before it OOM'd.
  - `--bounded-staging --retain-exclude fa3_hidden_m1` would fit (158 GiB bound). It crashes in finalize with `vllm_v1.fold`: "leaf must be a 32-byte digest" (`r20260926-115930-46a1`).
  - So #74 has no export. It needs a host with at least 320 GB, or a fix to the bounded/exclude finalize. The FP8 lanes have been told.
- **vyv-more-exports-moe (#67, `r20260926-082002-43e0`)** passed Build and Match. Its Commit coverage is OK and the C2 compare is 16120/16120 equal. The sampled replay has run since 11:40Z, then comes the export (600 s cap).
  - Memory is fine: 158 of 217 GiB non-reclaimable, with no limit hits.
  - The end may pass 13:30Z. At $2.18/h my $30 lasts on this pod alone until about 14:40Z.
  - **Ask:** keep this pod past 13:30Z, to 14:30Z at most. I'll terminate at $30 whatever state it's in.
- **Spend:** about $25.2 at 12:32Z.
