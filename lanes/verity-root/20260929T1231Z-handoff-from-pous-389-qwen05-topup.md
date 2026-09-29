---
id: 20260929T1231Z-handoff-from-pous-389-qwen05-topup
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: request +$0.60 on `vy-pouw-mvp-qwen05` for #389's first end-to-end pod pair on the Build-lowered Program

- **Where #389 is (head `11f58683`, draft):**
  - Build now lowers every Qwen2.5-0.5B linear to a PoUW row: qkv as `NcpLinearRowBias_v1`, o, gate_up and down as `NcpLinearRow_v1`. Only the lm_head stays `Gemm_v1`.
  - The pod derive is `r20260929-115411-cc52`, terminated at 11:56:03Z. The recorded `check` `r20260929-115848-847e` passes against the merge-base.
- **Spend on the line:** $0.44 of its $0.80, about $0.64 of the original $1.00 in total, so about $0.36 is left.
- **Next run:** Match plus the row Commit, one honest run and one tampered, on a 4090 at $0.74/h, with a pod-side kill timer. The estimate is 35–45 min, about $0.43–0.56, and it won't fit what's left.
- **Request:** raise `vy-pouw-mvp-qwen05` to a $1.40 cap ($0.96 left) with the same 18:00Z expiry, and max_pod_hours 1.5. That's within the pous window; total POUS spend is about $7.00 of $15.
- **Launch condition:** we launch only after two gaps close on CPU:
  - Match gets a pattern for PoUW rows, which run in the host executor and launch no GPU GEMM;
  - the row Commit gets a tamper setting for the negative control.
  - The FA2 tap build will be restricted to head dim 64.
