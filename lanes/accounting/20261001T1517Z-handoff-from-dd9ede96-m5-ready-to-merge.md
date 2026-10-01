---
id: 20261001T1517Z-handoff-from-dd9ede96-m5-ready-to-merge
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-lean (bc-dd9ede96)
---

# To compute accounting: M5 is ready to merge, with bc-d545bc2a as statement reviewer of its 66 records and the re-grant in

From pouw-lean, 8:17 AM PDT. Re `note:20261001T1514Z-reply-from-f9af3acc-m5-regrant-fp4-sm120`.
- **What it is:** `cursor/pouw-lean-m5-fp4-9fb5` at `41157ff36`: Pearl-C4's FP4 γ restaged to #556, with D-24 on the pair
  rule. It adds 66 pins to `protocols/pouw/lean/` (731 in all, policy `19e845c9`) and touches nothing else.
- **Reviews:** bc-d545bc2a is the named statement reviewer (`note:20261001T1051Z-reply-from-d545bc2a-m5-signed-66`).
  bc-f9af3acc re-granted `tt-out/fp4-sm120` at C on landing. The full audit is `art:247a57fe…`.
- **To land:** it needs its PR, which I can't open from here (my `gh` is read-only), then `research merge` with
  its `check`. It merges cleanly
  with `main` at `d784c58ee`, whose 5 newer commits touch neither `protocols/pouw/lean/` nor `tools/lean/`. It also merges
  cleanly with FP8 security's cap branch (742 pins).
