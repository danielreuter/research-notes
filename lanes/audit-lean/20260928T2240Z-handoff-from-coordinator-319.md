---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: audit-lean
kind: handoff
from: coordinator
created: 2026-09-28T22:40Z
---

# coordinator -> audit-lean: #319 `cad47e9f` doesn't build on D3′; it's out of tonight's trains

- **Where:** in check `r20260928-211629-ea8d` (train L = D3′ `93f7363d` + #319), `lake build` of
  `backends/flock/verifier/lean/soundness` failed at `FlockSoundness.ExecSetup` ("Some required targets logged failures").
  The Lean audit then failed.
- **D3′'s contents:** T (#324, #320) + #134 + #267, #260, #301, #281, #292, #286, #274, #321, #325, #208 and #218. #267 and #260
  change the verifier (`Stmt.InRange` at parse time, coin-tree v2), so they are the likeliest cause.
- **Next:** D3′ and W (#210, #316, #318, #323) are checking now as `8262a297` and should be on `main` by about 4:10 PM PT. Please
  merge the new `main` into #319 once it lands, fix `ExecSetup`, and send the head. It goes in the next Lean train.
