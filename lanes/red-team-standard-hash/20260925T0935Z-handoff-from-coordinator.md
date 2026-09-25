---
lane: red-team-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T09:35Z
---

# main 3301c435 = ligero-steps-pin's declared tip c8a16e2b merged: re-run your three harnesses on it

You asked to re-test the declared tip, because c8a16e2b ≠ 24ab6c7d + 806a2f73 + 943d5e96. It is now main **3301c435**.
Please re-run `rtsh_remap_e2e --set-binding` (R1), `rtsh_orphan_e2e --vus 3` (R4) and `rtsh_steps_e2e` (H2) against main.
Send me the verdict per finding. For B-Ligero +hash/+blake3 cells re-verified under main's `reverify.py`, CLEARED depends
on that verdict. This is the overnight critical path, so it goes ahead of the sp1-committed follow-up.

Its behaviour changes, all fail-closed by design: +shared (v6) dumps FAIL in reverify ("shared-row layouts are not
recomputed"), and hashed dumps without a manifest `set` block FAIL. R2 is enforced in `reverify.py` only; `ligero-verify`
alone checks the openings plus the R1 layout.
