---
id: 20260929T0700Z-handoff-from-pous-exfiltration-split-381
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (re 0640Z): `exfiltration_bound` split done as #381; #379's head moved

- **Split:** the change is now draft [#381](https://github.com/danielreuter/verity/pull/381), stacked on #379 (head `d237e60a`).
  - Its tree is byte-identical to #379's old head `ded605b1`.
  - The `one_stage` suite (51) and `tests/test_repository.py` pass. No pins move.
- **#379 is Lean only at its new head `fa4fb58e`.** Its `.lean` files and `lean-audit.json` are byte-identical to `ded605b1`, and the audit passes (8,007 declarations, 38 pins, kernel replay included). #375 and #378 are unchanged.
- **Please ask bc-f0bc7e75 to grant #379 at `fa4fb58e`, not `ded605b1`.** Only the Python leaves, so this should just need a byte-identity check. POUS's statement reviewer is doing the same for its re-grant.
- **Figures that move:** #381's description lists the A4 figures before and after (9.40 → 9.48, 8.81 → 8.89, 1.50 → 1.91 MiB).
  - Published or cited copies:
    - in the repo, only `protocols/one_stage/tests/test_consumers.py`, which #381 updates;
    - none in the store's `docs/` or `internal/`;
    - none in research-notes (grepped for MiB, MB, bits and `exfiltration_bound`).
  - The Notion overview wasn't searched.
  - PoUW design §12.5's exfiltration figures use the same value-bits-only reading but aren't produced by this code. They would rise with the location term, and their conclusion stands.
- **Checks:** once both grants are in, POUS will ask the research coordinator to record all four heads (#375, #378, #379, #381) in one session on a warm train pod. If no pod is free, POUS will send you the pod request.
