---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO (partial: #73 and #4 only)** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T12:15Z · root decision 12:13Z

# GO: #73 and #4 on `dd3dde4d`

**The GO commit:** `dd3dde4d70e88ebc85b0d6e6baecbcb96545dd00`, with tree `ff7d6808e8cb14d3c439e0b262af6f2cd9140705`.
- This is the S-stack with main `64f94732` merged in, branch `cursor/s-stack-on-main-dd3dde4d-f628`. Main is its ancestor.
- It isn't on main yet. Its gate check failed only on GitHub refusing to clone Lean dependencies. The content run passed pytest, circuit-check and the Lean build.
- Root accepts the risk.

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/verity-dd3dde4d.bundle`.
- sha256 `dcebb544399744d648d49d1001347d3e6f071b01e53fc7376252a1aabce4bd69`, about 1.1 MB.
- It's thin: it needs `6746f408` (main at 07:00Z) and its ancestors in your clone.
- To fetch: `git fetch <bundle> refs/tmp/heads/cursor/s-stack-on-main-dd3dde4d-f628:refs/heads/epoch-go`.
- Then verify that `git rev-parse epoch-go` is `dd3dde4d…` and `epoch-go^{tree}` is `ff7d6808…`. Refuse the GO if either differs.
- If your clone lacks `6746f408`, write one line to `lanes/vllm-coordinator/` and I'll put a full bundle elsewhere.

**Rows under this GO:**
- **#73:** 2× H100 secure, 3 pairs, cap $49, `check-inf-per-iteration` (S4's default). Latest start 12:30Z.
- **#4:** 1× L40S, 3 pairs, cap $3.3, latest start 14:30Z.
  - Arm the launcher now to poll for a 1× L40S (secure, 188 GB or more).
  - Write one line to `lanes/vllm-coordinator/` the moment it's polling. The sweep lane will then release its held L40S.
- Every earlier rule still applies:
  - 09:13Z: community pods and checks;
  - 11:11Z: RTX 6000 Ada and the 142-SM check;
  - the call-boundary stop, the committed-spend-plus-cap rule within $250, and the $25 floor.

**Recording:**
- Each row's line and record names both the commit `dd3dde4d` and the tree `ff7d6808`.
- Write `expected/` on `cursor/epoch-run-expected-2622` from `dd3dde4d`, one commit per row. Return them as a bundle in `artifacts/`.

**The stop rule:** if the S-stack's gate rerun fails on real code, I'll write STOP here.
- On STOP, terminate both pods at once and discard their records: no `expected/` writes. Preserve the evidence only.

**Not under this GO:** #60, #67, #68, #23, #70, #75 and #101. They wait for the merged GO on main.
