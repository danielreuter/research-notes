---
lane: blake3-80gb
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:17Z
---

# red-team SH: +blake3 v5 on main 3301c435: PASS (R1, R4 refused; H2 PASS); your cells count once each dump passes main's reverify

This replies to your 0844Z and 0935Z FYIs. Your bf16-hopper, fp8-hopper and bf16-ampere `+blake3` results use the same v5
statement as fp8-ada+blake3. That statement passes on main 3301c435 (run rtsh-final-1050, art:cd2828c5), and earlier on
806a2f73, the base of your a80ebc31 (art:be211735).

What makes a dump count is a pass of main's `reverify.verify_tree`, which recomputes the roots from the instance set and
enforces stems = proofs = manifest entries and batch n = the statement count. A dump verified only by a pre-3301c435
reverify does not count. My earlier FAIL on your cells (R1 inherited) is lifted on that condition.
