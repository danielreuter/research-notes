---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answer (decision) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T17:43Z · re: `lanes/vllm-coordinator/20260929T1745Z-handoff-from-vllm-epoch-run-101-gate.md`

# #101: both changes are sanctioned. Write it with the two checks forced

**1. `step_segmentation.component_steps_equal_cap`: false → true. Sanctioned.**
- The v1 record's "1 step, 31 unsegmented" was the old single-request path's defect.
- At `14f027c3` (#231/#297/#309/#321), the Build segments all 32 steps: steps = cap = sampling events = 32, with 0 unsegmented.
- This is the move a fix makes.

**2. `stoch_value.program_splits.<request>`: `{"derived": 142}` → `32`. Sanctioned.**
- #197 made the top-p split count a per-step constant, and #231 bound it into `GumbelTopPTokenSelect_v2{V,S}`.
- So the Program now carries S itself, where the old one carried the SM count it was derived from.
- `SplitsFor_v1(1, 142) = 32` (registry `topp_split`: 142 SMs, B1..B4 → 32), which is exactly the constant this row must have. It's a representation move from the epoch's own changes, not a regression.

**Write it:**
- Force exactly these two checks, and no others.
- The write commit names both, with this note as the reason, and the recovered record `art:90d543d8…` and the inputs `art:0491d23c…` / `art:5c84f58d…`.
- The row's digest line says "written (recovered off-pod; 2 checks sanctioned)".

**#422:** I'll review it and send its merge request.
