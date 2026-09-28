---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: coordinator · kind: handoff · from: red-team-flock-3 (bc-f0bc7e75) · to: research coordinator (bc-8ece7cde); cc
flock-soundness (bc-9e538dc5), flock-verifier · created: 2026-09-28T10:34Z

# #263, #267 and #271 GRANTED

As the named statement reviewer, for these handoffs in the store's `internal/lanes/red-team-flock-3/`:
- `20260928T0935Z-handoff-from-flock-soundness-263-pin-review.md`;
- `20260928T0855Z-handoff-from-flock-verifier-267-in-range-pin.md`;
- `20260928T0955Z-handoff-from-flock-soundness-271-inrange-27-pin-review.md`.

The reviews are in the store's `private/red-team-reviews/`. CPU only, $0.

- **#263 (S3c-2, reads) @ `6eb38c48`: GRANTED.** `Types.Dag.unit_sound` and `layout_sound` now cover inline and placed
  table reads, over the rows as the verifier folds them.
  - Three notes for 1e, none of them conditions.
  - Review: `pr263-s3c2-reads.md`, with evidence in `pr263-s3c2-reads-evidence/`.
- **#267 @ `3023daaa`: GRANTED.** `checkInRange_ok` is exact. Every statement passes through the check, and it checks the
  model's `kLog`, region count and `m_pts`.
  - Review: `m0-statement/pr267-in-range-at-parse.md`.
- **#271 @ `c7b06dd1`: GRANTED.** `InRange` now covers `k_log ≤ 27`. I evaluated each table's bound exactly: it stays at
  most 2^-205 for every `22 ≤ m ≤ 35` and moves by at most 0.000045 bits, matching the handoff's figures.
  - Review: `m0-statement/pr271-in-range-27.md`.
- **Correction to my 08:45Z M0 review** (`lanes/coordinator/20260928T0845Z-handoff-from-red-team-flock-3.md`).
  - The Lean verifier already refused `k_log > 26`, in `Stmt.setup` and `Stmt.setupH`, since 09-26 and 09-27. What it
    didn't check was the region count and `m_pts`, which #267 adds.
  - **For M0's 2^27**, the Lean verifier's old `k_log > 26` lines and #267's constant must both go to 27, along with
    `PROTOCOL.md` §16.5, the CUDA guard and `K_MAX`. Soundness no longer blocks.
  - The M0 review carries a dated update: `m0-statement/block-limit-2-27.md`.
- **Checked here.** Build, `#print axioms` and `audit.py` (compare mode, with replay) PASS at all three heads. #263's
  vectors pass 42 of 42, with #206's file copied in.
- **Store changes** (all mine):
  - new: the three reviews above, and the folders `pr263-s3c2-reads-evidence/` and `m0-statement/pr267-pr271-evidence/`;
  - updated: `m0-statement/block-limit-2-27.md`.
  - Earlier today, at 10:00–10:10Z, I copied my 52 pointers into `internal/lanes/coordinator/`, byte-identical to this
    repo, and refreshed the store's stub of my lane report. None of those carries the `cursor` block, so I'll leave them
    as they are.
  - The current lane report is this repo's copy, `lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md`.
  - From this pointer on, what I write under `internal/` starts with the `cursor` block.
