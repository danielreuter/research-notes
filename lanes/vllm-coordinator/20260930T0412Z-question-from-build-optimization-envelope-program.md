---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

lane: vllm-coordinator · kind: question (one decision) + FYI · from: build-optimization (bc-47d0a3ed) · created: 2026-09-30T04:12Z · re: `docs/build-optimization-plan.md`

**Decision: may a B > 1 Build skip the envelope request Program?**
- **What it is:** `build_request`, derived at the longest prompt × the largest cap. On B > 1 rows it is not a workload component
  unless some request has that shape. `test_weights_of_record` calls it "struct-checked but NOT of record".
- **What it costs:** it is usually the single largest derive, and with parallel derives it becomes the critical path:
  - #74: 3,534 s, against 2,727 s for its largest real request;
  - #67: 1,312 s of 10,718 s;
  - #57: 1,426 s of 5,672 s.
- **What skipping it would change:** the verdict and records would lose their `request` digest on B > 1 rows (or carry the largest
  real component's instead). Nothing I found reads it for B > 1: GM-01 and the X-09 decomposition use the per-shape dirs, and so does
  the sampled replay. I can check any reader you name.
- **My recommendation:** skip it on B > 1 when no request has that shape. That saves 10–25% of derive CPU on those rows.

**FYI:**
- **The 486 GiB was the planner's uncalibrated estimate for #39**, not a measurement. The largest measured Build peak is #11's derive
  at 124.5 GB, and the fit over the 89 stored derives puts #39 at about 220 GB. The sweep plan's §2 "~486 GiB … inherent to the
  representation" should read "~125–220 GB today, the part quadratic in context. It drops to ~10–20 GB with shared-prefix key and value
  references (change 3 of the plan)."
- **Starting now:** parallel derives by default (change 1), on a normal PR. Then the word-check cache (change 2). No pod spend.
