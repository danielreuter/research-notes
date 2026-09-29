---
id: 20260929T1801Z-handoff-from-pous-389-gate-passed
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #389 gate passed; the pair only needs the line extension

- The committer now uses every CPU thread, with bit-identical results (#389 at `53c9dfff`). A gate pod passed at
  20.1 s per forward against the 40 s limit (`r20260929-175322-92b4`, about $0.02).
- `vy-pouw-mvp-qwen05` stands at $1.64 of $2.55 and expires at 19:00Z. The honest-plus-tamper pair takes about
  75 min, so it can't finish inside the line.
- Asking again, per `20260929T1750Z-handoff-from-pous-389-line-extension`: extend to 22:00Z and raise to $2.85.
  bc-dd22acf8 starts the pair within a minute of the change landing in `budgets.toml`.
- Also still open: the `vy-pous-check364` extension to 21:00Z (no new money), per
  `20260929T1748Z-handoff-from-pous-421-ack-423-check-line`. It expired at 18:00Z.
