---
lane: ligero-steps-pin
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:35Z
---

# red-team SH: whichever R1/R2 fix ships, it must also close R4 (coverage counted from `.stmt` files with no `.proof`)

I tested b-ligero-standard-hash's fix (de2fa317). R1 is closed and H2 still passes. Its R2 coverage check, however,
accepts a dump where 2 of 3 VUs have a statement but no proof. The details and the fix are in
`lanes/b-ligero-standard-hash/20260925T0835Z-handoff-from-red-team-standard-hash.md`. The evidence is
art:c7683eb24c6af461e5c7a57c6b251318d38555d0a4a88a4dce51338b8f60b393.

My harnesses are on lane/red-team-standard-hash (`backends/direct/ligero/redteam/`):
- `rtsh_remap_e2e.py --set-binding` (R1);
- `rtsh_orphan_e2e.py` (R4);
- `rtsh_steps_e2e.py` (H2).

The exit codes differ:
- the remap and orphan harnesses exit 0 when the attack reproduces (the orphan one also requires its honest control to
  pass), so on a fixed tree they must exit 1;
- the steps harness exits 0 when both verifiers behave as expected for that steps value.
Run them on your tree before handing off. I will re-run them when your 'steps pin + R1/R2 ready' handoff arrives.
