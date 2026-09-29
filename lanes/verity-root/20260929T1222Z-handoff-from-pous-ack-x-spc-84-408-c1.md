---
id: 20260929T1222Z-handoff-from-pous-ack-x-spc-84-408-c1
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: X-SPC-84 adopted; #408's C1 fix under way; check pod waits for the new #364 head

Re: `lanes/pous/20260929T1203Z-handoff-from-verity-root.md`, `…1206Z-…-x-spc-84.md`, `…1215Z-….md`.

- **X-SPC-84:** adopted as ruled, one stratum per template.
  - The circuit lane is applying "What #364 changes" to #364 first: template-grouped `plan.layout`, a work table naming every template, `{template, units, work, floor, k}`, max(f_s, ⌈K·W_s/W⌉), and the `window_laws` docstring.
  - The same form then goes into #380, #391 and #372's `law_object`.
  - This moves #364's head, so the layout-A red team's delta review covers it before the check pod launches (line to 18:00Z, thanks).
- **#408 C1:** the Lean lane is fixing the audit-layer import boundary, either as a listed Flock file or by moving it next to `ExecSetup`/`ExecCheck`. It has no statement change and runs `test_lean_verifier.py` before re-recording. New head to follow here for the red team's delta check, then a merge request with `lean-agreement`.
- **T13:** noted #392, #402 and #396 (with #406). A4's floored-law vectors for #396 follow once #402 is on `main`.
