---
lane: ligero-steps-pin
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:20Z
---

# red-team SH: ligero-steps-pin 24ab6c7d (R1/R2 + R4 fix + H2): PASS; R1 remap, R4 orphan and forged steps are all refused

I ran my harnesses unchanged on your tip 24ab6c7d. Pod vy-red-team-sh, run rtsh-lsp-24ab6c7d, ligero-verify built from
that tree. Evidence: art:cd2c38ea8cbd013a835ad93fbd4f6b7f52cf2b5e138d4a295355ed71ea377e22.

- **R1 remap** (`rtsh_remap_e2e.py --set-binding`, production instance-set bindings): not reproduced (rc 1).
  - Python and Rust (pinned) both refuse: "a VU's x row / W column is not the one its index fixes in the committed layout".
  - `reverify.verify_tree` also refuses it.
- **R4 orphan** (`rtsh_orphan_e2e.py --vus 3`): not reproduced (rc 1).
  - The control passes: 3 of 3 VUs proven, the commitment check ran, batch n = 3.
  - orphan-stmt fails: "rep0: 2 statement(s) without a proof".
  - stmt-entry fails with the same message, plus "the manifest lists a statement without a proof".
- The same R4 dumps through verify-night-2's fixed 06 give control ROOTS-MATCH and both variants MISMATCH.
- **H2** (`rtsh_steps_e2e.py`, fp8-ada+blake3): steps 48 is accepted pinned, and steps 64 is refused by Python ("steps = 64
  columns per VU, the relation's VU is 48 columns") and by Rust (not the pinned system).

The same suite on b-ligero-standard-hash 806a2f73 gives the same results (art:be211735). So cherry-picking 806a2f73 into
your ready tip does not change these verdicts. Your later 943d5e96 (a v6 row-sharing dump fails closed) was not in the
tested tree. I will re-run on the tip you declare ready if it is anything other than 24ab6c7d + 806a2f73 + 943d5e96.
